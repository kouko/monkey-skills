"""RED/GREEN evidence for W1-02 — the ship station's §3 Memory text
documents probe graduation: non-overlapping pytest probes under a change's
`evidence/probes/` copy into the repo's permanent test directory.

A cheap string-presence assertion; it does not parse or execute the
prose, it only proves this task's paragraph landed in the file the ship
station reads, in the right place, within the section's word cap.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SHIP_SKILL_MD = REPO / "loom-code/skills/ship/SKILL.md"


def _section_3_memory() -> str:
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 3. Memory")
    end = text.index("## 3.5 The nit batch")
    return text[start:end]


def _unwrapped(section: str) -> str:
    """Markdown hard-wraps a paragraph across lines; join those wraps back
    into single-spaced prose before substring-matching a phrase that may
    straddle a line break."""
    return " ".join(section.split())


def test_memory_section_documents_probe_graduation() -> None:
    section = _section_3_memory()
    flat = _unwrapped(section)
    assert "evidence/probes/" in section
    assert "test-function name" in flat
    assert "cold-read" in flat.lower()
    assert "never graduate" in flat or "do not graduate" in flat


def test_probe_graduation_paragraph_after_store_entries_paragraph() -> None:
    section = _section_3_memory()
    store_idx = section.index("**Store entries**")
    probe_idx = section.index("evidence/probes/")
    assert probe_idx > store_idx


def test_probe_graduation_paragraph_within_word_cap() -> None:
    section = _section_3_memory()
    start = section.index("evidence/probes/")
    # back up to the start of the paragraph (previous blank line)
    para_start = section.rindex("\n\n", 0, start) + 2
    para_end = section.index("\n\n", start)
    paragraph = section[para_start:para_end]
    assert len(paragraph.split()) <= 60


def test_probe_graduation_paragraph_names_collision_not_duplicate() -> None:
    section = _section_3_memory()
    flat = _unwrapped(section)
    assert (
        "a name collision, not a duplicate" in flat
    ), "expected the name-collision-vs-duplicate clause in the graduation paragraph"
    assert "rename the probe copy rather than dropping it" in flat


def test_graduation_commit_reruns_branch_end_before_review_only_commit() -> None:
    section = _section_3_memory()
    flat = _unwrapped(section)
    assert (
        "before the review-only commit" in flat
    ), "expected the graduation commit to be placed before the review-only commit"
    assert (
        "re-run the `branch-end` checkpoint" in flat
        or "re-run the branch-end checkpoint" in flat
    ), "expected the graduation text to require re-running the branch-end checkpoint"
