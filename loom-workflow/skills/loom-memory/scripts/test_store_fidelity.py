"""Acceptance 3 of 2026-09-11-loom-memory-into-loom-workflow: the 293
migrated lesson concepts and the generated index must not have changed by
a single byte while this change relocates the *skill*, never the store.

Recomputed straight from Git rather than pinned to a committed snapshot: the
working tree's `docs/loom/memory/` is compared, path-for-path and
byte-for-byte, against `origin/main` — the trunk this branch forked from,
which never touched the store either. `README.md` is the one deliberate
exception: W1-02 repointed its command paths from the retired
`loom-memory/scripts/...` to the relocated `loom-workflow/skills/loom-memory/
scripts/...`, a legitimate content change this test must not flag.

Uses `git ls-tree -z` (not a bare `--name-only` scan) so a non-ASCII lesson
filename is never silently dropped by git's default quoting of "unusual"
path bytes (a documented gotcha in this repo's own memory).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
STORE_DIR = REPO_ROOT / "docs" / "loom" / "memory"
STORE_REL_PREFIX = "docs/loom/memory"
BASELINE_REF = "origin/main"


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        check=False,
    )


def _baseline_available() -> bool:
    return _git("rev-parse", "--verify", f"{BASELINE_REF}^{{commit}}").returncode == 0


def _baseline_paths() -> set[str]:
    result = _git("ls-tree", "-r", "-z", "--name-only", BASELINE_REF, "--", STORE_REL_PREFIX)
    result.check_returncode()
    raw = result.stdout.decode("utf-8")
    return {entry for entry in raw.split("\0") if entry}


def _baseline_blob(rel_path: str) -> bytes:
    result = _git("show", f"{BASELINE_REF}:{rel_path}")
    result.check_returncode()
    return result.stdout


def _working_paths() -> set[str]:
    return {
        str(path.relative_to(REPO_ROOT))
        for path in STORE_DIR.rglob("*")
        if path.is_file()
    }


@pytest.mark.skipif(
    not _baseline_available(),
    reason=f"{BASELINE_REF} is not available in this checkout",
)
def test_memory_store_is_byte_identical_to_trunk_except_readme() -> None:
    baseline_paths = _baseline_paths()
    working_paths = _working_paths()

    assert working_paths == baseline_paths, (
        "docs/loom/memory file set diverged from trunk: "
        f"added={sorted(working_paths - baseline_paths)} "
        f"removed={sorted(baseline_paths - working_paths)}"
    )

    changed = []
    for rel_path in sorted(working_paths):
        if rel_path == f"{STORE_REL_PREFIX}/README.md":
            continue
        working_bytes = (REPO_ROOT / rel_path).read_bytes()
        if working_bytes != _baseline_blob(rel_path):
            changed.append(rel_path)

    assert changed == [], f"content diverged from trunk: {changed}"
