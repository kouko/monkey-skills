"""Adversarial probes against `loom-code/scripts/rehearse_probes.py` (task W1-01).

Written before the implementer, so the RED comes from outside the code it
attacks. Every probe builds its own throwaway git repository under
`tmp_path` -- a real `git init`, real commits, a real bare `origin` where
the case needs one, `core.autocrlf` pinned false -- and drives the script
as a subprocess. None of them touches this repository's own history.

The classes attacked here: empty and absent input (a test path that is
not there, a repo that is not a repository), boundaries (the default glob
matches `test_probes_*.py` and stops there; a skip is information and
never moves the exit code), hostile input (a path outside the repository,
a repository path carrying spaces and non-ASCII, a trunk called `master`
instead of `main`), wrong state (an uncommitted edit in the working tree,
a bare repository handed to `--repo`), and a failing dependency (pytest
absent from the interpreter that runs inside the clone).

Today every probe is RED at `_require_script`: `rehearse_probes.py` does
not exist yet.
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

def _require_script() -> None:
    """Fail loudly, and with the reason, while W1-01 is unimplemented."""
    assert SCRIPT.is_file(), (
        f"{SCRIPT} does not exist -- the W1-01 rehearsal script is unwritten, "
        "so every probe in this file is red for that one reason"
    )


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=TIMEOUT
    )
    assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"
    return proc.stdout.strip()


def make_repo(root: Path, *, trunk: str = "main", name: str = "work") -> Path:
    """A minimal working tree with one commit on `trunk`."""
    repo = root / name
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    _git(repo, "symbolic-ref", "HEAD", f"refs/heads/{trunk}")
    _git(repo, "config", "core.autocrlf", "false")
    _git(repo, "config", "user.email", "adversary@example.invalid")
    _git(repo, "config", "user.name", "Adversary")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "README").write_text("committed content\n", encoding="utf-8")
    _git(repo, "add", "README")
    _git(repo, "commit", "-q", "-m", "first commit")
    return repo


def commit_file(repo: Path, relpath: str, text: str, message: str) -> Path:
    path = repo / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    _git(repo, "add", relpath)
    _git(repo, "commit", "-q", "-m", message)
    return path


def add_bare_origin(root: Path, repo: Path, trunk: str) -> Path:
    bare = root / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, capture_output=True)
    _git(repo, "remote", "add", "origin", str(bare))
    _git(repo, "push", "-q", "origin", trunk)
    return bare


def run_rehearse(
    *args: str,
    repo: Path | None = None,
    tmp_root: Path | None = None,
    env_extra: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    _require_script()
    env = dict(os.environ)
    if tmp_root is not None:
        env["TMPDIR"] = str(tmp_root)
    if env_extra:
        env.update(env_extra)
    argv = [sys.executable, str(SCRIPT)]
    if repo is not None:
        argv += ["--repo", str(repo)]
    argv += list(args)
    return subprocess.run(
        argv, capture_output=True, text=True, timeout=TIMEOUT, env=env, cwd=str(REPO_ROOT)
    )


def out(proc: subprocess.CompletedProcess) -> str:
    return proc.stdout + proc.stderr


def line_with(text: str, needle: str) -> str:
    for line in text.splitlines():
        if needle in line:
            return line
    raise AssertionError(f"no line containing {needle!r} in:\n{text}")


# --------------------------------------------------------------------------
# probe bodies injected into the throwaway repositories
# --------------------------------------------------------------------------

_HEADER = '''import subprocess
from pathlib import Path

import pytest


def _root():
    return subprocess.run(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def _git(*args):
    return subprocess.run(["git", "-C", _root(), *args], capture_output=True, text=True)


def _resolves(ref):
    return _git("rev-parse", "--verify", "--quiet", ref + "^{commit}").returncode == 0
'''

LOCAL_MAIN_PROBE = _HEADER + '''

def test_localMainProbe_readsLocalMainRef_findsTheReadme():
    """The shape that went red on CI three times: it reads a local `main`."""
    shown = _git("show", "main:README")
    assert shown.returncode == 0, shown.stderr
    assert "committed content" in shown.stdout
'''

ORIGIN_MAIN_PROBE = _HEADER + '''

def test_originMainProbe_noTrunkRefResolves_skipsInsteadOfFailing():
    """The rewrite: try `origin/main`, then `main`, then skip."""
    for ref in ("origin/main", "main"):
        if _resolves(ref):
            shown = _git("show", ref + ":README")
            assert "committed content" in shown.stdout
            return
    pytest.skip("no trunk ref resolves in this clone")
'''

CI_SHAPE_PROBE = _HEADER + '''
import os


def test_cloneShape_freshRehearsalClone_matchesCiCheckout():
    """Full history, origin/main, no local trunk branch, detached HEAD.

    The expected shas arrive by environment variable so that committing
    this file cannot invalidate the sha it pins.
    """
    assert _resolves(os.environ["ADVERSARY_OLD_SHA"]), "the clone lost history older than HEAD"
    assert _resolves("origin/main"), "origin/main does not resolve in the clone"
    assert not _resolves("refs/heads/main"), "the clone kept a local main branch"
    assert not _resolves("refs/heads/master"), "the clone kept a local master branch"
    assert _git("symbolic-ref", "-q", "HEAD").returncode != 0, "HEAD is still attached"
    assert _git("rev-parse", "HEAD").stdout.strip() == os.environ["ADVERSARY_HEAD_SHA"]
'''

MASTER_TRUNK_PROBE = _HEADER + '''

def test_cloneShape_trunkNamedMaster_dropsTheLocalMasterRef():
    assert not _resolves("refs/heads/master"), "the clone kept a local master branch"
    assert _resolves("origin/master"), "origin/master does not resolve in the clone"
    assert _git("symbolic-ref", "-q", "HEAD").returncode != 0, "HEAD is still attached"
'''

WORKING_TREE_PROBE = _HEADER + '''

def test_cloneContent_dirtyWorkingTree_carriesOnlyCommittedState():
    readme = (Path(_root()) / "README").read_text(encoding="utf-8")
    assert "committed content" in readme
    assert "DIRTY_CONTENT_MUST_NOT_APPEAR" not in readme
    assert not (Path(_root()) / "untracked_must_not_appear.txt").exists()
'''

GREEN_PROBE = '''def test_greenProbe_nothingHostile_passes():
    """A probe that always passes, used to read the rehearsal's exit code."""
    assert True
'''

RED_PROBE = '''def test_redProbe_nothingHostile_fails():
    """A probe that always fails, used to read the rehearsal's exit code."""
    assert False, "deliberate adversarial failure"
'''

FAIL_AND_SKIP_PROBE = '''import pytest


def test_mixedFile_deliberateFailure_fails():
    assert False, "deliberate adversarial failure"


def test_mixedFile_deliberateSkip_skips():
    pytest.skip("adversarial skip reason")
'''


# --------------------------------------------------------------------------
# 1-2. the acceptance pair: local `main` is red, the `origin/main` rewrite is green
# --------------------------------------------------------------------------

def test_rehearseProbes_probeReadsLocalMain_reportsFailedAndExitsNonZero(tmp_path: Path) -> None:
    """A probe reading a local `main` must go red inside the rehearsal even
    though the working tree has a `main` branch that satisfies it."""
    repo = make_repo(tmp_path, trunk="main")
    add_bare_origin(tmp_path, repo, "main")
    commit_file(repo, "tests/test_local_main_probe.py", LOCAL_MAIN_PROBE, "local main probe")

    # The same probe is green in the working tree -- that is the whole trap.
    local = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_local_main_probe.py", "-q",
         "-p", "no:cacheprovider"],
        cwd=str(repo), capture_output=True, text=True, timeout=TIMEOUT,
    )
    assert local.returncode == 0, f"the probe is meant to pass locally:\n{local.stdout}"

    proc = run_rehearse("tests/test_local_main_probe.py", repo=repo, tmp_root=tmp_path / "t")
    text = out(proc)
    assert proc.returncode != 0, f"the rehearsal stayed green on a local-main probe:\n{text}"
    failed = line_with(text, "test_localMainProbe_readsLocalMainRef_findsTheReadme")
    assert "test_local_main_probe.py" in failed
    assert "FAILED" in text


def test_rehearseProbes_probeSkipsWhenNoTrunkResolves_exitsZeroAndListsTheSkip(
    tmp_path: Path,
) -> None:
    """The rewritten probe is green in both worlds: it passes where
    `origin/main` resolves, and it skips -- exit code untouched, reason
    printed -- where nothing does."""
    trunkless = make_repo(tmp_path / "a", trunk="feature-only")
    commit_file(trunkless, "tests/test_origin_main_probe.py", ORIGIN_MAIN_PROBE, "rewrite")
    proc = run_rehearse(
        "tests/test_origin_main_probe.py", repo=trunkless, tmp_root=tmp_path / "ta"
    )
    text = out(proc)
    assert proc.returncode == 0, f"a skip changed the exit code:\n{text}"
    assert "SKIPPED (1)" in text, f"no skip header in:\n{text}"
    skipped = line_with(text, "test_originMainProbe_noTrunkRefResolves_skipsInsteadOfFailing")
    assert skipped.startswith("SKIPPED "), skipped
    assert "no trunk ref resolves in this clone" in skipped

    withmain = make_repo(tmp_path / "b", trunk="main")
    add_bare_origin(tmp_path / "b", withmain, "main")
    commit_file(withmain, "tests/test_origin_main_probe.py", ORIGIN_MAIN_PROBE, "rewrite")
    green = run_rehearse(
        "tests/test_origin_main_probe.py", repo=withmain, tmp_root=tmp_path / "tb"
    )
    assert green.returncode == 0, f"the origin/main rewrite went red:\n{out(green)}"


# --------------------------------------------------------------------------
# 3. the working tree must not leak into the clone
# --------------------------------------------------------------------------

def test_rehearseProbes_dirtyWorkingTree_cloneCarriesOnlyTheHeadCommit(tmp_path: Path) -> None:
    """Uncommitted edits and untracked files are exactly what CI never sees."""
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_working_tree.py", WORKING_TREE_PROBE, "working tree probe")
    (repo / "README").write_text("DIRTY_CONTENT_MUST_NOT_APPEAR\n", encoding="utf-8")
    (repo / "untracked_must_not_appear.txt").write_text("x\n", encoding="utf-8")
    head = _git(repo, "rev-parse", "HEAD")

    proc = run_rehearse("tests/test_working_tree.py", repo=repo, tmp_root=tmp_path / "t")
    text = out(proc)
    assert proc.returncode == 0, f"the clone carried working-tree state:\n{text}"
    first = proc.stdout.splitlines()[0]
    assert head[:7] in first, f"the first line does not name the rehearsed sha: {first!r}"


# --------------------------------------------------------------------------
# 4-5. the clone's shape
# --------------------------------------------------------------------------

def test_rehearseProbes_freshClone_isFullHistoryDetachedWithoutLocalTrunk(
    tmp_path: Path,
) -> None:
    """Full history (an old sha resolves), `origin/main`, no `refs/heads/main`
    and no `refs/heads/master`, HEAD detached at the caller's HEAD."""
    repo = make_repo(tmp_path, trunk="main")
    old = _git(repo, "rev-parse", "HEAD")
    commit_file(repo, "second.txt", "second\n", "second commit")
    _git(repo, "branch", "master")  # a second local trunk name, also to be dropped
    add_bare_origin(tmp_path, repo, "main")
    commit_file(repo, "tests/test_ci_shape.py", CI_SHAPE_PROBE, "ci shape probe")
    head = _git(repo, "rev-parse", "HEAD")
    assert old != head

    proc = run_rehearse(
        "tests/test_ci_shape.py",
        repo=repo,
        tmp_root=tmp_path / "t",
        env_extra={"ADVERSARY_OLD_SHA": old, "ADVERSARY_HEAD_SHA": head},
    )
    assert proc.returncode == 0, f"the clone is not CI-shaped:\n{out(proc)}"


def test_rehearseProbes_trunkNamedMaster_dropsTheLocalMasterRef(tmp_path: Path) -> None:
    """A repository whose trunk is `master` is the same trap under another name."""
    repo = make_repo(tmp_path, trunk="master")
    add_bare_origin(tmp_path, repo, "master")
    commit_file(repo, "tests/test_master_trunk.py", MASTER_TRUNK_PROBE, "master trunk probe")

    proc = run_rehearse("tests/test_master_trunk.py", repo=repo, tmp_root=tmp_path / "t")
    assert proc.returncode == 0, f"a master trunk survived the rehearsal:\n{out(proc)}"


# --------------------------------------------------------------------------
# 6-9. hostile and absent input
# --------------------------------------------------------------------------

def test_rehearseProbes_missingTestPath_failsLoudlyNamingThePath(tmp_path: Path) -> None:
    """An absent test path is a typo, not a green run with nothing collected."""
    repo = make_repo(tmp_path, trunk="main")
    proc = run_rehearse("tests/test_does_not_exist.py", repo=repo, tmp_root=tmp_path / "t")
    text = out(proc)
    assert proc.returncode != 0, f"an absent test path exited zero:\n{text}"
    assert "tests/test_does_not_exist.py" in text, text


def test_rehearseProbes_repoIsNotAGitRepository_failsLoudlyNamingThePath(
    tmp_path: Path,
) -> None:
    """`--repo` pointed at an ordinary directory."""
    plain = tmp_path / "not_a_repo"
    plain.mkdir()
    proc = run_rehearse("--keep", repo=plain, tmp_root=tmp_path / "t")
    text = out(proc)
    assert proc.returncode != 0, f"a non-repository exited zero:\n{text}"
    assert str(plain) in text or "not_a_repo" in text, text


def test_rehearseProbes_repoIsBare_failsLoudlyNamingThePath(tmp_path: Path) -> None:
    """A bare repository has no working tree to read test paths from."""
    bare = tmp_path / "bare.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, capture_output=True)
    proc = run_rehearse(repo=bare, tmp_root=tmp_path / "t")
    text = out(proc)
    assert proc.returncode != 0, f"a bare repository exited zero:\n{text}"
    assert "bare.git" in text, text


def test_rehearseProbes_testPathEscapesTheRepo_failsLoudlyNamingThePath(
    tmp_path: Path,
) -> None:
    """Traversal: a path that leaves the repository root must be refused,
    not silently resolved inside the clone."""
    repo = make_repo(tmp_path, trunk="main")
    outsider = tmp_path / "outside" / "test_outside.py"
    outsider.parent.mkdir()
    outsider.write_text(GREEN_PROBE, encoding="utf-8")

    relative = run_rehearse(
        "../outside/test_outside.py", repo=repo, tmp_root=tmp_path / "t1"
    )
    assert relative.returncode != 0, f"a traversal path exited zero:\n{out(relative)}"
    assert "../outside/test_outside.py" in out(relative)

    absolute = run_rehearse(str(outsider), repo=repo, tmp_root=tmp_path / "t2")
    assert absolute.returncode != 0, f"an outside absolute path exited zero:\n{out(absolute)}"
    assert str(outsider) in out(absolute)


# --------------------------------------------------------------------------
# 10-11. --keep and cleanup
# --------------------------------------------------------------------------

def _clone_dirs_under(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [p for p in root.iterdir() if p.is_dir() and (p / ".git").exists()]


def test_rehearseProbes_keepFlag_printsAndLeavesTheCloneDirectory(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_green.py", GREEN_PROBE, "green probe")
    root = tmp_path / "t"
    root.mkdir()

    proc = run_rehearse("--keep", "tests/test_green.py", repo=repo, tmp_root=root)
    text = out(proc)
    assert proc.returncode == 0, text
    kept = [
        token for token in text.replace("\n", " ").split()
        if token and Path(token.rstrip(".,:")).is_dir()
        and (Path(token.rstrip(".,:")) / ".git").exists()
    ]
    assert kept, f"--keep printed no surviving clone path:\n{text}"
    assert _clone_dirs_under(root), f"--keep left no clone under {root}"


def test_rehearseProbes_defaultRun_leavesNoCloneBehind(tmp_path: Path) -> None:
    """Without `--keep` the temporary root holds no git repository afterwards."""
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_green.py", GREEN_PROBE, "green probe")
    root = tmp_path / "t"
    root.mkdir()

    proc = run_rehearse("tests/test_green.py", repo=repo, tmp_root=root)
    assert proc.returncode == 0, out(proc)
    assert _clone_dirs_under(root) == [], f"a clone survived under {root}"


# --------------------------------------------------------------------------
# 12-14. CLI surface, the default glob, and the exit code under a mixed report
# --------------------------------------------------------------------------

def test_rehearseProbes_helpFlag_exitsZeroNamingEveryArgument(tmp_path: Path) -> None:
    proc = run_rehearse("--help")
    text = out(proc)
    assert proc.returncode == 0, text
    for token in ("--repo", "--keep", "loom-code/scripts/test_probes_*.py"):
        assert token in text, f"--help never mentions {token!r}:\n{text}"


def test_rehearseProbes_noPositionalPaths_expandsOnlyTheProbeGlob(tmp_path: Path) -> None:
    """The default is `loom-code/scripts/test_probes_*.py` and nothing wider:
    a failing neighbour one character outside the glob must not be collected."""
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "loom-code/scripts/test_probes_green.py", GREEN_PROBE, "matching probe")
    commit_file(repo, "loom-code/scripts/test_probe_red.py", RED_PROBE, "near miss")
    commit_file(repo, "loom-code/scripts/test_other_red.py", RED_PROBE, "unrelated test")

    proc = run_rehearse(repo=repo, tmp_root=tmp_path / "t")
    text = out(proc)
    assert proc.returncode == 0, f"the default glob collected too much:\n{text}"
    assert "test_probe_red.py" not in text, text
    assert "test_other_red.py" not in text, text


def test_rehearseProbes_failureAndSkipTogether_exitsNonZeroAndListsBoth(
    tmp_path: Path,
) -> None:
    """A skip alongside a failure neither hides the failure nor is hidden by it."""
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_mixed.py", FAIL_AND_SKIP_PROBE, "mixed probe")

    proc = run_rehearse("tests/test_mixed.py", repo=repo, tmp_root=tmp_path / "t")
    text = out(proc)
    assert proc.returncode != 0, f"a failure was swallowed:\n{text}"
    assert "FAILED" in text
    assert "SKIPPED (1)" in text, text
    skipped = line_with(text, "test_mixedFile_deliberateSkip_skips")
    assert skipped.startswith("SKIPPED ")
    assert "adversarial skip reason" in skipped


# --------------------------------------------------------------------------
# 15-16. a failing dependency, and a hostile repository path
# --------------------------------------------------------------------------

def test_rehearseProbes_pytestMissingFromInterpreter_reportsInsteadOfSwallowing(
    tmp_path: Path,
) -> None:
    """The dependency the rehearsal runs on disappears: the run must be loud."""
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_green.py", GREEN_PROBE, "green probe")
    shadow = tmp_path / "shadow"
    shadow.mkdir()
    (shadow / "pytest.py").write_text(
        'raise ImportError("adversary: pytest is absent")\n', encoding="utf-8"
    )

    proc = run_rehearse(
        "tests/test_green.py",
        repo=repo,
        tmp_root=tmp_path / "t",
        env_extra={"PYTHONPATH": str(shadow)},
    )
    text = out(proc)
    assert proc.returncode != 0, f"a missing pytest exited zero:\n{text}"
    assert "pytest" in text.lower(), text


def test_rehearseProbes_repoPathHasSpacesAndNonAscii_rehearsesCleanly(
    tmp_path: Path,
) -> None:
    """`file://` URL construction that concatenates strings breaks here."""
    repo = make_repo(tmp_path, trunk="main", name="ré hearse 日本 probes")
    add_bare_origin(tmp_path, repo, "main")
    commit_file(repo, "tests/test_green.py", GREEN_PROBE, "green probe")

    proc = run_rehearse("tests/test_green.py", repo=repo, tmp_root=tmp_path / "t")
    assert proc.returncode == 0, f"a non-ASCII repository path broke the clone:\n{out(proc)}"
