"""W1-02 — build / ship / write-plan / capture-intent carry the small-lane text.

Four station files gain the small-change-lane wording from
docs/loom/intent/2026-09-03-small-change-lane.md Proposed outcome 3-6:
build dispatches the adversary first for a gate-typed task, ship batches
nits into one commit before the push, and write-plan / capture-intent
ask the second-vendor question only when KICKOFF says `second-vendor: ask`.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

BUILD_SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"
SHIP_SKILL = REPO / "loom-code" / "skills" / "ship" / "SKILL.md"
WRITE_PLAN_SKILL = REPO / "loom-code" / "skills" / "write-plan" / "SKILL.md"
CAPTURE_INTENT_SKILL = REPO / "loom-design" / "skills" / "capture-intent" / "SKILL.md"
REVIEW_SKILL = REPO / "loom-code" / "skills" / "review" / "SKILL.md"


def test_build_dispatches_adversary_first_for_gate_tasks() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    assert "adversary-first" in text


def test_ship_batches_nits_before_the_push() -> None:
    text = SHIP_SKILL.read_text(encoding="utf-8")
    assert "nit batch" in text


def test_ship_nit_batch_ends_in_a_review_only_commit() -> None:
    """F1: the nit batch cannot reach push directly — a confirmation round
    plus a review-only commit must move reviewed_sha to the nit-batch
    commit before push runs, or push.review-only-head always blocks."""
    text = SHIP_SKILL.read_text(encoding="utf-8")
    section = text.split("## 3.5", 1)[1].split("## 4", 1)[0]
    assert "review-only commit" in section


def test_review_lane_paragraph_drops_artifact_types_override_claim() -> None:
    """F2: the checker never reads a KICKOFF artifact-types override —
    the Lane paragraph must not claim it exists."""
    text = REVIEW_SKILL.read_text(encoding="utf-8")
    assert "artifact-types:" not in text


def test_write_plan_second_vendor_ask() -> None:
    text = WRITE_PLAN_SKILL.read_text(encoding="utf-8")
    assert "second-vendor: ask" in text


def test_capture_intent_second_vendor_ask() -> None:
    text = CAPTURE_INTENT_SKILL.read_text(encoding="utf-8")
    assert "second-vendor: ask" in text
