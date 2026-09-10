"""Adversarial probe (surface 3): the store-fidelity proof's baseline-missing skip.

`loom-workflow/skills/loom-memory/scripts/test_store_fidelity.py` claims the
293 migrated lesson concepts are byte-identical to `origin/main`. The only
test in that file is gated with:

    @pytest.mark.skipif(not _baseline_available(), reason=...)

`_baseline_available()` is `git rev-parse --verify origin/main^{commit}`
returning success. A completely ordinary checkout shape — a fresh
single-branch `git clone` of just this feature branch, with no other remote
tracking refs fetched — has no `origin/main` at all. In that shape the test
is SKIPPED, not failed, and not run: a viewer sees "1 skipped" in green CI
output with zero assurance the store's bytes were compared to anything.

This probe proves the failure mode concretely: it clones this repository
(the feature branch alone, `origin` removed so no ref-completion can find
`main` from elsewhere), corrupts a real lesson file's content inside that
clone, and shows the fidelity test — which exists specifically to catch
exactly that corruption — reports SKIPPED rather than FAILED.

Run:
    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
        docs/loom/2026-09-11-loom-memory-into-loom-workflow/evidence/probes/test_adversarial_store_fidelity_silent_skip.py -v -s
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
CURRENT_BRANCH = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "rev-parse", "--abbrev-ref", "HEAD"],
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()


def _single_branch_clone_without_origin_main(dest: Path) -> Path:
    subprocess.run(
        [
            "git",
            "clone",
            "-q",
            "--no-hardlinks",
            "--single-branch",
            "--branch",
            CURRENT_BRANCH,
            str(REPO_ROOT),
            str(dest),
        ],
        check=True,
    )
    subprocess.run(["git", "-C", str(dest), "remote", "remove", "origin"], check=True)
    return dest


def test_store_fidelity_check_skips_instead_of_failing_when_origin_main_is_unreachable(tmp_path):
    """A single-branch clone with `origin` removed genuinely has no
    resolvable `origin/main` — this is asserted first so the probe fails
    loudly (not silently) if the fixture assumption ever stops holding."""
    clone = _single_branch_clone_without_origin_main(tmp_path / "clone")

    resolve = subprocess.run(
        ["git", "-C", str(clone), "rev-parse", "--verify", "origin/main^{commit}"],
        capture_output=True,
        text=True,
    )
    assert resolve.returncode != 0, (
        "fixture assumption broken: origin/main unexpectedly resolved in "
        "the single-branch clone; this probe no longer exercises the "
        "skip path and must be revised"
    )

    # Corrupt one real, non-README lesson file's content — the exact class
    # of regression the fidelity test exists to catch.
    memory_dir = clone / "docs" / "loom" / "memory"
    target = next(
        p for p in sorted(memory_dir.glob("*.md")) if p.name != "README.md"
    )
    original = target.read_bytes()
    assert original, "fixture assumption broken: chosen lesson file is empty"
    target.write_bytes(b"CORRUPTED CONTENT - all lesson bytes lost\n")

    scripts_dir = clone / "loom-workflow" / "skills" / "loom-memory" / "scripts"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "test_store_fidelity.py",
            "-v",
        ],
        cwd=scripts_dir,
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"},
    )

    combined = result.stdout + result.stderr
    # The defect: SKIPPED, not FAILED, despite genuine content corruption
    # sitting right there in the tree the test was pointed at.
    assert "1 skipped" in combined, combined
    assert "FAILED" not in combined, (
        "expected the corrupted content to go undetected (documenting the "
        "surviving gap); if this now fails, the skip-on-missing-baseline "
        "behavior has changed"
    )
