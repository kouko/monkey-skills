"""RED/GREEN evidence for W1-01 — review station text carries the small
change lane, the docs-lint clause, and consequence-based severity.

Three cheap string-presence assertions; they do not parse or execute the
prose, they only prove the three pieces of text this task adds actually
landed in the files the review station and its reviewer contract read.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_review_skill_md_documents_small_lane() -> None:
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    assert "small lane" in text


def test_reviewer_agent_documents_docs_lint() -> None:
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    assert "docs-lint" in text


def test_lenses_severity_section_defines_act_wrongly() -> None:
    text = (REPO / "loom-code/skills/review/references/lenses.md").read_text(encoding="utf-8")
    start = text.index("## Severity and verdict")
    section = text[start:]
    assert "act wrongly" in section
