"""Shared git-invocation body for loom-code's scripts/ directory.

`run_git` is the one git-invocation body in this directory: the
return/raise shape it hands back is selected entirely by its `check` and
`text` parameters, so the three failure shapes its callers used to
hand-roll independently live here instead. It was extracted from six
wrappers around `git -C <repo> ...`, five of which were deleted with the
pre-1.0 script families at loom-code 1.0; `loom_checker.py` is the caller
that remains. This docstring is the SSOT for the encoding/argv rationale
below -- a module that wraps `run_git` points back here rather than
restating it. Direct `subprocess.run(["git", ...])` calls that were never
one of those wrappers still exist (`check_doc_citations.py`); they keep
their own encoding behavior, and routing them here is a separate change,
not something this module claims to have done.

Encoding: `encoding="utf-8", errors="surrogateescape"` is passed explicitly
rather than the locale-dependent default `text=True` picks up
(locale.getencoding(), fixed at THIS interpreter's startup from
LC_ALL/LANG -- not the child's). git's own path output is raw bytes that
are valid UTF-8 whenever core.quotePath is left at its default
(quoted/escaped otherwise; git-config(1)) -- decoding as UTF-8
unconditionally, with surrogateescape to still tolerate a stray non-UTF-8
byte, keeps a non-ASCII path from raising UnicodeDecodeError under a
non-UTF-8 process locale. `encoding=`/`errors=` are applied ONLY when
text=True: passing them at all -- even under text=False -- forces
subprocess.run into text mode regardless, which would hand a `text=False`
caller (e.g. a raw-bytes `git show` read) a `str` where it requires raw
`bytes`.

argv is handed to the child as UTF-8 `bytes`, not `str`: on POSIX,
subprocess encodes `str` arguments with the filesystem encoding
(os.fsencode -- PEP 383), which is ASCII under an uncoerced C/POSIX
locale, so a repo-relative path such as `src/日本.py` inside a git argument
would otherwise raise UnicodeEncodeError before git ever ran (observed on
a Linux CI runner; macOS's filesystem encoding is always UTF-8, which is
why it did not reproduce locally). git itself treats paths as bytes, so
UTF-8 bytes are exactly what it expects regardless of the process locale
(git-config(1) core.quotePath describes the same byte-level model on
output).

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
