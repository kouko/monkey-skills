"""Behavioral grep-test for the cross-layer consistency lens (Task 14, cut
(c) — docs/loom/BACKLOG.md §knowledge-triage v2.1).

completeness-critic is prose-enforced (Claude reads SKILL.md + a references
file and applies the instruction; no Python resolver) — behavioral pytest
for the LENS ITSELF is structurally infeasible (see the auto-memory entry
`feedback_cc_ll_pytest_infeasibility.md`: LLM-as-decision-engine cannot be
pytest-asserted without an LLM-loop harness or a parallel Python impl, which
would just create a second source of truth). What IS testable, and what this
file asserts, is the PRESENCE of the load-bearing instruction text — same
convention as test_domain_tag_triage.py and test_completeness_critic_skill.py.

Guards:
1. `references/consistency-lens.md` exists and states the omission this lens
   hunts: a `spec.md` requirement silently RESOLVING a question `proposal.md`
   flagged as open. Grounded in the REAL leg-1 haiku dogfood failure — the
   worked example embeds literal phrases from the actual artifact (REQ-002's
   "only aggregate settled trades into positions" resolving proposal.md's
   "Which date controls monthly report bucketing?" open question) so the
   lens is proven to target a real, reproduced failure, not an invented one.
2. SKILL.md mounts the check with a pointer to the reference file, scoped to
   a measured window around the unique "Consolidate the panel union before
   writing back" anchor (per docs/loom/memory/grep-tests-scope-to-measured-
   neighborhood.md — this repo's existing knowledge-triage reference tests
   use the identical window-around-unique-anchor technique).

Stdlib only (pathlib). Resolve paths relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parent.parent / "skills" / "completeness-critic" / "SKILL.md"
REF = (Path(__file__).parent.parent / "skills" / "completeness-critic"
       / "references" / "consistency-lens.md")


def _skill_text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _window(text: str, anchor: str, before: int = 0, after: int = 400) -> str:
    """Character window around the unique `anchor` substring. Fails loud if
    the anchor is missing or not unique (non-unique anchor risks silently
    landing the window on the wrong occurrence)."""
    count = text.count(anchor)
    assert count == 1, f"anchor {anchor!r} must be unique in the file, found {count}"
    idx = text.index(anchor)
    start = max(0, idx - before)
    end = min(len(text), idx + len(anchor) + after)
    return text[start:end]


# --- reference file: the lens definition ------------------------------------

def test_reference_file_exists():
    assert REF.is_file(), f"references/consistency-lens.md is absent at {REF}"


def test_reference_states_the_omission_question():
    text = REF.read_text(encoding="utf-8")
    low = text.lower()
    assert "proposal.md" in text and "spec.md" in text, \
        "must name both artifact layers being cross-read"
    assert "silently" in low and ("resolve" in low or "resolves" in low), \
        "must state the failure mode: a requirement silently RESOLVING an open question"
    assert "omission" in low, \
        "must frame the finding as an OMISSION (this critic's mandate), not a bare inconsistency"


def test_reference_carries_real_leg1_worked_example_verbatim():
    # Literal phrases from the leg-1 haiku dogfood artifact (see docs/loom/
    # dogfood/2026-07-18-knowledge-triage-live-spec-leg.md "Severity-high"
    # bullet) — proves the lens targets the REAL reproduced failure, not an
    # invented stand-in.
    text = REF.read_text(encoding="utf-8")
    assert "only aggregate settled trades into positions" in text, \
        "must embed the real REQ-002 phrase that silently resolved the open question"
    assert "Which date controls monthly report bucketing?" in text, \
        "must embed the real proposal.md open-question phrase REQ-002 silently resolved"
    assert "evidence_needed: domain-convention" in text, \
        "worked example must show the proposal-side tag that spec.md dropped"


def test_reference_defines_severity_default():
    text = REF.read_text(encoding="utf-8")
    assert "3" in text and ("load-bearing" in text or "load bearing" in text), \
        "must default this finding class to severity 3 (load-bearing), per the critic's existing scale"


def test_reference_feeds_same_consolidated_pipeline():
    text = REF.read_text(encoding="utf-8")
    low = text.lower()
    assert "blind spot" in low, \
        "must write unresolved instances into '## Blind spots'"
    assert "consolidat" in low or "ranked" in low, \
        "must feed into the same consolidated/ranked set the panel produces, not a parallel channel"


# --- SKILL.md mount ----------------------------------------------------------

def test_skill_md_mounts_consistency_lens_at_consolidation_step():
    """The mount must sit at the consolidation step (post-panel, pre-write-
    back) — where the critic already holds both proposal.md and spec.md."""
    text = _skill_text()
    window = _window(text, "## Consolidate the panel union before writing back",
                     before=0, after=1000)
    assert "references/consistency-lens.md" in window, \
        "mount must point at references/consistency-lens.md"
    assert "proposal.md" in window and "spec.md" in window, \
        "mount must name both artifact layers"
    assert "omission" in window.lower(), \
        "mount must frame the check as an OMISSION finding"
