# concern: a malformed detector finding crashes merge_report with a traceback whose exit code 1 is the documented "needs revision" verdict, so an input error is reported as a result instead of exit 2.
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[5] / "skill-dev-toolkit" / "skills" / "skill-consistency-check" / "scripts"

GOOD = {"file": "SKILL.md", "lines": [1], "quote": "q"}
MALFORMED = [
    pytest.param({"id": "F1", "confidence": "high", "side_a": "SKILL.md:3", "side_b": GOOD}, id="side-is-string"),
    pytest.param({"id": "F1", "confidence": "high", "side_a": {"file": "SKILL.md", "lines": 3}, "side_b": GOOD}, id="lines-is-int"),
    pytest.param({"id": "F1", "confidence": "high", "side_a": {"lines": [1]}, "side_b": GOOD}, id="file-missing"),
]


@pytest.mark.parametrize("bad", MALFORMED)
def test_merge_report_malformed_side_exits_2(tmp_path, bad):
    """Any malformed side must end in exit 2 with an error line, never a traceback exit 1."""
    target = tmp_path / "t"
    target.mkdir()
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"grouped": False}), encoding="utf-8")
    # A second, well-formed finding forces the duplicate comparison to touch the bad side.
    ok = {"id": "F2", "confidence": "low", "side_a": GOOD, "side_b": GOOD}
    findings = tmp_path / "read-1.json"
    findings.write_text(json.dumps({"findings": [ok, bad]}), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "merge_report.py"), "--target", str(target),
         "--plan", str(plan), "--findings", str(findings), "--model", "sonnet",
         "--out", str(tmp_path / "run")],
        capture_output=True, text=True,
    )

    assert "Traceback" not in proc.stderr
    assert proc.returncode == 2
