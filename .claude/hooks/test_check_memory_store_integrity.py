"""Behavioral tests for the memory-store integrity PostToolUse hook.

The hook (``check-memory-store-integrity.sh``) is a shift-left guard for the
CI step that runs ``scripts/check_loom_memory_integrity.py``. It must:

- fire for any edit under ``docs/loom/memory/``, including the store's own
  ``README.md`` (deleting an index line breaks the invariant just as surely
  as forgetting to add one),
- derive the repo root from the edited path and invoke the real checker,
- exit 0 when the store is valid, exit 2 on a violation (with a stderr fix-hint
  naming the offending file). A PostToolUse exit 2 does not undo the write —
  the file has landed; the hook surfaces the problem to the agent at the edit
  instead of after push,
- no-op (exit 0) for any path outside the store,
- no-op (exit 0) when the checker is ABSENT — the store is portable
  (``loom-pipeline:loom-memory`` fires in any repo carrying
  ``docs/loom/memory/README.md``) while the checker ships inside no plugin,
  so a consuming repo must not be blocked by a missing-file error.

Why this hook exists: the §Index invariant was violated three times. The
first two shipped and were caught by CI after push, under a job named
``plugin version bump`` — which names a different check, so the failure did
not point at the store. The third was caught one step later than here, at
branch close-out, by an orchestrator following prose.

Tests drive the hook the way Claude Code does: a mock PostToolUse stdin-JSON
``{"tool_input": {"file_path": ...}}`` piped to the script.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "check-memory-store-integrity.sh"
CHECKER = REPO_ROOT / "scripts" / "check_loom_memory_integrity.py"

_ENTRY_NAME = "some-durable-lesson"
_ENTRY_DESC = "A one-line description that the index must carry byte-identical"


def run_hook(file_path: str) -> subprocess.CompletedProcess[str]:
    # Without this, a test asserting on a SIDE EFFECT passes vacuously while
    # the hook does not exist at all — green for the wrong reason. Keep it even
    # though no such side-effect test survives in this module today: the next
    # one added here would inherit the same trap.
    assert HOOK.is_file(), f"hook is absent at {HOOK}"
    stdin = json.dumps({"tool_input": {"file_path": file_path}})
    return subprocess.run(
        ["bash", str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
    )


def _make_store(tmp_path: Path, *, indexed: bool, with_checker: bool = True) -> Path:
    """Build a minimal repo carrying a memory store.

    Returns the path to the entry file (what the hook is fed).
    """
    if with_checker:
        (tmp_path / "scripts").mkdir()
        shutil.copy(CHECKER, tmp_path / "scripts" / "check_loom_memory_integrity.py")

    store = tmp_path / "docs" / "loom" / "memory"
    store.mkdir(parents=True)

    entry = store / f"{_ENTRY_NAME}.md"
    entry.write_text(
        f"---\nname: {_ENTRY_NAME}\ndescription: {_ENTRY_DESC}\n"
        "type: practice\norigin: test\n---\n\nThe fact.\n",
        encoding="utf-8",
    )

    index_line = f"[{_ENTRY_NAME}]({_ENTRY_NAME}.md) — {_ENTRY_DESC}\n" if indexed else ""
    (store / "README.md").write_text(
        f"# store\n\n## Index\n\n{index_line}", encoding="utf-8"
    )
    return entry


def test_blocks_when_index_line_is_missing(tmp_path: Path) -> None:
    """The recurring defect: the entry file is written, its index line is not."""
    entry = _make_store(tmp_path, indexed=False)

    result = run_hook(str(entry))

    assert result.returncode == 2, (
        f"must block on a store violation; got {result.returncode}\n{result.stderr}"
    )
    assert _ENTRY_NAME in result.stderr, \
        "the checker's own report must reach the reader, naming the file"
    # The hook's OWN contribution, not the checker's: the --write regen
    # command and the re-run command, neither of which a reader can get from
    # `$REPORT`. The mutation that isolates them keeps `$REPORT` on stderr and
    # deletes only the Fix body — that turns THIS assertion red, which is what
    # makes the two load-bearing. (Deleting the whole heredoc instead proves
    # nothing about them: it empties stderr, so the assertion above fails
    # first and these two never run. An earlier draft of this comment cited
    # exactly that mutation.)
    #
    # The re-run assertion below pins "then re-run the check:" together with
    # its command line, NOT the bare command string — the bare command
    # ("python3 scripts/check_loom_memory_integrity.py") is a substring of
    # the regen line above ("...check_loom_memory_integrity.py --write"), so
    # deleting only the re-run line could not turn a bare-command assertion
    # red independently. The "then re-run the check:" phrase appears nowhere
    # else in the Fix block, so this pin is unique to the re-run line and the
    # two assertions are independently falsifiable, as the module docstring
    # (and CI) require.
    assert "python3 scripts/check_loom_memory_integrity.py --write" in result.stderr, \
        "the fix-hint must give the regen command"
    assert (
        "then re-run the check:\n\n    python3 scripts/check_loom_memory_integrity.py\n"
        in result.stderr
    ), "the fix-hint must give the re-run command, distinct from the --write regen line"
    # --write itself can refuse (bad frontmatter, stray prose) instead of
    # regenerating — the Fix block must tell the reader what to do THEN, not
    # just what to do when --write succeeds.
    assert "If --write refuses" in result.stderr, \
        "the fix-hint must cover --write's own refusal, not just the happy path"


def test_passes_when_the_store_is_valid(tmp_path: Path) -> None:
    entry = _make_store(tmp_path, indexed=True)

    result = run_hook(str(entry))

    assert result.returncode == 0, \
        f"a valid store must not block; stderr was:\n{result.stderr}"


def test_fires_on_the_readme_itself(tmp_path: Path) -> None:
    """Deleting an index line breaks the invariant as surely as omitting one,
    so an edit to the store's own README must be checked too."""
    _make_store(tmp_path, indexed=False)
    readme = tmp_path / "docs" / "loom" / "memory" / "README.md"

    result = run_hook(str(readme))

    assert result.returncode == 2, \
        "an edit to the store README must be checked, not skipped"


def test_no_ops_outside_the_store(tmp_path: Path) -> None:
    """A guard that fires on unrelated edits gets disabled by its users."""
    _make_store(tmp_path, indexed=False)
    for rel in (
        "docs/loom/plans/some-plan.md",
        # Near-miss siblings: a prefix-only pattern (`*/docs/loom/memory*`)
        # swallows these, and the distant `plans/` probe alone cannot tell the
        # two patterns apart — widening the case survived the whole suite.
        "docs/loom/memory-archive/old-entry.md",
        "docs/loom/memoryX/entry.md",
    ):
        unrelated = tmp_path / rel
        unrelated.parent.mkdir(parents=True, exist_ok=True)
        unrelated.write_text("not a memory entry\n", encoding="utf-8")

        result = run_hook(str(unrelated))

        assert result.returncode == 0, (
            f"must no-op outside docs/loom/memory/ ({rel}), even with an "
            f"invalid store present; stderr:\n{result.stderr}"
        )


def test_no_ops_when_the_checker_is_absent(tmp_path: Path) -> None:
    """Portability: the store travels to other repos, the checker does not.

    A consuming repo with a store but no `scripts/check_loom_memory_integrity.py`
    must not be blocked by the missing file — that would turn a
    'No such file' error into a phantom store violation.
    """
    entry = _make_store(tmp_path, indexed=False, with_checker=False)

    result = run_hook(str(entry))

    assert result.returncode == 0, (
        "a repo without the checker must not be blocked; got "
        f"{result.returncode}\n{result.stderr}"
    )


# NOTE — there is deliberately no test for the hook's `PYTHONDONTWRITEBYTECODE=1`.
# A first draft asserted that no `scripts/__pycache__` appears after a run, and
# whole-branch review proved it an equivalent mutant: removing the env var from
# the hook keeps the suite green, because CPython never caches the `__main__`
# script and the checker imports stdlib only, so the directory is unreachable
# either way. The env var stays in the hook as cheap defence should the checker
# ever grow a local import; it is documented there, not guarded here. Writing a
# test that cannot fail is worse than writing none — it reports coverage that
# does not exist.
