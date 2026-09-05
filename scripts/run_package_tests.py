#!/usr/bin/env python3
"""Run one pytest session per `--`-separated group of arguments.

loom-design/scripts/ carries its own pytest.ini (importlib import mode); a
single session that also names loom-code paths adopts that ini and fails to
collect ~30 loom-code modules. Two sessions, one exit code.
"""
from __future__ import annotations

import subprocess
import sys


def split_groups(argv: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[]]
    for token in argv:
        if token == "--":
            groups.append([])
        else:
            groups[-1].append(token)
    return [g for g in groups if g]


def main(argv: list[str]) -> int:
    for group in split_groups(argv):
        code = subprocess.call([sys.executable, "-m", "pytest", *group])
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
