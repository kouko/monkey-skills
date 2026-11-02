"""Layer 1 preserves tool invocation order within its count tolerance."""

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/skill-refactor/scripts/equivalence_check.py"
SPEC = importlib.util.spec_from_file_location("equivalence_check", SCRIPT)
equivalence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(equivalence)


def compare(tmp_path, baseline, candidate):
    directories = [tmp_path / "baseline", tmp_path / "candidate"]
    for directory, calls in zip(directories, [baseline, candidate]):
        directory.mkdir()
        (directory / "output.md").write_text("## Result\n" + "same output " * 100)
        if calls is not None:
            (directory / "tool_calls.json").write_text(json.dumps({
                "calls": [{"tool": name} for name in calls],
            }))
    return equivalence.run_layer_1(*directories)


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
