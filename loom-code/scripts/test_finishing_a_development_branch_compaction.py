"""Static compaction oracle for finishing-a-development-branch."""

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "finishing-a-development-branch" / "SKILL.md"


def test_entrypoint_preserves_closeout_gates_publish_ci_and_report_within_word_range():
    text = SKILL.read_text(encoding="utf-8")
    words = int(
        subprocess.run(
            ["wc", "-w", str(SKILL)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split()[0]
    )
    assert 3129 <= words <= 3576

    # Loader-visible identity, stop behavior, and reference-consumed headings stay stable.
    for phrase in (
        "name: finishing-a-development-branch",
        "version: 0.10.1",
        "<SUBAGENT-STOP>",
        "## What this skill does",
        "## When NOT to use",
        "## When to use",
        "## Cross-skill contract — heavy delegation",
        "## Default flow — what happens if user just says \"finish this branch\"",
        "## Red Flags",
        "## What this skill does NOT do",
        "## See also",
    ):
        assert phrase in text

    # Close-out authorization and delegated whole-branch gates remain explicit.
    for phrase in (
        "record-only / docs-only / mixed / code-only",
        "closing out = review → verify → commit → push → PR — proceeding?",
        "requesting-code-review",
        "requesting-docs-review",
        "verification-before-completion",
        "ui-verification",
        "PASS_WITH_NOTES",
        "STILL_BLOCKING",
        "NEEDS_REVISION",
        "fix → re-review and digest silently until",
        "package-level tests",
        "0 tests ran",
        "If no UI",
        "surface or no ui-flows.md exists",
        "state N/A rather than omitting it",
    ):
        assert phrase in text

    # Memory, privacy, commit, staging, and final-HEAD safeguards stay inline.
    for phrase in (
        "loom-workflow:git-memory",
        "Memory-timing check",
        "privacy-scan.py",
        "privacy-judge-spec.md",
        "fail-closed",
        "git symbolic-ref -q HEAD",
        "Detached/different HEAD → STOP",
        "explicit file list",
        "memory-grep.sh --verify HEAD",
        "loom_gate_markers.py verified",
        "loom_gate_markers.py review-pass",
        "verification evidence must POSTDATE the close-out commit",
    ):
        assert phrase in text

    # Publishing uses a qualified push, authorized PR open, and bounded CI repair.
    for phrase in (
        "git push -u origin <branch>",
        "NEVER a bare `git push`",
        "Open the PR — no ask",
        "PR-carrier check",
        "post_pr_ci.py",
        "at most two automated repair attempts",
        'On status `"pass"`',
        'On status `"fail"`',
        "On `cancelled`",
        "On `timeout`, `no_checks`, `operational_error`, or `head_drift`",
        "head_drift",
        "never auto-merge",
        "gh pr merge <N> --squash",
    ):
        assert phrase in text

    # Repository close-out checks, the sole happy-path ask, and report survive.
    for phrase in (
        "check-living-spec-index.py --write-index",
        "archive_change_folder.py",
        "check_loom_memory_integrity.py",
        "Backlog-close check",
        "check_open_questions.py",
        'plan_card.py <plan-path> --set-stage "finishing"',
        "plan_card.py --stale-scan docs/loom/plans",
        "stale-scan: clean",
        "Purpose-linked betting",
        "print `docs/loom/PURPOSE.md`",
        "check_north_star_link.py",
        "STOP-and-ask",
        "agents never auto-promote",
        "consolidate inapplicable checks",
        "after the plain conclusion",
        "remove the worktree? (y/N)",
        "Close-out card",
        '"next bet:',
        '<name>"',
        '"bet queue empty"',
        "Include CI evidence",
        "checked PR head",
        "helper status",
        "repair",
        "attempt count",
    ):
        assert phrase in text
