"""Deep-read schemas + cross-chunk hierarchical synthesis + report renderer.

Holds the deep-read-specific JSON Schemas and synthesis/render logic,
kept OUT of the copied byte-identical `schemas.py`/`prompts.py`/`dedup.py`
so the MD5 drift check against deep-research stays clean.

Two binding schemas (JSON-Schema dicts, same dict style as schemas.py):
  - CHUNK_EXTRACT_SCHEMA — per-chunk extraction the agent emits (richer
    than EXTRACT_SCHEMA: a section role + claims + optional methodology /
    caveats per chunk).
  - READ_SCHEMA — the final merged structured understanding of one source.

Synthesis:
  - merge_chunks(chunk_extractions) -> dict — flatten + dedup claims across
    chunks (claim-text-normalized key), assemble `sections` in chunk order,
    preserve per-claim `section` provenance, collect methodology / caveats /
    openQuestions; produces a dict conforming to READ_SCHEMA.

Rendering:
  - render_report(understanding) -> str — a markdown READ report: a sections
    outline, a claims table (claim · section · importance · quote), then
    methodology / caveats / open-questions blocks. Table cells are escaped
    so a quote cannot break the table.

CLI:
  - `python deepread.py merge`  reads a JSON array of chunk extractions from
    stdin and prints the merged understanding object.
  - `python deepread.py report` reads a merged understanding object from
    stdin and prints the markdown report.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# JSON Schemas (deep-read-specific; dict style mirrors schemas.py)
# ---------------------------------------------------------------------------

# Per-chunk extraction shape: one chunk of a source, classified by section
# role, carrying the claims the agent pulled from it plus optional
# section-local methodology / caveats notes.
CHUNK_EXTRACT_SCHEMA = {
    "type": "object",
    "required": ["section", "claims"],
    "properties": {
        # the heading / structural role of this chunk (e.g. "Methods").
        "section": {"type": "string"},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["claim"],
                "properties": {
                    "claim": {"type": "string"},
                    # a verbatim supporting quote from the chunk.
                    "quote": {"type": "string"},
                    "importance": {"enum": ["high", "medium", "low"]},
                },
            },
        },
        # optional section-local notes folded into the merged understanding.
        "methodology": {"type": "string"},
        "caveats": {"type": "string"},
        # optional unresolved questions raised by this chunk.
        "openQuestions": {"type": "array", "items": {"type": "string"}},
    },
}

# Final merged understanding of one source: the deep-read deliverable.
READ_SCHEMA = {
    "type": "object",
    "required": ["sections", "claims"],
    "properties": {
        # an agent-supplied quality judgment of the source as a whole.
        "sourceQuality": {"type": "string"},
        # section roles in reading order.
        "sections": {"type": "array", "items": {"type": "string"}},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["claim", "section"],
                "properties": {
                    "claim": {"type": "string"},
                    "quote": {"type": "string"},
                    "importance": {"enum": ["high", "medium", "low"]},
                    # provenance: which section the claim came from.
                    "section": {"type": "string"},
                },
            },
        },
        # methodology / caveats aggregated across chunks (newline-joined).
        "methodology": {"type": "string"},
        "caveats": {"type": "string"},
        "openQuestions": {"type": "array", "items": {"type": "string"}},
        # v1: a simple ordered list of section roles (the document's spine).
        "argumentStructure": {"type": "array", "items": {"type": "string"}},
    },
}


# ---------------------------------------------------------------------------
# Cross-chunk synthesis
# ---------------------------------------------------------------------------

_WS = re.compile(r"\s+")


def _claim_key(text: str) -> str:
    """Canonical dedup key for a claim: lowercased, whitespace-collapsed,
    trailing punctuation stripped.

    Near-duplicate claims (case / spacing / a stray period) collapse to one
    key so the same point asserted in two chunks is merged, not double-counted.
    """
    folded = _WS.sub(" ", str(text)).strip().lower()
    return folded.rstrip(".!?;:, ")


def merge_chunks(chunk_extractions: List[Dict]) -> Dict:
    """Flatten + dedup chunk extractions into one READ_SCHEMA understanding.

    - `sections` / `argumentStructure`: the chunk `section` roles in chunk
      order (deduped, first occurrence wins).
    - `claims`: every chunk claim, tagged with its source `section`
      provenance; near-duplicate claims across chunks collapse to the first
      occurrence (claim-text-normalized key).
    - `methodology` / `caveats`: newline-joined across chunks that carry them.
    - `openQuestions`: concatenated across chunks (deduped, order-preserving).

    Fails loud on a non-list input.
    """
    if not isinstance(chunk_extractions, list):
        raise TypeError(
            f"merge_chunks expects a list, got {type(chunk_extractions).__name__}"
        )

    sections: List[str] = []
    claims: List[Dict] = []
    seen_claims: set = set()
    methodology: List[str] = []
    caveats: List[str] = []
    open_questions: List[str] = []
    seen_questions: set = set()

    for chunk in chunk_extractions:
        if not isinstance(chunk, dict):
            raise TypeError(
                f"each chunk extraction must be a dict, got {type(chunk).__name__}"
            )
        section = chunk.get("section", "")
        if section and section not in sections:
            sections.append(section)

        for raw in chunk.get("claims") or []:
            if not isinstance(raw, dict):
                raise TypeError(
                    f"each claim entry must be a dict, got {type(raw).__name__}"
                )
            key = _claim_key(raw.get("claim", ""))
            if key in seen_claims:
                continue
            seen_claims.add(key)
            claims.append(
                {
                    "claim": raw.get("claim", ""),
                    "quote": raw.get("quote", ""),
                    "importance": raw.get("importance", ""),
                    "section": section,
                }
            )

        if chunk.get("methodology"):
            methodology.append(chunk["methodology"])
        if chunk.get("caveats"):
            caveats.append(chunk["caveats"])
        for q in chunk.get("openQuestions") or []:
            if q not in seen_questions:
                seen_questions.add(q)
                open_questions.append(q)

    return {
        "sourceQuality": "",
        "sections": sections,
        "claims": claims,
        "methodology": "\n".join(methodology),
        "caveats": "\n".join(caveats),
        "openQuestions": open_questions,
        "argumentStructure": list(sections),
    }


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _escape_cell(text: str) -> str:
    """Keep a markdown table cell on one row: escape pipes, fold ALL newlines.

    Mirrors cite-check's _escape_cell — folds CRLF, lone CR, and LF so a
    quote containing a pipe or line break cannot break the table.
    """
    return (
        str(text)
        .replace("|", "\\|")
        .replace("\r\n", " ")
        .replace("\r", " ")
        .replace("\n", " ")
        .strip()
    )


def render_report(understanding: Dict) -> str:
    """Render a merged understanding into a markdown READ report.

    Layout: title + optional source-quality line, a sections outline, a
    claims table (claim · section · importance · quote), then methodology /
    caveats / open-questions blocks.

    Fails loud on a non-dict input.
    """
    if not isinstance(understanding, dict):
        raise TypeError(
            f"render_report expects a dict, got {type(understanding).__name__}"
        )

    lines: List[str] = ["# Deep read", ""]

    quality = understanding.get("sourceQuality")
    if quality:
        lines.append(f"**Source quality:** {quality}")
        lines.append("")

    # --- sections outline ---
    lines.append("## Sections")
    lines.append("")
    sections = understanding.get("sections") or []
    if sections:
        for section in sections:
            lines.append(f"1. {section}")
    else:
        lines.append("_(none)_")
    lines.append("")

    # --- claims table ---
    lines.append("## Claims")
    lines.append("")
    lines.append("| Claim | Section | Importance | Quote |")
    lines.append("| --- | --- | --- | --- |")
    for claim in understanding.get("claims") or []:
        c = _escape_cell(claim.get("claim", ""))
        s = _escape_cell(claim.get("section", ""))
        imp = _escape_cell(claim.get("importance", ""))
        q = _escape_cell(claim.get("quote", ""))
        lines.append(f"| {c} | {s} | {imp} | {q} |")
    lines.append("")

    # --- methodology / caveats / open questions blocks ---
    lines.append("## Methodology")
    lines.append("")
    lines.append(understanding.get("methodology") or "_(none)_")
    lines.append("")

    lines.append("## Caveats")
    lines.append("")
    lines.append(understanding.get("caveats") or "_(none)_")
    lines.append("")

    lines.append("## Open questions")
    lines.append("")
    questions = understanding.get("openQuestions") or []
    if questions:
        for q in questions:
            lines.append(f"- {q}")
    else:
        lines.append("_(none)_")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    import json
    import sys

    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or args[0] not in ("merge", "report"):
        name = args[0] if args else "(none)"
        print(
            f"unknown subcommand {name!r}; expected one of {{merge, report}}",
            file=sys.stderr,
        )
        return 1

    payload = json.load(sys.stdin)
    if args[0] == "merge":
        print(json.dumps(merge_chunks(payload), indent=2))
    else:
        print(render_report(payload))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
