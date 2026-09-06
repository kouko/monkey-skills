"""Adversarial probes against the squashed rehearsal shape (task W1-02).

`loom-code/scripts/rehearse_probes.py` today runs only one shape: a
CI-shaped clone that keeps the branch's full history (`_clone_ci_shaped`).
W1-02 adds a second shape to the *same run* -- the branch squashed to a
single commit off its trunk -- so a probe that only passes because it can
still see one of the branch's individual commits (for example, a probe
that asserts a specific commit subject is reachable, the way
`2026-09-05-artifact-charter-boundaries-and-edit-rights`'s squash merge
broke `plan-edits`) goes red before graduation instead of after the squash
merge lands on `main`.

These probes are written before the second shape exists. They drive
`rehearse_probes.py` exactly as today's callers do -- `paths... --repo
<repo>`, no new flag -- because the plan's own wording ("add a SECOND
shape to the SAME run") reads as: one invocation now does both shapes,
not a second CLI mode an existing caller has to opt into. If W1-02 lands
a different invocation shape (an opt-in flag, a separate script), these
probes stay red for an interface reason rather than a behavioral one --
that mismatch is itself something review has to reconcile against the
plan text, not something this file should paper over by guessing again.

Every probe builds its own throwaway git repository under `tmp_path` and
drives the script as a subprocess; none of them touches this repository's
own history. `core.autocrlf` is pinned `false` per
`docs/loom/memory/pre-*-git-autocrlf-input-masks-crlf-tests-pin-false-in-
temp-repo.md`-style precedent, even though these probes carry no CRLF
content, for the same reason every other scratch repo in this codebase
pins it: a byte-for-byte assumption should not depend on the host's
global git config.

Re-run any one test from the repo root:
    python3 -m pytest loom-code/scripts/test_probes_squash_abuse_squashed_rehearsal.py -q -k <name>
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "loom-code" / "scripts" / "rehearse_probes.py"

TIMEOUT = 300


# --------------------------------------------------------------------------
# harness
# --------------------------------------------------------------------------

def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=TIMEOUT
    )


def _git_ok(repo: Path, *args: str) -> str:
    proc = _git(repo, *args)
    assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"
    return proc.stdout.strip()


def make_repo(root: Path, *, trunk: str = "main", name: str = "work") -> Path:
    """A minimal working tree with one commit on `trunk`."""
    repo = root / name
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    _git_ok(repo, "symbolic-ref", "HEAD", f"refs/heads/{trunk}")
    _git_ok(repo, "config", "core.autocrlf", "false")
    _git_ok(repo, "config", "user.email", "adversary@example.invalid")
    _git_ok(repo, "config", "user.name", "Adversary")
    _git_ok(repo, "config", "commit.gpgsign", "false")
    (repo / "README").write_text("trunk content\n", encoding="utf-8")
    _git_ok(repo, "add", "README")
    _git_ok(repo, "commit", "-q", "-m", "first commit")
    return repo


def commit_file(repo: Path, relpath: str, text: str, message: str) -> Path:
    path = repo / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    _git_ok(repo, "add", relpath)
    _git_ok(repo, "commit", "-q", "-m", message)
    return path


def run_script(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, timeout=TIMEOUT,
        env={**os.environ, **(env or {})},
    )


GREEN_PROBE = "def test_ok():\n    assert True\n"

ORIGIN_MAIN_SKIP_PROBE = '''import subprocess
from pathlib import Path
import pytest


def _root():
    return subprocess.run(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def _resolves(ref):
    return subprocess.run(
        ["git", "-C", _root(), "rev-parse", "--verify", "--quiet", ref + "^{commit}"],
        capture_output=True, text=True,
    ).returncode == 0


def test_originMainSkipProbe_noTrunkRefResolves_skipsInsteadOfFailing():
    for ref in ("origin/main", "main"):
        if _resolves(ref):
            return
    pytest.skip("no trunk ref resolves in this clone")
'''

BRANCH_ONLY_COMMIT_PROBE = '''import subprocess
from pathlib import Path


def _root():
    return subprocess.run(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def test_branchOnlyCommitProbe_findsIntermediateCommitSubject_bySubjectGrep():
    log = subprocess.run(
        ["git", "-C", _root(), "log", "--oneline", "--all",
         "--grep=intermediate branch work", "--format=%H"],
        capture_output=True, text=True,
    )
    assert log.stdout.strip() != "", (
        "the commit subject 'intermediate branch work' is not reachable -- "
        "this probe depends on a commit that only exists before the branch "
        "is squashed to one commit off its trunk"
    )
'''

NESTED_MARKER_PROBE = """\
import os
from pathlib import Path

def test_marker_is_set_inside_whatever_clone_runs_this():
    marker = os.environ.get("REHEARSE_PROBES_NESTED")
    assert marker is not None, "REHEARSE_PROBES_NESTED is unset inside a rehearsal clone"
    marker_path = Path(marker)
    assert marker_path.is_absolute(), marker
    assert marker_path.resolve() == Path.cwd().resolve()
"""

RECURSING_PROBE = '''import os
import subprocess
import sys
from pathlib import Path


def test_recursingProbe_findsNestedMarkerSet_neverReRehearsesItself():
    marker = os.environ.get("REHEARSE_PROBES_NESTED")
    assert marker is not None, (
        "a probe that itself knows how to invoke rehearse_probes.py must see "
        "the nested marker inside every clone this script builds -- CI-shaped "
        "or squashed -- so it can skip instead of opening a second recursion path"
    )
'''


# --------------------------------------------------------------------------
# 1: a probe that skips when no trunk ref resolves must not be turned into
# a reported failure by the squashed shape when a trunk DOES exist but the
# repository is single-branch (nothing to squash off).
# --------------------------------------------------------------------------

def test_squashedShape_noOriginConfigured_originMainSkipProbeStaysGreen(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path, trunk="main")
    assert _git(repo, "remote").stdout.strip() == ""
    commit_file(repo, "tests/test_origin_main_skip.py", ORIGIN_MAIN_SKIP_PROBE, "origin-main skip probe")

    proc = run_script("tests/test_origin_main_skip.py", "--repo", str(repo))
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert "FAILED (0)" in proc.stdout, proc.stdout
    assert "Traceback" not in proc.stderr, proc.stderr


# --------------------------------------------------------------------------
# 2: a probe that needs a commit only the branch has (not the squashed
# trunk-relative history) must fail in the squashed shape, named with its
# reason, while the CI-shaped run (full history) stays green for the same
# probe -- the exact plan-commit-vs-squash-merge scenario this change
# exists to catch before graduation instead of after.
# --------------------------------------------------------------------------

def test_squashedShape_probeNeedingBranchOnlyCommit_isReportedFailedWithReason(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path, trunk="main")
    bare = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, capture_output=True)
    _git_ok(repo, "remote", "add", "origin", str(bare))
    _git_ok(repo, "push", "-q", "origin", "main")

    commit_file(repo, "src/marker.txt", "intermediate\n", "intermediate branch work")
    commit_file(
        repo, "tests/test_branch_only.py", BRANCH_ONLY_COMMIT_PROBE, "add branch-only probe"
    )

    proc = run_script("tests/test_branch_only.py", "--repo", str(repo))
    assert proc.returncode != 0, (
        "a probe that only passes because it can see a commit the trunk-"
        "relative squash collapses away must make the whole script fail "
        f"non-zero -- stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert "test_branch_only.py" in proc.stdout, (
        "the failing probe must be named in the output, not just a bare "
        f"non-zero exit code -- stdout:\n{proc.stdout}"
    )
    lowered = proc.stdout.lower()
    assert "squash" in lowered, (
        "the output must say which shape (the squashed one) is the one that "
        f"went red, not merely that something failed -- stdout:\n{proc.stdout}"
    )


# --------------------------------------------------------------------------
# 3: the source repository is never mutated or left with clones behind by
# running the squashed shape -- refs and HEAD are bit-identical before and
# after, and no rehearsal directory survives in a temp root only this run
# writes to.
# --------------------------------------------------------------------------

def test_squashedShape_run_leavesSourceRepoAndTempRootUntouched(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_green.py", GREEN_PROBE, "green")

    before_head = _git_ok(repo, "rev-parse", "HEAD")
    before_refs = _git_ok(repo, "show-ref")
    # A temp root private to this test: the script's `tempfile.mkdtemp`
    # honours TMPDIR, so every clone it makes lands here and nowhere else.
    # Diffing the shared system temp root instead races under xdist --
    # every sibling in this file spawns the same script, and one of them
    # creating or deleting its own `rehearse-probes-*` dir mid-run reads
    # as this run's leak (or hides one).
    tmp_root = tmp_path / "tmproot"
    tmp_root.mkdir()

    proc = run_script("tests/test_green.py", "--repo", str(repo), env={"TMPDIR": str(tmp_root)})
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"

    after_head = _git_ok(repo, "rev-parse", "HEAD")
    after_refs = _git_ok(repo, "show-ref")
    leftover = sorted(p.name for p in tmp_root.iterdir() if p.name.startswith("rehearse-probes-"))

    assert before_head == after_head, "the source repository's HEAD moved"
    assert before_refs == after_refs, "the source repository's refs changed"
    assert not leftover, f"the squashed shape's clone was not cleaned up: {leftover}"


# --------------------------------------------------------------------------
# 4: the squashed shape's clone must carry the same nesting guard as the
# CI-shaped clone (REHEARSE_PROBES_NESTED) -- a probe that itself knows how
# to re-invoke rehearse_probes.py must see the marker inside whichever
# clone runs it, not just the CI-shaped one, so no second recursion path
# opens up.
# --------------------------------------------------------------------------

def test_squashedShape_recursingProbe_seesNestedMarkerTooNotJustCiShaped(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_recursing.py", RECURSING_PROBE, "recursing probe")

    proc = run_script("tests/test_recursing.py", "--repo", str(repo))
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert "FAILED (0)" in proc.stdout, proc.stdout


# --------------------------------------------------------------------------
# 5: a repository with no trunk ref at all (no origin, trunk not named
# main/master) has nothing sensible to squash onto -- must not crash, and
# must say so rather than silently skipping the check.
# --------------------------------------------------------------------------

def test_noTrunkRefAtAll_squashedShapeHasNoTarget_doesNotCrashAndSaysSo(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path, trunk="develop")
    assert _git(repo, "remote").stdout.strip() == ""
    commit_file(repo, "tests/test_green.py", GREEN_PROBE, "green")

    proc = run_script("tests/test_green.py", "--repo", str(repo))
    assert "Traceback" not in proc.stderr, (
        f"an unhandled exception instead of a stated reason -- stderr:\n{proc.stderr}"
    )
    combined = proc.stdout + proc.stderr
    assert combined.strip() != "", "silence is not the same as saying so"


# --------------------------------------------------------------------------
# 6: a branch whose only commit IS the trunk commit (nothing diverges) has
# nothing to squash -- must not crash, and the CI-shaped result (which is
# unaffected) must still be reported.
# --------------------------------------------------------------------------

def test_branchIsTrunk_nothingToSquash_ciShapedResultStillReported(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, trunk="main")
    bare = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, capture_output=True)
    _git_ok(repo, "remote", "add", "origin", str(bare))
    _git_ok(repo, "push", "-q", "origin", "main")
    # the probe itself is the only commit ahead of what was just pushed
    commit_file(repo, "tests/test_green.py", GREEN_PROBE, "green")
    _git_ok(repo, "push", "-q", "origin", "main")  # trunk now equals HEAD exactly

    proc = run_script("tests/test_green.py", "--repo", str(repo))
    assert "Traceback" not in proc.stderr, proc.stderr
    assert "FAILED (0)" in proc.stdout, (
        f"the CI-shaped result must still be reported even though there is "
        f"nothing for the squashed shape to squash -- stdout:\n{proc.stdout}"
    )


# --------------------------------------------------------------------------
# 7: a completely empty repository (zero commits, unborn HEAD) must not
# crash the squashed shape any more than it crashes the existing CI-shaped
# one -- recorded here because the second shape is exactly where a new
# unguarded `git rev-parse HEAD` on an unborn branch would surface.
# --------------------------------------------------------------------------

def test_emptyRepoNoCommits_squashedShapeAttempt_doesNotRaiseUnhandled(tmp_path: Path) -> None:
    repo = tmp_path / "empty"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    _git_ok(repo, "config", "user.email", "adversary@example.invalid")
    _git_ok(repo, "config", "user.name", "Adversary")

    proc = run_script("tests/test_whatever.py", "--repo", str(repo))
    assert proc.returncode != 0, "an unborn HEAD cannot be rehearsed; this must be reported, not silently ok"
    assert "Traceback" not in proc.stderr, proc.stderr


# --------------------------------------------------------------------------
# 8: a red squashed shape must make the whole script exit non-zero even
# when the CI-shaped run for the exact same paths is green -- the exit
# code is the graduation gate, not the printed text.
# --------------------------------------------------------------------------

def test_exitCode_squashedShapeRed_isNonzeroEvenThoughCiShapedShapeIsGreen(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path, trunk="main")
    bare = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, capture_output=True)
    _git_ok(repo, "remote", "add", "origin", str(bare))
    _git_ok(repo, "push", "-q", "origin", "main")

    commit_file(repo, "src/marker.txt", "intermediate\n", "intermediate branch work")
    commit_file(repo, "tests/test_green.py", GREEN_PROBE, "an unrelated green probe")
    commit_file(
        repo, "tests/test_branch_only.py", BRANCH_ONLY_COMMIT_PROBE, "add branch-only probe"
    )

    proc = run_script(
        "tests/test_green.py", "tests/test_branch_only.py", "--repo", str(repo),
    )
    assert proc.returncode != 0, (
        "one red probe in the squashed shape must fail the whole run even "
        f"though a sibling probe is green in both shapes -- stdout:\n{proc.stdout}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
