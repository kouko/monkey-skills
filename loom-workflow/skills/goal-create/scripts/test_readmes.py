"""Tests for loom-workflow/skills/goal-create tri-language READMEs — Task 7.

Plan acceptance (Task 7):
  - all three README files exist
  - each names both mode names (SESSION, ARC)

This test also holds the content bar the task states in prose ("say what
the skill is for, name SESSION and ARC and what each produces, and point
at SKILL.md for the contract"): each README must additionally name what
SESSION produces (one of the four goal-shape field labels), what ARC
produces (both of its two draft field labels), and must point at SKILL.md
rather than restate its contract.
"""

from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
README_EN = SKILL_DIR / "README.md"
README_JA = SKILL_DIR / "README.ja.md"
README_ZHTW = SKILL_DIR / "README.zh-TW.md"

READMES = {
    "README.md (EN)": README_EN,
    "README.ja.md (JA)": README_JA,
    "README.zh-TW.md (zh-TW)": README_ZHTW,
}

MODE_NAMES = ("SESSION", "ARC")

# What SESSION produces: the four goal-shape field labels are literal
# English tokens used identically across languages — goal-shape.md is
# their SSOT and no README may translate or restate their definitions.
SESSION_FIELD_LABELS = ("Outcome", "Constraints", "Verification", "Stop-when")

# What ARC produces: its two draft field labels, likewise literal English
# tokens shared across languages — the purpose artifact is the format SSOT
# and README text only points at these label names, never their definitions.
ARC_FIELD_LABELS = ("Why", "Done when")

SKILL_MD_POINTER = "SKILL.md"


def test_tri_language_set_exists_and_names_both_modes():
    # 1. All three README files exist.
    for label, path in READMES.items():
        assert path.exists(), f"{label} does not exist at {path}"

    for label, path in READMES.items():
        text = path.read_text(encoding="utf-8")

        # 2. Each names both mode names.
        for mode in MODE_NAMES:
            assert mode in text, f"{label}: missing mode name {mode!r}"

        # 3. Each names what SESSION produces: at least one of the four
        # field labels the four-field goal shape is written in.
        assert any(field in text for field in SESSION_FIELD_LABELS), (
            f"{label}: does not name what SESSION produces "
            f"(expected one of {SESSION_FIELD_LABELS})"
        )

        # 4. Each names what ARC produces: both of its two draft field labels.
        for field in ARC_FIELD_LABELS:
            assert field in text, (
                f"{label}: does not name what ARC produces (missing {field!r})"
            )

        # 5. Each points at SKILL.md for the contract, rather than restating it.
        assert SKILL_MD_POINTER in text, (
            f"{label}: does not point at {SKILL_MD_POINTER} for the contract"
        )
