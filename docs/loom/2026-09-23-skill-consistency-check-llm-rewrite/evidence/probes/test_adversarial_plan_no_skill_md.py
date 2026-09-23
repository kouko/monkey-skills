# concern: plan_groups accepts a folder with no SKILL.md (empty, or a wrong path) and plans an empty group, so the check ends in "pass" on something that is not a skill.
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[5] / "skill-dev-toolkit" / "skills" / "skill-consistency-check" / "scripts"


@pytest.mark.parametrize("contents", [{}, {"notes.md": "just notes\n"}], ids=["empty", "no-skill-md"])
def test_plan_groups_folder_without_skill_md_exits_2(tmp_path, contents):
    """A target without SKILL.md at its root is a bad path: exit 2, as SKILL.md step 2 promises."""
    target = tmp_path / "t"
    target.mkdir()
    for name, text in contents.items():
        (target / name).write_text(text, encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "plan_groups.py"), str(target)],
        capture_output=True, text=True,
    )

    assert proc.returncode == 2
