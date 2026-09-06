"""Executable contract for `rehearse_probes.py` (plan task W1-01).

The adversary's `docs/loom/2026-09-05-graduated-probes-independent-of-
local-history/evidence/probes/test_abuse_rehearse_probes.py` is the
attack catalogue -- absent/hostile input, boundaries, wrong state, a
failing dependency -- and is not duplicated here. This file carries the
plan's own named acceptance test plus three things the adversary's file
does not exercise directly: `main([...])` called in-process rather than
through a subprocess, that the clone's `origin` remote actually points
back at the source repository (not merely that `origin/main` happens to
resolve), and `_parse_junit`'s behaviour on absent/malformed input --
white-box, since the adversary's probes only ever see the script from
the outside.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

import rehearse_probes


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=300
    )


def _git_ok(repo: Path, *args: str) -> str:
    proc = _git(repo, *args)
    assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"
    return proc.stdout.strip()


def make_repo(root: Path, *, trunk: str = "main", name: str = "work") -> Path:
    repo = root / name
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    _git_ok(repo, "symbolic-ref", "HEAD", f"refs/heads/{trunk}")
    _git_ok(repo, "config", "core.autocrlf", "false")
    _git_ok(repo, "config", "user.email", "companion@example.invalid")
    _git_ok(repo, "config", "user.name", "Companion")
    _git_ok(repo, "config", "commit.gpgsign", "false")
    (repo / "README").write_text("committed content\n", encoding="utf-8")
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


_HEADER = '''import subprocess
from pathlib import Path


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
    shown = _git("show", "main:README")
    assert shown.returncode == 0, shown.stderr
    assert "committed content" in shown.stdout
'''

ORIGIN_MAIN_PROBE = _HEADER + '''
import pytest


def test_originMainProbe_noTrunkRefResolves_skipsInsteadOfFailing():
    for ref in ("origin/main", "main"):
        if _resolves(ref):
            shown = _git("show", ref + ":README")
            assert "committed content" in shown.stdout
            return
    pytest.skip("no trunk ref resolves in this clone")
'''

TWO_SKIPS_PROBE = '''import pytest


def test_twoSkips_first_skips():
    pytest.skip("first companion skip reason")


def test_twoSkips_second_skips():
    pytest.skip("second companion skip reason")


def test_twoSkips_third_passes():
    assert True
'''


# --------------------------------------------------------------------------
# the plan's own named acceptance test, via rehearse_probes.main([...])
# --------------------------------------------------------------------------

def test_probe_reading_local_main_is_red_in_rehearsal_and_green_after_origin_main_skip(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    repo = make_repo(tmp_path, trunk="main")
    bare = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, capture_output=True)
    _git_ok(repo, "remote", "add", "origin", str(bare))
    _git_ok(repo, "push", "-q", "origin", "main")
    commit_file(repo, "tests/test_local_main_probe.py", LOCAL_MAIN_PROBE, "local main probe")

    red_code = rehearse_probes.main(
        ["tests/test_local_main_probe.py", "--repo", str(repo)]
    )
    red_out = capsys.readouterr().out
    assert red_code != 0, red_out
    assert "FAILED (1)" in red_out, red_out
    assert "test_local_main_probe.py" in red_out

    commit_file(
        repo, "tests/test_local_main_probe.py", ORIGIN_MAIN_PROBE, "rewrite to origin/main"
    )
    green_code = rehearse_probes.main(
        ["tests/test_local_main_probe.py", "--repo", str(repo)]
    )
    green_out = capsys.readouterr().out
    assert green_code == 0, green_out
    assert "FAILED (0)" in green_out, green_out
    assert "SKIPPED (0)" in green_out, green_out


# --------------------------------------------------------------------------
# companion 1: a repo with no origin at all -- the clone's own origin
# points back at the source repository, not merely "something" that
# happens to satisfy origin/main
# --------------------------------------------------------------------------

def test_repoWithNoOriginRemote_keptClone_growsAnOriginPointingAtTheSourceRepo(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    # `tempfile.gettempdir()` caches its answer for the life of this
    # interpreter -- monkeypatching TMPDIR mid-session (as the adversary's
    # fresh-subprocess-per-probe tests do) would not be honoured here, so
    # this test reads the kept path back out of the printed report instead
    # of assuming where it landed.
    repo = make_repo(tmp_path, trunk="main")
    assert _git(repo, "remote").stdout.strip() == ""  # no origin configured at all
    commit_file(repo, "tests/test_green.py", "def test_ok():\n    assert True\n", "green")

    code = rehearse_probes.main(["--keep", "tests/test_green.py", "--repo", str(repo)])
    out = capsys.readouterr().out
    assert code == 0, out
    kept_line = next(
        line for line in out.splitlines() if line.startswith("kept the rehearsal clone at: ")
    )
    clone = Path(kept_line.removeprefix("kept the rehearsal clone at: "))
    assert clone.is_dir() and (clone / ".git").exists(), kept_line
    try:
        origin_url = _git_ok(clone, "remote", "get-url", "origin")
        assert Path(origin_url.replace("file://", "")).resolve() == repo.resolve(), origin_url
        assert _git(clone, "rev-parse", "--verify", "--quiet", "origin/main").returncode == 0
    finally:
        shutil.rmtree(clone, ignore_errors=True)


# --------------------------------------------------------------------------
# companion 2: the SKIPPED (<n>) header lists one line per skip, in a
# multi-skip run -- the adversary's own file only ever exercises n == 1
# --------------------------------------------------------------------------

def test_multipleSkips_headerCountMatchesListedLines(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_two_skips.py", TWO_SKIPS_PROBE, "two skips")

    code = rehearse_probes.main(["tests/test_two_skips.py", "--repo", str(repo)])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "SKIPPED (2)" in out, out
    # This script's own "SKIPPED <nodeid>: <reason>" lines carry "::" in the
    # nodeid; pytest's native `-rs` summary line ("SKIPPED [1] path:line:
    # reason") also starts with "SKIPPED " but never contains "::" -- the
    # distinguishing feature between the two, this is the whole reason the
    # script does not scrape that native text for the SKIPPED list.
    skip_lines = [
        line for line in out.splitlines() if line.startswith("SKIPPED ") and "::" in line
    ]
    assert len(skip_lines) == 2, out
    assert any("first companion skip reason" in line for line in skip_lines), out
    assert any("second companion skip reason" in line for line in skip_lines), out


# --------------------------------------------------------------------------
# companion 3: `_parse_junit` on absent/malformed XML -- white-box, no
# clone or subprocess needed
# --------------------------------------------------------------------------

def test_parseJunit_missingFile_returnsEmptyLists(tmp_path: Path) -> None:
    failed, skipped = rehearse_probes._parse_junit(tmp_path / "does_not_exist.xml")
    assert failed == []
    assert skipped == []


def test_parseJunit_malformedXml_returnsEmptyListsInsteadOfRaising(tmp_path: Path) -> None:
    bad = tmp_path / "bad.xml"
    bad.write_text("<testsuites><testsuite><not-closed>", encoding="utf-8")
    failed, skipped = rehearse_probes._parse_junit(bad)
    assert failed == []
    assert skipped == []


# --------------------------------------------------------------------------
# wave-end:1-01 -- CI runs this script under Python 3.11
# (`.github/workflows/loom-code-ci.yml`); `tempfile.TemporaryDirectory`'s
# `delete=` keyword is 3.12+ only and would raise `TypeError` on every CI
# run. This drives the script's actual (non `--help`) path through a real
# Python 3.11 interpreter when one is available on this machine, so a
# regression back to the 3.12-only keyword is caught locally too.
# --------------------------------------------------------------------------

def _python311_interpreter() -> str | None:
    """Discover a Python 3.11 interpreter: `python3.11` on PATH, else
    `uv python find 3.11`, else the known local uv-managed install --
    in that order, never only the hard-coded path."""
    found = shutil.which("python3.11")
    if found:
        return found

    uv = shutil.which("uv")
    if uv:
        proc = subprocess.run(
            [uv, "python", "find", "3.11"], capture_output=True, text=True, timeout=30
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()

    fallback = "/Users/kouko/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11"
    if Path(fallback).exists():
        return fallback

    return None


def test_rehearseProbes_underPython311_doesNotRaiseTypeErrorOnTheTempfileDeleteKeyword(
    tmp_path: Path,
) -> None:
    interpreter = _python311_interpreter()
    if interpreter is None:
        pytest.skip(
            "no Python 3.11 interpreter found via python3.11 on PATH, "
            "`uv python find 3.11`, or the known local uv-managed install"
        )
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is required to give the Python 3.11 interpreter a pytest to run with")

    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_green.py", "def test_ok():\n    assert True\n", "green")

    # The script re-invokes pytest with its own `sys.executable` inside the
    # rehearsal clone, so the 3.11 interpreter needs pytest importable too --
    # `uv run --with pytest` supplies that without touching this project's
    # own environment.
    script = Path(rehearse_probes.__file__).resolve()
    proc = subprocess.run(
        [
            uv, "run", "--python", "3.11", "--with", "pytest", "--",
            "python", str(script), "tests/test_green.py", "--repo", str(repo),
        ],
        capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert "TypeError" not in proc.stderr, proc.stderr
    assert "delete" not in proc.stderr, proc.stderr
    assert "FAILED (0)" in proc.stdout, proc.stdout


def test_parseJunit_realReport_reconstructsNodeidsFromClassnameWhenFileAttrAbsent(
    tmp_path: Path,
) -> None:
    """This pytest's own junit output carries no `file` attribute per
    testcase (verified against the installed pytest version) -- the
    nodeid must be rebuilt from `classname`, dots turned back into
    slashes, with `.py` restored."""
    xml_path = tmp_path / "report.xml"
    xml_path.write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<testsuites><testsuite name="pytest" errors="0" failures="1" skipped="1" tests="2">'
        '<testcase classname="tests.test_x" name="test_fails">'
        '<failure message="assert False">boom</failure>'
        "</testcase>"
        '<testcase classname="tests.test_x" name="test_skips">'
        '<skipped message="a reason"/>'
        "</testcase>"
        "</testsuite></testsuites>",
        encoding="utf-8",
    )
    failed, skipped = rehearse_probes._parse_junit(xml_path)
    assert failed == ["tests/test_x.py::test_fails"]
    assert skipped == [("tests/test_x.py::test_skips", "a reason")]


# --------------------------------------------------------------------------
# recursion guard: the clone's pytest carries REHEARSE_PROBES_NESTED=1 so a
# graduated probe that clones and runs the probe files can skip inside a
# rehearsal instead of rehearsing again (found at the memory step: 40
# nested rehearsals before the tree was killed)
# --------------------------------------------------------------------------

NESTED_MARKER_PROBE = """\
import os
from pathlib import Path

def test_marker_is_set_inside_the_rehearsal_clone():
    marker = os.environ.get("REHEARSE_PROBES_NESTED")
    assert marker is not None
    marker_path = Path(marker)
    assert marker_path.is_absolute(), marker
    assert marker_path.resolve() == Path.cwd().resolve()
"""


def test_cloneRun_carriesTheNestedMarker_soCloneAndRunProbesCanSkip(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_marker.py", NESTED_MARKER_PROBE, "marker probe")
    code = rehearse_probes.main(["tests/test_marker.py", "--repo", str(repo)])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "FAILED (0)" in out, out


# --------------------------------------------------------------------------
# squashed shape (plan task W1-02) -- the adversary's
# `docs/loom/2026-09-06-graduated-probes-survive-squash/evidence/probes/
# test_abuse_squashed_rehearsal.py` is the attack catalogue and is not
# duplicated here; these companions drive the same scenario in-process via
# `rehearse_probes.main([...])` and add `_resolve_trunk_sha` white-box
# coverage the adversary's file, which only ever sees the script from the
# outside, does not exercise directly.
# --------------------------------------------------------------------------

def test_resolveTrunkSha_noOriginAndNonTrunkBranch_returnsNone(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, trunk="develop")
    assert rehearse_probes._resolve_trunk_sha(repo) == (None, None)


def test_resolveTrunkSha_originAheadOfLocalMain_returnsOriginSha(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, trunk="main")
    bare = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, capture_output=True)
    _git_ok(repo, "remote", "add", "origin", str(bare))
    _git_ok(repo, "push", "-q", "origin", "main")
    origin_sha = _git_ok(repo, "rev-parse", "origin/main")

    commit_file(repo, "tests/test_ahead.py", "def test_ok():\n    assert True\n", "ahead of origin")

    sha, ref = rehearse_probes._resolve_trunk_sha(repo)
    assert (sha, ref) == (origin_sha, "origin/main")
    assert sha != _git_ok(repo, "rev-parse", "HEAD")


BRANCH_ONLY_COMMIT_PROBE = _HEADER + '''

def test_branchOnlyCommitProbe_findsIntermediateCommitSubject_bySubjectGrep():
    log = _git("log", "--oneline", "--all", "--grep=intermediate branch work", "--format=%H")
    assert log.stdout.strip() != "", (
        "the commit subject 'intermediate branch work' is not reachable -- "
        "this probe depends on a commit that only exists before the branch "
        "is squashed to one commit off its trunk"
    )
'''


def test_squashedShape_probeNeedingBranchOnlyCommit_failsInProcessWhileCiShapedStaysGreen(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
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

    code = rehearse_probes.main(["tests/test_branch_only.py", "--repo", str(repo)])
    out = capsys.readouterr().out
    assert code != 0, out
    assert "test_branch_only.py" in out, out
    assert "SQUASHED SHAPE" in out, out
    # the CI-shaped section (printed first, before "SQUASHED SHAPE") stays
    # green -- only the squashed shape loses the branch-only commit
    ci_shaped_section = out.split("SQUASHED SHAPE", 1)[0]
    assert "FAILED (0)" in ci_shaped_section, out


def test_squashedShape_nothingToSquash_skipsAndStaysGreen(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    repo = make_repo(tmp_path, trunk="main")
    commit_file(repo, "tests/test_green.py", "def test_ok():\n    assert True\n", "green")

    code = rehearse_probes.main(["tests/test_green.py", "--repo", str(repo)])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "FAILED (0)" in out, out
    assert "SQUASHED SHAPE: skipped" in out, out
    assert "nothing to squash" in out, out
