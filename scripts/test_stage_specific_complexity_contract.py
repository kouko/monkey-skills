"""Cold-package pointer contract; Task 9 owns behavioral firing evidence."""

import shutil
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_stage_contract_owns_each_lens_and_forbids_private_plugin_paths(tmp_path: Path):
    """Prove cold packaging/local pointers only; composition stays in its suite."""
    expected = {
        "loom-design": {
            "skills/business-value/references/business-complexity-lens.md",
            "skills/design-system/references/visual-complexity-lens.md",
            "skills/interaction-flows/references/interaction-complexity-lens.md",
            "skills/spec-expansion/references/behavioral-complexity-lens.md",
        },
        "loom-code": {
            "skills/writing-plans/references/architecture-complexity-lens.md",
            "skills/requesting-code-review/references/implementation-complexity-lens.md",
        },
    }
    cold_roots = {
        plugin: shutil.copytree(ROOT / plugin, tmp_path / f"isolated-{plugin}")
        for plugin in expected
    }
    for plugin, paths in expected.items():
        for path in paths:
            lens = cold_roots[plugin] / path
            text = lens.read_text(encoding="utf-8")
            assert any(token in text.lower() for token in ("optional", "absent", "reasoned n/a"))
            assert "loom-code/skills" not in text and "loom-design/skills" not in text
            skill = lens.parents[1] / "SKILL.md"
            assert lens.name in skill.read_text(encoding="utf-8")
