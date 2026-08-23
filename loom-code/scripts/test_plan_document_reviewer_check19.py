"""Structural grep-window test guarding Check 19, added to
`plan-document-reviewer-prompt.md` by Task 10 of
`docs/loom/plans/2026-08-19-field-value-microstructure.md`.

plan-document-reviewer-prompt.md is a prompt/contract artifact, not
executable code: nothing importable observes whether a weak-tier
reviewer actually applies Check 19. This file IS the instruction that
reviewer reads, so its correctness condition is the PRESENCE of the
load-bearing phrases that make the check applicable by that reader --
same convention as `test_plan_document_reviewer_check17.py`.

The load-bearing claim this file exists to pin (source brief BI-4):
Check 19 must bind the reviewer to a verifiable ACTION -- run
`check_field_microstructure.py` and report what it reports -- never a
judgment call about whether a field is "atomic" / "well-shaped" /
"concise". Reintroducing the judgment-shaped rule in the reviewer
prompt would undo the field-value-microstructure arc from the other
end.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

from test_plan_document_reviewer_check17 import (
    _check_id_range_text,
    _needs_revision_range_text,
    _range_list_covers,
)

PROMPT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-document-reviewer-prompt.md"
)


def _text() -> str:
    assert PROMPT_MD.is_file(), f"plan-document-reviewer-prompt.md is absent at {PROMPT_MD}"
    return PROMPT_MD.read_text(encoding="utf-8")


def _check19_row(text: str) -> str:
    """Isolate the Check 19 table row -- the line beginning `| 19 |`."""
    for line in text.splitlines():
        if line.strip().startswith("| 19 |"):
            return line
    raise AssertionError("Check 19 table row (`| 19 |`) not found")


def test_check19_row_present_and_ranges_updated():
    """Check 19 row exists, names `check_field_microstructure.py`
    (the reviewer never re-derives the rule from prose), and states the
    check as a verifiable ACTION rather than a judgment call -- and both
    `check_id` ranges in the output contract cover check id 19."""
    text = _text()
    row = _check19_row(text)

    assert "check_field_microstructure.py" in row, (
        "Check 19 row must name check_field_microstructure.py so the "
        "reviewer runs it instead of re-deriving the rule from prose"
    )
    assert re.search(r"verifiable action", row, re.IGNORECASE), (
        "Check 19 row must state itself as a verifiable ACTION, not a "
        "judgment call -- mirroring Check 18's framing"
    )
    assert not re.search(r"judge whether|judges whether|decide whether", row, re.IGNORECASE), (
        "Check 19 row must not reintroduce a judgment-shaped rule "
        "('judges/decides whether each field is atomic')"
    )

    check_id_line = next(
        (line for line in text.splitlines() if "check_id:" in line),
        None,
    )
    assert check_id_line is not None, "gaps.check_id line not found"
    assert _range_list_covers(_check_id_range_text(check_id_line), 19), (
        "gaps.check_id range must cover check 19"
    )

    needs_revision_line = next(
        (
            line
            for line in text.splitlines()
            if line.strip().startswith("- **NEEDS_REVISION**")
        ),
        None,
    )
    assert needs_revision_line is not None, "NEEDS_REVISION verdict-mapping line not found"
    assert _range_list_covers(_needs_revision_range_text(needs_revision_line), 19), (
        "verdict mapping's NEEDS_REVISION range must cover check 19"
    )


PLAN_FORMAT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-format.md"
)


def test_check19_version_tag_matches_schema_introduction_version():
    """Check 19's leading `(vX.Y.Z+)` tag must name the INTRODUCTION
    version of the grammar it enforces -- the same tag its SSOT schema
    heading carries (`plan-format.md` `#### Field-value grammar
    (vX.Y.Z+)`) -- matching the frozen-introduction-version semantics of
    every other tagged row in the table (13/14: v0.8.0+, 17: v0.43.0+,
    18: v0.79.0+).

    History: from 0.89.0 to 0.98.0 this test compared the tag against
    plugin.json's CURRENT version (to avoid a hardcoded literal going
    stale mid-bump), which silently ratcheted the tag on every release
    and made row 19 the only drifting tag in the table -- reading as
    "applies from <current version> onward", factually wrong since the
    check has been in force since 0.89.0 (commit 544a586e). The 0.98.0
    docs-review panel caught the drift (both arms, independently:
    dual-semantics instruction defect + incorrect-fact). The live
    comparison target is now the schema SSOT heading, which keeps the
    original no-hardcoded-literal property without the ratchet: if the
    grammar is ever re-introduced at a new version, updating the schema
    heading updates the expectation here automatically.
    """
    text = _text()
    row = _check19_row(text)

    assert PLAN_FORMAT_MD.is_file(), f"plan-format.md is absent at {PLAN_FORMAT_MD}"
    schema_heading = next(
        (
            line
            for line in PLAN_FORMAT_MD.read_text(encoding="utf-8").splitlines()
            if line.startswith("#### Field-value grammar")
        ),
        None,
    )
    assert schema_heading is not None, (
        "plan-format.md `#### Field-value grammar` heading not found"
    )
    schema_match = re.search(r"\(v(\d+\.\d+\.\d+)\+\)", schema_heading)
    assert schema_match is not None, (
        "Field-value grammar heading must carry a `(vX.Y.Z+)` introduction tag"
    )

    row_match = re.search(r"\(v(\d+\.\d+\.\d+)\+\)", row)
    assert row_match is not None, "Check 19 row must open with a `(vX.Y.Z+)` version tag"
    assert row_match.group(1) == schema_match.group(1), (
        f"Check 19 version tag is v{row_match.group(1)}+, but its SSOT schema "
        f"heading (plan-format.md §Field-value grammar) reads "
        f"v{schema_match.group(1)}+ -- the row tag must mirror the schema's "
        "introduction version, never the shipping plugin version"
    )
