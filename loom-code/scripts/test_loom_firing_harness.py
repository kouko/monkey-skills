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

import os
import stat

import pytest

from loom_firing_harness import (
    CorpusError,
    MaxTurnsBelowFloorError,
    filter_contaminated,
    grade_corpus,
    grade_record,
    parse_corpus,
    run_one,
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


def test_grade_exact_family_miss_over():
    """Trap #4: EXACT vs FAMILY counted separately; expected=NONE only
    penalizes a loom-family fire, never a correct non-loom routing.

    Each record here is a merged corpus+run record: `expected` (from the
    corpus) plus `fired` (the skill id the run captured, or None if
    nothing fired). `family` = the plugin prefix before ':'.
    """
    # --- exact hit ---
    exact = {"expected": "loom-code:brainstorming", "fired": "loom-code:brainstorming"}
    assert grade_record(exact) == "EXACT"

    # --- sibling-family hit: same plugin prefix, different skill ---
    family = {
        "expected": "loom-spec:completeness-critic",
        "fired": "loom-spec:spec-expansion",
    }
    assert grade_record(family) == "FAMILY"

    # --- miss: expected a skill, nothing fired ---
    miss_nothing = {"expected": "loom-product-principles:product-principles", "fired": None}
    assert grade_record(miss_nothing) == "MISS"

    # --- miss: expected a skill, a non-loom skill fired instead ---
    miss_non_loom = {"expected": "loom-interface-design:design-system", "fired": "dataviz"}
    assert grade_record(miss_non_loom) == "MISS"

    # --- over-trigger: expected NONE, a loom-family skill fired anyway ---
    over = {"expected": "NONE", "fired": "loom-code:brainstorming"}
    assert grade_record(over) == "OVER"

    # --- NOT an over-trigger: expected NONE, a non-loom skill fired ---
    # (correct non-loom routing — the trap #4 grader rule)
    not_over = {"expected": "NONE", "fired": "dataviz"}
    assert grade_record(not_over) != "OVER"

    # --- NOT an over-trigger: expected NONE, nothing fired at all ---
    none_and_nothing = {"expected": "NONE", "fired": None}
    assert grade_record(none_and_nothing) != "OVER"

    # --- per-corpus aggregate: counts per verdict class + discarded passthrough ---
    counts = grade_corpus(
        [exact, family, miss_nothing, miss_non_loom, over, not_over, none_and_nothing],
        discarded_count=3,
    )
    assert counts["EXACT"] == 3  # exact + not_over + none_and_nothing
    assert counts["FAMILY"] == 1
    assert counts["MISS"] == 2
    assert counts["OVER"] == 1
    assert counts["discarded"] == 3


def _write_stub_claude(tmp_path):
    """A fake `claude` CLI on PATH: prints canned stream-json, no network."""
    stub = tmp_path / "claude"
    stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "events = [\n"
        '    {"type": "system", "subtype": "init"},\n'
        '    {"type": "assistant", "message": {"content": [\n'
        '        {"type": "tool_use", "name": "Skill",\n'
        '         "input": {"skill": "loom-code:brainstorming"}}\n'
        "    ]}},\n"
        '    {"type": "result", "subtype": "success",\n'
        '     "result": "Routed to brainstorming."},\n'
        "]\n"
        "for e in events:\n"
        "    print(json.dumps(e))\n"
    )
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return stub


def test_run_mode_captures_fired_skill(tmp_path, monkeypatch):
    """`run_one` shells to a stub `claude -p` and captures fired skill +
    subtype (Task F1c); trap #1's max-turns floor is enforced and named.
    """
    _write_stub_claude(tmp_path)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])

    record = {
        "query": "幫我做一個記帳 app，從零開始規劃功能與畫面",
        "expected": "loom-code:brainstorming",
        "notes": "smoke test for run mode",
    }

    result = run_one(record, claude_bin="claude", max_turns=4)
    assert result["fired"] == "loom-code:brainstorming"
    assert result["result_subtype"] == "success"
    assert "brainstorming" in result["text"]
    # corpus fields pass through untouched
    assert result["expected"] == "loom-code:brainstorming"
    assert result["query"] == record["query"]

    # trap #1: max-turns below the floor of 4 is refused with a named error
    with pytest.raises(MaxTurnsBelowFloorError):
        run_one(record, claude_bin="claude", max_turns=3)
