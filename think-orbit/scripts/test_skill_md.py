"""RED test for Task 11 — decision-session SKILL.md core sitting protocol.

@req: BI-6
@req: BI-7
@req: BI-12
"""
from __future__ import annotations

import re
from pathlib import Path

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


def test_decision_session_skill_names_cli_verbs_interrupts_view_prohibition_and_word_cap():
    # @req: BI-6
    text = SKILL_MD.read_text(encoding="utf-8")
    body = _body(text)

    assert len(body.split()) <= WORD_CAP, (
        f"SKILL.md body is {len(body.split())} words, cap is {WORD_CAP}"
    )

    for literal in REQUIRED_LITERALS:
        assert literal in body, f"SKILL.md body must name {literal!r}"

    assert re.search(r"never read.*views/", body, re.IGNORECASE) or re.search(
        r"views/.*never", body, re.IGNORECASE
    ), "SKILL.md body must state the views/ read prohibition"

    sentences = _sentences(body)
    for token in INTERRUPT_TOKENS:
        assert any(
            token in s and re.search(r"confirm|ask", s, re.IGNORECASE)
            for s in sentences
        ), f"no confirm/ask sentence names the interrupt point {token!r}"


def test_decision_session_minimal_examples_pass_check(tmp_path):
    # @req: BI-6
    body = _body(SKILL_MD.read_text(encoding="utf-8"))
    examples = EXAMPLE_BLOCK.findall(body)

    assert len(examples) >= 3, (
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
