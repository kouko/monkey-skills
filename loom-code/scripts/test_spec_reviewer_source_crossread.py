"""Structural grep-test guarding the conditional source cross-read
instruction added to spec-reviewer.md (Task 5a,
docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md).

spec-reviewer.md is a prompt artifact, not executable code. Its
correctness here is the PRESENCE of one added instruction: when the
plan/spec text under review carries a source citation, the reviewer
must open the cited source and confirm it says what the text claims.
This must be worded as a CONDITIONAL TRIGGER, not a blanket
verification mandate -- Anthropic's current model guidance is that an
unconditional "verify everything" instruction causes over-verification
with no capability gain, and this repo's own guidance
(judgment-rubrics.md quality-floor row) is that prose requiring a
judgment call fails at weak tiers while prose naming a checkable
action survives. spec-reviewer runs at sonnet or haiku
(subagent-driven-development/SKILL.md:182 -- one tier below the
implementer), which is exactly why the trigger must be explicit rather
than left to initiative.

The "worded as a trigger, not a mandate" assertion is scoped to the
ADDED text only, isolated via `_crossread_section` anchored on a
distinctive marker phrase unique to this addition. An unscoped
assertion over the whole file would be the wrong test: this file's
pre-existing `rule-sheet-v1` block already contains unconditional
"MUST" citation-discipline language for an unrelated concern (citing
standards), and code-quality-reviewer.md's dimension-table row for
`external-surface-grounding` (D7, "verify every external-surface call
in this task's diff carries a grounding cite" -- :372 as of this
writing; the peer file, Task 5b) independently carries an
unconditional external-surface mandate --
neither is what this task is about, and an unscoped grep would
conflate them with the new instruction or become unsatisfiable for
the wrong reason.

These checks assert on load-bearing PHRASES (intent), tolerant of
wording variation, so the test guards meaning without being brittle.

Stdlib only (pathlib). Resolve spec-reviewer.md relative to this test
file.
"""

from pathlib import Path

AGENT = Path(__file__).parents[1] / "agents" / "spec-reviewer.md"

# Anchors the added instruction. Must be unique to the new text so the
# isolated section cannot accidentally swallow unrelated pre-existing
# unconditional wording (see module docstring).
MARKER = "conditional source cross-read"


def _text() -> str:
    assert AGENT.is_file(), f"spec-reviewer.md is absent at {AGENT}"
    return AGENT.read_text(encoding="utf-8")


def _crossread_section(text: str) -> str:
    low = text.lower()
    start = low.index(MARKER)
    # The addition is a single list item / short paragraph; stop at
    # the next blank-line-preceded heading or numbered-list boundary
    # so the isolated snippet cannot bleed into an unrelated
    # pre-existing rule that happens to follow it.
    tail = text[start:]
    end_markers = ["\n\n", "\n#"]
    end = len(tail)
    for m in end_markers:
        idx = tail.find(m, len(MARKER))
        if idx != -1:
            end = min(end, idx)
    return tail[:end]


def test_spec_reviewer_carries_conditional_crossread():
    """The contract must state: (a) the if-a-citation-is-present
    condition, (b) the open-and-compare action, (c) an explicit
    no-citation no-op, (d) an inline definition of what counts as a
    source citation, and (e) that the added instruction is worded as a
    trigger, not an unconditional verify-everything mandate -- scoped
    to the added text only."""
    text = _text()
    assert MARKER in text.lower(), (
        "spec-reviewer.md must add a distinctly-named conditional "
        "source cross-read instruction"
    )
    section = _crossread_section(text)
    low = section.lower()

    # (a) condition: triggered only when a citation is present
    assert "citation" in low, "must name the citation condition"
    assert "if " in low or "when " in low, (
        "the citation check must be phrased conditionally (if/when), "
        "not as a standing requirement"
    )

    # (b) action: open the cited source and confirm/compare
    assert "open" in low, "must instruct opening the cited source"
    assert "confirm" in low or "compare" in low or "matches" in low, (
        "must instruct confirming the source says what the text claims"
    )

    # (c) explicit no-citation no-op
    assert "no citation" in low or "no such citation" in low or "carries no" in low, (
        "must state the no-citation case explicitly"
    )
    assert "no-op" in low, (
        "the no-citation case must be named a no-op, not left implicit"
    )

    # (d) inline definition of "source citation"
    assert "file:line" in low or "url" in low, (
        "must define inline what counts as a source citation "
        "(e.g. file:line pointer, URL, named doc+section, quoted excerpt)"
    )

    # (e) trigger, not an unconditional mandate -- scoped to this
    # section only (see module docstring on why unscoped is wrong)
    assert "trigger" in low, (
        "must self-label the instruction as a trigger"
    )
    assert "not a blanket" in low or "not an unconditional" in low or (
        "not a" in low and "mandate" in low
    ), (
        "must explicitly disclaim being a blanket/unconditional "
        "verification mandate"
    )
