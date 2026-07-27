"""Structural grep-test guarding Task 6 of
docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md: the three
shipped writing-plans READMEs (README.md / README.ja.md /
README.zh-TW.md) enumerate the per-task field list from
`references/plan-format.md`. Task 2 added a `Reuse-adequacy` field to
that schema; this test guards that all three READMEs' per-task field
lists were updated to mention it.

Section scoping (not whole-file grep): each README's field list sits
between its `- **Description**:` bullet (present verbatim, in English,
in all three language variants -- field *names* are not translated,
only the surrounding prose) and the next `## `-level heading. Anchoring
on `- **Description**:` rather than the section's own heading avoids
depending on the heading text, which IS translated per language
(`## What each task carries` / `## 各タスクが持つもの` /
`## 每個任務帶什麼`). Verified no fenced code block sits between the
field-list bullets and the next heading in any of the three files
(README.md / README.ja.md / README.zh-TW.md lines 30-49), so a naive
"next '## ' heading" boundary is safe here -- unlike a sibling test's
fenced-example gotcha elsewhere in this plan's task set.

Limitation this grep cannot catch: it only proves the field *name*
"Reuse-adequacy" appears somewhere inside the scoped field-list section
of each file. It does not verify the surrounding prose actually
describes the field's semantics (behaviour-match claim / why-acceptable
clause) -- plan-format.md §`Reuse-adequacy` is the source of truth for
semantics; the README is a terse index, matching how the other five
pre-existing field bullets are also one-line summaries, not full specs.

Stdlib only (pathlib). Resolve READMEs relative to this test file.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WRITING_PLANS = REPO_ROOT / "skills" / "writing-plans"

READMES = {
    "README.md": WRITING_PLANS / "README.md",
    "README.ja.md": WRITING_PLANS / "README.ja.md",
    "README.zh-TW.md": WRITING_PLANS / "README.zh-TW.md",
}

START_ANCHOR = "- **Description**:"
END_ANCHOR = "\n## "


def _field_list_section(path: Path) -> str:
    assert path.is_file(), f"README is absent at {path}"
    text = path.read_text(encoding="utf-8")
    start = text.index(START_ANCHOR)
    end = text.index(END_ANCHOR, start)
    return text[start:end]


def test_readmes_list_reuse_adequacy_field():
    """Each of the three READMEs' per-task field list must mention the
    Reuse-adequacy field Task 2 added to plan-format.md's schema --
    scoped to the field-list section itself (between the `Description`
    bullet and the next heading), not a whole-file grep, so a mention
    elsewhere in the file (e.g. a changelog line) cannot satisfy this."""
    for name, path in READMES.items():
        section = _field_list_section(path)
        assert "Reuse-adequacy" in section, (
            f"{name}: per-task field list does not mention "
            "Reuse-adequacy (scoped to the section between the "
            "Description bullet and the next '## ' heading)"
        )
