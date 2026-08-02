"""Structural grep-window tests guarding the `origin:` finding field
shipped by `docs/loom/plans/2026-08-02-finding-origin-attribution.md`.

Task 3 pins `origin:` into `code-reviewer.md`'s finding schema: the
field names an upstream artifact ONLY when the reviewer holds a
verbatim quote of the wrong statement, and writes `none` otherwise
with no penalty for doing so. Grammar transcribed verbatim from the
plan's `## Notes` "§Pinned field grammar":

    origin: none
    origin: <path> :: "<verbatim quote from that file>"

Scope: measured neighbourhood window per
`docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md` — the
`findings:` block through `### Aggregation rule` — not the whole file,
which is long enough that a whole-file substring check would go
false-green on an unrelated occurrence of a generic word like "quote"
or "none".

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

CODE_REVIEWER_MD = Path(__file__).parents[1] / "agents" / "code-reviewer.md"

# Two DISTINCT windows, split at the schema code fence's closing ```:
#   1. schema fields  — the indented `- severity: ...` list itself, still
#      inside the fence. Field lines here are indented (leading
#      whitespace); this is what tells the block apart from the later
#      verbatim grammar recap below, whose lines start at column 0.
#   2. explanatory prose — from the fence close through "### Aggregation
#      rule", where the quote-gate rule and the `none` fallback are
#      stated in prose (plus, inside it, the verbatim grammar recap).
_SCHEMA_FIELDS_RE = re.compile(r"findings:\n(.*?)\n```", re.DOTALL)


def _windows() -> tuple[str, str]:
    text = CODE_REVIEWER_MD.read_text(encoding="utf-8")
    fields_match = _SCHEMA_FIELDS_RE.search(text)
    assert fields_match, (
        f"could not locate the findings:...``` schema block in {CODE_REVIEWER_MD}"
    )
    agg_idx = text.index("### Aggregation rule")
    assert agg_idx > fields_match.end(), (
        "### Aggregation rule appears before the schema fence closes — "
        "window assumption broken"
    )
    prose = text[fields_match.end():agg_idx]
    return fields_match.group(1), prose


def test_code_reviewer_schema_carries_origin_and_the_quote_gate():
    schema_fields, prose = _windows()

    # The schema block itself declares the field, as an indented field
    # line (not merely a mention elsewhere in the window).
    assert re.search(r"^\s+origin:", schema_fields, re.MULTILINE), (
        "finding schema block does not declare an `origin:` field"
    )

    # Surrounding prose states the load-bearing quote-gate clause as ONE
    # contiguous instruction: name the artifact ONLY when a verbatim
    # quote is held, otherwise write `none`. Anchored as a single
    # ordered phrase — not three independently-satisfiable fragments —
    # so an inverted instruction ("do NOT quote ... always write
    # `none`") cannot satisfy this by reusing the same words out of
    # order or scattered across unrelated sentences (e.g. a grammar
    # recap or a code-fence placeholder elsewhere in the window).
    # Prose in this repo hard-wraps at ~80 columns (see the plan's
    # §Notes), so `\s+` tolerates the phrase splitting across a line
    # break; it does NOT tolerate other text being interposed between
    # the words.
    _QUOTE_GATE_CLAUSE_RE = re.compile(
        r"name\s+the\s+upstream\s+artifact\s+ONLY\s+when\s+you\s+can\s+"
        r"quote\s+the\s+wrong\s+statement\s+verbatim;\s*otherwise\s+"
        r"write\s+`none`"
    )
    assert _QUOTE_GATE_CLAUSE_RE.search(prose), (
        "surrounding text does not state the load-bearing quote-gate "
        "clause as one contiguous instruction (name the artifact ONLY "
        "when you can quote the wrong statement verbatim; otherwise "
        "write `none`)"
    )

    # Surrounding prose states `none` carries no penalty, again pinned
    # as one contiguous clause (tolerates the hard-wrap splitting the
    # `**no penalty**` emphasis markers across the line break).
    _NO_PENALTY_CLAUSE_RE = re.compile(
        r"`none`\s+carries\s+\*\*no\s+penalty\*\*:\s*the\s+field\s+"
        r"records\s+what\s+you\s+hold"
    )
    assert _NO_PENALTY_CLAUSE_RE.search(prose), (
        "surrounding text does not state the no-penalty clause as one "
        "contiguous instruction (`none` carries no penalty: the field "
        "records what you hold)"
    )

    # Negative control (supplement, not the fix by itself — the two
    # positive anchors above are what actually catch an inversion; this
    # only catches the specific case where the wording nearby states
    # the gate as a prohibition rather than an action).
    assert not re.search(r"do\s+NOT\s+quote", prose), (
        "surrounding text appears to state the quote gate as a "
        "prohibition, not the required action"
    )

    # Existing schema fields must remain unchanged by this addition.
    for field in ("severity:", "dimension:", "where:", "source:", "note:"):
        assert field in schema_fields, (
            f"existing schema field {field!r} missing from schema block"
        )
