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


# Each lens states the four handoff meanings in its own stage-native words —
# the branch deliberately ships no shared vocabulary — so the guard matches a
# semantic family per meaning rather than one pinned phrase. Verified to bite:
# the implementation lens at 7af88b70 matched no `worth` alternative, which is
# the drift a whole-branch review caught by hand.
_HANDOFF_MEANINGS = {
    "added burden": r"added complexity|adds?\b|added|introduc|new (vocabulary|decisions|objects|dependenc)|actual additions",
    "worth": r"worth|value that requires|value now|why each survivor|justif",
    "removed or avoided": r"delet|remov|avoid|collaps|drop\b",
    "downstream risk": r"downstream|risk",
}


def test_every_lens_carries_all_four_handoff_meanings():
    """Spec BI-2 requires all four meanings of every stage lens.

    Copied four-question prose drifting apart is the branch's own named
    downstream risk. One lens had already lost the worth question before review
    caught it, and the cold-package check below cannot see that class of drift.
    """
    import re

    root = Path(__file__).parents[1]
    lenses = [
        "loom-design/skills/business-value/references/business-complexity-lens.md",
        "loom-design/skills/design-system/references/visual-complexity-lens.md",
        "loom-design/skills/interaction-flows/references/interaction-complexity-lens.md",
        "loom-design/skills/spec-expansion/references/behavioral-complexity-lens.md",
        "loom-code/skills/writing-plans/references/architecture-complexity-lens.md",
        "loom-code/skills/requesting-code-review/references/implementation-complexity-lens.md",
    ]
    for relative in lenses:
        text = (root / relative).read_text(encoding="utf-8").lower()
        missing = [
            meaning
            for meaning, pattern in _HANDOFF_MEANINGS.items()
            if not re.search(pattern, text)
        ]
        assert not missing, f"{relative} states no {' / '.join(missing)} meaning"
