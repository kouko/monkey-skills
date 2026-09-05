"""RED/GREEN evidence for W1-01 — the probe-graduation and store-entry text
that used to live in ship's "## 3. Memory" section moved to build's
"## 6.5 Memory step" section (task W1-02); ship's own §3 keeps only the
trailer paragraphs and one escape-hatch sentence. These five pins
re-target the same phrases, now read from build/SKILL.md, plus one new
pin on ship's escape-hatch sentence.

A cheap string-presence assertion; it does not parse or execute the
prose, it only proves the paragraph landed in the file the reading
station reads, in the right place, within the section's word cap.

W2-01 adds: ship no longer closes the intent in its own commit, its own
checkpoint and a second push after the pull request exists (option A).
The close line now rides in the same review-only commit §3 already
amends for the memory trailers, and §6 is "Merge, then verify" — pins
below cover that shape, the PR body's new "## Closing log" section, and
the one-line backward-compatibility note for branches shipped under the
older `PR #<N>` grammar.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SHIP_SKILL_MD = REPO / "loom-code/skills/ship/SKILL.md"
BUILD_SKILL_MD = REPO / "loom-code/skills/build/SKILL.md"

_NEGATION_RE = re.compile(r"\b(?:not|never|no)\b|n't", re.IGNORECASE)


def _has_negation(sentence: str) -> bool:
    """True iff `sentence` contains a word-boundary negation token — 'not',
    'never' or 'no' as whole words, or an "n't" contraction."""
    return bool(_NEGATION_RE.search(sentence))


def _sentences(text: str) -> list[str]:
    """Split text into sentences after collapsing newlines to spaces, so a
    sentence that line-wraps in the SKILL.md source still reads as one
    unit here."""
    flat = " ".join(text.split())
    return [p for p in re.split(r"(?<=[.!?])\s+", flat) if p.strip()]


def _section_6_merge_then_verify() -> str:
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 6. Merge, then verify")
    end = text.index("## 7. Clean-up")
    return text[start:end]


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


def test_ship_close_line_rides_in_review_only_commit() -> None:
    """W2-01: ship's §6 states the intent's close line rides in the same
    review-only commit that carries `review.json` — pushed once and PR'd
    once, no separate close commit or second push. Affirmative,
    un-negated."""
    section = _section_6_merge_then_verify()
    hits = [
        s for s in _sentences(section)
        if "close line" in s.lower()
        and "review-only" in s.lower()
        and "pushed once and pr'd once" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "ship/SKILL.md §6 has no affirmative close-line-rides-in-commit sentence"
    )


def test_ship_push_review_only_head_admits_close_shape() -> None:
    """§6: `push.review-only-head` admits the `review.json` + one intent
    line shape — the rule this option relies on."""
    section = _section_6_merge_then_verify()
    hits = [
        s for s in _sentences(section)
        if "push.review-only-head" in s.lower()
        and "admits exactly that shape" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "ship/SKILL.md §6 has no push.review-only-head admits-exactly-that-shape "
        "sentence"
    )


def test_ship_older_pr_number_shape_still_accepted() -> None:
    """§6: a branch shipped before this rule used `status: closed <date> —
    PR #<N>`; the checker still accepts that older shape — a one-line
    backward-compatibility note, not a second code path this station
    produces."""
    section = _section_6_merge_then_verify()
    flat = _unwrapped(section)
    assert "PR #<N>" in flat
    assert "the checker still accepts that older shape" in flat


def test_ship_pr_body_has_closing_log_section_before_memory() -> None:
    """§5's PR-body template gains a `## Closing log` section that pastes
    `git log <reviewed_sha>..HEAD --format='%h %s'`, placed before
    `## Memory` — the trailer footer must stay the template's last
    block (`ship.pr-body-carries-trailer-footer`)."""
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    closing_idx = text.index("## Closing log")
    memory_idx = text.index("## Memory")
    assert closing_idx < memory_idx
    flat = _unwrapped(text)
    assert "git log <reviewed_sha>..HEAD --format='%h %s'" in flat


# --- synthetic self-tests for the negation-aware matcher --------------------


def test_matcher_close_line_sentence_negated_rejected() -> None:
    """A sentence carrying every required substring but negated with
    'never' must be rejected by the matcher, mirroring
    test_language_station_text.py's synthetic-negative pattern."""
    sentence = (
        "The intent's close line never rides in the review-only commit, "
        "pushed once and PR'd once."
    )
    assert _has_negation(sentence)


def test_matcher_review_only_head_sentence_negated_rejected() -> None:
    sentence = "`push.review-only-head` does not admit exactly that shape."
    assert _has_negation(sentence)


def test_matcher_close_line_sentence_affirmative_accepted() -> None:
    sentence = (
        "The intent's close line rides in the review-only commit, pushed "
        "once and PR'd once."
    )
    assert "rides in" in sentence.lower()
    assert not _has_negation(sentence)


def test_matcher_review_only_head_sentence_affirmative_accepted() -> None:
    sentence = "`push.review-only-head` admits exactly that shape."
    assert "admits exactly that shape" in sentence.lower()
    assert not _has_negation(sentence)


def test_ship_preflight_in_section_3_fallback_in_section_6() -> None:
    """§3 tells a cold agent to check the gating checker's own rule text
    BEFORE the amend that adds the close line (an older checker would
    otherwise block the push before any fallback text is reached); §6
    names the fallback the older checker accepts."""
    sec3 = _section_3_memory()
    flat3 = _unwrapped(sec3)
    assert "--list-rules | grep push.review-only-head" in flat3
    assert "leave the `status:` line untouched here" in flat3
    # the preflight is read before the amend command that stages the intent
    preflight_idx = sec3.index("--list-rules | grep push.review-only-head")
    amend_idx = sec3.index("git add docs/loom/<change-id>/review.json docs/loom/intent/<change-id>.md")
    assert preflight_idx < amend_idx, "§3 preflight sits after the amend command"
    assert "when the preflight admitted" in flat3
    flat = _unwrapped(_section_6_merge_then_verify())
    assert "§3's preflight" in flat
    hits = [
        s for s in _sentences(_section_6_merge_then_verify())
        if "closed <date> — PR #<N>" in s and "commit of its own" in s
        and not _has_negation(s)
    ]
    assert hits, "§6 has no affirmative fallback sentence for an older checker"
