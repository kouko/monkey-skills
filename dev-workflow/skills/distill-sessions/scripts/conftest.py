"""Keep the skill directory flat by suppressing pytest's incidental subdirs.

Why this exists: `.claude/hooks/validate-skill-folder-structure.sh` (PostToolUse
on Write|Edit) blocks any nested subdir under a skill folder. Pytest defaults
generate `__pycache__/` adjacent to test files. `sys.dont_write_bytecode = True`
catches the bulk of bytecode (event.py / ingest.py / test_ingest.py / etc.) but
conftest.py's *own* bytecode is written before this line runs — the chicken-
and-egg case. `pytest_sessionfinish` mops up the leftover after each run, so
the next Claude Write/Edit sees a clean tree and the hook stays green.

Paired with `pytest.ini` in the same dir, which redirects `.pytest_cache/` to
/tmp for the same reason.
"""

import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001  (pytest signature)
    cache = Path(__file__).parent / "__pycache__"
    if cache.is_dir():
        shutil.rmtree(cache, ignore_errors=True)
