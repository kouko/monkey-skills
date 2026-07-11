import re
from pathlib import Path

from backlog_parser import BacklogItem, parse_next_backlog_item

CAMPAIGN_DOC = (
    Path(__file__).resolve().parents[2] / "docs" / "dbt-wiki-quality-campaign.md"
)

# Phase 2 fully checked, but Phase 1 has an unchecked W2 and Phase 3 an
# unchecked G1 — the parser must stay scoped to Phase 2 and return None.
ALL_CHECKED_FIXTURE = """# campaign

## Phase 1 — loop enablers

- [x] **W1: harness** — done
- [ ] **W2: cross-doc consistency lint** — still open

## Phase 2 — backlog burn-down

High:
- [x] B1: first item done
  (a continuation clause that must not confuse the scan)
- [x] B2: second done
Medium:
- [x] B5: medium done
Low (next-touch, from PR reviews): some prose line, not a checkbox item.

## Phase 3 — generalization sweep

- [ ] G1: not a Phase 2 item
"""

# Mirrors the real campaign doc's B1 shape (a multi-line description with a
# continuation clause) WITHOUT depending on its live, mutable text -- B1 is a
# burn-down checklist item and will get checked off in normal operation, at
# which point a live-doc assertion on "B1"/its exact wording would break for
# a reason unrelated to the parser.
MULTILINE_ITEM_FIXTURE = """# campaign

## Phase 2 — backlog burn-down

High:
- [ ] B1: rescan ~450 lines inline pseudocode -> shipped TDD'd scripts
  (includes real list | set TypeError at old :203/:540)

## Phase 3 — generalization sweep
"""

# B1-B3 checked, B4 first unchecked (with a continuation line); B5 also
# unchecked but later; Phase 1 W2 unchecked. Correct answer is B4.
SCOPING_FIXTURE = """# campaign

## Phase 1 — loop enablers

- [ ] **W2: cross-doc consistency lint** — still open

## Phase 2 — backlog burn-down

High:
- [x] B1: done one
- [x] B2: done two
- [x] B3: done three
- [ ] B4: first still-open backlog item
  with a continuation clause folded in
Medium:
- [ ] B5: also open but later in the queue

## Phase 3 — generalization sweep
"""


def test_parses_first_unchecked_phase2_item():
    item = parse_next_backlog_item(MULTILINE_ITEM_FIXTURE)
    assert isinstance(item, BacklogItem)
    assert item.id == "B1"
    assert item.description.startswith("rescan ~450 lines inline pseudocode")


def test_multiline_description_is_folded_into_one():
    item = parse_next_backlog_item(MULTILINE_ITEM_FIXTURE)
    assert item is not None
    # The description spans two lines in the fixture; the continuation
    # (which mentions a TypeError) must be folded into the description.
    assert "TypeError" in item.description


def test_parser_returns_current_first_unchecked_item_from_real_doc():
    # Live-format canary: exercises the actual committed doc's current shape
    # without pinning to specific wording that this same doc's burn-down
    # workflow is expected to change over time (see MULTILINE_ITEM_FIXTURE
    # above for the wording-stable equivalent of this test).
    text = CAMPAIGN_DOC.read_text(encoding="utf-8")
    item = parse_next_backlog_item(text)
    assert item is None or isinstance(item, BacklogItem)
    if item is not None:
        assert re.match(r"^B\d+$", item.id)
        assert item.description.strip()


def test_returns_none_when_all_phase2_items_checked():
    assert parse_next_backlog_item(ALL_CHECKED_FIXTURE) is None


def test_unchecked_item_outside_phase2_is_ignored():
    # Both an unchecked Phase 1 (W2) and Phase 3 (G1) item exist, but every
    # Phase 2 item is checked — the parser must return None, not W2 or G1.
    assert parse_next_backlog_item(ALL_CHECKED_FIXTURE) is None


def test_skips_checked_items_and_respects_document_order():
    item = parse_next_backlog_item(SCOPING_FIXTURE)
    assert item is not None
    assert item.id == "B4"  # not W2 (Phase 1), not B5 (later)
    assert item.description == (
        "first still-open backlog item with a continuation clause folded in"
    )


def test_low_prose_line_is_not_parsed_as_an_item():
    # The "Low (next-touch...)" line inside Phase 2 is prose, not a checkbox;
    # it must never surface as a backlog item.
    item = parse_next_backlog_item(ALL_CHECKED_FIXTURE)
    assert item is None
