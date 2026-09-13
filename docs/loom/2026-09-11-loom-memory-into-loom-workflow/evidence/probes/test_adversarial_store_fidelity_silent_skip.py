"""Adversarial probe (surface 3): the store-fidelity proof's baseline-missing skip.

`loom-workflow/skills/loom-memory/scripts/test_store_fidelity.py` claims the
293 migrated lesson concepts are byte-identical to `origin/main`. The only
test in that file used to be gated with:

    @pytest.mark.skipif(not _baseline_available(), reason=...)

`_baseline_available()` is `git rev-parse --verify origin/main^{commit}`
returning success. A completely ordinary checkout shape — a fresh
single-branch `git clone` of just this feature branch, with no other remote
tracking refs fetched — has no `origin/main` at all. In that shape the test
used to be SKIPPED, not failed, and not run: a viewer saw "1 skipped" in
green CI output with zero assurance the store's bytes were compared to
anything, and the CI job that runs it (`.github/workflows/loom-workflow-
ci.yml`) checked out with no `fetch-depth`, so this was CI's actual behavior,
not a hypothetical.

This probe proves BOTH halves of the fix: (1) with `CI=1` set and no
reachable baseline, the test now FAILS, naming the missing baseline, instead
of skipping silently; (2) with a reachable baseline (the CI job now checks
out with `fetch-depth: 0`) and one lesson file corrupted in a scratch clone,
the test fails on the content — the corruption the proof exists to catch.

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


def test_store_fidelity_check_fails_naming_the_baseline_when_origin_main_is_unreachable_in_ci(tmp_path):
    """A single-branch clone with `origin` removed genuinely has no
    resolvable `origin/main` — this is asserted first so the probe fails
    loudly (not silently) if the fixture assumption ever stops holding.

    With `CI=1` set (as GitHub Actions always sets it), the fixed test must
    now FAIL, naming the missing baseline, instead of silently skipping —
    even with a real lesson file corrupted right there in the tree the
    proof was pointed at."""
    clone = _single_branch_clone_without_origin_main(tmp_path / "clone")

    resolve = subprocess.run(
        ["git", "-C", str(clone), "rev-parse", "--verify", "origin/main^{commit}"],
        capture_output=True,
        text=True,
    )
    assert resolve.returncode != 0, (
        "fixture assumption broken: origin/main unexpectedly resolved in "
        "the single-branch clone; this probe no longer exercises the "
        "missing-baseline path and must be revised"
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
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin", "CI": "1"},
    )

    combined = result.stdout + result.stderr
    # The fix: FAILED, not skipped, naming the missing baseline — a viewer
    # can no longer see green ("1 skipped") with zero assurance.
    assert "1 failed" in combined, combined
    assert "origin/main" in combined
    assert "not available" in combined
    assert "skipped" not in combined, (
        "expected the missing-baseline case to be a hard failure in CI, "
        "not a skip"
    )


def test_store_fidelity_check_fails_on_content_when_baseline_is_reachable(tmp_path):
    """Control / second half of the fix: an ordinary clone (with `origin`
    intact, so `origin/main` resolves) and the same real-lesson-file
    corruption now fails on the content itself — the proof runs and does
    its actual job when the baseline is reachable, CI or not."""
    clone = tmp_path / "clone-with-origin"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(REPO_ROOT), str(clone)],
        check=True,
    )
    # `REPO_ROOT` (this working tree) itself tracks the real GitHub
    # `origin/main` at `refs/remotes/origin/main`, distinct from its own
    # (possibly stale) local `refs/heads/main`. Fetching the FULL ref name
    # — never the shorthand `main`, which is ambiguous against a source
    # that carries both — copies that exact, up-to-date tip into the clone.
    subprocess.run(
        [
            "git", "-C", str(clone), "fetch", "-q", "origin",
            "+refs/remotes/origin/main:refs/remotes/origin/main",
        ],
        check=True,
    )

    resolve = subprocess.run(
        ["git", "-C", str(clone), "rev-parse", "--verify", "origin/main^{commit}"],
        capture_output=True,
        text=True,
    )
    assert resolve.returncode == 0, (
        "fixture assumption broken: origin/main did not resolve in the "
        "ordinary clone; this probe no longer exercises the "
        "baseline-reachable path and must be revised"
    )

    memory_dir = clone / "docs" / "loom" / "memory"
    target = next(
        p for p in sorted(memory_dir.glob("*.md")) if p.name != "README.md"
    )
    original = target.read_bytes()
    assert original, "fixture assumption broken: chosen lesson file is empty"
    target.write_bytes(b"CORRUPTED CONTENT - all lesson bytes lost\n")

    scripts_dir = clone / "loom-workflow" / "skills" / "loom-memory" / "scripts"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test_store_fidelity.py", "-v"],
        cwd=scripts_dir,
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"},
    )

    combined = result.stdout + result.stderr
    assert "1 failed" in combined, combined
    assert "content diverged from trunk" in combined
    assert str(target.relative_to(clone)) in combined or target.name in combined
