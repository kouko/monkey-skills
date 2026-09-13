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

from .helpers import GIT_TIMEOUT, git_maybe, glob_to_regex, load_manifest




_CONTENT_TREE_CACHE: dict[tuple[str, str, tuple[str, ...]], str | None] = {}


def functional_content_digest(
    repo: Path, sha: str, change_id: str, manifest: dict | None = None
) -> str | None:
    """Return a Git-derived identity with only declared publication metadata
    for this change excluded. The declaration is repo-neutral; replacing
    ``<change-id>`` scopes every pattern so another change's evidence remains
    ordinary functional content."""
    contract = manifest if manifest is not None else load_manifest()
    patterns = tuple(
        str(pattern).replace("<change-id>", change_id)
        for pattern in contract.get("publication_only_paths", [])
    )
    key = (sha, change_id, patterns)
    if key in _CONTENT_TREE_CACHE:
        return _CONTENT_TREE_CACHE[key]
    listing = git_maybe(repo, "ls-tree", "-r", sha)
    if listing is None:
        _CONTENT_TREE_CACHE[key] = None
        return None

    matchers = [glob_to_regex(pattern) for pattern in patterns]
    kept: list[str] = []
    for line in listing.splitlines():
        if not line or "\t" not in line:
            continue
        path = line.split("\t", 1)[1]
        if not any(matcher.fullmatch(path) for matcher in matchers):
            kept.append(line)
    digest = _hash_object_stdin(repo, "\n".join(kept))
    _CONTENT_TREE_CACHE[key] = digest
    return digest


def _hash_object_stdin(repo: Path, content: str) -> str | None:
    """`git hash-object --stdin -t blob` over `content` -- `run_git` (the
    shared git-invocation body) has no stdin plumbing, and adding it there
    is a change to a file outside this one; this one call stays local and
    uses the same encoding discipline (`git_exec.run_git`'s own
    docstring): UTF-8 text with `surrogateescape` on both sides."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "hash-object", "--stdin", "-t", "blob"],
            input=content, capture_output=True, timeout=GIT_TIMEOUT,
            text=True, encoding="utf-8", errors="surrogateescape",
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


__all__ = [name for name in globals() if not name.startswith("__")]
