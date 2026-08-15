"""T14: the Axis-4 research-results template must lead with the
recommendation ("My take: Recommend / Why / Conditional reversal"), THEN
surface the alternatives with source + pros/cons — conclusion-first, per
plain-relay rule 1. Today the template buries "My take" after the 3
alternatives; this test pins the reordered invariant.

WHY this test exists: `loom-code/skills/brainstorming/references/
axis4-research-protocol.md` §Output format is the template an agent
follows when surfacing research results. The brief (plain-relay Axis 5 /
spec §4.3) says the recommendation must come FIRST so the user learns
"which one" before reading three alternatives' worth of evidence —
aligning with CLAUDE.md plain-language-first and plain-relay rule 1
(conclusion-first). The old end-position instruction in
`brainstorming/SKILL.md:~150/152` ("end in an explicit recommendation")
becomes obsolete and is reworded in the same change.

Block scoping: the template check is scoped to the fenced code block
under "## Output format — surfacing alternatives to the user" in
axis4-research-protocol.md (between the opening ``` and closing ```).
A whole-file grep would false-green if "My take" appeared elsewhere.
The SKILL.md check is scoped to the Axis-4 region between
"### Axis 4 — Alternatives Considered" and "### Axis 5 — What Becomes
Obsolete" — this deliberately excludes the line-58 brief-before-fork
region (Task 10's territory, already committed).

check(root) takes an arbitrary root so RED verification can run against
an extracted, perturbed temp copy without touching the real tree (house
pattern; repo memory: mutation/RED limited to extracted copies — see
scripts/test_router_card_rule_tokens.py /
scripts/test_brief_before_fork_pointer_brainstorming.py).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

PROTOCOL_REL = "loom-code/skills/brainstorming/references/axis4-research-protocol.md"
SKILL_REL = "loom-code/skills/brainstorming/SKILL.md"

# Template region anchors (axis4-research-protocol.md). The output
# template lives in a fenced code block under this heading.
TEMPLATE_HEADING = "## Output format — surfacing alternatives to the user"

# Recommendation marker — the "My take" block is the recommendation.
RECOMMENDATION_MARKER = "My take (given your context):"
# First-alternative marker — the numbered alternatives/evidence block.
FIRST_ALTERNATIVE_MARKER = "1. <Approach name>"

# SKILL.md Axis-4 region anchors.
SKILL_REGION_START = "### Axis 4 — Alternatives Considered"
SKILL_REGION_END = "### Axis 5 — What Becomes Obsolete"

# Old end-position phrase that MUST be gone from the Axis-4 region.
REMOVED_PHRASE = "end in an explicit recommendation"
# Recommendation-first wording that MUST now appear in the region.
LEAD_PHRASES = ("lead with", "recommendation first")


def extract_template_block(text: str, rel_path: str) -> tuple[int, int]:
    """Return (start, end) offsets of the fenced code block under the
    "## Output format" heading. Raises if the heading or the fences are
    missing — a missing anchor is itself a regression the test must
    surface, not silently pass on."""
    heading = text.find(TEMPLATE_HEADING)
    if heading == -1:
        raise ValueError(f"{TEMPLATE_HEADING!r} not found in {rel_path}")
    fence_start = text.find("```", heading)
    if fence_start == -1:
        raise ValueError(f"opening fence not found after heading in {rel_path}")
    fence_end = text.find("```", fence_start + 3)
    if fence_end == -1:
        raise ValueError(f"closing fence not found in {rel_path}")
    return fence_start, fence_end


def extract_skill_region(text: str, rel_path: str) -> str:
    """Return the substring of SKILL.md between the Axis-4 and Axis-5
    headings (the ~line 150/152 region). Raises if an anchor is missing."""
    start = text.find(SKILL_REGION_START)
    if start == -1:
        raise ValueError(f"{SKILL_REGION_START!r} not found in {rel_path}")
    end = text.find(SKILL_REGION_END, start)
    if end == -1:
        raise ValueError(f"{SKILL_REGION_END!r} not found in {rel_path}")
    return text[start:end]


def check(root: Path) -> None:
    """Assert the recommendation leads the template (conclusion-first)
    AND the SKILL.md Axis-4 prose no longer says "end in an explicit
    recommendation" and now carries recommendation-first wording.

    Raises AssertionError naming each problem — the failure message is
    the fix list a real edit needs to act on, not a bare "mismatch"."""
    problems: list[str] = []

    # --- Template ordering check (axis4-research-protocol.md) ---
    protocol_path = root / PROTOCOL_REL
    protocol_text = protocol_path.read_text(encoding="utf-8")
    blk_start, blk_end = extract_template_block(protocol_text, PROTOCOL_REL)
    block = protocol_text[blk_start:blk_end]

    rec_idx = block.find(RECOMMENDATION_MARKER)
    alt_idx = block.find(FIRST_ALTERNATIVE_MARKER)
    if rec_idx == -1:
        problems.append(
            f"recommendation marker {RECOMMENDATION_MARKER!r} missing from "
            f"output template in {PROTOCOL_REL}"
        )
    if alt_idx == -1:
        problems.append(
            f"first-alternative marker {FIRST_ALTERNATIVE_MARKER!r} missing "
            f"from output template in {PROTOCOL_REL}"
        )
    if rec_idx != -1 and alt_idx != -1 and not (rec_idx < alt_idx):
        problems.append(
            f"recommendation does not lead: {RECOMMENDATION_MARKER!r} at "
            f"offset {rec_idx} is NOT before {FIRST_ALTERNATIVE_MARKER!r} at "
            f"offset {alt_idx} in {PROTOCOL_REL} output template"
        )

    # --- SKILL.md Axis-4 prose check ---
    skill_path = root / SKILL_REL
    skill_text = skill_path.read_text(encoding="utf-8")
    region = extract_skill_region(skill_text, SKILL_REL)

    if REMOVED_PHRASE in region:
        problems.append(
            f"old end-position phrase {REMOVED_PHRASE!r} still in Axis-4 "
            f"region of {SKILL_REL}"
        )
    if not any(p in region for p in LEAD_PHRASES):
        problems.append(
            f"recommendation-first wording (one of {LEAD_PHRASES}) missing "
            f"from Axis-4 region of {SKILL_REL}"
        )

    if problems:
        raise AssertionError(
            "axis4 recommendation-first invariant violated:\n"
            + "\n".join(problems)
        )


def test_recommendation_precedes_alternatives():
    check(REPO_ROOT)


def test_check_catches_old_order_restored(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    Restores the OLD order (alternatives first, My take last) in an
    isolated tmp_path copy of the protocol file and shows check() raises
    naming the ordering problem — zero mutation residue in the real tree.
    """
    src = REPO_ROOT / PROTOCOL_REL
    dst = tmp_path / PROTOCOL_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    # SKILL.md must also be present (check() reads it); copy real tree.
    skill_src = REPO_ROOT / SKILL_REL
    skill_dst = tmp_path / SKILL_REL
    skill_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(skill_src, skill_dst)

    check(tmp_path)  # baseline: unmutated copy passes (post-edit real tree)

    # Restore old order: move ONLY the My-take block to AFTER the
    # alternatives. The recommendation block spans from its marker up to
    # (but not including) the first-alternative marker.
    text = dst.read_text(encoding="utf-8")
    blk_start, blk_end = extract_template_block(text, PROTOCOL_REL)
    block = text[blk_start:blk_end]
    rec_idx = block.find(RECOMMENDATION_MARKER)
    assert rec_idx != -1
    alt_idx = block.find(FIRST_ALTERNATIVE_MARKER, rec_idx)
    assert alt_idx != -1
    rec_block = block[rec_idx:alt_idx]
    remainder = block[:rec_idx] + block[alt_idx:]
    # Append the recommendation block at the end (old order: alternatives
    # first, My take last).
    new_block = remainder.rstrip() + "\n\n" + rec_block.rstrip() + "\n"
    mutated = text[:blk_start] + new_block + text[blk_end:]
    dst.write_text(mutated, encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)
    message = str(exc_info.value)
    assert "recommendation does not lead" in message