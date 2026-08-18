"""RED test for Task 11 — decision-session SKILL.md core sitting protocol.

brief-item: BI-6
brief-item: BI-7
brief-item: BI-12
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

import dag

SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "decision-session"
    / "SKILL.md"
)

WORD_CAP = 4500

REQUIRED_LITERALS = (
    "dag.py check <root>",
    "dag.py claims <root>",
    "dag.py render <root>",
    "break-assumption",
    "references/node-schema.md",
    "references/research-rules.md",
    "references/blind-spot-checklist.md",
)

# The three interrupt points: each token must appear in a sentence that also
# carries the interrupt verb ("confirm" / "ask") — naming the token alone is
# not the contract, being an interrupt point is.
INTERRUPT_TOKENS = ("GOAL", "assumption", "DECISION")


# Machine-readable example convention: each fenced example block in SKILL.md is
# preceded by a marker line `<!-- example: <relpath> -->` naming where the block
# belongs inside a project root.
EXAMPLE_BLOCK = re.compile(
    r"<!-- example: (?P<relpath>[^\s>]+) -->\n```[a-z]*\n(?P<content>.*?)```",
    re.DOTALL,
)


def _body(text: str) -> str:
    """Return the SKILL.md body — everything after the YAML frontmatter."""
    _, body = dag.split_frontmatter(text)
    assert body != text, "SKILL.md must open with YAML frontmatter"
    return body


def _sentences(body: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+|\n", body) if s.strip()]


def _asserts_views_prohibition(body: str) -> None:
    """The `views/` read prohibition must be stated, in either word order."""
    assert re.search(r"never read.*views/", body, re.IGNORECASE) or re.search(
        r"views/.*never", body, re.IGNORECASE
    ), "SKILL.md body must state the views/ read prohibition"


def test_decision_session_skill_names_cli_verbs_interrupts_view_prohibition_and_word_cap():
    # brief-item: BI-6
    text = SKILL_MD.read_text(encoding="utf-8")
    body = _body(text)

    assert len(body.split()) <= WORD_CAP, (
        f"SKILL.md body is {len(body.split())} words, cap is {WORD_CAP}"
    )

    for literal in REQUIRED_LITERALS:
        assert literal in body, f"SKILL.md body must name {literal!r}"

    _asserts_views_prohibition(body)

    sentences = _sentences(body)
    for token in INTERRUPT_TOKENS:
        assert any(
            token in s and re.search(r"confirm|ask", s, re.IGNORECASE)
            for s in sentences
        ), f"no confirm/ask sentence names the interrupt point {token!r}"


def test_decision_session_minimal_examples_pass_check(tmp_path):
    # brief-item: BI-6
    body = _body(SKILL_MD.read_text(encoding="utf-8"))
    examples = EXAMPLE_BLOCK.findall(body)

    assert len(examples) == 4, (
        "expected the minimal GOAL / CLAIM / assumption examples to carry "
        f"`<!-- example: ... -->` markers, found {len(examples)}"
    )

    for relpath, content in examples:
        target = tmp_path / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    violations = dag.check(dag.load_project(tmp_path))
    assert violations == [], (
        "SKILL.md examples must be gate-clean when written verbatim:\n"
        + "\n".join(violations)
    )


ROUTER_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "using-think-orbit"
    / "SKILL.md"
)

BREAK_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "break-assumption"
    / "SKILL.md"
)

ROUTER_WORD_CAP = 2500

ROUTER_REQUIRED_LITERALS = (
    "decision-session",
    "break-assumption",
    "dag.py check <root>",
    "dag.py claims <root>",
)


def test_router_skill_routes_to_verbs_and_forbids_views():
    # brief-item: BI-6
    body = _body(ROUTER_SKILL_MD.read_text(encoding="utf-8"))

    assert len(body.split()) <= ROUTER_WORD_CAP, (
        f"SKILL.md body is {len(body.split())} words, cap is {ROUTER_WORD_CAP}"
    )

    for literal in ROUTER_REQUIRED_LITERALS:
        assert literal in body, f"router SKILL.md body must name {literal!r}"

    _asserts_views_prohibition(body)


ALL_SKILL_MDS = (SKILL_MD, ROUTER_SKILL_MD, BREAK_SKILL_MD)

# Every CLI mention must be copy-pasteable: a bare `dag.py <verb>` sends the
# reader to a script that is not on their PATH.

DAG_INVOCATION = re.compile(r"dag\.py (?:check|break|claims|render|impact)\b")
FULL_PREFIX = "${CLAUDE_PLUGIN_ROOT}/scripts/"


@pytest.mark.parametrize("skill_md", ALL_SKILL_MDS, ids=lambda p: p.parent.name)
def test_every_skill_always_uses_full_invocation_prefix(skill_md):
    # brief-item: BI-6
    body = _body(skill_md.read_text(encoding="utf-8"))

    bare = [
        body[max(0, m.start() - 60) : m.end()]
        for m in DAG_INVOCATION.finditer(body)
        if not body[: m.start()].endswith(FULL_PREFIX)
    ]
    assert bare == [], (
        "every dag.py invocation must be written "
        f"`{FULL_PREFIX}dag.py <verb> <root>`; bare mentions: {bare}"
    )


def test_router_skill_states_root_resolution_ladder():
    # brief-item: BI-6
    body = _body(ROUTER_SKILL_MD.read_text(encoding="utf-8"))

    for marker in ("current working directory", "ask", "session"):
        assert marker in body, f"root-resolution ladder must mention {marker!r}"


BREAK_WORD_CAP = 2000

BREAK_REQUIRED_LITERALS = (
    "dag.py break <root> <assumption-id>",
    "impact-",
    "direct dependents",
    "full impact",
    "references/node-schema.md",
)


def test_break_assumption_skill_names_break_verb_and_two_followups():
    # brief-item: BI-6
    body = _body(BREAK_SKILL_MD.read_text(encoding="utf-8"))

    assert len(body.split()) <= BREAK_WORD_CAP, (
        f"SKILL.md body is {len(body.split())} words, cap is {BREAK_WORD_CAP}"
    )

    for literal in BREAK_REQUIRED_LITERALS:
        assert literal in body, f"break-assumption SKILL.md must name {literal!r}"

    # The whole point of the skill: the user declares, the agent only asks.
    assert re.search(r"declare", body, re.IGNORECASE), (
        "SKILL.md must state that the user declares the break, not the agent"
    )

    # Nothing downstream is recomputed — the user decides what to re-examine.
    assert re.search(r"recomput", body, re.IGNORECASE), (
        "SKILL.md must state that nothing is recomputed"
    )

    _asserts_views_prohibition(body)

