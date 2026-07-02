"""Structural grep-test guarding the reviewer role-anchor against
dispatch-time role confusion.

The agent contract is a prompt artifact, not executable code. The contract
under guard: a dispatched `code-reviewer` must know it IS the reviewer.
Observed failure (2026-07-03 ui-verification close-out): "review request"
phrasing in the dispatch prompt role-confused the agent into acting as an
orchestrator — it announced "I've dispatched the whole-branch review" to
nobody and produced no verdict. The existing prohibition ("may not dispatch
other subagents", role-contract rule 3) did not prevent this: a negative
rule buried mid-contract cannot fix a mistaken identity. The fix is a
POSITIVE identity anchor — "You ARE the reviewer" — carried in BOTH places
the agent reads at dispatch time:

1. the agent contract's role statement (loom-code/agents/code-reviewer.md),
2. the input-contract prompt template the orchestrator copies
   (same file, §Input contract), so every dispatch opens with it.

The orchestrating skill (requesting-code-review SKILL.md §Process) must
instruct the orchestrator to keep that opening line when building the
dispatch prompt — otherwise the template drifts out of real dispatches.

These checks assert on the load-bearing PHRASE (intent), tolerant of
surrounding wording, so the test guards meaning without being brittle.

Stdlib only (pathlib). Resolve files relative to this test file.
"""

from pathlib import Path

_ROOT = Path(__file__).parents[1]

AGENT = _ROOT / "agents" / "code-reviewer.md"
RCR = _ROOT / "skills" / "requesting-code-review" / "SKILL.md"

_ANCHOR = "You ARE the reviewer"


def _text(p: Path) -> str:
    assert p.is_file(), f"file is absent at {p}"
    return p.read_text(encoding="utf-8")


def test_agent_contract_carries_role_anchor():
    """The agent contract must state the positive identity up front —
    a prohibition alone ("may not dispatch") failed in the observed
    incident because the agent never believed it was the reviewer."""
    assert _ANCHOR in _text(AGENT), \
        "code-reviewer.md must carry the positive role anchor " \
        f"'{_ANCHOR}' — the negative rule 3 alone does not prevent " \
        "dispatch-time role confusion"


def test_input_contract_template_opens_with_anchor():
    """The §Input contract prompt template is what real dispatches copy;
    the anchor must be inside the template's fenced block so every
    dispatch prompt opens with it, not only the agent's own contract."""
    text = _text(AGENT)
    marker = "## Input contract"
    assert marker in text, "code-reviewer.md lost its §Input contract"
    contract_section = text.split(marker, 1)[1]
    fenced = contract_section.split("```", 2)
    assert len(fenced) >= 3, "§Input contract lost its fenced template"
    assert _ANCHOR in fenced[1], \
        f"'{_ANCHOR}' must be INSIDE the input-contract prompt template " \
        "(the text orchestrators copy into every dispatch)"


def test_rcr_dispatch_step_instructs_the_anchor():
    """requesting-code-review's dispatch step must tell the orchestrator
    to open the dispatch prompt with the anchor — the template only
    protects dispatches that actually copy it."""
    assert _ANCHOR in _text(RCR), \
        "requesting-code-review SKILL.md's dispatch step must instruct " \
        f"opening the dispatch prompt with '{_ANCHOR}'"
