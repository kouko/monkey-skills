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

from .helpers import glob_to_regex




def _artifact_type_for(manifest, path: str) -> str | None:
    """Same first-match-wins order as `artifact_types`, but for one path."""
    for entry in manifest["artifact_types"]:
        if glob_to_regex(entry["glob"]).match(path):
            return entry["type"]
    return None


_TEST_NAME_RE = re.compile(r"(?:test_[^/]*|[^/]*_test)\.py\Z")


_REQUIREMENTS_NAME_RE = re.compile(r"requirements[^/]*\.txt\Z")


_CI_CONFIG_EXT_RE = re.compile(r"\.(?:toml|ya?ml|json)\Z")


_NO_CANONICAL_TREE = (
    "no canonical (this checker is the .codex/hooks/ copy, or no contract "
    "package sits beside it)"
)


__all__ = [name for name in globals() if not name.startswith("__")]
