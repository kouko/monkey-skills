"""Shared git-invocation body for loom-code's scripts/ directory.

`run_git` is the single subprocess.run wrapper around `git -C <repo> ...`;
the return/raise shape it hands back is selected entirely by its `check`
and `text` parameters, so the three failure-shape variants that six call
sites (`loom_gate_markers._git`, `review_context._git`, `review_scope._git`,
and others) hand-rolled independently collapse into one body here.

Encoding (argv as UTF-8 `bytes`, `encoding="utf-8", errors="surrogateescape"`
under `text=True`): transcribed from `batch_review_cli._run_subprocess`'s
docstring, which is the SSOT for why -- not restated here.

Sibling-module import (no `__init__.py`, no conftest), following the
existing `import distribute` precedent in this same scripts/ directory.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def run_git(
    repo: Path,
    *args: str,
    timeout: float | None = None,
    check: bool = False,
    text: bool = True,
    strip: bool = True,
):
    """Run `git -C <repo> <*args>` and return its shape per `check`/`text`.

    check=False: stripped stdout, or None on OSError / non-zero exit /
    TimeoutExpired. check=True: raises exactly what
    `subprocess.run(check=True)` raises (CalledProcessError on non-zero
    exit); OSError / TimeoutExpired propagate. text=False: raw bytes, no
    strip regardless of `strip`. strip=False: unstripped stdout.
    """
    argv = ["git", "-C", str(repo), *args]
    argv_bytes = [
        arg.encode("utf-8", "surrogateescape") if isinstance(arg, str) else arg
        for arg in argv
    ]
    text_kwargs = {"encoding": "utf-8", "errors": "surrogateescape"} if text else {}
    try:
        result = subprocess.run(
            argv_bytes, capture_output=True, timeout=timeout, check=check,
            text=text, **text_kwargs,
        )
    except (OSError, subprocess.TimeoutExpired):
        if check:
            raise
        return None

    if not check and result.returncode != 0:
        return None

    stdout = result.stdout
    if text and strip:
        stdout = stdout.strip()
    return stdout
