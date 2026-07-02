"""Structural grep-test guarding the complex-fork briefing escalation in the
`## Asking the user` gates.

SKILL.md is a prompt artifact, not executable code. The contract under guard:
when a technical fork surfaced to the user is genuinely complex — the shared
threshold triple (>=3 trade-offs / >=2 implementation paths / architectural
blast radius) — the agent must run `dev-workflow:brief-before-asking`
(6-block briefing, Mental Model first) BEFORE firing the AskUserQuestion,
instead of dumping options on a user who cannot evaluate them (the observed
pain: "technical choices I can't really evaluate").

Rollout follows PR #355/#358's mirror-principle: each skill carries its own
in-place sentence (no copied block), but the THRESHOLD TRIPLE is the shared
trigger contract and must stay lockstep across every skill that carries the
escalation — a drifted threshold means the same fork briefs in one skill and
doesn't in another.

These checks assert on load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

_SKILLS = Path(__file__).parents[1] / "skills"

BRAINSTORMING = _SKILLS / "brainstorming" / "SKILL.md"
SDD = _SKILLS / "subagent-driven-development" / "SKILL.md"
RCR = _SKILLS / "requesting-code-review" / "SKILL.md"

# The shared trigger contract — must appear verbatim-equivalent in every
# skill that carries the escalation.
_THRESHOLD_MARKS = ("≥3 trade-offs", "≥2 implementation paths",
                    "architectural blast radius")


def _text(p: Path) -> str:
    assert p.is_file(), f"SKILL.md is absent at {p}"
    return p.read_text(encoding="utf-8")


def _carries_escalation(text: str) -> bool:
    return "brief-before-asking" in text and all(
        m in text for m in _THRESHOLD_MARKS)


def test_brainstorming_carries_complex_fork_briefing():
    """The originating rule (shipped pre-#468) must keep carrying it."""
    assert _carries_escalation(_text(BRAINSTORMING)), \
        "brainstorming must brief complex forks via " \
        "dev-workflow:brief-before-asking with the shared threshold triple"


def test_sdd_gate2_carries_complex_fork_briefing():
    """SDD's asking gates surface implementation-time technical forks
    (NEEDS_CONTEXT / BLOCKED / 4th-retry escalations, design choices) — the
    place the user most often meets a choice they cannot evaluate. Gate 2
    (what to bring) must escalate complex forks to a briefing, not just a
    (Recommended) option."""
    assert _carries_escalation(_text(SDD)), \
        "subagent-driven-development must brief complex forks via " \
        "dev-workflow:brief-before-asking with the shared threshold triple"


def test_rcr_gate2_carries_complex_fork_briefing():
    """Review findings can open remediation forks (e.g. an architectural
    finding with 2+ viable fixes). The relay's gate 2 must escalate those to
    a briefing instead of a bare fix/defer/merge ask."""
    assert _carries_escalation(_text(RCR)), \
        "requesting-code-review must brief complex forks via " \
        "dev-workflow:brief-before-asking with the shared threshold triple"


def test_threshold_triple_lockstep():
    """Every carrier states the SAME three thresholds — the trigger is a
    shared contract; per-skill drift silently changes when a fork briefs."""
    for p in (BRAINSTORMING, SDD, RCR):
        text = _text(p)
        missing = [m for m in _THRESHOLD_MARKS if m not in text]
        assert not missing, \
            f"{p.parent.name}: threshold triple drifted — missing {missing}"
