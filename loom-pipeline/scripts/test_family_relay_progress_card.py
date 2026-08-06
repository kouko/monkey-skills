"""Mechanical marker-grep pins for family-relay.md §(a2) Progress card.

2026-08-06 progress-cards-and-plan-ledger plan, Task 6: family-relay.md
gains the plan-progress variant of the rollup card (pinned text N5),
inserted immediately BEFORE `### (b) Visual defaults`. These pins
freeze:
  1. the variant heading  — "### (a2) Progress card"
  2. the four field names in their fixed order:
     Goal / task table / Stage / next (bold anchors, within §(a2))
  3. the localization rule sentence — the relayer adds only a one-line
     conversational frame in the live conversation language, same
     localized-content rule as the rollup card (whitespace-normalized;
     the source wraps across lines)
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
    """The relayer frames in the live conversation language — same
    localized-content rule as the rollup card. Whitespace-normalized
    because the sentence wraps across source lines."""
    normalized = _normalized(_progress_section(_read(FAMILY_RELAY)))
    assert (
        "the relayer adds only a one-line conversational frame in the "
        "live conversation language, same localized-content rule as "
        "the rollup card above" in normalized
    ), "missing the §(a2) localization rule sentence"


def test_control_user_rollup_heading_still_present():
    """Positive-fact control: §(a) User-rollup card heading unchanged."""
    text = _read(FAMILY_RELAY)
    assert "### (a) User-rollup card" in text
