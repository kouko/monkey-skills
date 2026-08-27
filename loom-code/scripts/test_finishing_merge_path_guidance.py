"""Structural grep-test guarding the SINGLE-merge-path guidance in
finishing-a-development-branch/SKILL.md.

History, because this file reverses its own earlier assertions: it was first
written after four PRs merged through the GitHub web UI in one session, two of
which shipped title-only because the merge dialog's description textarea had
been cleared. The remedy encoded then was to offer BOTH paths — the web URL
with a reminder to glance at the prefill, plus the CLI command — and to let the
human choose. Five more bodies were lost under that rule, and the two runs that
showed only the CLI command kept theirs. The reminder asked a person to
remember a check at the moment of clicking, and offering the link beside the
command meant the link usually won.

So the assertions below now guard the opposite shape: ONE merge path, the CLI
command completed with `--body-file` (the merge-time dialog is editable by
whoever clicks merge; passing the body as an argument removes that surface),
and the PR URL present only as a link to VIEW the PR. The durable record is
docs/loom/memory/squash-dialog-can-drop-entire-pr-body.md — this test does not
restate it.

Neighborhood-scoped (mirrors test_finishing_archive_step.py): Step 11 and Step
13 are sliced independently so a whole-file substring check can't false-green
off one step carrying all the required phrases while the other carries none.

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
        "11. Open the PR — no ask",
        '12. ASK user: "Branch was in .worktrees/',
    )


def _step13_slice(text: str) -> str:
    return _step_slice(
        text,
        "13. Report final state",
        "**ASK = stop and wait for user.**",
    )


def test_step11_offers_the_cli_merge_command():
    """Step 11 (gh pr create) must carry the ready-to-run CLI merge command.

    Not an alternative to anything — it is the only merge path the report
    offers, so its absence leaves the reader with no way to merge at all."""
    step11 = _step11_slice(_text())
    assert "gh pr merge" in step11, \
        "Step 11 must carry the `gh pr merge <N> --squash` CLI command"
    assert "--squash" in step11, \
        "Step 11's merge command must be a squash merge"


def test_step11_carries_no_prefill_reminder():
    """The glance-the-prefill reminder is deliberately gone.

    This assertion reverses the one it replaces. That reminder was added
    after four incidents and five more followed it: it asks a human to
    remember a check at the moment of clicking, which is the
    judgment-shaped prose this repo has repeatedly measured as unable to
    hold (docs/loom/memory/a-mechanical-check-can-go-green-by-skipping.md
    is the sibling shape). The reminder is replaced by removing the second
    merge path, not by wording it better.
    """
    step11 = _step11_slice(_text())
    assert "glance" not in step11.lower(), \
        "the prefill reminder must not return — remove the path, not reword the caveat"
    assert "prefill" not in step11.lower(), \
        "the prefill reminder must not return — remove the path, not reword the caveat"


def test_step11_never_auto_merges():
    """The merge command must stay human-executed, not orchestrator-run —
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


def test_step13_report_requires_step11s_merge_command():
    """Step 13 must require the merge command, by reference to Step 11.

    It used to spell the command out a second time. The command grew a
    body-reading subshell and a resolved PR number, and two copies of a command
    that specific drift apart — so Step 13 now points at Step 11's rather than
    restating it. What it must still carry is the requirement itself.
    """
    step13 = _step13_slice(_text())
    low = step13.lower()
    assert "merge command" in low, \
        "Step 13 must require the merge command in the report"
    assert "step 11" in low, \
        "Step 13 must point at Step 11's command rather than restating it"


def test_step13_report_carries_no_prefill_reminder():
    """Step 13 mirrors Step 11's reversal — see the note there."""
    step13 = _step13_slice(_text())
    assert "glance" not in step13.lower(), \
        "the prefill reminder must not return in the report step either"
    assert "prefill" not in step13.lower(), \
        "the prefill reminder must not return in the report step either"


def test_step11_carrier_check_precedes_merge_paths_bullet():
    """The PR-carrier check can still edit the PR body ('fix the body before
    submitting'); the merge-paths bullet must only be offered once the body
    is final, so the carrier-check anchor must appear before the
    merge-paths anchor within Step 11."""
    step11 = _step11_slice(_text())
    carrier_idx = step11.find("PR-carrier check")
    merge_paths_idx = step11.find("Merge path in the report")
    assert carrier_idx != -1, "Step 11 must contain the PR-carrier check bullet"
    assert merge_paths_idx != -1, "Step 11 must contain the merge-path bullet"
    assert carrier_idx < merge_paths_idx, \
        "PR-carrier check bullet must precede the merge-paths bullet in Step 11"


def test_step13_points_at_close_out_card():
    """Step 13's report format authority must point at family-relay.md
    §(a)'s Close-out card specialization, not the generic user-rollup
    card — the close-out report renders as that 10-row table."""
    step13 = _step13_slice(_text())
    assert "family-relay.md" in step13, \
        "Step 13 must point at family-relay.md"
    assert "Close-out card" in step13, \
        "Step 13 must point at family-relay.md §(a)'s Close-out card, not just the generic rollup card"


def test_memory_pointer_appears_exactly_once():
    """The incident record is pointed at once (Step 11); Step 13 reuses
    the guidance by reference instead of restating the path — avoids the
    cross-file §refs Shotgun-Surgery smell of duplicating a pointer path."""
    text = _text()
    assert text.count(MEMORY_POINTER) == 1, \
        f"{MEMORY_POINTER} must appear exactly once, found {text.count(MEMORY_POINTER)}"


def test_merge_command_carries_body_file():
    """The CLI command must pass the body explicitly.

    `--squash` alone lets the host compose the squash message, which is the
    same surface the web dialog drops. Only `--body-file` guarantees the
    composed PR body reaches the squash commit, so the command the report
    hands the user is incomplete without it.
    """
    step11 = _step11_slice(_text())
    assert "--body-file" in step11, \
        "Step 11's merge command must pass --body-file, not bare --squash"


def test_no_second_merge_path_is_offered():
    """Exactly one MERGE path is presented; the PR URL is a link, not a path.

    Five squash bodies were lost while both paths were offered side by side
    and two survived when only the CLI command was shown, so co-equal
    presentation is the defect. The URL still appears — for viewing the PR —
    but never framed as a way to merge.
    """
    for name, slice_fn in (("Step 11", _step11_slice), ("Step 13", _step13_slice)):
        low = slice_fn(_text()).lower()
        assert "both merge paths" not in low, \
            f"{name} must not offer two merge paths"
        assert "web merge" not in low, \
            f"{name} must not frame the web dialog as a merge path"



def test_merge_command_reads_the_body_at_merge_time():
    """The body must come from the PR page, not a file the report wrote.

    The human runs this command on their own schedule — after CI, or the next
    day — so any path the report quotes may be gone by then: a worktree Step 12
    offered to remove, or a scratchpad the OS cleared. Naming a location without
    a lifetime moves the failure from one deleter to another. The PR page is the
    carrier that survived every recorded occurrence.
    """
    step11 = _step11_slice(_text())
    assert "gh pr view" in step11 and "--json body" in step11, \
        "the merge command must read the body from the PR at merge time"


def test_body_file_mandate_cites_the_record_that_justifies_it():
    """`--body-file` must be justified by the title-only squash default.

    Removing the editable merge dialog is what distinguishes CLI merge from web
    merge — bare `--squash` already does that, so it cannot be the reason for
    the flag. The reason is that GitHub's default squash message for a
    single-commit PR keeps only the title, which a repo without
    `squash_merge_commit_message=PR_BODY` gets. This prose ships to such repos.
    """
    step11 = _step11_slice(_text())
    assert "github-squash-merge-single-commit-drops-body.md" in step11, \
        "the --body-file mandate must cite the title-only-squash record"
