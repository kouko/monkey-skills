"""twse_ixbrl_parser.py — generic TW MOPS iXBRL fact extraction (Layer A).

Parses an already-decoded TW inline-XBRL document (the MOPS `t164sb01`
filing body, Big5-decoded by the fetch layer) into a flat list of
normalized fact records — every tagged `ix:nonFraction` (numeric) and
`ix:nonNumeric` (text) element, uniformly, including all note-level
facts. This is "full 附註" at the data layer: nothing dropped.

CRITICAL: extraction is regex-only over `ix:` tags — NEVER DOM/tree
traversal. A DOM/HTML-tree-repair parse over a real TW filing silently
drops ~85% of facts nested inside `<td>` (measured: TSMC 2330 2024Q3
DOM-iter=387 vs true=2002 — docs/loom/specs/2026-07-19-tw-ixbrl-
ingestion.md edge case #10). stdlib only (`re`) — no lxml/bs4.

Each fact record:
    {
        "concept": str,       # "ns:localname", e.g. "ifrs-full:Cash..."
        "context_ref": str,
        "raw_value": float | str,   # numeric facts: fully scaled value
                                     # (see Scaling below); text facts:
                                     # the raw text, stripped.
        "decimals": str | None,     # raw `decimals` attribute (precision
                                     # metadata; NOT the scaling driver —
                                     # see Scaling below).
        "unit": str | None,         # raw `unitRef` attribute.
        "period": dict | None,      # {"type": "instant", "instant": ...}
                                     # or {"type": "duration", "start":
                                     # ..., "end": ...} — resolved from
                                     # the fact's context_ref.
        "entity": str | None,       # resolved from the same context.
        "fact_type": "nonFraction" | "nonNumeric",
    }

Scaling: TW iXBRL numeric facts carry BOTH `scale` (the ixt:numdotdecimal
transformation exponent — the raw text is the true value divided by
10**scale, per the inline-XBRL spec) and `decimals` (rounding-precision
metadata on the recovered true value). For thousands-denominated
statement facts the two coincide (e.g. scale=3, decimals=-3, both give
x1000) — but they diverge on other facts in this same filing (e.g.
tifrs-notes:PercentageOfOwnership4 carries decimals=4/scale=-2 with raw
text "100.00"; the correct true value is 1.0 i.e. 100%, which only
`scale`-driven division recovers — a decimals-driven multiplier would
wrongly yield 0.01). This module scales by `scale` (spec-correct) and
keeps `decimals` as a passthrough metadata field on the record.

Usage (as a library import — this module exposes no CLI; it is composed
by twse_ixbrl.py, Task 5):
    import twse_ixbrl_parser
    facts = twse_ixbrl_parser.parse_ixbrl_facts(decoded_html_str)
"""
from __future__ import annotations

import re
import sys
from typing import Any

_LOG_TAG = "twse-ixbrl-parser"


def _log(stage: str, msg: str = "") -> None:
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


_CONTEXT_RE = re.compile(
    r'<xbrli:context\s+id="([^"]+)"[^>]*>(.*?)</xbrli:context>', re.S
)
_ENTITY_RE = re.compile(r"<xbrli:identifier[^>]*>([^<]*)</xbrli:identifier>", re.S)
_INSTANT_RE = re.compile(r"<xbrli:instant>([^<]*)</xbrli:instant>")
_START_RE = re.compile(r"<xbrli:startDate>([^<]*)</xbrli:startDate>")
_END_RE = re.compile(r"<xbrli:endDate>([^<]*)</xbrli:endDate>")

_FACT_RE = re.compile(r"<ix:(nonFraction|nonNumeric)\b([^>]*)>(.*?)</ix:\1>", re.S)
_ATTR_RE = re.compile(r'([\w:-]+)="([^"]*)"')


def _parse_contexts(document: str) -> dict[str, dict[str, Any]]:
    """Build context_id -> {"entity": str|None, "period": dict|None}."""
    contexts: dict[str, dict[str, Any]] = {}
    for ctx_id, body in _CONTEXT_RE.findall(document):
        entity_match = _ENTITY_RE.search(body)
        entity = entity_match.group(1).strip() if entity_match else None

        instant_match = _INSTANT_RE.search(body)
        if instant_match:
            period: dict[str, Any] | None = {
                "type": "instant",
                "instant": instant_match.group(1).strip(),
            }
        else:
            start_match = _START_RE.search(body)
            end_match = _END_RE.search(body)
            if start_match or end_match:
                period = {
                    "type": "duration",
                    "start": start_match.group(1).strip() if start_match else None,
                    "end": end_match.group(1).strip() if end_match else None,
                }
            else:
                period = None

        contexts[ctx_id] = {"entity": entity, "period": period}
    return contexts


def _parse_attrs(attr_str: str) -> dict[str, str]:
    return dict(_ATTR_RE.findall(attr_str))


def _clean_numeric_text(raw_text: str) -> float | None:
    text = raw_text.strip().replace(",", "")
    if text in ("", "-", "—"):  # blank / bare dash / em-dash placeholder
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _scaled_value(raw_text: str, attrs: dict[str, str]) -> float | None:
    value = _clean_numeric_text(raw_text)
    if value is None:
        return None
    if attrs.get("sign") == "-":
        value = -value
    scale_str = attrs.get("scale")
    if scale_str is not None:
        try:
            value = value * (10 ** int(scale_str))
        except ValueError:
            _log("bad scale attribute", f"scale={scale_str!r}, left unscaled")
    return value


def parse_ixbrl_facts(document: str) -> list[dict[str, Any]]:
    """Parse a decoded TW iXBRL document into normalized fact records.

    Extraction is regex-only over `ix:nonFraction`/`ix:nonNumeric` tags
    (see module docstring for why DOM traversal is forbidden here).
    """
    contexts = _parse_contexts(document)
    facts: list[dict[str, Any]] = []

    for tag, attr_str, raw_text in _FACT_RE.findall(document):
        attrs = _parse_attrs(attr_str)
        context_ref = attrs.get("contextRef")
        ctx = contexts.get(context_ref, {})
        if context_ref is not None and context_ref not in contexts:
            _log("context miss", f"contextRef={context_ref!r} has no <xbrli:context> definition")

        fact: dict[str, Any] = {
            "concept": attrs.get("name"),
            "context_ref": context_ref,
            "decimals": attrs.get("decimals"),
            "unit": attrs.get("unitRef"),
            "period": ctx.get("period"),
            "entity": ctx.get("entity"),
            "fact_type": tag,
        }

        if tag == "nonFraction":
            fact["raw_value"] = _scaled_value(raw_text, attrs)
        else:
            fact["raw_value"] = raw_text.strip()

        facts.append(fact)

    return facts
