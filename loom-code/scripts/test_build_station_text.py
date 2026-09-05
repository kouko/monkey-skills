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


def _package_tests_before_memory_before_review(paragraph: str) -> bool:
    """True iff, in order, a package-tests reference (§6) precedes a
    memory-step reference (§6.5) precedes the review-station call --
    the sequencing wave-end:1-01 fixed. `rindex` on the review call
    picks the call itself, not the earlier "do not call ... here"
    sentence that may also name it."""
    flat = " ".join(paragraph.split())
    try:
        i_pkg = flat.index("§6 (package tests)")
        i_mem = flat.index("§6.5 (the memory step)")
        i_review = flat.rindex("loom-code:review")
    except ValueError:
        return False
    return i_pkg < i_mem < i_review


def test_lastwaveparagraph_orders_packagetests_then_memorystep_then_reviewcall() -> None:
    paragraph = _last_wave_paragraph()
    assert _package_tests_before_memory_before_review(paragraph), (
        "build's §5 last-wave paragraph does not order §6 before §6.5 "
        "before the review-station call"
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
