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

from .intake import check_plan_field_caps
from ..helpers import UsageError, read_text, report




def cmd_plan(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """`loom_checker.py plan <path>` -- runs `plan.field-caps` (and any other
    `plan.*` rule) against one plan file directly, independent of a
    change-id -- the shape the `plan` subcommand's own tests and the
    write-plan / push callers both rely on. This is a raw-content check on
    whatever file `<path>` names, by design: `plan-edits` and `push`
    instead resolve and read the canonical `docs/loom/<change-id>/plan.md`
    for that change-id."""
    if not args:
        raise UsageError("plan needs a path.")
    if len(args) > 1:
        raise UsageError(f"unexpected argument {args[1]!r}.")
    path = Path(args[0])
    if not path.is_file():
        err.write(f"no such plan file: {path}\n")
        return 2
    try:
        text = read_text(path)
    except OSError as exc:
        err.write(f"cannot read plan file {path}: {exc}\n")
        return 2
    return report(check_plan_field_caps(text), err)


__all__ = [name for name in globals() if not name.startswith("__")]
