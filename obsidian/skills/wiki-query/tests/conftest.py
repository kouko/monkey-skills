"""Pytest config for wiki-query tests.

Suppress `__pycache__` directory creation. The repo's skill-folder hook
(`.claude/hooks/validate-skill-folder-structure.sh`) forbids nested
subdirectories under any skill subfolder, and pytest would otherwise
leave `tests/__pycache__/` behind which triggers the hook on the next
Write/Edit under this skill.

Two-layer defense:
  1. `sys.dont_write_bytecode = True` prevents bytecode for every module
     imported AFTER this conftest is loaded (the test module and the
     dynamically loaded query_frontmatter module).
  2. An atexit cleanup removes conftest's own bytecode, which Python
     writes BEFORE this file executes (the chicken-and-egg case).

With both, pytest leaves the tests/ directory flat regardless of whether
the caller set `PYTHONDONTWRITEBYTECODE=1`.
"""
from __future__ import annotations

import atexit
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def _cleanup_pycache() -> None:
    pycache = Path(__file__).resolve().parent / "__pycache__"
    if pycache.is_dir():
        shutil.rmtree(pycache, ignore_errors=True)


atexit.register(_cleanup_pycache)
