"""Layer 1 preserves tool invocation order within its count tolerance."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/skill-refactor/scripts/equivalence_check.py"


def compare(tmp_path, baseline, candidate):
    directories = [tmp_path / "baseline", tmp_path / "candidate"]
    for directory, calls in zip(directories, [baseline, candidate]):
        directory.mkdir()
        (directory / "output.md").write_text("## Result\n" + "same output " * 100)
        if calls is not None:
            (directory / "tool_calls.json").write_text(json.dumps({
                "calls": [{"tool": name} for name in calls],
            }))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--baseline-dir", str(directories[0]),
         "--candidate-dir", str(directories[1])],
        capture_output=True, text=True, timeout=10,
    )
    report = json.loads(result.stdout)
    assert result.returncode == (0 if report["pass"] else 1), result.stderr
    return report


@pytest.mark.parametrize("baseline,candidate", [
    (["Read", "Write", "Read"], ["Read", "Write", "Read"]),
    (["Read", "Write"], ["Read", "Read", "Write"]),
    (["Read", "Write"], ["Read", "Write", "Write"]),
    (["Read", "Write", "Read"], ["Read", "Read", "Write", "Read"]),
    (["Read", "Read", "Write"], ["Read", "Write"]),
    ([], []),
    (None, None),
])
def test_ordered_trace_tolerance(tmp_path, baseline, candidate):
    report = compare(tmp_path, baseline, candidate)
    assert report["checks"]["tool_calls"] is True
    assert report["verdict"] == "PASS_LAYER_1"


@pytest.mark.parametrize("baseline,candidate", [
    (["Read", "Write"], ["Write", "Read"]),
    (["Read", "Read", "Write"], ["Read", "Write", "Write"]),
    (["Read", "Write", "Read"], ["Read", "Read", "Write"]),
    (["Read", "Write"], ["Read", "Write", "Write", "Write"]),
    (["Read", "Write"], ["Read", "Search", "Write"]),
    (["Read", "Write"], ["Write", "Read", "Read"]),
    (["Read"], []),
])
def test_reordered_trace_rejected(tmp_path, baseline, candidate):
    report = compare(tmp_path, baseline, candidate)
    assert all(value for name, value in report["checks"].items() if name != "tool_calls")
    assert report["checks"]["tool_calls"] is False
    assert report["pass"] is False
    assert report["verdict"] == "FAIL_LAYER_1"
