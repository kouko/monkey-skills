"""T10: brainstorming's brief-before-fork copy is replaced by a one-line
pointer to the family SSOT (`loom-pipeline/hooks/family-reception.md`
§Brief before a complex fork). The duplicated threshold text is removed;
the pointer + brainstorming-specific anchor remain.

WHY this test exists: `loom-code/skills/brainstorming/SKILL.md` line 58
previously carried a full copy of the brief-before-fork rule — including
the trigger threshold ("≥3 trade-offs, ≥2 implementation paths, or
architectural blast radius") and the stakes-first framing — which now
lives canonically in `loom-pipeline/hooks/family-reception.md`
§Brief before a complex fork (Task 5). Six router/skill copies of this
rule drift when edited in one place and not the others; this test pins
the brainstorming copy as a pointer, not a duplicate.

Block scoping: the check is scoped to the region between the anchor
line ending "coherent set." (close of the preceding paragraph) and
"### Axis 0 — Upstream artifacts" (open of the next section). This is
the ~line 58 region ONLY — it deliberately excludes the ~line 150/152
Axis-4 research-protocol prose, which Task 14 edits separately. A
whole-file grep would false-green if a removed threshold phrase
re-appeared in the Axis-4 region (a different concern) and masked a
real removal from the brief-before-fork region itself.

check(root) takes an arbitrary root so RED verification can run against
an extracted, perturbed temp copy without touching the real tree (house
pattern; repo memory: mutation/RED limited to extracted copies — see
scripts/test_router_card_rule_tokens.py).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

SKILL_REL = "loom-code/skills/brainstorming/SKILL.md"
SSOT_REL = "loom-pipeline/hooks/family-reception.md"

# Region anchors — the brief-before-fork paragraph lives between these
# two lines (confirmed verbatim substrings in the file). Scoping the
# search here is what makes the test false-green-resistant: a threshold
# match in the Axis-4 region (~line 150) does NOT count.
REGION_START = "together the three read as one coherent set."
REGION_END = "### Axis 0 — Upstream artifacts"

# Pointer tokens that MUST appear in the region after the edit.
POINTER_TOKENS = (
    "loom-pipeline/hooks/family-reception.md",
    "Brief before a complex fork",
    "§",
)

# Distinctive phrases from the OLD full copy that MUST be gone from the
# region — these are the duplicated threshold text + framing that now
# lives in the SSOT, not here.
REMOVED_PHRASES = (
    "≥3 trade-offs, ≥2 implementation paths, or architectural blast radius",
    "canonical source for this framing",
    "in-workflow shorthand",
)


def extract_region(text: str, rel_path: str) -> str:
    """Return the substring between the two anchor lines (the
    brief-before-fork region, ~line 58). Raises if an anchor is missing
    — which would itself be a regression (the surrounding structure
    changed and the test must be re-anchored, not silently pass)."""
    start = text.find(REGION_START)
    if start == -1:
        raise ValueError(f"{REGION_START!r} not found in {rel_path}")
    end = text.find(REGION_END, start)
    if end == -1:
        raise ValueError(f"{REGION_END!r} not found in {rel_path}")
    return text[start:end]


def check(root: Path) -> None:
    """Assert the brainstorming brief-before-fork region points at the
    family SSOT AND the old full-copy threshold/framing phrases are gone.

    Raises AssertionError naming each missing pointer token and each
    remnant old phrase — the failure message is the sweep list a real
    edit needs to act on, not a bare "mismatch"."""
    skill_path = root / SKILL_REL
    text = skill_path.read_text(encoding="utf-8")
    region = extract_region(text, SKILL_REL)

    problems: list[str] = []

    for token in POINTER_TOKENS:
        if token not in region:
            problems.append(f"pointer token missing from region: {token!r}")

    for phrase in REMOVED_PHRASES:
        if phrase in region:
            problems.append(f"old copy phrase still in region: {phrase!r}")

    # The SSOT section must actually exist where we point — otherwise the
    # pointer is a dangling reference and the dedup is illusory.
    ssot_path = root / SSOT_REL
    ssot_text = ssot_path.read_text(encoding="utf-8")
    if "## Brief before a complex fork" not in ssot_text:
        problems.append(
            f"SSOT section '## Brief before a complex fork' missing from {SSOT_REL}"
        )

    if problems:
        raise AssertionError(
            "brainstorming brief-before-fork pointer mismatch:\n"
            + "\n".join(problems)
        )


def test_brainstorming_points_at_source():
    check(REPO_ROOT)


def test_check_catches_a_reinserted_copy(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    The real tree currently satisfies check() exactly, so the test above
    alone would stay green even if check() were broken (e.g. always a
    no-op). This test extracts the REAL skill file into an isolated
    tmp_path copy (zero mutation residue in the real tree — house
    RED-on-extracted-copy pattern), re-inserts the old threshold phrase
    into the brief-before-fork region, and shows check() actually
    raises, naming that phrase.
    """
    src = REPO_ROOT / SKILL_REL
    dst = tmp_path / SKILL_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    # SSOT must also be present in the copy root for check() to find it.
    ssot_src = REPO_ROOT / SSOT_REL
    ssot_dst = tmp_path / SSOT_REL
    ssot_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ssot_src, ssot_dst)

    check(tmp_path)  # baseline: unmutated copy passes

    text = dst.read_text(encoding="utf-8")
    region_start = text.find(REGION_START)
    assert region_start != -1
    # Re-insert the old threshold phrase right after the region start
    # anchor — simulating a regression where the old copy crept back in.
    insert_at = region_start + len(REGION_START)
    mutated = (
        text[:insert_at]
        + "\n\n**Above all — lead with the stakes.** When the fork is "
        "genuinely complex (≥3 trade-offs, ≥2 implementation paths, or "
        "architectural blast radius), **brief before you ask**: that skill "
        "is the canonical source for this framing; the rules here are its "
        "in-workflow shorthand.\n"
        + text[insert_at:]
    )
    dst.write_text(mutated, encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert "≥3 trade-offs, ≥2 implementation paths, or architectural blast radius" in message
    assert "canonical source for this framing" in message
    assert "in-workflow shorthand" in message