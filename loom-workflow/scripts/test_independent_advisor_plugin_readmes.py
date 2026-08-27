"""independent-advisor must be visible in the plugin and root READMEs.

The root README's `loom-workflow` row is asserted against the filesystem
(skill-directory count, manifest version) rather than against a literal,
so the row cannot silently rot again.
"""

import json
import re
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_DIR.parent
SKILL_NAME = "independent-advisor"
PLUGIN_READMES = ["README.md", "README.ja.md", "README.zh-TW.md"]


def _skill_dir_count() -> int:
    return len([p for p in (PLUGIN_DIR / "skills").iterdir() if p.is_dir()])


def _manifest_version() -> str:
    manifest = json.loads(
        (PLUGIN_DIR / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    return manifest["version"]


def _root_workflow_row() -> list[str]:
    for line in (REPO_ROOT / "README.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| [`loom-workflow`]"):
            return [cell.strip() for cell in line.strip().strip("|").split("|")]
    raise AssertionError("root README has no `loom-workflow` table row")


def test_skill_is_listed_in_every_readme():
    for name in PLUGIN_READMES:
        text = (PLUGIN_DIR / name).read_text(encoding="utf-8")
        # skill table row linking the skill directory
        assert re.search(
            rf"^\|\s*\[`{SKILL_NAME}`\]\(skills/{SKILL_NAME}/\)\s*\|", text, re.M
        ), f"{name} skill table is missing a `{SKILL_NAME}` row"
        # directory tree block entry
        assert re.search(rf"^│\s+├──\s+{SKILL_NAME}/\s*$", text, re.M), (
            f"{name} directory tree is missing `{SKILL_NAME}/`"
        )

    row = _root_workflow_row()
    assert SKILL_NAME in row[-1], "root README loom-workflow row does not name the skill"


def test_root_readme_row_agrees_with_filesystem():
    row = _root_workflow_row()
    assert row[1] == _manifest_version(), (
        f"root README version cell {row[1]!r} != manifest {_manifest_version()!r}"
    )
    assert row[2] == str(_skill_dir_count()), (
        f"root README skill count {row[2]!r} != {_skill_dir_count()} skill directories"
    )
