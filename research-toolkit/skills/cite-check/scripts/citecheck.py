"""Cite-check schemas + support-verdict logic.

Holds the cite-check-specific JSON Schemas and verdict normalization,
kept OUT of the copied byte-identical `schemas.py`/`prompts.py` so the
MD5 sync check against deep-research stays clean.

Two binding schemas (JSON-Schema dicts, same dict style as schemas.py):
  - EXTRACT_CITED_CLAIMS — claim↔citation binding output shape.
  - SUPPORT_VERDICT       — per-citation 3-way support verdict.

Verdict logic:
  - classify_support(verdict_obj) -> {"support": ..., "flags": [...]}.
  - summarize(rows) -> audit summary counts.

CLI: `python citecheck.py verdict` reads a JSON array of per-citation
support objects from stdin and prints an audit summary object to stdout.
(The markdown report renderer + `report` subcommand are added in C5.)
"""
from __future__ import annotations

from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# JSON Schemas (cite-check-specific; dict style mirrors schemas.py)
# ---------------------------------------------------------------------------

# Stage-1 binding output: deterministic parse anchors bound to claims by the
# agent's LLM. Each item ties one claim to one cited source + a locator.
EXTRACT_CITED_CLAIMS = {
    "type": "object",
    "required": ["claims"],
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["claim"],
                "properties": {
                    "claim": {"type": "string"},
                    # exactly one of citedUrl / citedRef is expected per claim;
                    # citedRef carries a non-URL reference (flag-and-skip in v1).
                    "citedUrl": {"type": "string"},
                    "citedRef": {"type": "string"},
                    "locator": {"type": "string"},
                },
            },
        },
    },
}

# Stage-3 per-citation support verdict (3-way + flags + evidence quote).
SUPPORT_VERDICT = {
    "type": "object",
    "required": ["support"],
    "properties": {
        "support": {"enum": ["supported", "partial", "unsupported"]},
        # the cited source talks about a DIFFERENT claim than the one cited for.
        "misattributed": {"type": "boolean"},
        # the cited source could not be fetched (dead / paywalled / 404).
        "unresolvable": {"type": "boolean"},
        # a verbatim quote from the cited source backing the support call.
        "evidence": {"type": "string"},
    },
}

# Valid 3-way support values from the schema enum.
SUPPORT_STATES = tuple(SUPPORT_VERDICT["properties"]["support"]["enum"])

# All buckets the audit summary rolls up. The three support states plus the
# two flags plus the "no resolvable citation" class.
COUNT_KEYS = (
    "supported",
    "partial",
    "unsupported",
    "misattributed",
    "unresolvable",
    "unsourced",
)


# ---------------------------------------------------------------------------
# Verdict normalization
# ---------------------------------------------------------------------------


def classify_support(verdict_obj: Dict) -> Dict:
    """Normalize one raw support verdict into {"support", "flags": [...]}.

    Rules:
      - unresolvable=True overrides everything → support="unresolvable"
        (a dead/paywalled source cannot support OR refute a claim).
      - missing/empty support with no flags → support="unsourced"
        (the claim had no resolvable citation to check against).
      - misattributed is a FLAG, not a support state — the support call
        still stands (supported/partial/unsupported), but the audit notes
        the source was cited for the wrong claim.

    Fails loud on a non-dict input or an out-of-enum support value.
    """
    if not isinstance(verdict_obj, dict):
        raise TypeError(
            f"classify_support expects a dict verdict, got {type(verdict_obj).__name__}"
        )

    flags: List[str] = []
    unresolvable = bool(verdict_obj.get("unresolvable"))
    misattributed = bool(verdict_obj.get("misattributed"))
    if misattributed:
        flags.append("misattributed")

    if unresolvable:
        flags.append("unresolvable")
        return {"support": "unresolvable", "flags": flags}

    raw = verdict_obj.get("support")
    if raw is None:
        # no support call and not unresolvable → no citation was resolved.
        return {"support": "unsourced", "flags": flags}
    if raw not in SUPPORT_STATES:
        raise ValueError(
            f"invalid support value {raw!r}; expected one of {SUPPORT_STATES}"
        )
    return {"support": raw, "flags": flags}


def summarize(rows: List[Dict]) -> Dict:
    """Roll up a list of raw per-citation support objects into audit counts.

    Returns {"counts": {<each COUNT_KEYS>: int}, "total": int}.
    A row contributes to exactly one of the mutually-exclusive support
    buckets (supported/partial/unsupported/unresolvable/unsourced) AND
    additionally increments `misattributed` when that flag is set.
    """
    if not isinstance(rows, list):
        raise TypeError(f"summarize expects a list, got {type(rows).__name__}")

    counts = {key: 0 for key in COUNT_KEYS}
    for row in rows:
        norm = classify_support(row)
        counts[norm["support"]] += 1
        if "misattributed" in norm["flags"]:
            counts["misattributed"] += 1
    return {"counts": counts, "total": len(rows)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or args[0] != "verdict":
        name = args[0] if args else "(none)"
        print(
            f"unknown subcommand {name!r}; expected one of {{verdict}}",
            file=sys.stderr,
        )
        return 1

    rows = json.load(sys.stdin)
    print(json.dumps(summarize(rows), indent=2))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
