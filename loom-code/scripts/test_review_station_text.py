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


def test_review_skill_md_tests_only_is_name_or_location() -> None:
    """Branch-end fix: the small-lane 'tests only' class is name/location
    only (test_*.py, *_test.py, tests/ segment), never content-verified,
    and distinct from the §6 artifact-type table (which still maps a
    tests/-relocated production file to `code`)."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    assert "name or location only" in text


def test_reviewer_agent_documents_docs_lint() -> None:
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    assert "docs-lint" in text


def test_lenses_severity_section_defines_act_wrongly() -> None:
    text = (REPO / "loom-code/skills/review/references/lenses.md").read_text(encoding="utf-8")
    start = text.index("## Severity and verdict")
    section = text[start:]
    assert "act wrongly" in section


def _you_own_paragraph(text: str) -> str:
    """Return the block whose first non-blank line starts `You own`."""
    blocks = [b for b in text.split("\n\n") if b.strip()]
    hits = [b for b in blocks if b.lstrip().startswith("You own")]
    assert hits, "no `You own` paragraph found"
    return hits[0]


def test_reviewer_agent_owns_reconciliation_paragraph_under_80_words() -> None:
    """W1-01: reviewer.md carries a `You own` positioning paragraph, <= 80
    words counted with `len(str.split())` (never `wc` — BSD/GNU disagree)."""
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    assert len(para.split()) <= 80


def test_adversary_agent_owns_negative_paragraph_under_80_words() -> None:
    """W1-01: adversary.md carries a `You own` positioning paragraph, <= 80
    words counted with `len(str.split())` (never `wc`)."""
    text = (REPO / "loom-code/agents/adversary.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    assert len(para.split()) <= 80


def test_fix_rounds_reader_finding_to_probe_sentence_under_60_words() -> None:
    """W1-01: fix-rounds.md gains a block naming `important`, the adversary,
    and a probe, <= 60 words counted with `len(str.split())`."""
    text = (
        REPO / "loom-code/skills/review/references/fix-rounds.md"
    ).read_text(encoding="utf-8")
    blocks = [b for b in text.split("\n\n") if b.strip()]
    hits = [
        b
        for b in blocks
        if "important" in b.lower()
        and "adversary" in b.lower()
        and "probe" in b.lower()
    ]
    assert hits, "no block naming `important` + adversary + probe found"
    assert len(hits[0].split()) <= 60
