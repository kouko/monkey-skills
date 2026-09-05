"""Permanent regression tests for `plan.field-caps` (W1-01).

These are the implementer's own tests, distinct from the adversary's RED
probes at
`docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_field_caps.py`:
where the probes drive the rule through the CLI end to end, these call
`check_plan_field_caps` directly against small in-memory plan bodies, so a
future change to the rule's internals gets a fast, focused signal without
spinning up a subprocess for every case.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loom_checker import check_plan_field_caps  # noqa: E402


def _plan(
    *,
    charter: str | None = "charter: 1.0",
    files: str = "src/a.py, src/b.py",
    test: str = "the new behaviour works",
    risk: str = "agent-decided -- low",
    risks_item: str = "A small residual risk, agent-decided and bounded.",
    cse_bullet: str = "Forward: some/path.py:1 names the current gap.",
) -> str:
    lines = ["# Sample -- plan", "intent: sample@deadbeef"]
    if charter is not None:
        lines.append(charter)
    lines += [
        "",
        "## Current State Evidence",
        f"- {cse_bullet}",
        "",
        "## Task DAG",
        "",
        "**T1 Sample task**  after: --",
        f"- Files: {files}",
        f"- Test: {test}",
        f"- Risk: {risk}",
        "",
        "## Questions asked",
        "",
        "## Risks",
        f"1. {risks_item}",
    ]
    return "\n".join(lines) + "\n"


def _words(n: int) -> str:
    return " ".join(f"w{i}" for i in range(n))


def test_check_plan_field_caps_all_fields_within_cap_returns_no_failures() -> None:
    """A plan whose every field sits inside its own cap yields an empty
    failure list -- the baseline every over-cap test below deviates from
    by exactly one field."""
    failures = check_plan_field_caps(_plan())
    assert failures == []


def test_check_plan_field_caps_no_charter_line_skips_regardless_of_content() -> None:
    """Grandfathering is presence-based: a plan missing `charter:` entirely
    is skipped even when every field is grotesquely over cap."""
    failures = check_plan_field_caps(_plan(charter=None, test=_words(500), risk=_words(500)))
    assert failures == []


def test_check_plan_field_caps_test_field_over_cap_names_task_and_field() -> None:
    """An over-cap Test field produces one failure naming the task id and
    the field, with the rule id `plan.field-caps` attached."""
    failures = check_plan_field_caps(_plan(test=_words(41)))
    assert len(failures) == 1
    rule_id, reason = failures[0]
    assert rule_id == "plan.field-caps"
    assert "T1.Test" in reason
    assert "41" in reason and "40" in reason


def test_check_plan_field_caps_files_entries_over_cap_counts_entries_not_words() -> None:
    """Files is capped by comma-separated entry count, not by word count --
    nine short entries block even though none of them is a long path."""
    nine = ", ".join(f"f{i}.py" for i in range(9))
    failures = check_plan_field_caps(_plan(files=nine))
    assert len(failures) == 1
    rule_id, reason = failures[0]
    assert rule_id == "plan.field-caps"
    assert "T1.Files" in reason
    assert "9 entries" in reason and "cap 8" in reason


def test_check_plan_field_caps_missing_test_line_is_a_failure_not_a_zero_count() -> None:
    """A task with no `- Test:` line at all is a failure naming the field
    as missing -- not silently treated as a zero-word Test field, which
    would trivially pass any word cap."""
    plan_text = _plan().replace("- Test: the new behaviour works\n", "")
    failures = check_plan_field_caps(plan_text)
    assert any(
        rule_id == "plan.field-caps" and "T1.Test missing" in reason
        for rule_id, reason in failures
    )


def test_check_plan_field_caps_risks_and_cse_are_capped_independently_of_task_fields() -> None:
    """An over-cap `## Risks` item and an over-cap `## Current State
    Evidence` bullet each block on their own, even while every Task DAG
    field stays inside its cap -- two distinct sources of failure in one
    plan, not one masking the other."""
    failures = check_plan_field_caps(
        _plan(risks_item=_words(41), cse_bullet=_words(31))
    )
    reasons = [reason for _, reason in failures]
    assert any("Risks#1" in reason for reason in reasons)
    assert any("Current State Evidence#1" in reason for reason in reasons)
    assert len(failures) == 2


def test_check_plan_field_caps_cjk_run_with_no_spaces_counts_as_one_word() -> None:
    """A CJK run with no internal whitespace is one word by
    `len(text.split())` -- documented behaviour, not a bug -- so a Test
    field made only of such a run passes even though it is far longer than
    40 characters."""
    failures = check_plan_field_caps(_plan(test="測" * 200))
    assert failures == []
