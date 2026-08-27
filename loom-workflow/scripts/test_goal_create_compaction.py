import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/goal-create/SKILL.md"


def _normalize(text: str) -> str:
    # Constraint 3: normalise whitespace before pinning a sentence verbatim
    # so a pure re-wrap (line-break/indent reflow that leaves the words and
    # their order untouched) costs nothing, while a genuine reword — an
    # added/dropped/reordered word — still flips the pin. Collapsing every
    # run of whitespace (including newlines) to a single space achieves
    # exactly that: it is blind to *where* the text wraps, not to *what*
    # it says.
    return re.sub(r"\s+", " ", text).strip()


def test_entrypoint_preserves_modes_floor_and_invocation():
    text = SKILL_PATH.read_text(encoding="utf-8")
    normalized = _normalize(text)

    # --- both mode names ---
    assert "## SESSION mode" in text
    assert "## ARC mode" in text
    assert "**SESSION** and **ARC**" in normalized

    # --- ARC's not-applicable path: names the reason, scaffolds nothing ---
    # Bound to the sentence structure (conditional -> names which is
    # missing -> scaffolds nothing -> scaffolding is someone else's job),
    # not to a character window around it, per constraint 1.
    arc_not_applicable = _normalize(
        """
        ARC is conditional. When the repository has neither a
        `docs/loom/PURPOSE.md`
        nor any `docs/loom/` store directory at all, ARC reports itself not
        applicable, names which of the two is missing, and scaffolds
        nothing —
        creating the store is `loom-init`'s job, not this skill's.
        """
    )
    assert arc_not_applicable in normalized, (
        "ARC's not-applicable path (conditional guard, naming which "
        "artifact is missing, and scaffolding nothing) no longer matches "
        "the pinned sentence verbatim (whitespace-normalised)."
    )

    # --- the floor's invocation ---
    assert "python3 scripts/goal_lint.py <goal-file>" in text

    # --- never-fires-on-its-own statement, from the invocation contract ---
    never_fires = _normalize(
        "This skill never fires on its own — the description above makes "
        "no auto-fire claim."
    )
    assert never_fires in normalized, (
        "The never-fires-on-its-own statement in the Invocation section "
        "no longer matches the pinned sentence verbatim "
        "(whitespace-normalised)."
    )

    # No word-count / size-ceiling assertion here: test_handoff_compaction.py
    # (this plugin's precedent) carries no such assertion either — this
    # repository's skill-body size caps (CLAUDE.md "SKILL.md body 硬上限
    # ~6,000 tokens ... 軟目標 ~5,000 tokens") are enforced by
    # `.claude/hooks/validate-skill-folder-structure.sh` at write/edit time,
    # not by this per-skill compaction test. Duplicating a token-count
    # threshold here would be a second, driftable copy of that cap; this
    # file pins content survival only.
