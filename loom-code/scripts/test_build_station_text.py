"""W1-04 -- build's dispatch-order paragraph widens from gate-only to every
full-lane `code` or `gate` task, small lane keeps implementer-first.

docs/loom/2026-09-04-checker-seams/plan.md W1-04, intent item 8 /
Acceptance #9: the paragraph in loom-code/skills/build/SKILL.md `## 2`
that opens with the adversary-first sentence must name both the `code`
and `gate` artifact types for the full lane, and must say the small lane
(the checker's `change_lane` recompute) keeps the implementer first with
the adversary attacking at the checkpoint instead.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILD_SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"


def _dispatch_order_paragraph() -> str:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    section = text.split("## 2. The dispatch prompt", 1)[1]
    # the paragraph runs up to the next blank-line-delimited block that
    # starts the "Dispatch `loom-code:implementer`" instruction.
    return section.split("Dispatch `loom-code:implementer`", 1)[0]


def test_full_lane_adversary_first_covers_code_and_gate() -> None:
    paragraph = _dispatch_order_paragraph()
    assert "adversary-first" in paragraph
    assert "`code`" in paragraph
    assert "`gate`" in paragraph


def test_small_lane_keeps_implementer_first() -> None:
    paragraph = _dispatch_order_paragraph()
    assert "small lane" in paragraph
    assert "change_lane" in paragraph
    assert "checkpoint" in paragraph


def test_paragraph_states_the_reason() -> None:
    paragraph = _dispatch_order_paragraph()
    # the named study and measured false-pass rate that justify independent
    # adversarial tests over the implementing agent's own tests.
    assert "SWE-ABS" in paragraph
    assert "19.7%" in paragraph


def test_word_cap_within_soft_bound() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    word_count = len(text.split())
    assert word_count <= 3750, f"word count {word_count} exceeds soft cap 3750"


def test_order_is_discipline_not_a_gate() -> None:
    paragraph = _dispatch_order_paragraph()
    flat = " ".join(paragraph.split())
    assert "process discipline, not a gate" in flat
    assert "dispatch[]" in flat
    assert "no push rule refuses an implementer-first task" in flat


def test_paragraph_drops_this_repos_own_change_citation() -> None:
    paragraph = _dispatch_order_paragraph()
    assert "this change's own" not in paragraph


# --- W1-02: memory step moves to build, before the plan's final checkpoint -


def _headings() -> list[tuple[str, int]]:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    return [
        (m.group(1).strip(), m.start())
        for m in re.finditer(r"^##\s+(.*)$", text, re.MULTILINE)
    ]


def test_memorysection_heading_exists_beforehandoff() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    headings = _headings()
    titles = [t.lower() for t, _ in headings]
    memory_idx = next((i for i, t in enumerate(titles) if "memory" in t), None)
    handoff_idx = next(
        (i for i, t in enumerate(titles) if "hand-off" in t or "handoff" in t), None
    )
    assert memory_idx is not None, "build/SKILL.md has no heading naming memory"
    assert handoff_idx is not None, "build/SKILL.md has no hand-off heading"
    assert memory_idx < handoff_idx, (
        "the memory heading must sit before the hand-off heading"
    )


def test_memorysection_names_graduation_and_memory_store() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    headings = _headings()
    idx = next(i for i, (t, _) in enumerate(headings) if "memory" in t.lower())
    start = headings[idx][1]
    end = headings[idx + 1][1] if idx + 1 < len(headings) else len(text)
    body = text[start:end].lower()
    assert "evidence/probes/" in body or "graduat" in body
    assert "docs/loom/memory/" in body


def test_step4and5_fencedblocks_name_git_log_and_task_trailer() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    for heading in ("## 4. After each task returns", "## 5. Wave end"):
        section = text.split(heading, 1)[1]
        # stop at the next top-level heading
        section = re.split(r"\n## ", section, 1)[0]
        blocks = re.findall(r"```\n(.*?)```", section, re.DOTALL)
        assert any("git log" in b and "Task:" in b for b in blocks), (
            f"{heading} has no fenced block naming both 'git log' and 'Task:'"
        )


def test_step5_names_reviewed_sha_dot_dot_head() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    section = text.split("## 5. Wave end", 1)[1]
    section = re.split(r"\n## ", section, 1)[0]
    assert "<reviewed_sha>..HEAD" in section


# --- wave-end:1-03: last-wave sequencing (package tests -> memory step ----
# --- -> the single closing review call, recorded branch-end) -------------


def _last_wave_paragraph() -> str:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    section = text.split("## 5. Wave end", 1)[1]
    section = re.split(r"\n## ", section, 1)[0]
    marker = "**Last wave of the plan.**"
    assert marker in section, "no last-wave paragraph in build's §5"
    tail = section.split(marker, 1)[1]
    para_end = tail.index("\n\n")
    return marker + tail[:para_end]


_NEGATED_CALL = re.compile(r"\b(?:not|never|no)\b|n't")


def _package_tests_before_memory_before_review(paragraph: str) -> bool:
    """True iff the paragraph contains EXACTLY ONE affirmative sentence that
    calls the review station (a sentence naming `loom-code:review` with no
    negation token -- "Do not call ... here" is a refusal, not a call), and
    that single call comes after both the package-tests reference (§6) and
    the memory-step reference (§6.5) -- the sequencing wave-end:1-01 fixed,
    tightened in round 2 so an early call plus a late call is rejected."""
    flat = " ".join(paragraph.split())
    sentences = re.split(r"(?<=[.!?])\s+", flat)
    calls = [
        s for s in sentences
        if "loom-code:review" in s and not _NEGATED_CALL.search(s)
    ]
    if len(calls) != 1:
        return False
    try:
        i_pkg = flat.index("§6 (package tests)")
        i_mem = flat.index("§6.5 (the memory step)")
    except ValueError:
        return False
    i_review = flat.index(calls[0]) + calls[0].index("loom-code:review")
    return i_pkg < i_mem < i_review


def test_lastwaveparagraph_orders_packagetests_then_memorystep_then_reviewcall() -> None:
    paragraph = _last_wave_paragraph()
    assert _package_tests_before_memory_before_review(paragraph), (
        "build's §5 last-wave paragraph does not order §6 before §6.5 "
        "before the review-station call"
    )


def test_orderchecker_synthetic_twocalls_rejected() -> None:
    """Self-test: a paragraph that calls review before package tests AND
    again after the memory step orders the last call correctly yet is not
    a single closing round -- it must be rejected."""
    synthetic = (
        "**Last wave of the plan.** Call `loom-code:review` for the wave. "
        "Then continue to §6 (package tests) and §6.5 (the memory step), "
        "then call `loom-code:review` again for the closing round."
    )
    assert not _package_tests_before_memory_before_review(synthetic), (
        "the order-checker accepted a paragraph with two review calls"
    )


def test_orderchecker_synthetic_reviewfirst_rejected() -> None:
    """Self-test on the order-checker above: a synthetic paragraph that
    calls review BEFORE naming §6 and §6.5 must be rejected."""
    synthetic = (
        "**Last wave of the plan.** Call `loom-code:review` once here, "
        "then continue to §6 (package tests) and §6.5 (the memory step)."
    )
    assert not _package_tests_before_memory_before_review(synthetic), (
        "the order-checker accepted a synthetic paragraph that calls "
        "review before §6 and §6.5 -- it should have rejected it"
    )


def test_closinground_recorded_branch_end_near_section5_reference() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    section = text.split("## 7. Hand-off", 1)[1]
    section = re.split(r"\n## ", section, 1)[0]
    assert "branch-end" in section, (
        "build's §7 no longer names the closing round's recorded scope "
        "value 'branch-end'"
    )
    assert "§5" in section, (
        "build's §7 no longer ties the branch-end recording back to §5's "
        "closing call"
    )


# --- branch-end-02: §6.5 Commits fallback names both branches -------------


def _commits_paragraph() -> str:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    section = text.split("## 6.5 Memory step", 1)[1]
    section = re.split(r"\n## ", section, 1)[0]
    marker = "**Commits.**"
    assert marker in section, "no Commits paragraph in build's §6.5"
    tail = section.split(marker, 1)[1]
    return marker + tail


def test_commitsparagraph_names_reuse_branch_for_existing_memory_task() -> None:
    """A plan written before the memory-step rule may already carry a task
    doing the memory work under another id (files = graduated probe
    copies and the docs/loom/memory/ entries) -- build must reuse that
    id and append nothing, per branch-end-02."""
    paragraph = _commits_paragraph()
    flat = " ".join(paragraph.split())
    assert "reuse" in flat.lower(), (
        "the Commits paragraph does not name the reuse-existing-id branch"
    )
    assert "graduated probe copies" in flat and "docs/loom/memory/" in flat, (
        "the reuse branch does not name its files: the graduated probe "
        "copies and the docs/loom/memory/ entries"
    )
    assert "append nothing" in flat or "appends nothing" in flat, (
        "the reuse branch does not say build appends nothing"
    )


def test_commitsparagraph_names_appendonlywhenabsent_branch() -> None:
    """Only a plan with NO such task gets `W<n>-memory` appended -- the
    paragraph must state the append path is conditional on absence, not
    unconditional."""
    paragraph = _commits_paragraph()
    flat = " ".join(paragraph.split())
    assert "no such task" in flat.lower(), (
        "the Commits paragraph does not name the no-such-task condition "
        "that gates appending W<n>-memory"
    )
    assert "W<n>-memory" in flat or "`W<n>-memory`" in paragraph, (
        "the append branch does not name the id it appends, W<n>-memory"
    )


# --- W1-03: dispatch records commit once per wave, not once per record -----

from prose_pin import NEGATION_RE as _NEGATION_RE  # shared matcher, one place to widen


def _has_negation(sentence: str) -> bool:
    """True iff `sentence` contains a word-boundary negation token — 'not',
    'never' or 'no' as whole words, or an "n't" contraction."""
    return bool(_NEGATION_RE.search(sentence))


def _flat_sentences(text: str) -> list[str]:
    """Split text into sentences after collapsing newlines to spaces, so a
    sentence that line-wraps in the SKILL.md source still reads as one
    unit here."""
    flat = " ".join(text.split())
    return [p for p in re.split(r"(?<=[.!?])\s+", flat) if p.strip()]


def _dispatch_record_section() -> str:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    start = text.index("## 3. The dispatch record")
    end = text.index("## 4.", start)
    return text[start:end]


def _perwave_commit_paragraph() -> str:
    """Return the blank-line-delimited paragraph naming the per-wave
    commit literal -- isolated by paragraph, not by sentence-split,
    because the preceding json code block and bold markdown in §3 defeat
    a `.`/`!`/`?` sentence splitter (its own unterminated fragments merge
    across paragraph boundaries and drag in an unrelated 'never')."""
    section = _dispatch_record_section()
    paragraphs = [p for p in section.split("\n\n") if p.strip()]
    hits = [p for p in paragraphs if "chore(loom): dispatch <wave>" in p]
    assert hits, "no paragraph in §3 names chore(loom): dispatch <wave>"
    return hits[0]


def test_dispatch_record_commits_once_per_wave_not_per_record() -> None:
    """PR#792's branch had 56 commits, 16 dispatch records, because
    'commit it on its own' was read as one commit per record. §3 must
    instead carry an affirmative sentence that one wave's implementer
    records are appended once and committed once, before the wave's
    first dispatch."""
    paragraph = _perwave_commit_paragraph()
    flat = " ".join(paragraph.split())
    hits = [
        s for s in _flat_sentences(flat)
        if "appended once" in s.lower()
        and "committed once" in s.lower()
        and "first dispatch" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "build/SKILL.md §3 has no affirmative sentence stating one wave's "
        "implementer records are appended once and committed once before "
        "the wave's first dispatch"
    )


def test_dispatch_record_commit_message_is_per_wave() -> None:
    """The per-task commit message `chore(loom): dispatch <task-id>` is
    replaced by a per-wave one, `chore(loom): dispatch <wave>` -- the
    gate's ordering meaning (write the record before you dispatch) is
    unchanged; only the commit *count* changes."""
    section = _dispatch_record_section()
    assert "chore(loom): dispatch <wave>" in section
    assert "chore(loom): dispatch <task-id>" not in section


def test_dispatch_record_gate_marker_intact() -> None:
    """The gate marker comment lines must survive the rewrite verbatim --
    the checker keys off them, not the prose between them."""
    section = _dispatch_record_section()
    assert "<!-- gate: build.no-dispatch-without-a-record -->" in section
    assert "<!-- /gate -->" in section


def test_matcher_perwave_sentence_negated_rejected() -> None:
    sentence = (
        "This wave's implementer records are never appended once and "
        "committed once before the wave's first dispatch."
    )
    assert _has_negation(sentence)


def test_matcher_perwave_sentence_affirmative_accepted() -> None:
    sentence = (
        "This wave's implementer records are appended once and committed "
        "once, before the wave's first dispatch, as "
        "`chore(loom): dispatch <wave>`."
    )
    assert "appended once" in sentence.lower()
    assert "committed once" in sentence.lower()
    assert "first dispatch" in sentence.lower()
    assert not _has_negation(sentence)
