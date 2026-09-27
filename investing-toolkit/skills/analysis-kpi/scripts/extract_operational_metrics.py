#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
extract_operational_metrics.py — investing-toolkit LLM-based operational metrics extraction (Level 2).

Analysis layer: takes prose text from SEC filings (MD&A, Business Description, Risk Factors,
earnings releases) and extracts operational metrics with confidence scoring and source attribution.

This is the Analysis layer (Layer 2) — pure computation, no I/O. Data layer (data-markets)
provides the raw prose text; Report layer (report-equity-memo) consumes the structured output.

Three-level extraction pipeline:
  Level 1 (data-markets): Mechanical table parsing (_parse_segment_revenue_table, _parse_tesla_operational_summary)
  Level 2 (this script): LLM prose extraction with confidence + attribution
  Level 3 (this script): Cross-validation (volume × ASP ≈ revenue, customer growth ≈ revenue growth)

Architecture:
  - This module provides PURE functions: prompt generation, response parsing, cross-validation, formatting
  - LLM CALL is OUTSIDE this module:
      * When run as standalone CLI: uses HTTP fallback (requires OPENAI_API_KEY/OPENROUTER_API_KEY; without a key falls back to regex)
      * When called from Claude Code session: caller uses Agent tool with get_llm_prompt()
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Operational metrics we extract
OPERATIONAL_METRICS = {
    "production": {"unit": "units|vehicles|barrels|boe|tonnes|count", "description": "Production volumes"},
    "deliveries": {"unit": "units|vehicles", "description": "Delivery/shipping counts"},
    "customer_count": {"unit": "count", "description": "Customer/subscriber counts"},
    "asp": {"unit": "dollars", "description": "Average selling price"},
    "headcount": {"unit": "count", "description": "Employee headcount"},
}

# Regex fallback patterns (kept for compatibility when no LLM key)
REGEX_PATTERNS = {
    "production": [
        r"(?:production|produced|manufactured)\s+(?:approximately\s+|about\s+)?([\d,]+(?:\.\d+)?)\s*(?:units?|vehicles?|barrels?|boe?|tonnes?)",
        r"(?:production\s+capacity|capacity)\s+(?:is\s+|at\s+)?([\d,]+(?:\.\d+)?)\s*(?:units?|vehicles?|barrels?|boe?|tonnes?)",
    ],
    "deliveries": [
        r"(?:deliveries?|delivered|shipped)\s+(?:approximately\s+|about\s+)?([\d,]+(?:\.\d+)?)\s*(?:units?|vehicles?)",
    ],
    "customer_count": [
        r"(?:customer\s+count|customers?|subscribers?)\s+(?:is\s+|at\s+|reached\s+|approximately\s+|about\s+)?([\d,]+(?:\.\d+)?)",
        r"(?:customer\s+base|installed\s+base)\s+(?:is\s+|at\s+|approximately\s+|about\s+)?([\d,]+(?:\.\d+)?)",
    ],
    "asp": [
        r"(?:average\s+selling\s+price|asp)\s+(?:is\s+|at\s+|approximately\s+|about\s+)?\$?([\d,]+(?:\.\d+)?)\s*(?:per\s+unit)?",
        r"(?:selling\s+price)\s+(?:averages?|averaged?)\s+\$?([\d,]+(?:\.\d+)?)",
    ],
    "revenue_by_product": [
        r"(?:revenue\s+from\s+|sales\s+of\s+)([A-Za-z\s]+)\s+(?:was\s+|totaled\s+|amounted\s+to\s+)?\$?([\d,]+(?:\.\d+)?)\s*(?:million|billion)?",
    ],
}

# ---------------------------------------------------------------------------
# LLM Prompt Generation (PURE - no I/O)
# ---------------------------------------------------------------------------

# Prompt-assembly bounds. A blind 8000-char head-truncation dropped real
# numbers past offset 8000 (live 2026-09-27: TSLA 8-K Item 2.02 kept the
# "447,450" production total but lost the "497,099" deliveries total at
# char 8013), so long texts are assembled from metric-bearing lines instead.
PROSE_PASSTHROUGH_CHARS = 8000  # short texts pass through whole
PROMPT_MAX_CHARS = 60_000       # hard budget for the assembled sample

# A line "qualifies" as metric-bearing when it carries a digit AND matches
# one of these operational keywords (same vocabulary as OPERATIONAL_METRICS).
OPERATIONAL_KEYWORD_RE = re.compile(
    r"(?:production|produced|deliver(?:y|ies|ed)?|vehicle|manufactur|"
    r"headcount|customer|subscriber|units?|capacity|sold|sales)\b",
    re.IGNORECASE,
)

SYSTEM_PROMPT = """You are a precise SEC filing analyst. Extract operational metrics from the text below.

Only extract metrics that are EXPLICITLY stated with a numeric value in the text. Do NOT infer, calculate, or estimate any values.

Output JSON with this schema:
{
  "metrics": {
    "production": {"value": "<number>", "unit": "units|vehicles|barrels|boe|tonnes|count", "confidence": 0.8-1.0, "context": "<quoted source text>"},
    "deliveries": {"value": "<number>", "unit": "units|vehicles", "confidence": 0.8-1.0, "context": "<quoted source text>"},
    "customer_count": {"value": "<number>", "unit": "count", "confidence": 0.8-1.0, "context": "<quoted source text>"},
    "asp": {"value": "<number>", "unit": "dollars", "confidence": 0.8-1.0, "context": "<quoted source text>"},
    "headcount": {"value": "<number>", "unit": "count", "confidence": 0.8-1.0, "context": "<quoted source text>"}
  }
}

Set confidence to 1.0 for explicitly stated, unambiguous numbers. Lower to 0.8 for approximate qualifiers ("approximately", "about", "over"). Omit any metric not mentioned. Parse "million" as ×1,000,000 and "billion" as ×1,000,000,000 into raw integer values. Round non-integer values to 1 decimal place."""


def _select_operational_regions(text: str) -> str:
    """Select metric-bearing lines from long filing text.

    Keeps every line that carries a digit AND an operational keyword
    (production, deliveries, customers, ASP, …) — wherever it sits in the
    filing — joined with elision markers, within PROMPT_MAX_CHARS. Lines
    without a keyword (boilerplate, risk-factor prose) are dropped so they
    cannot crowd out the numbers past a blind head-truncation offset.
    """
    lines = text.split("\n")
    keep = [False] * len(lines)
    for i, line in enumerate(lines):
        if any(ch.isdigit() for ch in line) and OPERATIONAL_KEYWORD_RE.search(line):
            keep[i] = True

    selected: list[str] = []
    budget = PROMPT_MAX_CHARS
    prev_kept = False
    for i, line in enumerate(lines):
        if not keep[i]:
            prev_kept = False
            continue
        if not prev_kept and selected:
            selected.append("[...]")
        if len(line) > budget:
            selected.append(line[:budget])
            break
        selected.append(line)
        budget -= len(line) + 1
        prev_kept = True
        if budget <= 0:
            break

    return "\n".join(selected)


def get_llm_prompt(text: str) -> tuple[str, str]:
    """
    Get the system and user prompts for LLM extraction.

    Short texts pass through whole. Long texts are assembled from
    metric-bearing regions (see _select_operational_regions) so numbers
    past a blind head-truncation offset still reach the LLM.

    Returns:
        (system_prompt, user_prompt) - ready to use with any LLM client
    """
    if len(text) <= PROSE_PASSTHROUGH_CHARS:
        sample = text
    else:
        sample = _select_operational_regions(text)
    user_prompt = f"""Extract operational metrics from this SEC filing text:\n\n{sample}"""
    return SYSTEM_PROMPT, user_prompt


def parse_llm_response(raw_response: str) -> dict | None:
    """
    Parse LLM response into standardized metric format.

    Args:
        raw_response: Raw text response from LLM (should be JSON)

    Returns:
        Standardized metrics dict or None if parsing fails
    """
    try:
        parsed = json.loads(raw_response)
    except (json.JSONDecodeError, TypeError):
        return None

    metrics = parsed.get("metrics", {})
    if not metrics:
        return None

    result: dict = {}
    for metric_name, info in metrics.items():
        if not isinstance(info, dict):
            continue
        value = info.get("value")
        if value is None:
            continue
        result[metric_name] = {
            "value": str(value),
            "confidence": info.get("confidence", 0.9),
            "source": "llm_agent",  # Indicates LLM via Agent tool
            "unit": info.get("unit", "count"),
            "extraction_method": "llm_v1_agent",
            "context": info.get("context", "")[:200],
        }

    return result if result else None


# ---------------------------------------------------------------------------
# Regex Fallback (PURE - no I/O)
# ---------------------------------------------------------------------------


def _regex_extract(text: str) -> dict | None:
    """Regex-based operational metrics extraction (fallback when no LLM available)."""
    results: dict = {}
    text_lower = text.lower()

    for metric_name, pattern_list in REGEX_PATTERNS.items():
        for pattern in pattern_list:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                match = matches[0]
                if isinstance(match, tuple):
                    if len(match) == 2:
                        if metric_name == "revenue_by_product":
                            product_name = match[0].strip()
                            value_str = match[1]
                            results[f"revenue_{product_name.replace(' ', '_')}"] = value_str.replace(",", "")
                        else:
                            value_str = match[1]
                    else:
                        value_str = match[0]
                else:
                    value_str = match
                value_str = value_str.replace(",", "")
                if re.match(r"^[\d.]+$", value_str):
                    results[metric_name] = value_str

    return results if results else None


# ---------------------------------------------------------------------------
# Cross-Validation (PURE - no I/O)
# ---------------------------------------------------------------------------


def _extract_value(metrics_dict: dict, key: str) -> float | None:
    """Extract raw numeric value from metric dict (handles both LLM and regex formats)."""
    val = metrics_dict.get(key)
    if val is None:
        return None
    if isinstance(val, dict):
        val = val.get("value")
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _cross_validate(operational_metrics: dict | None, segment_revenue: list | None) -> dict | None:
    """Cross-validate operational metrics against segment revenue and each other."""
    if operational_metrics is None and segment_revenue is None:
        return None

    validation: dict = {
        "checks": [],
        "quality_score": 1.0,
        "inconsistencies": [],
    }

    prose = operational_metrics.get("prose_operational", {}) if operational_metrics else {}
    production = _extract_value(prose, "production")
    asp = _extract_value(prose, "asp")
    deliveries = _extract_value(prose, "deliveries")
    customer_count = _extract_value(prose, "customer_count")

    # Check 1: volume × ASP ≈ segment revenue (within 20% margin)
    if production is not None and asp is not None:
        implied_revenue = production * asp
        if segment_revenue:
            for seg in segment_revenue:
                for val in seg.get("values", []):
                    if val and len(str(val)) >= 4:
                        try:
                            actual = float(val)
                            diff_pct = abs(implied_revenue - actual) / max(actual, 1)
                            if diff_pct > 0.2:
                                validation["inconsistencies"].append({
                                    "type": "volume_asp_revenue_mismatch",
                                    "production": production,
                                    "asp": asp,
                                    "implied_revenue": implied_revenue,
                                    "segment_value": actual,
                                    "diff_pct": round(diff_pct * 100, 1),
                                    "threshold_pct": 20,
                                })
                        except (ValueError, TypeError):
                            pass
                        break

    # Check 2: Customer growth consistency (placeholder for historical series)
    if customer_count is not None and segment_revenue:
        validation["checks"].append({
            "type": "customer_growth_revenue_growth_placeholder",
            "note": "Historical series needed for growth comparison; single-period values insufficient",
        })

    # Check 3: Segment revenue sums
    if segment_revenue and len(segment_revenue) > 1:
        total_from_segments = 0.0
        segment_names = []
        for seg in segment_revenue:
            vals = seg.get("values", [])
            if vals:
                try:
                    total_from_segments += float(vals[0])
                    segment_names.append(seg.get("name", "unknown"))
                except (ValueError, TypeError):
                    pass
        if segment_names:
            validation["checks"].append({
                "type": "segment_sum",
                "segment_count": len(segment_revenue),
                "summed_total": total_from_segments,
                "segments_included": segment_names,
            })

    if validation["inconsistencies"]:
        validation["quality_score"] = max(0, 1.0 - 0.3 * len(validation["inconsistencies"]))

    return validation if validation["checks"] or validation["inconsistencies"] else None


# ---------------------------------------------------------------------------
# Formatting (PURE - no I/O)
# ---------------------------------------------------------------------------


def _format_for_pack(
    tesla_operational: dict | None,
    segment_revenue: list | None,
    prose_operational: dict | None,
    cross_validation: dict | None = None,
) -> dict:
    """Format extracted metrics for memo-fetch pack output."""
    # Determine extraction level
    has_llm = False
    if prose_operational:
        for val in prose_operational.values():
            if isinstance(val, dict) and val.get("source", "").startswith("llm_"):
                has_llm = True
                break

    result: dict = {
        "extraction_level": "level2_llm" if has_llm else "level1_mechanical",
        "fields": {},
    }

    if tesla_operational:
        metrics_list = tesla_operational.get("metrics", [])
        for m in metrics_list:
            metric_name = m.get("metric", "").strip()
            values = m.get("values", [])
            if metric_name and values:
                key = metric_name.lower().replace(" ", "_").replace("/", "_")
                result["fields"][key] = {
                    "values": values,
                    "confidence": 0.95,
                    "source": "tesla_operational_summary",
                    "quarters": tesla_operational.get("quarters", []),
                    "yoy_pct": m.get("yoy_pct"),
                }

    if segment_revenue:
        for i, seg in enumerate(segment_revenue):
            name = seg.get("name", f"segment_{i}")
            period_labels = seg.get("period_labels", [])
            result["fields"][name.lower().replace(" ", "_")] = {
                "values": seg.get("values", []),
                "unit": "millions",
                "confidence": 0.9,
                "source": "segment_table",
                "period_labels": period_labels,
            }

    if prose_operational:
        for metric_name, value in prose_operational.items():
            if isinstance(value, dict):
                result["fields"][metric_name] = dict(value)
            else:
                result["fields"][metric_name] = {
                    "value": value,
                    "confidence": 0.7,
                    "source": "prose_extraction",
                    "extraction_method": "regex_pattern_match",
                }

    if cross_validation:
        result["cross_validation"] = cross_validation

    return result


# ---------------------------------------------------------------------------
# Main Pipeline Functions (PURE - no I/O except regex)
# ---------------------------------------------------------------------------


def _llm_extract_via_http(text: str) -> dict | None:
    """HTTP fallback for standalone CLI: call an OpenAI-compatible LLM endpoint.

    Requires OPENAI_API_KEY/OPENROUTER_API_KEY in the environment; returns None
    (caller falls back to regex) when no key is set. In Claude Code sessions the
    caller should use the Agent tool with get_llm_prompt() instead of this path.
    """
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return None

    # Only invoke LLM when text is long enough to benefit
    if len(text) < 500:
        return None

    system_prompt, user_prompt = get_llm_prompt(text)

    try:
        import httpx
    except ImportError:
        return None

    api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")

    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"},
    }

    try:
        resp = httpx.Client(timeout=30.0).post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        raw = data["choices"][0]["message"]["content"]
        return json.loads(raw)
    except Exception:
        return None


def extract_operational_metrics_from_prose(text: str) -> dict | None:
    """
    Main entry: extract operational metrics from prose.

    For Claude Code sessions, the caller should:
    1. Call get_llm_prompt(text) to get prompts
    2. Use Agent tool to call LLM with those prompts
    3. Call parse_llm_response(agent_response) to parse result

    For standalone CLI, this function provides HTTP fallback if API key available.

    Args:
        text: Prose text to extract from

    Returns:
        Extracted metrics dict or None if no metrics found
    """
    # Try LLM extraction via HTTP (standalone CLI; requires API key).
    # In Claude Code sessions the caller uses the Agent tool directly
    # with get_llm_prompt() + parse_llm_response() instead.
    llm_result = _llm_extract_via_http(text)
    if llm_result and llm_result.get("metrics"):
        return parse_llm_response(json.dumps(llm_result))

    # Level 1: Fall back to regex pattern matching
    return _regex_extract(text)


def extract_operational_metrics(
    filings: list[dict],
    segment_revenue: list[dict] | None = None,
) -> dict | None:
    """Full extraction pipeline from memo-fetch filings data.

    Args:
        filings: List of filing dicts with sections containing text_path
        segment_revenue: Optional pre-extracted segment revenue tables

    Returns:
        Formatted operational metrics dict with extraction_level, fields, cross_validation
    """
    # Parse filings structure
    if isinstance(filings, dict):
        filings_rows = filings.get("filings", [])
    else:
        filings_rows = filings

    out: dict = {}

    # Collect prose text from relevant sections
    prose_texts: list[str] = []

    for f in filings_rows:
        role = f.get("role", "")
        if role not in ("8-K", "10-K"):
            continue
        for s in f.get("sections", []):
            text_path = s.get("text_path", "")
            if not text_path or not Path(text_path).exists():
                continue
            text = Path(text_path).read_text(encoding="utf-8", errors="ignore")

            # Tesla Operational Summary (8-K Item 2.02)
            if "Operational Summary" in text or (role == "8-K" and "production" in text.lower()):
                # Note: Tesla parsing stays in data-markets Level 1
                pass

            # Segment revenue tables
            KNOWN_APPLE_SEGMENT_NAMES = {
                "iphone", "mac", "ipad", "wearables", "home and accessories",
                "products", "services",
                "americas", "europe", "greater china", "japan", "rest of asia pacific",
                "total net sales", "total gross margin", "research and development",
                "selling, general and administrative", "total operating expenses",
                "provision for income taxes",
            }
            if "Net sales by" in text or "Revenue by" in text or ("Segment" in text and "$" in text):
                # Handled by Level 1 parser in data-markets
                pass

            # Collect prose for LLM extraction
            prose_texts.append(text)

    # Combine all prose text for LLM extraction
    if prose_texts:
        combined_text = "\n\n---\n\n".join(prose_texts)
        prose_metrics = extract_operational_metrics_from_prose(combined_text)
        if prose_metrics:
            out["prose_operational"] = prose_metrics

    # Cross-validation
    cross_val = _cross_validate(
        {"prose_operational": out.get("prose_operational", {})} if out.get("prose_operational") else None,
        segment_revenue,
    )
    if cross_val:
        out["cross_validation"] = cross_val

    # Format for pack output
    formatted = _format_for_pack(
        out.get("tesla_operational"),
        segment_revenue,
        out.get("prose_operational"),
        cross_val,
    )

    return formatted


# ---------------------------------------------------------------------------
# CLI (uses HTTP for LLM)
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract operational metrics from SEC filing prose")
    parser.add_argument("--text", type=str, help="Prose text to extract from (stdin if not provided)")
    parser.add_argument("--text-file", type=str, help="File containing prose text")
    parser.add_argument("--segment-revenue", type=str, help="JSON file with segment revenue data")
    parser.add_argument("--output", type=str, help="Output file (stdout if not provided)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    # Read input text
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    # Read segment revenue if provided
    segment_revenue = None
    if args.segment_revenue:
        segment_revenue = json.loads(Path(args.segment_revenue).read_text(encoding="utf-8"))

    # Extract
    result = extract_operational_metrics_from_prose(text)
    if result is None:
        result = {}

    # Write output
    output_json = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())