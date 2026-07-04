"""Tests for loom_firing_harness's corpus layer (Task F1a).

Covers two of the harness's five documented method traps (see the
module docstring in loom_firing_harness.py for all five and which
layer enforces each):

- trap #2 (self-containedness): `validate_corpus` WARNS (never fails)
  on suspiciously short queries that read as context-less clarify-first,
  not a real trigger-miss.
- trap #3 (session/rate-limit contamination): `filter_contaminated`
  DISCARDS run-result records whose subtype signals a true run failure
  (harness_error, unknown subtypes) or whose text mentions a session
  limit, and reports how many were discarded; `error_max_turns` records
  are kept and graded normally (F3 accounting-debt fix).

Canned fixtures only — no live `claude` calls, no network.
"""

import json
import os
import stat
from pathlib import Path

import pytest

import loom_firing_harness
from loom_firing_harness import (
    CorpusError,
    MaxTurnsBelowFloorError,
    filter_contaminated,
    grade_corpus,
    grade_record,
    parse_corpus,
    run_corpus,
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

    # --- contamination filter: discard error/session-limit records,
    #     but error_max_turns is a valid signal and stays (F3 debt fix) ---
    run_results = [
        {"result_subtype": "success", "text": "Skill tool_use: brainstorming"},
        {"result_subtype": "error_max_turns", "text": "hit max turns"},
        {"result_subtype": "success", "text": "Session limit reached, try later"},
        {"result_subtype": "success", "text": "Skill tool_use: using-loom-spec"},
    ]
    kept, discarded_count = filter_contaminated(run_results)
    assert discarded_count == 1
    assert len(kept) == 3
    assert [r["result_subtype"] for r in kept] == [
        "success",
        "error_max_turns",
        "success",
    ]
    assert all("session limit" not in r["text"].lower() for r in kept)


def test_error_max_turns_grades_normally_only_true_failures_discarded():
    """F3 accounting-debt fix: a session that fires a skill and keeps
    working past the turn cap is a SUCCESS signal, not contamination —
    F3 dropped 6/28 records (all with useful fires) under the old
    filter. Discarded now: harness_error, session-limit text, and any
    unknown/absent subtype (trap #3 still guards unrecognized failure
    modes). Kept and graded: success AND error_max_turns.
    """
    run_results = [
        {"result_subtype": "success", "fired": "loom-code:brainstorming", "text": "ok"},
        {
            "result_subtype": "error_max_turns",
            "fired": "loom-code:using-loom-code",
            "text": "hit max turns after firing",
        },
        {"result_subtype": "harness_error", "fired": None, "text": "subprocess crash"},
        {"result_subtype": "success", "fired": None, "text": "Session limit reached"},
        {"result_subtype": "error_max_turns", "fired": None, "text": "session limit hit mid-run"},
        {"result_subtype": "", "fired": None, "text": ""},  # no result event
        {"result_subtype": "error_during_execution", "fired": None, "text": "boom"},
    ]
    kept, discarded_count = filter_contaminated(run_results)
    assert discarded_count == 5
    assert [r["result_subtype"] for r in kept] == ["success", "error_max_turns"]
    # the kept error_max_turns record carries its fired signal into grading
    assert kept[1]["fired"] == "loom-code:using-loom-code"


def test_grade_aggregate_surfaces_unparsed_lines(tmp_path, capsys):
    """F3 accounting-debt fix (2nd item): `unparsed_lines` reaches the
    grade aggregate — summed across ALL records (including discarded
    ones; their noise still happened) and printed by the grade CLI,
    never swallowed at the per-record layer.
    """
    counts = grade_corpus(
        [{"expected": "loom-code:brainstorming", "fired": "loom-code:brainstorming"}],
        discarded_count=1,
        unparsed_lines=5,
    )
    assert counts["unparsed_lines"] == 5

    merged = [
        {
            "expected": "loom-code:brainstorming",
            "fired": "loom-code:brainstorming",
            "result_subtype": "success",
            "text": "ok",
            "unparsed_lines": 2,
        },
        {
            "expected": "loom-code:brainstorming",
            "fired": None,
            "result_subtype": "harness_error",
            "text": "crash",
            "unparsed_lines": 3,
        },
    ]
    in_path = tmp_path / "merged.jsonl"
    in_path.write_text(
        "\n".join(json.dumps(r) for r in merged) + "\n", encoding="utf-8"
    )
    loom_firing_harness.main(["grade", "--in", str(in_path)])
    out = capsys.readouterr().out
    assert "EXACT: 1" in out
    assert "discarded: 1" in out
    assert "unparsed_lines: 5" in out  # 2 (kept) + 3 (discarded) — both surfaced


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


def _write_noisy_stub_claude(tmp_path):
    """A fake `claude` CLI that interleaves non-JSON banner/noise lines
    around the real stream-json events, mimicking verbose CLI output."""
    stub = tmp_path / "claude"
    stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "print('claude-cli v9.9.9 starting up (not json)')\n"
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
        "print('-- trailing noise, not json --')\n"
    )
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return stub


def test_run_one_tolerates_noise_lines_in_stdout(tmp_path, monkeypatch):
    """Sanctioned addition (F1c follow-up): non-JSON lines in stdout (CLI
    banners, verbose noise) must not crash parsing — they are skipped and
    counted into `unparsed_lines`, surfaced never silent, while the real
    stream-json events are still parsed correctly.
    """
    _write_noisy_stub_claude(tmp_path)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])

    record = {
        "query": "幫我做一個記帳 app，從零開始規劃功能與畫面",
        "expected": "loom-code:brainstorming",
        "notes": "tolerant parsing smoke test",
    }

    result = run_one(record, claude_bin="claude", max_turns=4)
    assert result["fired"] == "loom-code:brainstorming"
    assert result["result_subtype"] == "success"
    assert result["unparsed_lines"] == 2  # leading banner + trailing noise


def test_run_corpus_isolates_per_record_failures(monkeypatch):
    """Sanctioned addition (F1c follow-up): a record whose subprocess call
    raises must not abort the whole batch. It is captured as
    `{"result_subtype": "harness_error", "text": <error>}`, which the
    contamination filter then discards downstream (composition traced by
    the final `filter_contaminated` assertion below).
    """
    records = [
        {"query": "ok query", "expected": "loom-code:brainstorming", "notes": "n1"},
        {"query": "boom query", "expected": "loom-code:brainstorming", "notes": "n2"},
    ]

    class _FakeCompletedProcess:
        def __init__(self, stdout):
            self.stdout = stdout

    def _fake_run(argv, capture_output, text, check):
        query = argv[2]
        if query == "boom query":
            raise OSError("simulated subprocess crash")
        events = [
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Skill",
                            "input": {"skill": "loom-code:brainstorming"},
                        }
                    ]
                },
            },
            {"type": "result", "subtype": "success", "result": "ok"},
        ]
        stdout = "\n".join(json.dumps(e) for e in events) + "\n"
        return _FakeCompletedProcess(stdout)

    monkeypatch.setattr(loom_firing_harness.subprocess, "run", _fake_run)

    results = run_corpus(records, claude_bin="claude", max_turns=4)
    assert len(results) == 2
    assert results[0]["fired"] == "loom-code:brainstorming"
    assert results[0]["result_subtype"] == "success"
    assert results[1]["result_subtype"] == "harness_error"
    assert "simulated subprocess crash" in results[1]["text"]

    # composition: the contamination filter discards the harness_error
    # record downstream, never grading it as a routing miss.
    kept, discarded_count = filter_contaminated(results)
    assert discarded_count == 1
    assert kept[0]["query"] == "ok query"


def test_run_corpus_refuses_below_floor(monkeypatch):
    """`run_corpus` has its OWN batch-level max-turns floor guard (trap #1),
    distinct from `run_one`'s per-call guard: a below-floor value must fail
    the whole batch fast and loud BEFORE any subprocess is attempted — it
    must never be swallowed into per-record `harness_error` isolation.
    """

    def _forbidden_run(*args, **kwargs):
        pytest.fail("subprocess.run must never be called when max_turns is below the floor")

    monkeypatch.setattr(loom_firing_harness.subprocess, "run", _forbidden_run)

    records = [
        {"query": "any self-contained query", "expected": "loom-code:brainstorming", "notes": "n"},
    ]
    with pytest.raises(MaxTurnsBelowFloorError):
        run_corpus(records, claude_bin="claude", max_turns=3)


def test_shipped_corpus_validates():
    """F2: the three shipped firing corpora parse and validate cleanly.

    Each of goal-oriented.jsonl / near-miss.jsonl / direct-ask.jsonl must:
    parse via `parse_corpus`, have >= 8 entries, produce zero
    self-containedness warnings (trap #2 — no context-less fragments),
    and every `expected` value must be a well-formed "<plugin:skill>" id
    or the literal "NONE".
    """
    repo_root = Path(__file__).resolve().parents[2]
    corpus_dir = repo_root / "docs" / "loom" / "firing-corpus"
    for name in ("goal-oriented.jsonl", "near-miss.jsonl", "direct-ask.jsonl"):
        path = corpus_dir / name
        assert path.exists(), f"missing shipped corpus file: {path}"
        records = parse_corpus(path.read_text(encoding="utf-8"))
        assert len(records) >= 8, f"{name}: expected >= 8 entries, got {len(records)}"
        warnings = validate_corpus(records)
        assert warnings == [], f"{name}: self-containedness warnings: {warnings}"
        for record in records:
            expected = record["expected"]
            assert expected == "NONE" or ":" in expected, (
                f"{name}: malformed expected value {expected!r} "
                "(must be 'NONE' or '<plugin:skill>')"
            )
