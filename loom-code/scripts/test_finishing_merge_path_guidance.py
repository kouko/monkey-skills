"""Structural grep-test guarding the dual-merge-path guidance in
finishing-a-development-branch/SKILL.md.

Incident: four PRs merged via the GitHub web UI in one session — two
squash bodies landed fine, two shipped title-only because the web merge
dialog's description-box prefill silently failed (repo squash settings
verified correct throughout). `gh pr merge <N> --squash` bypasses the
dialog and faithfully uses the PR body. The durable lesson already lives
at docs/loom/memory/squash-dialog-can-drop-entire-pr-body.md — this test
does not restate the incident, it guards that the orchestrator's PR-open
step (Step 11) and final report (Step 13) both surface BOTH merge paths:
the web URL (with a reminder to glance that the dialog's description box
is prefilled before confirming) and the ready-to-run CLI alternative
`gh pr merge <N> --squash`, framed for the human to run themselves —
never auto-merge.

Neighborhood-scoped (mirrors test_finishing_archive_step.py): Step 11
and Step 13 are sliced independently so a whole-file substring check
can't false-green off one step carrying all the required phrases while
the other carries none.

Grounding for the `gh pr merge <N> --squash` surface: it is not a new
invention here — the repo already treats it as a checkpoint the guard
and the memory skill both reason about. See
loom-code/hooks/git-guard.py:14 (git-guard's own comment lists
``gh pr create``, ``gh pr merge`` as commands requiring fresh markers)
and dev-workflow/skills/git-memory/SKILL.md:27 ("`gh pr merge` (esp.
`--squash`) is the last checkpoint before the branch closes").

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "finishing-a-development-branch" / "SKILL.md"

MEMORY_POINTER = "docs/loom/memory/squash-dialog-can-drop-entire-pr-body.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _step_slice(text: str, start_marker: str, end_marker: str) -> str:
    """Window of text from start_marker up to (not including) end_marker.

    Scopes assertions to one numbered step so generic words shared across
    steps don't produce a false-green whole-file match."""
    start = text.find(start_marker)
    assert start != -1, f"start marker not found: {start_marker!r}"
    end = text.find(end_marker, start)
    assert end != -1, f"end marker not found after start: {end_marker!r}"
    assert end > start, "end marker must follow start marker"
    return text[start:end]


def _step11_slice(text: str) -> str:
    return _step_slice(
        text,
        '11. ASK user: "Open a PR? (y/N)"',
        '12. ASK user: "Branch was in .worktrees/',
    )


def _step13_slice(text: str) -> str:
    return _step_slice(
        text,
        "13. Report final state",
        "**ASK = stop and wait for user.**",
    )


def test_step11_offers_cli_merge_alternative():
    """Step 11 (gh pr create) must offer the ready-to-run CLI merge command
    as an alternative to the web merge dialog."""
    step11 = _step11_slice(_text())
    assert "gh pr merge" in step11, \
        "Step 11 must offer the `gh pr merge <N> --squash` CLI alternative"
    assert "--squash" in step11, \
        "Step 11's CLI alternative must be a squash merge command"


def test_step11_reminds_to_glance_the_prefilled_dialog():
    """Step 11 must remind the user to glance that the web merge dialog's
    description box is prefilled before confirming — the failure mode
    that shipped two title-only PRs."""
    step11 = _step11_slice(_text())
    assert "glance" in step11.lower(), \
        "Step 11 must include a glance-the-prefill reminder"
    assert "prefill" in step11.lower(), \
        "Step 11's reminder must name the prefill failure mode"


def test_step11_never_auto_merges():
    """The CLI alternative must stay human-executed, not orchestrator-run —
    consistent with this skill's no-auto-merge contract."""
    step11 = _step11_slice(_text())
    assert "human" in step11.lower() or "user" in step11.lower(), \
        "Step 11 must frame the CLI command as user-executed, not automatic"


def test_step11_points_at_the_incident_memory_record():
    """Step 11 must point at the durable memory-store record instead of
    restating the incident inline."""
    step11 = _step11_slice(_text())
    assert MEMORY_POINTER in step11, \
        f"Step 11 must point at {MEMORY_POINTER}"


def test_step13_report_includes_cli_merge_alternative():
    """Step 13's final-report content list must also require surfacing the
    CLI merge alternative when a PR was created — not just the PR URL."""
    step13 = _step13_slice(_text())
    assert "gh pr merge" in step13, \
        "Step 13 must require the CLI merge alternative in the report"
    assert "--squash" in step13, \
        "Step 13's CLI alternative must be a squash merge command"


def test_step13_report_reminds_to_glance_the_prefilled_dialog():
    """Step 13's report requirement must carry the same prefill-glance
    reminder as Step 11, not just the bare PR URL."""
    step13 = _step13_slice(_text())
    assert "glance" in step13.lower(), \
        "Step 13 must include a glance-the-prefill reminder"
    assert "prefill" in step13.lower(), \
        "Step 13's reminder must name the prefill failure mode"


def test_step11_carrier_check_precedes_merge_paths_bullet():
    """The PR-carrier check can still edit the PR body ('fix the body before
    submitting'); the merge-paths bullet must only be offered once the body
    is final, so the carrier-check anchor must appear before the
    merge-paths anchor within Step 11."""
    step11 = _step11_slice(_text())
    carrier_idx = step11.find("PR-carrier check")
    merge_paths_idx = step11.find("Offer BOTH merge paths")
    assert carrier_idx != -1, "Step 11 must contain the PR-carrier check bullet"
    assert merge_paths_idx != -1, "Step 11 must contain the merge-paths bullet"
    assert carrier_idx < merge_paths_idx, \
        "PR-carrier check bullet must precede the merge-paths bullet in Step 11"


def test_memory_pointer_appears_exactly_once():
    """The incident record is pointed at once (Step 11); Step 13 reuses
    the guidance by reference instead of restating the path — avoids the
    cross-file §refs Shotgun-Surgery smell of duplicating a pointer path."""
    text = _text()
    assert text.count(MEMORY_POINTER) == 1, \
        f"{MEMORY_POINTER} must appear exactly once, found {text.count(MEMORY_POINTER)}"
