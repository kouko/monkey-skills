"""Prose-pin test for Task 1 (2026-08-17 artifact-table-routing plan).

Plan: docs/loom/plans/2026-08-17-artifact-table-routing.md, Task 1, Pin A.

family-relay.md §(b) Visual defaults gains a new bullet, inserted
immediately after the existing "≥2 options at a fork" bullet and before
the `ascii-graph-toolkit` bullet, stating that the same fork rule binds
written artifacts (briefs/plans/specs), not just chat.

Pins (transcribed VERBATIM from the plan's §Pinned wording, Pin A):
  1. "The same fork rule binds written artifacts"
  2. "one load-bearing column stating chosen / rejected-because"
  3. "Shape-based, never count-based"

Each must appear exactly once, scoped to the text between
`### (b) Visual defaults` and `### (c)` (the section this task is
allowed to touch). The heading itself must stay unique file-wide —
session-start:81-87 extracts this section at runtime by the
`### (b)` -> `### (c)` heading range, and
loom-design/scripts/pipeline/test_family_relay.py:246,331 pins the
heading literal.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FAMILY_RELAY = REPO_ROOT / "loom-code" / "hooks" / "family-relay.md"

HEADING_B = "### (b) Visual defaults"
HEADING_C = "### (c)"

PIN_A_PHRASES = (
    "The same fork rule binds written artifacts",
    "one load-bearing column stating chosen / rejected-because",
    "Shape-based, never count-based",
)


def _text() -> str:
    assert FAMILY_RELAY.is_file(), f"family-relay.md is absent at {FAMILY_RELAY}"
    return FAMILY_RELAY.read_text(encoding="utf-8")


def _section_b_body(text: str) -> str:
    start = text.index(HEADING_B)
    end = text.index(HEADING_C, start)
    return text[start:end]


def _normalize(s: str) -> str:
    return " ".join(s.split())


def test_visual_defaults_carries_artifact_scope_bullet():
    text = _text()

    assert text.count(HEADING_B) == 1, (
        f"heading {HEADING_B!r} must be unique file-wide, "
        f"found {text.count(HEADING_B)}"
    )

    # Normalize whitespace: the markdown source hard-wraps prose, so a
    # multi-word pin phrase may straddle a line break in the raw text.
    section_body = _normalize(_section_b_body(text))

    for phrase in PIN_A_PHRASES:
        count = section_body.count(phrase)
        assert count == 1, (
            f"Pin A phrase {phrase!r} must appear exactly once inside "
            f"{HEADING_B!r}..{HEADING_C!r}, found {count}"
        )
