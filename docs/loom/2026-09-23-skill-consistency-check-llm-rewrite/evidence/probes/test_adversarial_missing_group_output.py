# concern: merge_report never compares the findings files it got against the plan's groups, so a detector group that failed or was skipped silently drops out and the report says "pass" with no sign that part of the package went unchecked.
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[5] / "skill-dev-toolkit" / "skills" / "skill-consistency-check" / "scripts"


def test_merge_report_fewer_outputs_than_groups_not_silent_pass(tmp_path):
    """Four planned detector groups but one output file must not yield a clean exit-0 pass."""
    target = tmp_path / "t"
    target.mkdir()
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({
        "grouped": True, "over_limit": False, "uncovered_pairs": [],
        "groups": {"read": [["SKILL.md", "a.md"], ["SKILL.md", "b.md"]],
                   "simulate": [["SKILL.md", "b.md"], ["SKILL.md", "a.md"]]},
    }), encoding="utf-8")
    findings = tmp_path / "read-1.json"
    findings.write_text(json.dumps({"findings": []}), encoding="utf-8")
    run = tmp_path / "run"

    proc = subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "merge_report.py"), "--target", str(target),
         "--plan", str(plan), "--findings", str(findings), "--model", "sonnet", "--out", str(run)],
        capture_output=True, text=True,
    )

    report = (run / "consistency-report.md").read_text(encoding="utf-8") if proc.returncode != 2 else ""
    silent_pass = proc.returncode == 0 and "unchecked" not in report.lower()
    assert not silent_pass
