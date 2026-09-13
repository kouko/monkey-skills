from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml

from git_exec import run_git

from .helpers import kickoff_defaults




_EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


_REGULAR_FILE_MODE = "100644"


TEST_COMMAND_MARKERS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("pyproject.toml", "pytest.ini", "tox.ini", "setup.cfg"), "python3 -m pytest -q"),
    (("package.json",), "npm test"),
    (("Cargo.toml",), "cargo test"),
    (("go.mod",), "go test ./..."),
)


NO_PACKAGE_TESTS = "none"


def command_names_artifact(command: str, artifact: str) -> bool:
    """True when one argument of `command` IS `artifact`.

    A substring test cannot tell `python3 attack0.py` from
    `python3 noop.py  # attack0.py`: both contain the path, only one runs
    it. The command is read the way a shell reads it -- a trailing `#`
    comment dropped, then split into arguments -- and the artifact has to
    be one of those arguments. `./x/y.py` and `x/y.py` name the same file
    and both count.
    """
    try:
        tokens = shlex.split(command, comments=True)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    wanted = os.path.normpath(artifact)
    return any(os.path.normpath(token) == wanted for token in tokens)


SHELL_METACHARACTERS = re.compile(r"[;&|<>()$`*?\[\]{}\n]")


PROBE_RUN_TIMEOUT = int(os.environ.get("LOOM_PROBE_RUN_TIMEOUT", "600"))


def argv_for(command: str) -> list[str]:
    """`command` as an argv list, or ValueError if a shell would be needed."""
    if SHELL_METACHARACTERS.search(command):
        raise ValueError(
            "it contains shell metacharacters; declare a plain argv command "
            "(a program and its arguments) instead"
        )
    tokens = shlex.split(command, comments=True)
    if not tokens:
        raise ValueError("it is empty")
    return tokens


def command_executes_artifact(command: str, artifact: str) -> bool:
    """True when argv directly executes the named Python, shell, or executable file."""
    tokens = argv_for(command)
    wanted = os.path.normpath(artifact)
    suffix = Path(artifact).suffix.lower()
    if suffix == ".py":
        python = Path(tokens[0]).name.startswith("python")
        direct = len(tokens) >= 2 and os.path.normpath(tokens[1]) == wanted
        pytest_direct = (
            len(tokens) >= 4 and tokens[1:3] == ["-m", "pytest"]
            and os.path.normpath(tokens[3]) == wanted
        )
        return python and (direct or pytest_direct)
    if suffix == ".sh":
        return len(tokens) >= 2 and Path(tokens[0]).name in {"bash", "sh"} and os.path.normpath(tokens[1]) == wanted
    return os.path.normpath(tokens[0]) in {wanted, os.path.join(".", wanted)}


def declared_test_command(repo: Path) -> tuple[str | None, str]:
    """The repo's own package-test command, and where it was read from.

    A recorded probe is compared against THIS, so that a command which
    exits 0 without running the suite cannot stand in for the suite. The
    repo's own KICKOFF-DEFAULTS line wins, because only the repo knows;
    otherwise the same markers the build station reads are read here."""
    declared = kickoff_defaults(repo).get("package-tests", "").strip()
    if declared:
        return declared, "docs/loom/KICKOFF-DEFAULTS.md"
    for markers, command in TEST_COMMAND_MARKERS:
        if any((repo / marker).is_file() for marker in markers):
            return command, f"detected {markers[0]}"
    for pattern in ("test_*.py", "*_test.py"):
        if next(repo.rglob(pattern), None) is not None:
            return "python3 -m pytest -q", f"detected {pattern} files"
    return None, ""


__all__ = [name for name in globals() if not name.startswith("__")]
