"""RED/GREEN evidence for W1-01 — the probe-graduation and store-entry text
that used to live in ship's "## 3. Memory" section moved to build's
"## 6.5 Memory step" section (task W1-02); ship's own §3 keeps only the
trailer paragraphs and one escape-hatch sentence. These five pins
re-target the same phrases, now read from build/SKILL.md, plus one new
pin on ship's escape-hatch sentence.

A cheap string-presence assertion; it does not parse or execute the
prose, it only proves the paragraph landed in the file the reading
station reads, in the right place, within the section's word cap.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SHIP_SKILL_MD = REPO / "loom-code/skills/ship/SKILL.md"
BUILD_SKILL_MD = REPO / "loom-code/skills/build/SKILL.md"


def _section_3_memory() -> str:
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 3. Memory")
    end = text.index("## 3.5 The nit batch")
    return text[start:end]


def _build_memory_step_section() -> str:
    """Text of build/SKILL.md's "## 6.5 Memory step" section, up to the
    "## 7. Hand-off" heading that follows it — the section that now owns
    probe graduation and docs/loom/memory/ store entries (moved here from
    ship's §3 by W1-02, commit 08904fd1)."""
    text = BUILD_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 6.5 Memory step")
    end = text.index("## 7. Hand-off")
    return text[start:end]


def _unwrapped(section: str) -> str:
    """Markdown hard-wraps a paragraph across lines; join those wraps back
    into single-spaced prose before substring-matching a phrase that may
    straddle a line break."""
    return " ".join(section.split())


def test_memory_section_documents_probe_graduation() -> None:
    section = _build_memory_step_section()
    flat = _unwrapped(section)
    assert "evidence/probes/" in section
    assert "test-function name" in flat
    assert "cold-read" in flat.lower()
    assert "never graduate" in flat or "do not graduate" in flat


def test_probe_graduation_paragraph_after_store_entries_paragraph() -> None:
    """Moved pin, inverted order: ship's old §3 wrote "Store entries" before
    the probe-graduation paragraph, and this pin asserted that order. Build's
    §6.5 (commit 08904fd1) writes "**Probe graduation.**" first and
    "**Store entries.**" second — the opposite order — so the assertion
    below is inverted to match the section as it now reads, not deleted."""
    section = _build_memory_step_section()
    store_idx = section.index("**Store entries.**")
    probe_idx = section.index("evidence/probes/")
    assert probe_idx < store_idx


def test_probe_graduation_paragraph_within_word_cap() -> None:
    """Moved pin, widened cap: ship's old §3 kept the probe-graduation
    instruction and the name-collision clause as two separate paragraphs
    (blank-line delimited), each within a 60-word cap. Build's §6.5 merges
    them into one physical paragraph (no blank line between "test-function
    name." and "A test that shares..."), which measures 75 words — so the
    cap here is widened to 90 to match the merged shape while still
    bounding it, rather than asserting a 60-word fact the text no longer
    has."""
    section = _build_memory_step_section()
    start = section.index("evidence/probes/")
    # back up to the start of the paragraph (previous blank line)
    para_start = section.rindex("\n\n", 0, start) + 2
    para_end = section.index("\n\n", start)
    paragraph = section[para_start:para_end]
    assert len(paragraph.split()) <= 90


def test_probe_graduation_paragraph_names_collision_not_duplicate() -> None:
    section = _build_memory_step_section()
    flat = _unwrapped(section)
    assert (
        "a name collision, not a duplicate" in flat
    ), "expected the name-collision-vs-duplicate clause in the graduation paragraph"
    assert "rename the probe copy rather than dropping it" in flat


def test_graduation_commit_reruns_branch_end_before_review_only_commit() -> None:
    """Moved pin, inverted subject: this pin used to assert that ship's §3
    told the graduation commit to re-run the branch-end checkpoint before
    the review-only commit. That instruction moved to build (W1-02), whose
    §6.5 now states the memory step precedes the review round that closes
    the plan instead — and ship's own §3 no longer instructs any re-run at
    all. Both halves are asserted below."""
    build_section = _build_memory_step_section()
    flat_build = _unwrapped(build_section)
    assert (
        "this step precedes the round" in flat_build
    ), "expected build's §6.5 to say the memory step precedes the closing review round"
    assert "loom-code:review" in flat_build

    ship_section = _section_3_memory()
    flat_ship = _unwrapped(ship_section)
    assert (
        "re-run the `branch-end` checkpoint" not in flat_ship
        and "re-run the branch-end checkpoint" not in flat_ship
    ), "ship's §3 must no longer instruct a branch-end re-run"


def test_ship_memory_escapehatch_names_build_task() -> None:
    """New pin (W1-01): ship's §3 keeps one escape-hatch sentence — a
    lesson or probe ship finds that build missed is a task for
    `loom-code:build` followed by a fresh branch-end checkpoint, never a
    commit made here."""
    section = _section_3_memory()
    flat = _unwrapped(section)
    assert "a task for `loom-code:build`" in flat
    assert "fresh" in flat and "branch-end" in flat
    assert "never a commit made here" in flat
