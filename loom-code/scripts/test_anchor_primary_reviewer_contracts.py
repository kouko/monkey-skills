"""Structural grep-test guarding the anchor-primary inversion of the R2
evidence rule in `loom-code/scripts/_reviewer-discipline.md` (the SSOT for
the reviewer-discipline-v1 block `distribute.py` propagates into the four
verdict-producing agents).

Before this inversion the R2 block prescribed the OPPOSITE ordering: it
made `file:line`, commit SHA, or commit SHA range the citation form. This
test pins the inverted ordering so a later edit that reverts to line-first
is caught at CI before the block propagates.

The SSOT is a prompt/contract artifact, not executable code; its
correctness condition is the PRESENCE of the load-bearing phrases that
make the rule executable by the reader (same convention as
`test_anchor_primary_plan_format.py`). Assertions target intent-bearing
phrases, tolerant of surrounding wording, so the guard survives a
rephrase and fails a removal.

This file is SHARED across three sequential tasks (T5, T6, T7):
- T5 (this task) adds `test_r2_is_anchor_primary_at_ssot` only.
- T6 adds `test_docs_reviewer_rule_7_and_schema_are_anchor_primary`.
- T7 adds `test_quality_gate_is_anchor_primary_at_ssot`.
Do not add the T6/T7 tests here.

Stdlib only (pathlib + re). `_reviewer-discipline.md` is resolved relative
to this test file.
"""

import re
from pathlib import Path

REVIEWER_DISCIPLINE_SSOT = (
    Path(__file__).parents[1] / "scripts" / "_reviewer-discipline.md"
)


def _text() -> str:
    assert REVIEWER_DISCIPLINE_SSOT.is_file(), (
        f"_reviewer-discipline.md is absent at {REVIEWER_DISCIPLINE_SSOT}"
    )
    return REVIEWER_DISCIPLINE_SSOT.read_text(encoding="utf-8")


def _r2_section(text: str) -> str:
    """Isolate the `## Rule R2` section body.

    Scoping to the section means the conjunct assertions below can only be
    satisfied by the R2 rule itself -- an incidental mention of "anchor" or
    "line number" elsewhere in the file cannot keep this test green. The
    section runs from its heading to the next `##`-level heading.
    """
    match = re.search(r"^##\s+Rule R2\b.*$", text, re.MULTILINE)
    assert match is not None, (
        "_reviewer-discipline.md carries no '## Rule R2' heading -- the "
        "evidence-citation rule must be a findable section a reviewer agent "
        "and the drift checker can be pointed at"
    )
    rest = text[match.end():]
    next_heading = re.search(r"^##\s+\S", rest, re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def _flatten(text: str) -> str:
    """Collapse whitespace runs to single spaces for whitespace-insensitive
    substring matching."""
    return re.sub(r"\s+", " ", text)


def test_r2_is_anchor_primary_at_ssot():
    """The R2 block cites the ANCHOR as the locator, with a line number as
    optional precision -- not the line-first `file:line` prescription the
    block carried before the inversion."""
    section = _r2_section(_text())
    flat = _flatten(section)
    low = flat.lower()

    # PRESENCE: anchor-primary wording
    assert "verbatim string" in low and "stable heading" in low, (
        "R2 must name the anchor forms -- 'verbatim string' and 'stable "
        "heading' -- as the locator a `where:` value carries"
    )
    assert "anchor" in low, (
        "R2 must use the term 'anchor' for the verbatim-string / "
        "stable-heading locator"
    )
    assert "line number is optional" in low or (
        "optional precision" in low and "line number" in low
    ), (
        "R2 must state that a line number is OPTIONAL precision, not the "
        "locator itself -- the pairing duty inverts: the anchor IS the "
        "locator, the line is the add-on"
    )
    assert "ambiguous" in low, (
        "R2 must state WHEN the optional line number becomes required -- "
        "when the anchor alone is ambiguous (the string occurs more than "
        "once in the file); without this the optionality is unbounded and "
        "the anchor can be silently dropped"
    )

    # Each artifact type needs its own anchor form. Checking complete clauses
    # prevents unrelated tokens elsewhere in R2 from masking a swapped or
    # incomplete category pairing.
    category_clauses = {
        "prose": (
            r"prose\s+uses\s+a\s+stable\s+heading\s+or\s+"
            r"distinctive\s+phrase\b"
        ),
        "code": (
            r"code\s+uses\s+a\s+function,\s+class,\s+or\s+method\s+"
            r"signature,\s+a\s+constant,\s+or\s+a\s+distinctive\s+"
            r"message\b"
        ),
        "config/data": (
            r"config/data\s+uses\s+a\s+key\s+path\s+plus\s+a\s+"
            r"distinctive\s+value\s+fragment\b"
        ),
    }
    for artifact_type, clause in category_clauses.items():
        assert re.search(clause, low), (
            f"R2 must keep the complete {artifact_type}-to-anchor clause; "
            "independent tokens can conceal a wrong category pairing"
        )
    assert "commit sha or commit sha range" in low, (
        "R2 must retain commit SHA and commit SHA range as alternatives for "
        "revision-history evidence"
    )

    # ABSENCE: the retired line-first prescription
    assert "file:line, commit sha, or commit sha range" not in low, (
        "the line-first prescription 'file:line, commit SHA, or commit SHA "
        "range' is retired -- it made the line number the citation and the "
        "anchor an added pairing duty, the opposite of the anchor-primary "
        "rule R2 now states"
    )


# ---------------------------------------------------------------------------
# T6 surface -- docs-reviewer.md role-contract item 7 + output schema.
#
# `docs-reviewer.md` is a prose contract under the loom tree, so its
# evidence-citation surface is edited in place (NOT via distribute.py).
# This test pins the anchor-primary inversion of that local surface so a
# later revert to line-first is caught at CI.
# ---------------------------------------------------------------------------

DOCS_REVIEWER_AGENT = (
    Path(__file__).parents[1] / "agents" / "docs-reviewer.md"
)


def _docs_reviewer_text() -> str:
    assert DOCS_REVIEWER_AGENT.is_file(), (
        f"docs-reviewer.md is absent at {DOCS_REVIEWER_AGENT}"
    )
    return DOCS_REVIEWER_AGENT.read_text(encoding="utf-8")


def _item_7_region(text: str) -> str:
    """Isolate role-contract item 7.

    The role contract is a numbered list; item 7 starts at a line beginning
    with `7.` and runs until the next top-level list item (`8.` at line
    start). The region is small and self-contained.
    """
    match = re.search(r"^7\.\s+Cite the exact text\.", text, re.MULTILINE)
    assert match is not None, (
        "docs-reviewer.md carries no '7. Cite the exact text.' item -- the "
        "evidence-citation rule must be a findable numbered item in the "
        "role contract"
    )
    rest = text[match.start():]
    next_item = re.search(r"^8\.\s", rest[1:], re.MULTILINE)
    return rest[: 1 + next_item.start()] if next_item else rest


def _output_schema_region(text: str) -> str:
    """Isolate the Output contract fenced block + the aggregation rule.

    The `where:` placeholders live in the fenced code block under
    `## Output contract`. The section runs from that heading to the next
    `##`-level heading (`### Aggregation rule` / `### Dimensions`).
    """
    match = re.search(r"^##\s+Output contract\b", text, re.MULTILINE)
    assert match is not None, (
        "docs-reviewer.md carries no '## Output contract' heading -- the "
        "output schema must be a findable section"
    )
    rest = text[match.end():]
    # the next ##-level heading inside Output contract is `### Aggregation
    # rule`; include it so the schema block is fully captured.
    next_heading = re.search(r"^##\s+\S", rest, re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def test_docs_reviewer_rule_7_and_schema_are_anchor_primary():
    """docs-reviewer.md item 7 + output schema cite the ANCHOR as the
    locator, with a line number as optional precision -- not the line-first
    `file:line` prescription the surface carried before the inversion."""
    text = _docs_reviewer_text()

    # ---- Surface 1: role-contract item 7 ----
    item7 = _flatten(_item_7_region(text))
    low7 = item7.lower()

    # PRESENCE: anchor-primary terms
    assert ("file path" in low7) or ("path" in low7), (
        "item 7 must name 'file path' (or 'path') as what `where:` locates"
    )
    assert "primary locator" in low7, (
        "item 7 must name `quote:` the PRIMARY locator -- the term is the "
        "load-bearing inversion marker distinguishing anchor-primary from "
        "the old line-first prescription"
    )
    assert "optional precision" in low7, (
        "item 7 must state a line number is OPTIONAL precision, not the "
        "locator itself"
    )
    assert ("anchor" in low7) or ("verbatim string" in low7), (
        "item 7 must use the term 'anchor' or 'verbatim string' for the "
        "primary locator `quote:` carries"
    )

    # ABSENCE: the retired line-first prescription
    assert "where:` is a path-like citation (`file:line`)" not in low7, (
        "the line-first prescription '`where:` is a path-like citation "
        "(`file:line`)' is retired from item 7 -- it made the line number "
        "the citation, the opposite of the anchor-primary rule"
    )

    # ---- Surface 2: output schema `where:` placeholders ----
    schema = _flatten(_output_schema_region(text))
    low_schema = schema.lower()

    # ABSENCE: the old required `where: <file:line>` form
    assert "where: <file:line>" not in low_schema, (
        "the schema placeholder `where: <file:line>` is retired -- the "
        "output schema must not prescribe a line number as the required "
        "`where:` form"
    )
    assert "where: <read-context file:line>" not in low_schema, (
        "the read-context schema placeholder `where: <read-context "
        "file:line>` is retired -- it must drop the line-number prescription"
    )

    # PRESENCE: the new anchor-primary `where: <path>` form
    assert "where: <path>" in low_schema, (
        "the schema placeholder `where: <path>` must be present -- the "
        "file path is the required `where:` form under anchor-primary"
    )
    assert "where: <read-context path>" in low_schema, (
        "the read-context schema placeholder `where: <read-context path>` "
        "must be present -- the file path, not file:line"
    )
    assert "primary locator" in low_schema, (
        "the schema `quote:` field must be annotated as the primary locator"
    )


# ---------------------------------------------------------------------------
# T7 surface -- quality-gate.md SSOT Output Format + closing line.
#
# `domain-teams/skills/code-team/rubrics/quality-gate.md` is the SSOT that
# `distribute.py` propagates into the loom-code copy. This test pins the
# anchor-primary inversion of that surface so a later revert to line-first
# is caught at CI before the block propagates.
# ---------------------------------------------------------------------------

QUALITY_GATE_SSOT = (
    Path(__file__).parents[2]
    / "domain-teams"
    / "skills"
    / "code-team"
    / "rubrics"
    / "quality-gate.md"
)


def _quality_gate_text() -> str:
    assert QUALITY_GATE_SSOT.is_file(), (
        f"quality-gate.md SSOT is absent at {QUALITY_GATE_SSOT}"
    )
    return QUALITY_GATE_SSOT.read_text(encoding="utf-8")


def test_quality_gate_is_anchor_primary_at_ssot():
    """The quality-gate SSOT cites the ANCHOR as the locator, with a line
    number as optional precision -- not the line-first `File path + line
    number` prescription the Output Format carried before the inversion."""
    flat = _flatten(_quality_gate_text())
    low = flat.lower()

    # PRESENCE: anchor-primary wording
    assert "anchor" in low, (
        "quality-gate SSOT must use the term 'anchor' for the "
        "verbatim-string / stable-heading locator"
    )
    assert ("verbatim string" in low) or ("stable heading" in low), (
        "quality-gate SSOT must name the anchor forms -- 'verbatim string' "
        "or 'stable heading' -- as the locator"
    )
    assert "optional precision" in low, (
        "quality-gate SSOT must state a line number is OPTIONAL precision, "
        "not the locator itself"
    )

    # ABSENCE: the retired line-first prescription
    assert "file path + line number" not in low, (
        "the line-first prescription 'File path + line number' is retired "
        "from the quality-gate SSOT -- it made the line number the citation, "
        "the opposite of the anchor-primary rule"
    )


def test_reviewer_family_local_contracts_do_not_require_line_locators():
    """Local reviewer prose uses path + anchor; a line is never identity."""
    surfaces = {
        "code-quality-reviewer.md": Path(__file__).parents[1]
        / "agents"
        / "code-quality-reviewer.md",
        "spec-reviewer.md": Path(__file__).parents[1]
        / "agents"
        / "spec-reviewer.md",
        "code-reviewer.md": Path(__file__).parents[1]
        / "agents"
        / "code-reviewer.md",
    }
    retired = {
        "code-quality-reviewer.md": ["a `file:line` reference"],
        "spec-reviewer.md": [
            "reference the artifact path:line",
            "a `file:line` reference",
        ],
        "code-reviewer.md": [
            "violating `file:line` in `where`",
            "one row per marker with its `file:line`",
            "marker's `file:line` in `where`",
            "cite the marker's `file:line`",
        ],
    }

    for name, path in surfaces.items():
        low = _flatten(path.read_text(encoding="utf-8")).lower()
        for phrase in retired[name]:
            assert phrase not in low, f"{name} retains line-first contract: {phrase}"
        assert "verbatim string" in low and "stable heading" in low, (
            f"{name} must retain anchor-primary evidence wording"
        )


def test_docs_review_panel_union_ignores_optional_line_precision():
    """Panel dedupe identity is path + anchor + dimension, not file:line."""
    path = (
        Path(__file__).parents[1]
        / "skills"
        / "requesting-docs-review"
        / "SKILL.md"
    )
    low = _flatten(path.read_text(encoding="utf-8")).lower()

    assert "same `file:line` and same dimension" not in low
    assert "path + anchor + dimension" in low
    assert "line" in low and "ignored" in low and "identity" in low


def test_requesting_code_review_published_readmes_are_anchor_primary():
    skill_dir = (
        Path(__file__).parents[1] / "skills" / "requesting-code-review"
    )
    retired = {
        "README.md": "file:line or commit sha range",
        "README.zh-TW.md": "file:line 或 commit sha range",
        "README.ja.md": "file:line または commit sha range",
    }
    required_semantics = {
        "README.md": (
            "path",
            "verbatim string",
            "stable heading",
            "optional line precision",
        ),
        "README.zh-TW.md": (
            "路徑",
            "逐字字串",
            "穩定標題錨點",
            "行號只是可選精度",
        ),
        "README.ja.md": (
            "パス",
            "逐語文字列",
            "安定した見出しアンカー",
            "行番号は任意の精度情報",
        ),
    }
    for filename, phrase in retired.items():
        low = _flatten((skill_dir / filename).read_text(encoding="utf-8")).lower()
        assert phrase not in low, f"{filename} retains line-first where contract"
        for semantic in required_semantics[filename]:
            assert semantic.lower() in low, (
                f"{filename} must state anchor-primary evidence semantic: {semantic}"
            )
        assert "commit sha range" in low, (
            f"{filename} must preserve the commit SHA range alternative"
        )
