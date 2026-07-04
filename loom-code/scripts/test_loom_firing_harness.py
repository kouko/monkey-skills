"""Tests for loom_firing_harness's corpus layer (Task F1a).

Covers two of the harness's five documented method traps (see the
module docstring in loom_firing_harness.py for all five and which
layer enforces each):

- trap #2 (self-containedness): `validate_corpus` WARNS (never fails)
  on suspiciously short queries that read as context-less clarify-first,
  not a real trigger-miss.
- trap #3 (session/rate-limit contamination): `filter_contaminated`
  DISCARDS run-result records whose subtype signals an error or whose
  text mentions a session limit, and reports how many were discarded.

Canned fixtures only — no live `claude` calls, no network.
"""

import pytest

from loom_firing_harness import (
    CorpusError,
    filter_contaminated,
    parse_corpus,
    validate_corpus,
)


def test_corpus_parse_and_contamination_discard():
    # --- corpus parsing: one JSON record per line ---
    raw = (
        '{"query": "幫我做一個記帳 app，從零開始規劃功能與畫面", '
        '"expected": "loom-product-principles:product-principles", '
        '"notes": "goal-oriented, product-shaped"}\n'
        '{"query": "make an app", '
        '"expected": "NONE", "notes": "control, too short to be self-contained"}\n'
    )
    records = parse_corpus(raw)
    assert len(records) == 2
    assert records[0]["query"].startswith("幫我做一個記帳")
    assert records[0]["expected"] == "loom-product-principles:product-principles"
    assert records[1]["expected"] == "NONE"

    # --- self-containedness validator: warns, never fails, on short queries ---
    warnings = validate_corpus(records)
    assert len(warnings) == 1
    assert "make an app" in warnings[0]

    # --- malformed line fails loud with a named exception ---
    with pytest.raises(CorpusError):
        parse_corpus('{"query": "missing expected field"}\n')

    with pytest.raises(CorpusError):
        parse_corpus("not even json\n")

    # --- contamination filter: discard error/session-limit records ---
    run_results = [
        {"result_subtype": "success", "text": "Skill tool_use: brainstorming"},
        {"result_subtype": "error_max_turns", "text": "hit max turns"},
        {"result_subtype": "success", "text": "Session limit reached, try later"},
        {"result_subtype": "success", "text": "Skill tool_use: using-loom-spec"},
    ]
    kept, discarded_count = filter_contaminated(run_results)
    assert discarded_count == 2
    assert len(kept) == 2
    assert all(r["result_subtype"] == "success" for r in kept)
    assert all("session limit" not in r["text"].lower() for r in kept)
