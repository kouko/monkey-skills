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

Rendering:
  - render_audit(results) -> a markdown audit report (per-citation
    verdict table + summary counts).

CLI:
  - `python citecheck.py verdict` reads a JSON array of per-citation
    support objects from stdin and prints an audit summary object.
  - `python citecheck.py report` reads the same JSON array from stdin
    and prints the markdown audit report.
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
# Markdown rendering
# ---------------------------------------------------------------------------


def _cited_source(row: Dict) -> str:
    """Pick the human-readable cited source for a result row.

    Prefers a resolvable URL; falls back to a non-URL reference; emits a
    dash when the claim carried no citation at all (unsourced).
    """
    url = row.get("citedUrl")
    if url:
        return url
    ref = row.get("citedRef")
    if ref:
        return ref
    return "—"


def _escape_cell(text: str) -> str:
    """Keep a markdown table cell on one row: escape pipes, fold newlines."""
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def render_audit(results: List[Dict]) -> str:
    """Render a list of per-citation result rows into a markdown audit report.

    A result row is a per-citation support object (same shape `summarize`
    consumes) optionally carrying `claim` / `citedUrl` / `citedRef` for
    display. The report is a per-citation verdict table (claim · cited
    source · verdict · note/flags) followed by a summary section with the
    six audit counts.

    Fails loud on a non-list input.
    """
    if not isinstance(results, list):
        raise TypeError(f"render_audit expects a list, got {type(results).__name__}")

    lines: List[str] = ["# Citation audit", ""]

    # --- per-citation verdict table ---
    lines.append("## Citations")
    lines.append("")
    lines.append("| Claim | Cited source | Verdict | Note/flags |")
    lines.append("| --- | --- | --- | --- |")
    for row in results:
        norm = classify_support(row)
        claim = _escape_cell(row.get("claim", ""))
        source = _escape_cell(_cited_source(row))
        verdict = _escape_cell(norm["support"])
        note = _escape_cell(", ".join(norm["flags"]))
        lines.append(f"| {claim} | {source} | {verdict} | {note} |")
    lines.append("")

    # --- summary counts ---
    counts = summarize(results)["counts"]
    lines.append("## Summary")
    lines.append("")
    lines.append("| Bucket | Count |")
    lines.append("| --- | --- |")
    for key in COUNT_KEYS:
        lines.append(f"| {key} | {counts[key]} |")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or args[0] not in ("verdict", "report"):
        name = args[0] if args else "(none)"
        print(
            f"unknown subcommand {name!r}; expected one of {{verdict, report}}",
            file=sys.stderr,
        )
        return 1

    rows = json.load(sys.stdin)
    if args[0] == "report":
        print(render_audit(rows))
    else:
        print(json.dumps(summarize(rows), indent=2))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
