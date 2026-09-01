"""One pytest invocation must collect every loom-design station directory.

Before the scoped `pytest.ini` existed, the five station directories held
test modules with colliding basenames (e.g. `test_marketplace_entry.py` in
both `discovery/` and `interface/`), so a single rootdir-wide collection
failed with `import file mismatch` errors and CI had to fan out into one
pytest job per directory. This test pins the unified invocation so that
fan-out cannot silently come back.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUITE = "loom-design/scripts/"


def test_unified_collection_reports_no_errors():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", SUITE, "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    output = proc.stdout + proc.stderr
    error_lines = [ln for ln in output.splitlines() if ln.startswith("ERROR ")]
    assert not error_lines, (
        "unified collection reported errors:\n" + "\n".join(error_lines)
    )
    assert "during collection" not in output, (
        f"unified collection was interrupted:\n{output[-4000:]}"
    )
    assert proc.returncode == 0, (
        f"unified collection exited {proc.returncode}:\n{output[-4000:]}"
    )
