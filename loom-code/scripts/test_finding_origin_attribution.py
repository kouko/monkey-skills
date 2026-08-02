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


# ---------------------------------------------------------------------------
# Task 4 — loom-code/agents/code-quality-reviewer.md (per-task reviewer).
#
# Same `origin:` field, but this agent's verdicts never reach
# `loom_gate_markers.py` (only whole-branch verdicts mint a marker), so the
# contract must say the field is emitted here but NOT marker-enforced. That
# asymmetry statement is the load-bearing sentence this task adds — anchored
# the same way as Task 3's quote-gate clause: one contiguous, ordered-word
# regex spanning the whole clause, joined by `\s+` so it tolerates this
# repo's ~80-column hard wrap but cannot be satisfied by reordered or
# scattered fragments.
# ---------------------------------------------------------------------------

CODE_QUALITY_REVIEWER_MD = (
    Path(__file__).parents[1] / "agents" / "code-quality-reviewer.md"
)

# `findings:` here carries a trailing `# ...` comment before its newline
# (code-reviewer.md's does not), so the field-block regex tolerates any
# trailing text on that line rather than requiring a bare `findings:\n`.
_QUALITY_SCHEMA_FIELDS_RE = re.compile(r"findings:[^\n]*\n(.*?)\n```", re.DOTALL)


def _quality_windows() -> tuple[str, str]:
    text = CODE_QUALITY_REVIEWER_MD.read_text(encoding="utf-8")
    fields_match = _QUALITY_SCHEMA_FIELDS_RE.search(text)
    assert fields_match, (
        f"could not locate the findings:...``` schema block in {CODE_QUALITY_REVIEWER_MD}"
    )
    agg_idx = text.index("### Verdict aggregation rule")
    assert agg_idx > fields_match.end(), (
        "### Verdict aggregation rule appears before the schema fence "
        "closes — window assumption broken"
    )
    prose = text[fields_match.end():agg_idx]
    return fields_match.group(1), prose


def test_code_quality_reviewer_states_origin_is_not_marker_enforced():
    schema_fields, prose = _quality_windows()

    # The schema block itself declares the field, as an indented field
    # line (not merely a mention elsewhere in the window).
    assert re.search(r"^\s+origin:", schema_fields, re.MULTILINE), (
        "finding schema block does not declare an `origin:` field"
    )

    # Surrounding prose states the not-marker-enforced asymmetry as ONE
    # contiguous instruction, anchored the same way as Task 3's clause —
    # not three independently-satisfiable fragments, so a passage stating
    # the opposite ("per-task verdicts always reach ... IS marker-enforced")
    # cannot satisfy this by reusing the same vocabulary out of order.
    _NOT_MARKER_ENFORCED_CLAUSE_RE = re.compile(
        r"Per-task\s+verdicts\s+never\s+reach\s+`loom_gate_markers\.py`,?\s+"
        r"so\s+`origin:`\s+is\s+emitted\s+here\s+but\s+not\s+"
        r"marker-enforced"
    )
    assert _NOT_MARKER_ENFORCED_CLAUSE_RE.search(prose), (
        "surrounding text does not state the not-marker-enforced "
        "asymmetry as one contiguous instruction (per-task verdicts "
        "never reach `loom_gate_markers.py`, so `origin:` is emitted "
        "here but not marker-enforced)"
    )

    # Negative control (supplement, not the fix by itself — the positive
    # anchor above is what actually catches an inversion). Catches the
    # specific case where nearby wording claims the opposite of "never
    # reach": that per-task verdicts DO reach the marker minter.
    assert not re.search(r"always\s+reach\s+`loom_gate_markers\.py`", prose), (
        "surrounding text appears to claim per-task verdicts DO reach "
        "loom_gate_markers.py"
    )

    # Existing schema fields must remain unchanged by this addition.
    for field in ("severity:", "dimension:", "where:", "source:", "note:"):
        assert field in schema_fields, (
            f"existing schema field {field!r} missing from schema block"
        )


# ---------------------------------------------------------------------------
# Task 5 — loom-code/skills/requesting-code-review/SKILL.md (whole-branch
# verdict structure — the block confirmed by its `cross-task-coherence` and
# `principles-conformance` dimension_scores entries, which the per-task
# agent's block does not carry).
#
# This block must NOT restate code-reviewer.md's quote-gate rule — it must
# point at the agent instead (the `class:` field at :150 is the existing
# precedent for scoping a field inline rather than re-deriving its rule).
# The negative assertion below reuses the exact clause regex from
# test_code_reviewer_schema_carries_origin_and_the_quote_gate above: it is
# discriminating because it is anchored to the actual rule text, not a
# generic keyword — pasting the full rule into this block trips it.
# ---------------------------------------------------------------------------

REVIEW_SKILL_MD = (
    Path(__file__).parents[1] / "skills" / "requesting-code-review" / "SKILL.md"
)

_REVIEW_FIELDS_RE = re.compile(r"findings:\n(.*?)\nsimplification_ledger:", re.DOTALL)


def _review_windows() -> tuple[str, str]:
    text = REVIEW_SKILL_MD.read_text(encoding="utf-8")
    section_start_idx = text.index("## Verdict structure")
    fields_match = _REVIEW_FIELDS_RE.search(text, section_start_idx)
    assert fields_match, (
        "could not locate the findings:...simplification_ledger: schema "
        f"block in {REVIEW_SKILL_MD}"
    )
    fence_close_idx = text.index("```", fields_match.end())
    red_flags_idx = text.index("## Red Flags", fence_close_idx)
    assert red_flags_idx > fence_close_idx, (
        "## Red Flags appears before the schema fence closes — window "
        "assumption broken"
    )
    # `section` spans the WHOLE §Verdict structure section — heading
    # through the next heading, fence interior included. A negative
    # assertion anchored only to the fence-close-onward prose is blind to
    # a restatement pasted inside the fence (e.g. after
    # `simplification_ledger:`) or between the heading and the fence
    # open; all three placements are real, measured escapes (see the
    # finding this test closes).
    section = text[section_start_idx:red_flags_idx]
    return fields_match.group(1), section


def test_review_skill_verdict_structure_names_origin_without_restating_the_rule():
    schema_fields, section = _review_windows()

    # The schema block declares the field, as an indented field line (not
    # merely a mention elsewhere in the window) — same shape as the
    # `class:` precedent it sits next to.
    assert re.search(r"^\s+origin:", schema_fields, re.MULTILINE), (
        "requesting-code-review §Verdict structure findings block does "
        "not declare an `origin:` field"
    )

    # The field's own line points at code-reviewer.md rather than staying
    # silent about where the rule lives — the same inline-comment shape as
    # `class:` ("semantics owned by requesting-docs-review").
    origin_line_match = re.search(r"^\s+origin:.*$", schema_fields, re.MULTILINE)
    assert origin_line_match, "origin: field line not found"
    assert re.search(r"code-reviewer\.md", origin_line_match.group(0)), (
        "origin: field line does not point at code-reviewer.md as the "
        "owner of the quote-gate rule"
    )

    # Negative: the quote-gate rule itself must NOT be restated in full
    # anywhere in §Verdict structure — heading through the next heading,
    # fence interior included, not merely the prose after the fence
    # closes. Anchored as the exact contiguous clause from code-reviewer.md
    # (same regex as the positive assertion in
    # test_code_reviewer_schema_carries_origin_and_the_quote_gate) so it is
    # discriminating: a generic substring check on a word like "quote"
    # would go false-red on the field's own grammar recap, and a bare
    # "not restated" claim with no anchor would go false-green forever
    # without ever being exercised. This one fires exactly when someone
    # pastes the rule in — including inside the fence (e.g. spliced into
    # the `origin:` line itself, or after `simplification_ledger:`) or
    # between the heading and the fence open, all three measured to slip
    # past a fence-close-onward-only window.
    _QUOTE_GATE_CLAUSE_RE = re.compile(
        r"name\s+the\s+upstream\s+artifact\s+ONLY\s+when\s+you\s+can\s+"
        r"quote\s+the\s+wrong\s+statement\s+verbatim;\s*otherwise\s+"
        r"write\s+`none`"
    )
    assert not _QUOTE_GATE_CLAUSE_RE.search(section), (
        "requesting-code-review/SKILL.md restates code-reviewer.md's "
        "quote-gate rule in full instead of pointing at the agent — a "
        "second copy of the rule is a second source of truth"
    )


# ---------------------------------------------------------------------------
# Task 9 — loom-code/agents/code-reviewer.md self-derives upstream artifacts.
#
# The dispatch packet carries diff/rubrics/checklists/branch context but no
# plan/brief/spec path (packet-passing was rejected: the orchestrator has no
# branch→plan resolution rule, and plans are dated-and-slugged and plural).
# The fix mirrors D8's self-derivation shape for `docs/loom/PRINCIPLES.md`:
# the reviewer derives candidate upstream artifacts itself, and finding none
# is an ordinary `none`, not a defect. Reuses the same `_windows()` prose
# window as Task 3 (this content lives in the same origin: explanatory
# paragraph, before "### Aggregation rule") and the same anchoring shape:
# one contiguous ordered-word clause joined by `\s+`, not keyword presence —
# a passage inverting the meaning while reusing the same vocabulary must NOT
# satisfy it.
# ---------------------------------------------------------------------------


def test_code_reviewer_self_derives_upstream_artifacts():
    _schema_fields, prose = _windows()

    # States WHERE the reviewer looks: it derives candidates from
    # docs/loom/plans/ and docs/loom/specs/ itself — not a path the
    # orchestrator hands it.
    _SELF_DERIVE_CLAUSE_RE = re.compile(
        r"derives\s+candidate\s+upstream\s+planning\s+artifacts\s+from\s+"
        r"`docs/loom/plans/`\s+and\s+`docs/loom/specs/`\s+itself"
    )
    assert _SELF_DERIVE_CLAUSE_RE.search(prose), (
        "surrounding text does not state that the reviewer self-derives "
        "candidate upstream planning artifacts from docs/loom/plans/ and "
        "docs/loom/specs/"
    )

    # Cites the D8 self-derivation precedent rather than re-deriving a
    # fresh mechanism (e.g. restating the git rev-parse anchor logic).
    _D8_CITATION_RE = re.compile(
        r"self-derivation\s+shape\s+D8\s+already\s+uses\s+for\s+"
        r"`docs/loom/PRINCIPLES\.md`"
    )
    assert _D8_CITATION_RE.search(prose), (
        "surrounding text does not cite the D8 self-derivation precedent "
        "rather than re-deriving its own mechanism"
    )

    # Finding none is stated as ordinary, not a defect — one contiguous
    # clause, same anchoring discipline as the clauses above.
    _NONE_NOT_DEFECT_RE = re.compile(
        r"[Ff]inding\s+none\s+there\s+is\s+an\s+ordinary\s+`none`,?\s+"
        r"not\s+a\s+defect"
    )
    assert _NONE_NOT_DEFECT_RE.search(prose), (
        "surrounding text does not state that finding no upstream artifact "
        "is an ordinary `none`, not a defect"
    )

    # Negative control: guards against an inversion instructing the
    # reviewer to keep searching / treat an empty result as a gap. Uses a
    # fixed-width negative lookbehind for "not " so it does not trip on
    # this task's own sanctioned phrasing ("must not search harder").
    assert not re.search(r"(?<!not )search\s+harder", prose), (
        "surrounding text appears to instruct the reviewer to search "
        "harder rather than accept an ordinary `none`"
    )


# ---------------------------------------------------------------------------
# Drift guard — the plan's §Pinned field grammar is the SSOT (plan's own
# words: "Transcribe VERBATIM from this pin, never from each other and never
# re-derived"). The three tests above each pin their own file in isolation;
# none of them compares a copy against the pin, or against each other, so a
# copy that drifts from the pin — while still being internally well-formed —
# passes every existing test. This test closes that gap directly.
#
# The three copies are NOT the same shape (by design, per Task 5's
# Description): code-reviewer.md and code-quality-reviewer.md each carry the
# full two-line grammar fence verbatim; requesting-code-review/SKILL.md
# carries only the schema FIELD LINE — folding both grammar values into one
# `|`-separated line — because restating the two-line fence there would be
# the same "second copy of the rule" problem the test above already guards
# against. So this test pins each copy against what it is actually supposed
# to carry, not one assertion forcing all three into one shape.
#
# "Match" is defined operationally, not by a regex: the plan's fence is
# indented two spaces (it sits inside a `- **§Pinned field grammar**` bullet)
# while both agent-file fences sit at column 0, so a byte-for-byte compare
# needs an explicit dedent — done here by stripping exactly a two-space
# prefix per line, not str.strip() (which would also silently swallow a
# real indentation drift inside the fence).
# ---------------------------------------------------------------------------

PLAN_MD = (
    Path(__file__).parents[2]
    / "docs"
    / "loom"
    / "plans"
    / "2026-08-02-finding-origin-attribution.md"
)


def _fence_lines_after(text: str, marker: str) -> list[str]:
    """Non-blank lines inside the first ``` fence found after `marker`."""
    marker_idx = text.index(marker)
    fence_open_idx = text.index("```", marker_idx)
    content_start = fence_open_idx + 3
    fence_close_idx = text.index("```", content_start)
    content = text[content_start:fence_close_idx]
    return [line for line in content.splitlines() if line.strip()]


def _dedent_two_spaces(line: str) -> str:
    # The plan's pin fence sits inside a bullet, so every content line is
    # prefixed with exactly two spaces of list-continuation indent.
    assert line.startswith("  "), (
        f"pin fence line {line!r} does not carry the expected 2-space "
        "bullet-continuation indent — dedent assumption broken"
    )
    return line[2:]


def test_pinned_field_grammar_matches_across_all_three_shipped_copies():
    pin_lines = [
        _dedent_two_spaces(line)
        for line in _fence_lines_after(
            PLAN_MD.read_text(encoding="utf-8"), "**§Pinned field grammar**"
        )
    ]
    assert pin_lines == [
        "origin: none",
        'origin: <path> :: "<verbatim quote from that file>"',
    ], f"unexpected pin shape in {PLAN_MD} — did §Pinned field grammar change?"
    pin_value_none, pin_value_quoted = (
        line.split("origin: ", 1)[1] for line in pin_lines
    )

    # code-reviewer.md and code-quality-reviewer.md: full two-line fence,
    # transcribed verbatim — compared line-for-line against the pin.
    for agent_path, marker in (
        (CODE_REVIEWER_MD, "transcribed verbatim from the field's pin:"),
        (CODE_QUALITY_REVIEWER_MD, "transcribed verbatim from the field's pin:"),
    ):
        agent_lines = _fence_lines_after(
            agent_path.read_text(encoding="utf-8"), marker
        )
        assert agent_lines == pin_lines, (
            f"{agent_path} grammar fence has drifted from the plan's "
            f"§Pinned field grammar: {agent_lines!r} != {pin_lines!r}"
        )

    # requesting-code-review/SKILL.md: by design carries only the schema
    # FIELD LINE, not the two-line fence (Task 5 — a second copy of the
    # fence would itself be "restating the rule"). Its value portion, after
    # stripping the `origin: ` key and the trailing inline comment, must
    # equal the pin's two values joined by " | " in the same order the
    # field line already uses.
    schema_fields, _section = _review_windows()
    origin_line_match = re.search(r"^\s+origin:\s*(.+)$", schema_fields, re.MULTILINE)
    assert origin_line_match, "origin: field line not found in SKILL.md schema block"
    value_and_comment = origin_line_match.group(1)
    value_part = value_and_comment.split("  #", 1)[0].strip()
    assert value_part == f"{pin_value_none} | {pin_value_quoted}", (
        "requesting-code-review/SKILL.md's origin: field line value has "
        f"drifted from the plan's §Pinned field grammar: {value_part!r} "
        f"!= {pin_value_none!r} | {pin_value_quoted!r}"
    )

    # Existing schema fields must remain unchanged by this addition.
    for field in ("severity:", "dimension:", "where:", "source:", "note:", "class:"):
        assert field in schema_fields, (
            f"existing schema field {field!r} missing from schema block"
        )
