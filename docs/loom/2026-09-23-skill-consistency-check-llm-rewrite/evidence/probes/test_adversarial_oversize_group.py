# concern: plan_groups flags over_limit only when the core exceeds group_max, so one large non-core file yields a group above the validated 25,000-token size with no warning anywhere in the plan or report.
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[5] / "skill-dev-toolkit" / "skills" / "skill-consistency-check" / "scripts"


def test_plan_groups_group_above_group_max_flagged(tmp_path):
    """Every group above group_max must be flagged (over_limit true); a silent oversize group is the defect."""
    target = tmp_path / "t"
    (target / "references").mkdir(parents=True)
    (target / "SKILL.md").write_text("see references/a.md\n", encoding="utf-8")
    (target / "references" / "a.md").write_text("x\n", encoding="utf-8")
    (target / "references" / "big.md").write_text("word " * 24000, encoding="utf-8")
    (target / "references" / "other.md").write_text("word " * 2000, encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "plan_groups.py"), str(target)],
        capture_output=True, text=True, check=True,
    )
    plan = json.loads(proc.stdout)
    tokens = {f["path"]: f["tokens"] for f in plan["files"]}
    sizes = [sum(tokens[p] for p in g) for g in plan["groups"]["read"] + plan["groups"]["simulate"]]

    assert plan["grouped"] is True
    assert not (max(sizes) > plan["group_max"] and plan["over_limit"] is False)
