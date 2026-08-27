"""Plan Task 1 (docs/loom/plans/2026-08-28-review-loop-convergence.md): pin
the ledger-driven delta-confirmation loop that replaces
`requesting-code-review`'s old unconditional "same skill, fresh subagent"
re-review rule.

WHY this test exists: the new loop contract is dense prose spread across
many required clauses (ledger vocabulary, arm selection, the two-cycle cap,
delta admissibility, the escalation valve, the terminal-wrapper minting
rule, the lost-handle restart rule). Nothing else pins that every one of
these clauses actually landed, and that the verbatim old rule it replaces
is gone. This test is that lock.

The skill is allowed (per the standing word-cap authorization) to push the
loop's detail into a `references/` file and keep only a summary + pointer
in SKILL.md — mirroring how `requesting-docs-review/SKILL.md` points at
`references/convergence-contract.md`. So this test's "present" assertions
search the UNION of SKILL.md plus any `references/*.md` file it links,
rather than pinning to one exact file. The "absent" (old rule) and
"retained" (Dead-arm / MALFORMED_PACKET) assertions stay scoped to
SKILL.md, since those anchors are Step 3 text that this task does not
move.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "loom-code/skills/requesting-code-review"
SKILL_MD = SKILL_DIR / "SKILL.md"

OLD_RULE = (
    "Re-dispatch if user fixed and wants re-review — same skill, fresh "
    "subagent (no state carry-over between rounds for clean evaluation)"
)

# Anchors that must survive the rewrite untouched (Step 3, not in scope).
RETAINED_ANCHORS = (
    "Dead-arm rule",
    "verdict: MALFORMED_PACKET",
    "One packet-fix re-dispatch is the bound",
)

# Ledger vocabulary + core loop rules the task requires present somewhere
# in SKILL.md or a references/ file it links.
PRESENT_TOKENS = (
    "CONFIRMED_RESOLVED",
    "STILL_BLOCKING",
    # arm-selection rule (rounds 2+ dispatch only to arms with open entries)
    "arms holding open entries",
    # two-cycle cap
    "at most two delta-confirmation cycles",
    # delta-admissibility rule
    "only inside the fix diff",
    # backlog debt route
    "docs/loom/backlog/",
    # escalation valve + never-closes-entries rule
    "escalation valve",
    "never closes an open ledger entry",
    # stable arm name: carve-out
    "code-review-arm-a",
    "code-review-arm-b",
    # terminal-wrapper minting rule
    "terminal wrapper",
    # lost-handle restart rule
    "never a ledger flip",
)


def _union_text() -> str:
    """SKILL.md content plus every references/*.md file it links to."""
    skill_text = SKILL_MD.read_text(encoding="utf-8")
    parts = [skill_text]
    refs_dir = SKILL_DIR / "references"
    if refs_dir.is_dir():
        for ref_path in sorted(refs_dir.glob("*.md")):
            name = ref_path.name
            if name in skill_text or f"references/{name}" in skill_text:
                parts.append(ref_path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def test_skill_carries_ledger_confirmation_loop():
    combined = _union_text()

    missing = [token for token in PRESENT_TOKENS if token not in combined]
    assert not missing, f"missing loop-contract tokens: {missing}"

    assert OLD_RULE not in combined, (
        "verbatim old re-review rule survived the rewrite: " + OLD_RULE
    )

    skill_text = SKILL_MD.read_text(encoding="utf-8")
    missing_retained = [a for a in RETAINED_ANCHORS if a not in skill_text]
    assert not missing_retained, (
        f"retained Step-3 anchors went missing from SKILL.md: {missing_retained}"
    )
