"""Mechanical marker-grep pins for family-relay.md §(a2) Progress card.

2026-08-06 progress-cards-and-plan-ledger plan, Task 6: family-relay.md
gains the plan-progress variant of the rollup card (pinned text N5),
inserted immediately BEFORE `### (b) Visual defaults`. These pins
freeze:
  1. the variant heading  — "### (a2) Progress card"
  2. the four field names in their fixed order:
     Goal / task table / Stage / next (bold anchors, within §(a2))
  3. the frame contract v2 clauses (N1, 2026-08-06 roadmap plan) —
     the frame-language lead ("The relayer's frame, in the live
     conversation language:"), the stop-reason opening for `[!]` rows,
     the pipeline-station-narration ban, and the grounded-gloss clause
     (whitespace-normalized; the source wraps across lines). N1
     deleted the original one-line-frame localization sentence; its
     pin was re-pointed, not dropped.
  4. positive-fact control — the "### (a) User-rollup card" heading
     must still be present (guards against a moved/emptied file
     passing the negative shape of these greps)
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FAMILY_RELAY = REPO_ROOT / "loom-pipeline/hooks/family-relay.md"

PROGRESS_HEADING = "### (a2) Progress card"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _progress_section(text: str) -> str:
    """Return the §(a2) body: from its heading to the next ### heading."""
    start = text.find(PROGRESS_HEADING)
    assert start != -1, f"missing heading: {PROGRESS_HEADING!r}"
    rest = text[start + len(PROGRESS_HEADING):]
    end = rest.find("\n### ")
    return rest if end == -1 else rest[:end]


def test_progress_card_heading():
    text = _read(FAMILY_RELAY)
    assert PROGRESS_HEADING in text, (
        "family-relay.md must carry the §(a2) Progress card variant "
        "heading (N5)"
    )


def test_progress_card_field_names_in_order():
    """Field order is fixed: Goal, task table, Stage, next — N5 pins it."""
    section = _progress_section(_read(FAMILY_RELAY))
    fields = ["**Goal**", "**task table**", "**Stage**", "**next**"]
    indices = []
    for field in fields:
        idx = section.find(field)
        assert idx != -1, f"missing progress-card field name: {field!r}"
        indices.append(idx)
    assert indices == sorted(indices), (
        "progress-card field names must appear in the fixed order "
        "Goal / task table / Stage / next"
    )


def test_progress_card_localization_rule():
    """The relayer's frame is written in the live conversation language.
    N1 (2026-08-06 roadmap plan) deleted the sentence this pin froze
    ("the relayer adds only a one-line conversational frame ... same
    localized-content rule") — the pin is re-pointed at N1's
    replacement clause. Whitespace-normalized because the sentence
    wraps across source lines."""
    normalized = _normalized(_progress_section(_read(FAMILY_RELAY)))
    assert (
        "The relayer's frame, in the live conversation language:"
        in normalized
    ), "missing the §(a2) frame-language clause (frame contract v2, N1)"


def test_progress_card_stop_reason_opening():
    """Every `[!]` row's explanation OPENS with the stop reason —
    needs your decision / waiting on an external condition (N1)."""
    normalized = _normalized(_progress_section(_read(FAMILY_RELAY)))
    assert "OPENS with the stop reason" in normalized, (
        "missing the §(a2) stop-reason opening requirement for [!] rows"
    )
    assert '"needs your decision: …"' in normalized, (
        "missing the needs-your-decision stop-reason form"
    )
    assert '"waiting on an external condition: …"' in normalized, (
        "missing the external-condition stop-reason form"
    )


def test_progress_card_station_narration_ban():
    """Pipeline-station narration (waves, reviewer arms, verdicts)
    stays out of the frame unless a pending decision needs it (N1)."""
    normalized = _normalized(_progress_section(_read(FAMILY_RELAY)))
    assert (
        "Pipeline-station narration (waves, reviewer arms, verdicts) "
        "stays out of the frame" in normalized
    ), "missing the §(a2) pipeline-station-narration ban"


def test_progress_card_grounded_gloss():
    """The `next:` gloss is derived from that task's own plan fields —
    cite the source item, never invent (N1)."""
    normalized = _normalized(_progress_section(_read(FAMILY_RELAY)))
    assert "cite the source item, never invent" in normalized, (
        "missing the §(a2) grounded-gloss clause for next:"
    )


def test_control_user_rollup_heading_still_present():
    """Positive-fact control: §(a) User-rollup card heading unchanged."""
    text = _read(FAMILY_RELAY)
    assert "### (a) User-rollup card" in text
