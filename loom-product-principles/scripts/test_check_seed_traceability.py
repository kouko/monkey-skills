"""Tests for check_seed_traceability.py's oracle parser (Task 1) — the
parser that DEFINES the oracle format contract for the Level-2 mechanical
traceability gate (brief §Level 2,
docs/loom/specs/2026-07-10-principles-replay-loop.md).

Synthetic content only. Fixtures built INLINE (flat-folder rule: no
fixtures/ subdir, no conftest.py — same convention as
test_validate_principles_output.py).
"""

import pytest

from check_seed_traceability import parse_oracle


def test_parse_oracle_extracts_three_token_lists():
    text = (
        "named_anchors: HEART; MoSCoW; Nielsen's 10 Usability Heuristics\n"
        "deferred_items: upgrade appetite unclear (single deferred item)\n"
        "negative: \"forced login\" as accepted behavior\n"
    )
    result = parse_oracle(text)
    assert result == {
        "named_anchors": ["HEART", "MoSCoW", "Nielsen's 10 Usability Heuristics"],
        "deferred_items": ["upgrade appetite unclear (single deferred item)"],
        "negative": ['"forced login" as accepted behavior'],
    }


def test_none_in_this_seed_sentinel_parses_to_empty_list():
    # Sentinel may carry trailing parenthetical commentary (seed1-oracle.md
    # shape: "none in this seed (2-deferred trap lives in seed 2)").
    text = (
        "named_anchors: HEART\n"
        "deferred_items: none in this seed (2-deferred trap lives in seed 2)\n"
        "negative: none in this seed\n"
    )
    result = parse_oracle(text)
    assert result["deferred_items"] == []
    assert result["negative"] == []


def test_absent_key_parses_to_empty_list():
    text = "named_anchors: HEART; MoSCoW\n"
    result = parse_oracle(text)
    assert result["deferred_items"] == []
    assert result["negative"] == []


def test_ignores_stances_and_out_of_jurisdiction_bait_keys():
    # Out of checker scope by design (brief §Level 2) — must not leak into
    # the returned dict, and must not be mistaken for one of the three keys.
    text = (
        "named_anchors: HEART\n"
        "out_of_jurisdiction_bait: some timeline text; another bait\n"
        "stances: task=x; user=y\n"
    )
    result = parse_oracle(text)
    assert set(result.keys()) == {"named_anchors", "deferred_items", "negative"}
    assert result["named_anchors"] == ["HEART"]


def test_missing_all_three_keys_raises_value_error_naming_them():
    text = "stances: task=x\nout_of_jurisdiction_bait: y\n"
    with pytest.raises(ValueError) as exc_info:
        parse_oracle(text)
    message = str(exc_info.value)
    assert "named_anchors" in message
    assert "deferred_items" in message
    assert "negative" in message


def test_multi_token_values_are_stripped_of_surrounding_whitespace():
    text = "named_anchors:   HEART ;  MoSCoW  ;IBM Carbon\n"
    result = parse_oracle(text)
    assert result["named_anchors"] == ["HEART", "MoSCoW", "IBM Carbon"]
