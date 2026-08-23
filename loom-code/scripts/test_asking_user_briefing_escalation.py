"""Structural grep-test guarding the complex-fork briefing escalation in the
`## Asking the user` gates.

SKILL.md is a prompt artifact, not executable code. The contract under guard:
when a technical fork surfaced to the user is genuinely complex — the shared
threshold triple (>=3 trade-offs / >=2 implementation paths / architectural
blast radius) — the agent must run `loom-workflow:brief-before-asking`
(6-block briefing, Mental Model first) BEFORE firing the AskUserQuestion,
instead of dumping options on a user who cannot evaluate them (the observed
pain: "technical choices I can't really evaluate").

Dedup (plain-relay PR): the threshold triple + brief-first rule now live in a
single family SSOT — `loom-code/hooks/family-reception.md §Brief before a
complex fork`. The six routers/skills that previously carried in-place copies
of the trigger (using-loom-discovery, using-loom-interface-design,
using-loom-product-principles, using-loom-spec, brainstorming,
subagent-driven-development) now POINT at that SSOT instead of duplicating the
triple. Two surfaces were intentionally NOT dedup'd and still carry the triple
in-place: `requesting-code-review` (an independent review-remediation surface,
not a copy of the brief-before-fork template) and the SessionStart
`router-card.md` (the proactive action-moment surface that must fire the
imperative inline, not via a pointer). This test encodes the post-dedup
invariant: the SSOT + the two remaining carriers state the triple; the two
dedup'd loom-code skills point at the SSOT.

These checks assert on load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

_SKILLS = Path(__file__).parents[1] / "skills"
_HOOKS = Path(__file__).parents[1] / "hooks"

BRAINSTORMING = _SKILLS / "brainstorming" / "SKILL.md"
SDD = _SKILLS / "subagent-driven-development" / "SKILL.md"
RCR = _SKILLS / "requesting-code-review" / "SKILL.md"
ROUTER_CARD = _HOOKS / "router-card.md"
SSOT = _HOOKS / "family-reception.md"

# The shared trigger contract — carried verbatim by the SSOT + the two
# remaining in-place carriers (RCR, router-card).
_THRESHOLD_MARKS = ("≥3 trade-offs", "≥2 implementation paths",
                    "architectural blast radius")

# The SSOT pointer fragment the dedup'd skills cite instead of the triple.
_SSOT_POINTER = ("family-reception.md", "Brief before a complex fork")


def _text(p: Path) -> str:
    assert p.is_file(), f"SKILL.md is absent at {p}"
    return p.read_text(encoding="utf-8")


def _carries_escalation(text: str) -> bool:
    return "brief-before-asking" in text and all(
        m in text for m in _THRESHOLD_MARKS)


def _points_at_ssot(text: str) -> bool:
    return all(frag in text for frag in _SSOT_POINTER)


def test_brainstorming_points_at_complex_fork_ssot():
    """brainstorming was dedup'd: it points at the family SSOT for the trigger
    threshold + brief-first rule instead of carrying the triple in-place
    (the canonical source relocated to family-reception.md)."""
    assert _points_at_ssot(_text(BRAINSTORMING)), \
        "brainstorming must point at family-reception.md §Brief before a " \
        "complex fork (the dedup'd SSOT), not carry the threshold triple"


def test_sdd_gate2_points_at_complex_fork_ssot():
    """SDD's asking gates surface implementation-time technical forks
    (NEEDS_CONTEXT / BLOCKED / 4th-retry escalations, design choices) — the
    place the user most often meets a choice they cannot evaluate. Dedup'd to
    point at the family SSOT instead of carrying the triple in-place."""
    assert _points_at_ssot(_text(SDD)), \
        "subagent-driven-development must point at family-reception.md " \
        "§Brief before a complex fork (the dedup'd SSOT), not carry the " \
        "threshold triple"


def test_rcr_gate2_carries_complex_fork_briefing():
    """Review findings can open remediation forks (e.g. an architectural
    finding with 2+ viable fixes). RCR was NOT part of the brief-before-fork
    dedup — it still carries the triple in-place as an independent
    review-remediation surface. The relay's gate 2 must escalate those to a
    briefing instead of a bare fix/defer/merge ask."""
    assert _carries_escalation(_text(RCR)), \
        "requesting-code-review must brief complex forks via " \
        "loom-workflow:brief-before-asking with the shared threshold triple"


def test_router_card_names_bba_with_triple():
    """The SessionStart router card (rule 5) is the action-moment surface —
    it must NAME loom-workflow:brief-before-asking (not just paraphrase
    'research before asking') and carry the shared threshold triple
    verbatim, so the imperative fires proactively before the ask, not just
    inside the deeper skills a session may never load. NOT dedup'd — a
    pointer would defeat the proactive inline fire."""
    assert _carries_escalation(_text(ROUTER_CARD)), \
        "router-card.md rule 5 must name loom-workflow:brief-before-asking " \
        "with the shared threshold triple"


def test_ssot_carries_threshold_triple():
    """The family SSOT (family-reception.md §Brief before a complex fork) is
    the single canonical home of the threshold triple post-dedup — the six
    routers point here, so this file must actually carry the triple."""
    text = _text(SSOT)
    missing = [m for m in _THRESHOLD_MARKS if m not in text]
    assert not missing, \
        f"family-reception.md SSOT missing threshold triple marks {missing}"


def test_threshold_triple_lockstep():
    """Every REMAINING in-place carrier states the SAME three thresholds — the
    trigger is a shared contract; per-skill drift silently changes when a fork
    briefs. Post-dedup the carrier set is the SSOT + RCR + router-card;
    brainstorming and SDD were dedup'd to pointers and are no longer
    triple-carriers."""
    for p in (SSOT, RCR, ROUTER_CARD):
        text = _text(p)
        missing = [m for m in _THRESHOLD_MARKS if m not in text]
        assert not missing, \
            f"{p.parent.name}: threshold triple drifted — missing {missing}"