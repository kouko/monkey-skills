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

from ..helpers import UsageError, load_manifest, report




REQUIRED_VERSION = re.compile(r"(\d+)\.(\d+)")


def cmd_contract(args: list[str], out=sys.stdout, err=sys.stderr) -> int:
    """`loom_checker.py contract --require <major>.<minor>` -- the check
    loom-design and loom-workflow run at station start (concept-model §1).
    Same major and a high enough minor passes; anything else blocks with the
    one instruction the user can act on."""
    required = None
    rest = list(args)
    while rest:
        token = rest.pop(0)
        if token != "--require":
            raise UsageError(f"unexpected argument {token!r}.")
        if not rest:
            raise UsageError("--require needs a <major>.<minor> version.")
        required = rest.pop(0)
    if required is None:
        raise UsageError("contract needs `--require <major>.<minor>`.")
    wanted = REQUIRED_VERSION.fullmatch(required.strip())
    if not wanted:
        raise UsageError(f"`--require {required}` is not <major>.<minor>.")

    version = str(load_manifest().get("version", "")).strip()
    shipped = REQUIRED_VERSION.match(version)
    if not shipped:
        raise UsageError(f"the contract manifest declares no readable version ({version!r}).")

    same_major = shipped.group(1) == wanted.group(1)
    if same_major and int(shipped.group(2)) >= int(wanted.group(2)):
        out.write(f"contract {version} satisfies requires-contract >={required}\n")
        return 0
    if int(wanted.group(1)) < int(shipped.group(1)):
        # This repo's contract has already moved past the required major --
        # the consuming plugin is what is stale, not loom-code.
        reason = (
            f"this repo ships loom contract {version}, but the consuming plugin "
            f"declares an old contract major (--require {required}); update that "
            "plugin's requires-contract to a supported major."
        )
    else:
        # Either the required major is higher than shipped, or the major
        # matches but the minor floor isn't met -- either way loom-code
        # itself is what needs updating.
        reason = (
            f"this repo ships loom contract {version}, but >={required} is "
            "required — 請更新 loom-code。"
        )
    return report([("contract.requires", reason)], err)


__all__ = [name for name in globals() if not name.startswith("__")]
