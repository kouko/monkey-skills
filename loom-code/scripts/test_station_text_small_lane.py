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


def test_build_dispatches_adversary_first_for_gate_tasks() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    assert "adversary-first" in text


def test_ship_batches_nits_before_the_push() -> None:
    text = SHIP_SKILL.read_text(encoding="utf-8")
    assert "nit batch" in text


def test_write_plan_second_vendor_ask() -> None:
    text = WRITE_PLAN_SKILL.read_text(encoding="utf-8")
    assert "second-vendor: ask" in text


def test_capture_intent_second_vendor_ask() -> None:
    text = CAPTURE_INTENT_SKILL.read_text(encoding="utf-8")
    assert "second-vendor: ask" in text
