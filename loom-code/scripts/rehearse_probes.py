#!/usr/bin/env python3
"""Run the graduated probes in a CI-shaped clone (plan task W1-01).

A probe that reads local repository state -- a branch called `main`, an
ancestor commit that only exists on this developer's machine -- can pass
in the working tree and still go red the moment CI checks the same
change out with `fetch-depth: 0` onto a detached HEAD with no local
trunk branch (`docs/loom/memory/
pre-branch-end-ci-rehearsal-uses-full-history-without-a-local-main.md`).
This script closes that gap before graduation: it clones the repository
the same way, without hardlinks or alternates so the clone's history is
genuinely its own (`git clone --no-local`), detaches HEAD at the
caller's own HEAD commit, drops any local `main`/`master` ref the clone
picked up, and runs the requested test paths there with `pytest`.

Design choices the plan marks agent-decided:

- The clone always sources from `--repo` itself (never that repository's
  own configured `origin`), so `git clone`'s own remote bookkeeping
  gives the clone an `origin` remote pointing at `--repo` regardless of
  whether `--repo` had one of its own -- this is what makes a
  repository with no `origin` at all rehearse cleanly.
- `--repo`'s filesystem path is turned into the clone source with
  `Path.as_uri()`, not by concatenating `"file://" + str(path)`: string
  concatenation leaves spaces and non-ASCII bytes unescaped, which
  breaks git's URL parser; `as_uri()` percent-encodes per RFC 3986.
- The FAILED and SKIPPED lists in the report are read back from a junit
  XML report (`--junit-xml`), not scraped from pytest's own `-q -rs`
  text: `-rs` prints skip reasons with no nodeid attached, and `-v`
  truncates a reason at the terminal width. The `-q -rs` text is still
  forwarded verbatim as human-readable context, after the FAILED/SKIPPED
  section rather than before it, so a search for a test name lands on
  this script's own line first.
- `pytest-xdist` (`-n auto`) is deliberately never added: measured here,
  it swallows the "file or directory not found" diagnostic for an
  absent explicit test path (the worker-startup collection error never
  reaches the controller's captured output), which would silently
  degrade the missing-path case this script has to report loudly. The
  plan's "add `-n auto` only when xdist imports" framing was in service
  of not requiring the plugin, not mandating its use; measured against
  that goal, leaving it off entirely is the safer reading.
- Exit code is pytest's own return code; a skip never changes it. A
  skip is information for a human to read (the build station's
  graduation paragraph says so), not a gate condition here.
- Cleanup goes through `tempfile.mkdtemp` + an explicit `shutil.rmtree`
  gated on `--keep`, never a shell `rm -rf`. Not `TemporaryDirectory`'s
  `delete=False` keyword: that is Python 3.12+ only, and CI runs this
  script under Python 3.11.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

NESTED_ENV = "REHEARSE_PROBES_NESTED"
from pathlib import Path

from git_exec import run_git  # sibling module (no __init__.py, no conftest)

DEFAULT_GLOB = "loom-code/scripts/test_probes_*.py"
GIT_TIMEOUT = 300
PYTEST_TIMEOUT = 900


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rehearse_probes.py",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, width=200),
        description=(
            "Clone the repository the way CI checks it out -- full history, "
            "origin/main, no local trunk branch, detached HEAD -- and run the "
            "given test paths there, so a probe that reads local repository "
            "state a CI checkout never has goes red before it graduates."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=[],
        help=(
            "test paths to rehearse, relative to --repo "
            f"(default: {DEFAULT_GLOB}, expanded by this script)"
        ),
    )
    parser.add_argument(
        "--repo",
        default=None,
        help=(
            "repository to rehearse (default: `git rev-parse --show-toplevel` "
            "of the current directory)"
        ),
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="leave the CI-shaped clone on disk for inspection instead of deleting it",
    )
    return parser


def _fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def _resolve_repo(raw: str | None) -> Path | None:
    if raw is not None:
        return Path(raw)
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    return Path(proc.stdout.strip())


def _validate_repo(repo: Path):
    """Return (toplevel, "") for a usable non-bare repository, else (None, message)."""
    is_bare = run_git(repo, "rev-parse", "--is-bare-repository", timeout=GIT_TIMEOUT)
    if is_bare is None:
        return None, f"--repo is not a git repository: {repo}"
    if is_bare == "true":
        return (
            None,
            f"--repo is a bare repository (no working tree to read test paths from): {repo}",
        )
    toplevel = run_git(repo, "rev-parse", "--show-toplevel", timeout=GIT_TIMEOUT)
    if toplevel is None:
        return None, f"--repo is not a git repository: {repo}"
    return Path(toplevel), ""


def _relativize_test_path(raw: str, repo_root: Path) -> str | None:
    """Return `raw` as a path relative to `repo_root` (posix form), or None
    when it escapes the repository.

    Every accepted path -- absolute or relative -- is turned into a
    repo-relative string before it reaches pytest's argv: an absolute path
    inside the repo, forwarded verbatim, would still resolve against the
    caller's own working tree (pytest resolves an absolute argument without
    consulting `cwd`), which is exactly the uncommitted-edit leak the
    CI-shaped clone exists to close. A relative string is looked up inside
    whatever `cwd` pytest runs with -- the clone -- so it can never name
    anything outside it.
    """
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    try:
        resolved = candidate.resolve()
        rel = resolved.relative_to(repo_root.resolve())
    except (OSError, ValueError):
        return None
    return rel.as_posix()


def _default_paths(repo_root: Path) -> list[str]:
    return sorted(
        p.relative_to(repo_root).as_posix() for p in repo_root.glob(DEFAULT_GLOB)
    )


def _clone_ci_shaped(repo_root: Path, dest: Path) -> str:
    """Clone `repo_root` into the already-existing empty directory `dest`,
    CI-shaped, and return the rehearsed HEAD sha.

    Raises subprocess.CalledProcessError / OSError / TimeoutExpired on
    any git failure; callers turn that into a script-level error.
    """
    head_sha = run_git(repo_root, "rev-parse", "HEAD", timeout=GIT_TIMEOUT, check=True)
    source_uri = repo_root.resolve().as_uri()
    run_git(
        dest.parent, "clone", "--no-local", "-q", source_uri, str(dest),
        timeout=GIT_TIMEOUT, check=True,
    )
    run_git(dest, "checkout", "-q", "--detach", head_sha, timeout=GIT_TIMEOUT, check=True)
    for trunk in ("main", "master"):
        # a missing ref is expected and not an error -- check=False (the default)
        run_git(dest, "update-ref", "-d", f"refs/heads/{trunk}", timeout=GIT_TIMEOUT)
    return head_sha


def _classname_to_nodeid_prefix(classname: str, repo_root: Path | None) -> str:
    """Rebuild the `<file>::<Class>` prefix a nodeid needs from a junit
    `classname` attribute, when this pytest's junit output carries no `file`
    attribute of its own.

    `classname` is dotted module segments, optionally followed by one dotted
    class-name segment -- both encoded the same way, so the two cannot be
    told apart from the string alone (a class inside a test module becomes
    an extra segment, same as a directory would). When `repo_root` is
    given, each prefix length is tried, longest first, against the actual
    clone on disk: the longest prefix whose `.py` file exists there is the
    module path, and whatever segments remain are class names, emitted as
    `::Class` parts. Absent a usable `repo_root` (or when no prefix
    resolves to a real file -- absent/malformed input, a repo-less test),
    the whole classname is treated as the module path, unchanged from
    before this split existed.
    """
    parts = classname.split(".")
    if repo_root is not None:
        for k in range(len(parts), 0, -1):
            module_path = "/".join(parts[:k]) + ".py"
            if (repo_root / module_path).is_file():
                remainder = "".join(f"::{seg}" for seg in parts[k:])
                return f"{module_path}{remainder}"
    return f"{classname.replace('.', '/')}.py" if classname else ""


def _parse_junit(
    path: Path, repo_root: Path | None = None,
) -> tuple[list[str], list[tuple[str, str]]]:
    """Read FAILED nodeids and (nodeid, reason) SKIPPED pairs from a junit
    XML report. Absent or malformed input yields two empty lists rather
    than raising -- the raw pytest text is still in the report either way.

    `repo_root` -- the clone's own root, still on disk while this is called
    -- lets a `classname` that also carries a test class name be split at
    the real module boundary instead of being spliced whole into a
    fabricated path; see `_classname_to_nodeid_prefix`.
    """
    failed: list[str] = []
    skipped: list[tuple[str, str]] = []
    if not path.is_file():
        return failed, skipped
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return failed, skipped
    for testcase in root.iter("testcase"):
        file_attr = testcase.get("file")
        if not file_attr:
            classname = testcase.get("classname", "")
            file_attr = _classname_to_nodeid_prefix(classname, repo_root)
        name = testcase.get("name", "")
        nodeid = f"{file_attr}::{name}" if file_attr else name
        if testcase.find("failure") is not None or testcase.find("error") is not None:
            failed.append(nodeid)
            continue
        skip = testcase.find("skipped")
        if skip is not None:
            # An expected failure (`@pytest.mark.xfail`) is not a skip -- it
            # is junit-encoded as a `<skipped type="pytest.xfail">` element,
            # and the SKIPPED section is what a reader audits for probes
            # that verified nothing; mixing expected failures into it would
            # inflate that count with tests that did run and did fail on
            # purpose.
            if (skip.get("type") or "").startswith("pytest.xfail"):
                continue
            reason = skip.get("message") or (skip.text or "").strip() or "no reason given"
            skipped.append((nodeid, reason))
    return failed, skipped


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    repo = _resolve_repo(args.repo)
    if repo is None:
        return _fail(
            "could not determine the repository to rehearse "
            "(`git rev-parse --show-toplevel` failed)"
        )

    repo_root, error = _validate_repo(repo)
    if repo_root is None:
        return _fail(error)

    paths: list[str] = []
    for raw in args.paths:
        rel = _relativize_test_path(raw, repo_root)
        if rel is None:
            return _fail(f"test path escapes the repository: {raw}")
        paths.append(rel)
    if not args.paths:
        paths = _default_paths(repo_root)
        if not paths:
            return _fail(
                f"no test paths matched the default glob {DEFAULT_GLOB!r}; "
                "pass explicit paths, or add a matching file, rather than "
                "letting the rehearsal collect the whole repository"
            )

    # `tempfile.mkdtemp` (not `TemporaryDirectory`) because `--keep` must
    # leave the directory behind past this function returning: the
    # `delete=` keyword that would otherwise express that on a
    # `TemporaryDirectory` object is Python 3.12+ only, and CI runs this
    # script under Python 3.11 (`.github/workflows/loom-code-ci.yml`).
    # `mkdtemp` never auto-removes anything, so cleanup is always this
    # function's own explicit `shutil.rmtree` call, gated on `--keep`.
    clone_dir = Path(tempfile.mkdtemp(prefix="rehearse-probes-"))
    try:
        head_sha = _clone_ci_shaped(repo_root, clone_dir)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr or exc.stdout or str(exc)
        print(
            f"could not build the CI-shaped clone of {repo_root}: {detail}",
            file=sys.stderr,
        )
        if not args.keep:
            shutil.rmtree(clone_dir, ignore_errors=True)
        return 2
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"could not build the CI-shaped clone of {repo_root}: {exc}", file=sys.stderr)
        if not args.keep:
            shutil.rmtree(clone_dir, ignore_errors=True)
        return 2

    junit_path = clone_dir / ".rehearsal-junit.xml"
    cmd = [
        sys.executable, "-m", "pytest", *paths,
        "-q", "-rs", "-p", "no:cacheprovider",
        "--junit-xml", str(junit_path),
    ]

    # Mark the clone's pytest as nested: a graduated probe that itself clones
    # the repository and runs the probe files reads this and skips, so a
    # rehearsal never re-enters itself from inside its own clone.
    env = {**os.environ, NESTED_ENV: "1"}
    try:
        proc = subprocess.run(
            cmd, cwd=str(clone_dir), capture_output=True, text=True,
            timeout=PYTEST_TIMEOUT, env=env,
        )
    except subprocess.TimeoutExpired as exc:
        print(f"pytest timed out inside the rehearsal clone: {exc}", file=sys.stderr)
        if not args.keep:
            shutil.rmtree(clone_dir, ignore_errors=True)
        return 2

    failed, skipped = _parse_junit(junit_path, clone_dir)

    report = [f"Rehearsed {head_sha} ({repo_root})", ""]
    report.append(f"FAILED ({len(failed)})")
    report.extend(f"FAILED {nodeid}" for nodeid in failed)
    report.append(f"SKIPPED ({len(skipped)})")
    report.extend(f"SKIPPED {nodeid}: {reason}" for nodeid, reason in skipped)
    report.append("")
    if proc.stdout:
        report.append(proc.stdout.rstrip("\n"))
    if proc.stderr:
        report.append(proc.stderr.rstrip("\n"))
    if args.keep:
        report.append("")
        report.append(f"kept the rehearsal clone at: {clone_dir}")
    print("\n".join(report))

    if not args.keep:
        shutil.rmtree(clone_dir, ignore_errors=True)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
