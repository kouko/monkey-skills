#!/usr/bin/env python3
"""Run one pytest session per `--then`-separated group of arguments.

loom-design/scripts/ carries its own pytest.ini (importlib import mode); a
single session that also names loom-code paths adopts that ini, and the
loom-code modules that rely on bare sibling imports (three files, ~90
tests) fail to collect. Two sessions, one exit code.
"""
from __future__ import annotations

import subprocess
import sys


def split_groups(argv: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[]]
    for token in argv:
        if token == "--then":
            groups.append([])
        else:
            groups[-1].append(token)
    return [g for g in groups if g]


def main(argv: list[str]) -> int:
    groups = split_groups(argv)
    if not groups:
        print("run_package_tests: no path group given", file=sys.stderr)
        return 2
    for group in groups:
        code = subprocess.call([sys.executable, "-m", "pytest", *group])
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
