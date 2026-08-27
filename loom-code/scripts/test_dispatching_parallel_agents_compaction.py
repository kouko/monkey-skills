"""Static compaction oracle for dispatching-parallel-agents."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "dispatching-parallel-agents" / "SKILL.md"


def _section(text: str, heading: str) -> str:
    """Window from the line matching `heading` to the next `## `/`### `
    heading. Used to narrow a pin to the section it actually governs,
    instead of matching anywhere in the whole file."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i
            break
    assert start is not None, (
        f"heading {heading!r} not found -- section renamed or removed"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            end = j
            break
    return "".join(lines[start:end])


def test_entrypoint_preserves_independence_fanout_tdd_and_integration():
    text = SKILL.read_text(encoding="utf-8")

    # Frontmatter, stop behavior, and the portable dispatch dependency stay inline.
    assert "name: dispatching-parallel-agents" in text
    assert "version: 0.9.0" in text
    assert "<SUBAGENT-STOP>" in text
    assert "## When to use vs. when NOT to" in text
    assert "### 3. Dispatch all N subagents in one fan-out step" in text
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
    assert "### 2. Write domain-focused prompts" in text

    # Two rules the child prompt must carry, pinned inside the section that
    # governs child-prompt contents. Both change what a dispatcher writes:
    # a prompt that assumes inherited session context, or that names no
    # forbidden paths, is a different artifact.
    prompt_section = _section(text, "### 2. Write domain-focused prompts")
    assert "self-contained" in prompt_section
    assert "must not touch" in prompt_section

    # The fan-out concurrency invariant is a named mechanism, not prose:
    # pin it inside the section that governs it, not anywhere in the file.
    fanout_section = _section(text, "### 3. Dispatch all N subagents in one fan-out step")
    # Resolution of the dispatch profile is per-child and precedes spawning;
    # the filename pin above alone would survive a demotion to "see also".
    assert "for every child before spawning" in fanout_section
    assert "issue all N spawn calls before waiting for any result" in fanout_section
    assert "without an intervening wait" in fanout_section

    # Branch discipline and integration discipline are separate mandatory gates.
    assert "tdd-iron-law" in text
    assert "failing test first" in text
    integrate_section = _section(text, "### 4. Aggregate without smoothing")
    assert "Run the package-level test suite" in integrate_section
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
    # Targeted-retry and partial-replace are named mechanisms of the
    # aggregation step, pinned inside the section that governs them.
    assert "re-dispatch only that branch" in integrate_section
    assert "never retry blindly" in text
    assert "replace only its prior result" in integrate_section

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
