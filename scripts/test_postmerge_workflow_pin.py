"""T3 (terminal-state-gates plan): pin the post-merge squash-body workflow
`.github/workflows/memory-verify-merged.yml` — the red light that already
fired unseen on #681 (run 11390166) — so its notification half (PR comment
on the exit-4 wipe shape) and its permissions cannot silently regress.

Pinned properties (whitespace-normalized text pins, per plan §Task 3):
  1. the workflow file exists (asserted FIRST);
  2. the verify step still invokes `--verify-merged HEAD` via memory-grep.sh;
  3. the exit-4 branch exists (conditional on rc 4), comments on the PR via
     `gh pr comment`, and still fails with `exit 1` (the red stays red);
  4. the `permissions:` block grants `pull-requests: write` AND keeps
     `contents: read`;
  5. the trigger is push -> main (`push` + `branches:` + `main`).

Block extraction is LINE-based for the top-level `on:` / `permissions:` /
`jobs:` keys — the file's WHY comment block itself contains the substring
"`on:`" in prose, so a naive text.find() would anchor on the wrong spot.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "memory-verify-merged.yml"


def _normalized(text: str) -> str:
    """Collapse all whitespace runs to single spaces (indentation-proof pin)."""
    return " ".join(text.split())


def _top_level_block(text: str, start_key: str, end_keys: tuple[str, ...]) -> str:
    """Return the lines from the top-level line `start_key` up to the first
    subsequent top-level line in `end_keys` (exclusive). Line-based so prose
    mentions of e.g. "on:" inside the WHY comment cannot false-anchor."""
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip() == start_key and not ln.startswith(" "))
    block: list[str] = []
    for ln in lines[start + 1 :]:
        if not ln.startswith(" ") and ln.strip() in end_keys:
            break
        block.append(ln)
    return "\n".join(block)


def test_workflow_file_exists():
    assert WORKFLOW.exists(), f"missing workflow file: {WORKFLOW}"


def test_verify_step_still_invokes_verify_merged_head():
    text = _normalized(WORKFLOW.read_text(encoding="utf-8"))
    assert (
        "bash loom-workflow/skills/git-memory/scripts/memory-grep.sh --verify-merged HEAD" in text
    ), "the --verify-merged HEAD invocation was removed or reworded"


def _verify_step_script(raw: str) -> str:
    """The verify step's `run: |` script body only — sliced from the step's
    `- name: Verify` line to the end of file (it is the last step). Scoping
    the exit-4 pins here means a YAML comment elsewhere mentioning
    `gh pr comment` can never satisfy them (T3 review 🟡, 2026-08-10:
    the whole-file pin stayed green with the comment line deleted)."""
    lines = raw.splitlines()
    start = next(
        i for i, ln in enumerate(lines) if ln.strip().startswith("- name: Verify")
    )
    return "\n".join(
        ln for ln in lines[start:] if not ln.lstrip().startswith("#")
    )


def test_exit_4_branch_comments_on_pr_and_keeps_the_red():
    script = _normalized(_verify_step_script(WORKFLOW.read_text(encoding="utf-8")))
    assert 'if [ "$rc" -eq 4 ]; then' in script, "exit-4 conditional missing"
    assert "gh pr comment" in script, "PR-comment notification missing from exit-4 branch"
    assert "exit 1" in script, "exit-4 branch no longer fails the workflow (red light lost)"


def test_permissions_block_grants_pr_write_and_keeps_contents_read():
    raw = WORKFLOW.read_text(encoding="utf-8")
    block = _normalized(_top_level_block(raw, "permissions:", ("jobs:",)))
    assert "pull-requests: write" in block, "permissions: lacks pull-requests: write"
    assert "contents: read" in block, "permissions: lost contents: read"


def test_trigger_is_push_to_main():
    raw = WORKFLOW.read_text(encoding="utf-8")
    block = _normalized(_top_level_block(raw, "on:", ("permissions:", "jobs:")))
    assert "push:" in block, "trigger lost push:"
    assert "branches:" in block, "trigger lost branches: filter"
    assert "[main]" in block, "trigger no longer scoped to main"
