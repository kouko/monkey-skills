#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
sector_classifier.py — pure-function sector classification for analysis-comps.

Reads two yaml SoT files in references/:
  - sector-routing.yaml   — (sector, industry_pattern) → schema_id ordered rules
  - sector-overrides.yaml — issuer-level override map

Library API:
    from sector_classifier import classify, ClassificationResult
    result = classify(ticker="JPM", sector="Financial Services", industry="Banks - Diversified")
    # result.schema_id == "bank"
    # result.source    == "industry_match"
    # result.matched_rule == "industry_contains:Bank"

CLI (debug):
    uv run sector_classifier.py --ticker JPM --sector "Financial Services" --industry "Banks - Diversified"
    uv run sector_classifier.py --schema-list   # list all known schema_ids

The classifier is a Layer-2 pure function: no network, no file I/O beyond
loading the two yamls at module import time. Per ADR-0008 single-consumer
model — analysis-comps owns this; no MCP exposure.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# Resolve references/ relative to this script (scripts/sector_classifier.py
# → ../references/).
_REFERENCES_DIR = Path(__file__).resolve().parent.parent / "references"
_ROUTING_PATH = _REFERENCES_DIR / "sector-routing.yaml"
_OVERRIDES_PATH = _REFERENCES_DIR / "sector-overrides.yaml"

# Canonical schema_ids — every value emitted by classify() must appear here.
# Drift rule: adding a schema_id means adding references/schema-<id>.json.
KNOWN_SCHEMA_IDS: tuple[str, ...] = (
    "default",
    "bank",
    "insurance",
    "asset-manager",
    "reit",
    "tech-saas",
    "tech-semis",
    "energy",
    "utilities",
)


@dataclass(frozen=True)
class ClassificationResult:
    """Result of sector classification.

    Attributes:
        schema_id:     One of KNOWN_SCHEMA_IDS.
        source:        How the classification was reached:
                       'override'        — matched sector-overrides.yaml
                       'industry_match'  — matched a sector's industry_contains rule
                       'sector_default'  — matched a sector's _default fallback
                       'unknown_sector'  — sector missing or absent from routing.yaml
        matched_rule:  Human-readable description of the matching rule
                       (e.g. "industry_contains:Bank" / "sector_default:Energy" /
                        "override:JPM" / "unknown_sector_fallback").
        note:          Override note (when source == 'override') or None.
    """
    schema_id: str
    source: str
    matched_rule: str
    note: str | None = None


# -- YAML loading -----------------------------------------------------------

def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"sector_classifier required yaml missing: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must be a yaml mapping at top level; got {type(payload).__name__}")
    return payload


def _validate_routing(routing: dict[str, Any]) -> None:
    """Sanity-check sector-routing.yaml shape early — fail loud, not silent."""
    if "routes" not in routing or not isinstance(routing["routes"], dict):
        raise ValueError("sector-routing.yaml must contain top-level `routes:` mapping")
    fallback = routing.get("unknown_sector_fallback")
    if fallback not in KNOWN_SCHEMA_IDS:
        raise ValueError(
            f"sector-routing.yaml unknown_sector_fallback={fallback!r} not in KNOWN_SCHEMA_IDS"
        )
    for sector, rules in routing["routes"].items():
        if not isinstance(rules, list):
            raise ValueError(f"routes[{sector!r}] must be a list of rules; got {type(rules).__name__}")
        for idx, rule in enumerate(rules):
            if not isinstance(rule, dict):
                raise ValueError(f"routes[{sector!r}][{idx}] must be a mapping")
            if "_default" in rule:
                if rule["_default"] not in KNOWN_SCHEMA_IDS:
                    raise ValueError(
                        f"routes[{sector!r}][{idx}] _default={rule['_default']!r} not in KNOWN_SCHEMA_IDS"
                    )
            elif "industry_contains" in rule:
                if rule.get("schema") not in KNOWN_SCHEMA_IDS:
                    raise ValueError(
                        f"routes[{sector!r}][{idx}] schema={rule.get('schema')!r} not in KNOWN_SCHEMA_IDS"
                    )
            else:
                raise ValueError(
                    f"routes[{sector!r}][{idx}] must have either `industry_contains` or `_default` key"
                )


def _validate_overrides(overrides: dict[str, Any]) -> None:
    if "overrides" not in overrides:
        raise ValueError("sector-overrides.yaml must contain top-level `overrides:` mapping")
    if not isinstance(overrides["overrides"], dict):
        raise ValueError("`overrides:` must be a mapping ticker → {schema, note}")
    for ticker, entry in overrides["overrides"].items():
        if not isinstance(entry, dict):
            raise ValueError(f"overrides[{ticker!r}] must be a mapping; got {type(entry).__name__}")
        if entry.get("schema") not in KNOWN_SCHEMA_IDS:
            raise ValueError(
                f"overrides[{ticker!r}] schema={entry.get('schema')!r} not in KNOWN_SCHEMA_IDS"
            )
        if not entry.get("note"):
            raise ValueError(
                f"overrides[{ticker!r}] missing required `note` field — every override must "
                f"document its rationale (audit policy)"
            )


# Loaded lazily and cached at module level.
_ROUTING: dict[str, Any] | None = None
_OVERRIDES: dict[str, Any] | None = None


def _routing() -> dict[str, Any]:
    global _ROUTING
    if _ROUTING is None:
        _ROUTING = _load_yaml(_ROUTING_PATH)
        _validate_routing(_ROUTING)
    return _ROUTING


def _overrides() -> dict[str, Any]:
    global _OVERRIDES
    if _OVERRIDES is None:
        _OVERRIDES = _load_yaml(_OVERRIDES_PATH)
        _validate_overrides(_OVERRIDES)
    return _OVERRIDES


# -- Classification ---------------------------------------------------------

def classify(
    ticker: str | None,
    sector: str | None,
    industry: str | None,
) -> ClassificationResult:
    """Classify (ticker, sector, industry) → schema_id + provenance.

    Resolution order:
      1. ticker in sector-overrides.yaml → override
      2. sector in routing → walk rules in order:
           - industry_contains substring match (case-insensitive) → industry_match
           - _default → sector_default
      3. otherwise → unknown_sector fallback

    All inputs may be None / empty; the function never raises on input
    shape (only on yaml validation failures, which fire at load time).
    """
    overrides = _overrides()["overrides"]
    if ticker and ticker in overrides:
        entry = overrides[ticker]
        return ClassificationResult(
            schema_id=entry["schema"],
            source="override",
            matched_rule=f"override:{ticker}",
            note=entry.get("note"),
        )

    routing = _routing()
    routes = routing["routes"]
    fallback = routing.get("unknown_sector_fallback", "default")

    if not sector or sector not in routes:
        return ClassificationResult(
            schema_id=fallback,
            source="unknown_sector",
            matched_rule="unknown_sector_fallback",
        )

    industry_lower = (industry or "").lower()
    for rule in routes[sector]:
        if "_default" in rule:
            return ClassificationResult(
                schema_id=rule["_default"],
                source="sector_default",
                matched_rule=f"sector_default:{sector}",
            )
        pattern = rule["industry_contains"]
        if pattern.lower() in industry_lower:
            return ClassificationResult(
                schema_id=rule["schema"],
                source="industry_match",
                matched_rule=f"industry_contains:{pattern}",
            )

    # Should not happen if routing yaml is well-formed (every sector has
    # _default last) — fall back to global default.
    return ClassificationResult(
        schema_id=fallback,
        source="unknown_sector",
        matched_rule=f"sector_default_missing:{sector}",
    )


def classify_pack(pack: dict[str, Any]) -> ClassificationResult:
    """Convenience: classify from a comps-multiples pack JSON.

    Reads `ticker` + `info[ticker].sector` + `info[ticker].industry`.
    Falls back gracefully when pack shape is partial.
    """
    ticker = pack.get("ticker")
    info_block: dict[str, Any] = {}
    if isinstance(pack.get("info"), dict):
        if ticker and ticker in pack["info"]:
            info_block = pack["info"][ticker] or {}
        elif len(pack["info"]) == 1:
            # Resolve ticker by sole info{} key
            ticker = next(iter(pack["info"].keys()))
            info_block = pack["info"][ticker] or {}
    return classify(
        ticker=ticker,
        sector=info_block.get("sector"),
        industry=info_block.get("industry"),
    )


# -- CLI --------------------------------------------------------------------

def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify (ticker, sector, industry) → schema_id (debug helper for analysis-comps)."
    )
    parser.add_argument("--ticker", required=False, help="Ticker symbol (for override lookup)")
    parser.add_argument("--sector", required=False, help="yfinance info.sector")
    parser.add_argument("--industry", required=False, help="yfinance info.industry")
    parser.add_argument(
        "--pack", type=Path, default=None,
        help="Path to a comps-multiples pack JSON (auto-extracts ticker/sector/industry)",
    )
    parser.add_argument(
        "--schema-list", action="store_true",
        help="Print known schema_ids and exit",
    )
    args = parser.parse_args()

    if args.schema_list:
        for sid in KNOWN_SCHEMA_IDS:
            print(sid)
        return 0

    if args.pack is not None:
        try:
            pack = json.loads(args.pack.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"[sector_classifier ERROR] cannot read pack {args.pack}: {exc}\n")
            return 1
        result = classify_pack(pack)
    else:
        result = classify(
            ticker=args.ticker,
            sector=args.sector,
            industry=args.industry,
        )

    json.dump(
        {
            "schema_id":    result.schema_id,
            "source":       result.source,
            "matched_rule": result.matched_rule,
            "note":         result.note,
        },
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
