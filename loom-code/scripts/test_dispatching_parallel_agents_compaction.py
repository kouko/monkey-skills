"""Static compaction oracle for dispatching-parallel-agents."""

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "dispatching-parallel-agents" / "SKILL.md"


def test_entrypoint_preserves_independence_fanout_tdd_and_integration_within_word_range():
    text = SKILL.read_text(encoding="utf-8")
    words = int(
        subprocess.run(
            ["wc", "-w", str(SKILL)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split()[0]
    )
    assert 1279 <= words <= 1461

    # Frontmatter, stop behavior, and the portable dispatch dependency stay inline.
    assert "name: dispatching-parallel-agents" in text
    assert "version: 0.9.0" in text
    assert "<SUBAGENT-STOP>" in text
    assert "## When to use vs. when NOT to" in text
    assert "### 3. Dispatch all N subagents in one fan-out step" in text
    assert "Resolve the dispatch profile" in text
    assert "dispatch-profile.md" in text

    # Independence is proven, never guessed: files/symbols/state and data flow matter.
    for phrase in (
        "No shared file",
        "No shared symbol",
        "No sequential data dependency",
        "shared a root cause",
        "read-only",
        "shared configuration",
        "operationally coupled",
    ):
        assert phrase in text

    assert "one domain" in text
    assert "self-contained paths and reference context" in text
    assert "explicit paths it must not touch" in text
    assert "issue all N spawn calls before waiting for any result" in text
    assert "without an intervening wait" in text

    # Branch discipline and integration discipline are separate mandatory gates.
    assert "tdd-iron-law" in text
    assert "failing test first" in text
    assert "Run the package-level test suite" in text
    assert "integration point" in text

    # Plans and concurrent sessions retain their collision controls.
    assert "independent: true" in text
    assert "files touched" in text
    assert "Worktree-per-agent" in text
    assert "Static up-front partition" in text
    assert "Shared ledger" in text
    assert "PR-per-agent" in text

    # Result aggregation retains all non-clean and retry outcomes.
    for verdict in (
        "all `DONE` / `PASS`",
        "DONE_WITH_CONCERNS",
        "PASS_WITH_NOTES",
        "NEEDS_REVISION",
        "BLOCKED",
        "NEEDS_CONTEXT",
    ):
        assert verdict in text
    assert "re-dispatch only that branch" in text
    assert "never retry blindly" in text
    assert "replace only its prior result" in text

    # Plan proof and the two concurrency modes remain distinct.
    for phrase in (
        "complete declared file sets pairwise",
        "no task consumes another task's output",
        "mode (a): one orchestrator",
        "Mode (b)—separate sessions",
        "Mode (a) children deliberately share",
        "Mode (b) sessions cannot rely",
    ):
        assert phrase in text

    # Refusals keep both the forbidden shortcut and its remedy.
    for phrase in (
        "let git sort it out",
        "prove disjointness or sequence",
        "skip TDD",
        "run integrated verification",
        "first identify whether they shared a root cause",
        "inspect files and dependencies",
    ):
        assert phrase in text
