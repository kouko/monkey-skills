# concern: merge_report's "never write inside the checked skill" guard compares paths by spelling, so a case-variant --out on a case-insensitive filesystem writes the report into the target (Acceptance 5).
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[5] / "skill-dev-toolkit" / "skills" / "skill-consistency-check" / "scripts"


def test_merge_report_case_variant_out_leaves_target_untouched(tmp_path):
    """A --out spelled with different letter case must not create anything inside the target."""
    target = tmp_path / "Target"
    target.mkdir()
    (target / "SKILL.md").write_text("# s\n", encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"grouped": False}), encoding="utf-8")
    findings = tmp_path / "read-1.json"
    findings.write_text(json.dumps({"findings": []}), encoding="utf-8")
    before = sorted(p.name for p in target.iterdir())

    out = tmp_path / "target" / "run"  # same directory as Target on case-insensitive filesystems
    subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "merge_report.py"), "--target", str(target),
         "--plan", str(plan), "--findings", str(findings), "--model", "sonnet", "--out", str(out)],
        capture_output=True, text=True,
    )

    assert sorted(p.name for p in target.iterdir()) == before
