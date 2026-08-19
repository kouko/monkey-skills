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

import json
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


PLUGIN_JSON = Path(__file__).parents[1] / ".claude-plugin" / "plugin.json"


def test_check19_version_tag_matches_shipping_version():
    """Check 19's leading `(vX.Y.Z+)` tag must name the version this
    arc actually ships under.

    Pinned live against `loom-code/.claude-plugin/plugin.json`'s
    current value, not a hardcoded literal: Task 12 of
    `docs/loom/plans/2026-08-19-field-value-microstructure.md` bumped
    plugin.json 0.88.0 -> 0.89.0, and that bump is the objection a
    hardcoded literal existed to dodge (a live comparison would have
    failed while plugin.json still read 0.88.0). With the bump landed,
    the two must move together from here on -- a future version bump
    that forgets to update the Check 19 tag is exactly the drift this
    test exists to catch.
    """
    text = _text()
    row = _check19_row(text)

    assert PLUGIN_JSON.is_file(), f"plugin.json is absent at {PLUGIN_JSON}"
    plugin_version = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]

    match = re.search(r"\(v(\d+\.\d+\.\d+)\+\)", row)
    assert match is not None, "Check 19 row must open with a `(vX.Y.Z+)` version tag"
    assert match.group(1) == plugin_version, (
        f"Check 19 version tag is v{match.group(1)}+, but "
        f"loom-code/.claude-plugin/plugin.json reads {plugin_version} -- "
        "whichever one is stale, update it to match the other"
    )
