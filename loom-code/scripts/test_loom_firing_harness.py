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
from functools import lru_cache
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


@lru_cache(maxsize=None)
def _installed_skill_ids(repo_root):
    """Every `<plugin>:<skill>` id the repo actually ships.

    Read from the plugin manifests + skill dirs on disk, so the corpus
    guard below cannot drift the way a hand-maintained list would.
    Cached: the corpus guard calls this once per record.
    """
    ids = set()
    for manifest in repo_root.glob("*/.claude-plugin/plugin.json"):
        plugin = json.loads(manifest.read_text(encoding="utf-8"))["name"]
        skills_dir = manifest.parent.parent / "skills"
        if not skills_dir.is_dir():
            continue
        for skill in skills_dir.iterdir():
            if (skill / "SKILL.md").is_file():
                ids.add(f"{plugin}:{skill.name}")
    return frozenset(ids)


def test_corpus_parse_and_contamination_discard():
    # --- corpus parsing: one JSON record per line ---
    raw = (
        '{"query": "幫我做一個記帳 app，從零開始規劃功能與畫面", '
        '"expected": "loom-design:product-principles", '
        '"notes": "goal-oriented, product-shaped"}\n'
        '{"query": "make an app", '
        '"expected": "NONE", "notes": "control, too short to be self-contained"}\n'
    )
    records = parse_corpus(raw)
    assert len(records) == 2
    assert records[0]["query"].startswith("幫我做一個記帳")
    assert records[0]["expected"] == "loom-design:product-principles"
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
        {"result_subtype": "success", "text": "Skill tool_use: using-loom-design"},
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
        "expected": "loom-design:completeness-critic",
        "fired": "loom-design:spec-expansion",
    }
    assert grade_record(family) == "FAMILY"

    # --- miss: expected a skill, nothing fired ---
    miss_nothing = {"expected": "loom-design:product-principles", "fired": None}
    assert grade_record(miss_nothing) == "MISS"

    # --- miss: expected a skill, a non-loom skill fired instead ---
    miss_non_loom = {"expected": "loom-design:design-system", "fired": "dataviz"}
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


def test_compare_hosts_normalizes_baseline_candidate_replicates(tmp_path, monkeypatch, capsys):
    """Both hosts retain raw evidence, but compare only observables.

    One changed replicate is not enough to claim a regression.  The same
    baseline/candidate observable difference must recur in at least two
    replicates before the comparison has a divergence verdict.
    """
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    raw_dir = tmp_path / "raw"
    baseline.mkdir()
    candidate.mkdir()
    for root in (baseline, candidate):
        (root / ".codex-plugin").mkdir()
        (root / ".codex-plugin" / "plugin.json").write_text(
            '{"name": "loom-code"}\n', encoding="utf-8"
        )

    invocations = []

    def runner(invocation):
        invocations.append(invocation)
        changed = (
            invocation.root_label == "candidate"
            and invocation.record["query"] == "diverge"
            and (invocation.replicate == 0 or invocation.record.get("repeat"))
        )
        fired = "loom-code:other" if changed else "loom-code:brainstorming"
        if invocation.host == "claude":
            return "\n".join((
                json.dumps({"type": "assistant", "message": {"content": [{
                    "type": "tool_use", "name": "Skill",
                    "input": {"skill": fired},
                }]} }),
                json.dumps({"type": "result", "subtype": "success", "result": "wording varies"}),
            ))
        return "\n".join((
            json.dumps({"type": "item.completed", "item": {
                "type": "command_execution", "command": "skill " + fired,
            }}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 3}}),
        ))

    records = [{"query": "diverge", "expected": "loom-code:brainstorming", "notes": "n"}]
    inconclusive = loom_firing_harness.compare_hosts(
        records, baseline, candidate, replicates=2, raw_dir=raw_dir, runner=runner
    )
    assert {item["host"] for item in inconclusive["runs"]} == {"claude", "codex"}
    assert all(Path(item["raw_transcript_path"]).is_file() for item in inconclusive["runs"])
    assert {item["plugin_root"] for item in inconclusive["runs"]} == {str(baseline), str(candidate)}
    assert all("text" not in item["observable"] for item in inconclusive["runs"])
    assert {item["verdict"] for item in inconclusive["comparisons"]} == {"INCONCLUSIVE"}
    codex_invocations = [item for item in invocations if item.host == "codex"]
    assert {item.codex_home for item in codex_invocations} == {
        raw_dir / "codex-home-baseline", raw_dir / "codex-home-candidate",
    }
    assert all(item.environment["CODEX_HOME"] == str(item.codex_home) for item in codex_invocations)

    commands = []

    class Completed:
        returncode = 0
        stdout = "{}\n"
        stderr = ""

    def fake_subprocess(argv, *, env, **_kwargs):
        commands.append((tuple(argv), env["CODEX_HOME"]))
        return Completed()

    monkeypatch.setattr(loom_firing_harness.subprocess, "run", fake_subprocess)
    loom_firing_harness.run_host(codex_invocations[0])
    baseline_home = raw_dir / "codex-home-baseline"
    assert commands == [
        (
            ("codex", "plugin", "marketplace", "add", str(baseline_home / "marketplace")),
            str(baseline_home),
        ),
        (
            ("codex", "plugin", "add", "loom-code@loom-harness-baseline"),
            str(baseline_home),
        ),
        (codex_invocations[0].argv, str(baseline_home)),
    ]
    assert (baseline_home / "marketplace" / "loom-code" / ".codex-plugin" / "plugin.json").is_file()

    compared = loom_firing_harness.compare_hosts(
        [{**records[0], "repeat": True}], baseline, candidate,
        replicates=3, raw_dir=raw_dir, runner=runner
    )
    assert {item["verdict"] for item in compared["comparisons"]} == {"REGRESSION"}

    claude_argv = loom_firing_harness.host_argv_for_root(
        "claude", baseline, records[0], max_turns=4, working_directory=tmp_path
    )
    codex_argv = loom_firing_harness.host_argv_for_root(
        "codex", candidate, records[0], max_turns=4, working_directory=tmp_path
    )
    assert "--plugin-dir" in claude_argv and str(baseline) in claude_argv
    assert codex_argv[:2] == ("codex", "exec")
    assert "--plugin-dir" not in codex_argv

    corpus = tmp_path / "corpus.jsonl"
    comparison_out = tmp_path / "comparison.json"
    corpus.write_text(json.dumps(records[0]) + "\n", encoding="utf-8")
    monkeypatch.setattr(loom_firing_harness, "run_host", runner)
    loom_firing_harness.main([
        "compare", "--corpus", str(corpus), "--baseline", str(baseline),
        "--candidate", str(candidate), "--raw-dir", str(raw_dir),
        "--out", str(comparison_out),
    ])
    stdout = capsys.readouterr().out
    assert '"verdict": "INCONCLUSIVE"' in stdout
    assert json.loads(comparison_out.read_text(encoding="utf-8"))["comparisons"]


def test_compare_hosts_passes_explicit_economy_models_to_each_host(tmp_path):
    """The two CLIs must receive their own explicitly pinned economy model."""
    record = {"query": "exercise the skill", "expected": "NONE", "notes": "model pin"}

    claude_argv = loom_firing_harness.host_argv_for_root(
        "claude", tmp_path, record, max_turns=4, working_directory=tmp_path,
        claude_model="haiku", codex_model="gpt-5.6-luna",
    )
    codex_argv = loom_firing_harness.host_argv_for_root(
        "codex", tmp_path, record, max_turns=4, working_directory=tmp_path,
        claude_model="haiku", codex_model="gpt-5.6-luna",
    )

    assert claude_argv[claude_argv.index("--model") + 1] == "haiku"
    assert codex_argv[codex_argv.index("--model") + 1] == "gpt-5.6-luna"


def test_run_host_rejects_nonzero_exit(monkeypatch, tmp_path):
    """Authentication and host failures must never normalize into PASS."""
    invocation = loom_firing_harness.HostInvocation(
        host="claude",
        root_label="baseline",
        plugin_root=tmp_path,
        record={"query": "probe", "expected": "NONE", "notes": "failure"},
        replicate=0,
        argv=("claude", "-p", "probe"),
        codex_home=None,
        environment={},
    )

    class Failed:
        returncode = 1
        stdout = '{"type":"error","message":"unauthorized"}\n'
        stderr = "credential detail must not leak"

    monkeypatch.setattr(loom_firing_harness.subprocess, "run", lambda *a, **k: Failed())

    with pytest.raises(RuntimeError, match="claude host exited with status 1"):
        loom_firing_harness.run_host(invocation)


def _codex_invocation(plugin_root, codex_home):
    return loom_firing_harness.HostInvocation(
        host="codex", root_label="baseline", plugin_root=plugin_root,
        record={"query": "probe", "expected": "NONE", "notes": "isolation"},
        replicate=0, argv=("codex", "exec", "probe"), codex_home=codex_home,
        environment={"CODEX_HOME": str(codex_home)},
    )


def test_prepare_codex_root_rejects_manifest_name_path_traversal(tmp_path):
    plugin_root = tmp_path / "plugin"
    (plugin_root / ".codex-plugin").mkdir(parents=True)
    (plugin_root / ".codex-plugin" / "plugin.json").write_text(
        '{"name": "../escaped"}\n', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="invalid identifier"):
        loom_firing_harness._prepare_codex_root(
            _codex_invocation(plugin_root, tmp_path / "home"), {}
        )
    assert not (tmp_path / "home" / "escaped").exists()


def test_prepare_codex_root_rejects_symlinked_home_without_deleting_target(
    tmp_path, monkeypatch
):
    plugin_root = tmp_path / "plugin"
    (plugin_root / ".codex-plugin").mkdir(parents=True)
    (plugin_root / ".codex-plugin" / "plugin.json").write_text(
        '{"name": "loom-code"}\n', encoding="utf-8"
    )
    outside = tmp_path / "outside"
    (outside / "marketplace").mkdir(parents=True)
    sentinel = outside / "marketplace" / "sentinel"
    sentinel.write_text("keep", encoding="utf-8")
    home = tmp_path / "home"
    home.symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="symlink"):
        loom_firing_harness._prepare_codex_root(
            _codex_invocation(plugin_root, home), {}
        )
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_prepare_codex_root_rejects_symlinked_home_ancestor_without_deleting_target(
    tmp_path,
):
    plugin_root = tmp_path / "plugin"
    (plugin_root / ".codex-plugin").mkdir(parents=True)
    (plugin_root / ".codex-plugin" / "plugin.json").write_text(
        '{"name": "loom-code"}\n', encoding="utf-8"
    )
    outside = tmp_path / "outside"
    (outside / "home" / "marketplace").mkdir(parents=True)
    sentinel = outside / "home" / "marketplace" / "sentinel"
    sentinel.write_text("keep", encoding="utf-8")
    alias = tmp_path / "alias"
    alias.symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="alias|symlink"):
        loom_firing_harness._prepare_codex_root(
            _codex_invocation(plugin_root, alias / "home"), {}
        )
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_prepare_codex_root_rejects_symlinked_marker_without_overwriting_target(
    tmp_path,
):
    plugin_root = tmp_path / "plugin"
    (plugin_root / ".codex-plugin").mkdir(parents=True)
    (plugin_root / ".codex-plugin" / "plugin.json").write_text(
        '{"name": "loom-code"}\n', encoding="utf-8"
    )
    home = tmp_path / "home"
    home.mkdir()
    sentinel = tmp_path / "sentinel"
    sentinel.write_text("KEEP", encoding="utf-8")
    (home / ".loom-harness-prepared").symlink_to(sentinel)

    with pytest.raises(ValueError, match="marker.*symlink"):
        loom_firing_harness._prepare_codex_root(
            _codex_invocation(plugin_root, home), {}
        )
    assert sentinel.read_text(encoding="utf-8") == "KEEP"


def test_prepare_codex_root_refreshes_changed_plugin_bytes(tmp_path, monkeypatch):
    roots = []
    for label in ("old", "new"):
        root = tmp_path / label
        (root / ".codex-plugin").mkdir(parents=True)
        (root / ".codex-plugin" / "plugin.json").write_text(
            '{"name": "loom-code"}\n', encoding="utf-8"
        )
        (root / "identity").write_text(label, encoding="utf-8")
        roots.append(root)

    class Completed:
        returncode = 0

    monkeypatch.setattr(
        loom_firing_harness.subprocess, "run", lambda *args, **kwargs: Completed()
    )
    home = tmp_path / "home"
    for root in roots:
        loom_firing_harness._prepare_codex_root(_codex_invocation(root, home), {})

    assert (home / "marketplace" / "loom-code" / "identity").read_text() == "new"
    installed = home / "marketplace" / "loom-code" / "identity"
    installed.write_text("tampered", encoding="utf-8")
    loom_firing_harness._prepare_codex_root(_codex_invocation(roots[-1], home), {})
    assert installed.read_text(encoding="utf-8") == "new"


def test_plugin_tree_fingerprint_frames_file_boundaries(tmp_path):
    first = tmp_path / "first"; first.mkdir()
    second = tmp_path / "second"; second.mkdir()
    (first / "a").write_bytes(b"XF\0b\0Y")
    (second / "a").write_bytes(b"X")
    (second / "b").write_bytes(b"Y")

    assert (
        loom_firing_harness._plugin_tree_fingerprint(first)
        != loom_firing_harness._plugin_tree_fingerprint(second)
    )


def test_plugin_tree_fingerprint_includes_executable_mode(tmp_path):
    root = tmp_path / "plugin"; root.mkdir()
    executable = root / "hook"
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    before = loom_firing_harness._plugin_tree_fingerprint(root)
    executable.chmod(executable.stat().st_mode | 0o100)
    assert loom_firing_harness._plugin_tree_fingerprint(root) != before


def test_compare_hosts_empty_transcripts_are_inconclusive(tmp_path):
    result = loom_firing_harness.compare_hosts(
        [{"query": "same", "expected": "NONE", "notes": "empty"}],
        tmp_path / "baseline", tmp_path / "candidate", replicates=2,
        raw_dir=tmp_path / "raw", runner=lambda invocation: "",
    )
    assert {item["verdict"] for item in result["comparisons"]} == {"INCONCLUSIVE"}


def test_compare_hosts_pairs_duplicate_queries_by_record_index(tmp_path):
    records = [
        {"query": "same", "expected": "loom-code:brainstorming", "notes": "first"},
        {"query": "same", "expected": "loom-code:brainstorming", "notes": "second"},
    ]

    def runner(invocation):
        fired = "loom-code:brainstorming"
        if invocation.root_label == "candidate" and invocation.record["notes"] == "second":
            fired = "loom-code:other"
        if invocation.host == "claude":
            return "\n".join((
                json.dumps({"type": "assistant", "message": {"content": [{
                    "type": "tool_use", "name": "Skill", "input": {"skill": fired},
                }]}}),
                json.dumps({"type": "result", "subtype": "success", "result": "ok"}),
            ))
        return "\n".join((
            json.dumps({"type": "item.completed", "item": {
                "type": "command_execution", "command": f"skill {fired}",
            }}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}),
        ))

    result = loom_firing_harness.compare_hosts(
        records, tmp_path / "baseline", tmp_path / "candidate", replicates=2,
        raw_dir=tmp_path / "raw", runner=runner,
    )
    verdicts = {(item["record_index"], item["host"]): item["verdict"] for item in result["comparisons"]}
    assert verdicts[(0, "claude")] == "PASS"
    assert verdicts[(0, "codex")] == "PASS"
    assert verdicts[(1, "claude")] == "REGRESSION"
    assert verdicts[(1, "codex")] == "REGRESSION"


def test_codex_root_invocation_loads_isolated_plugin_config(tmp_path):
    """CODEX_HOME is isolated already; ignoring its config hides the plugin."""
    argv = loom_firing_harness.host_argv_for_root(
        "codex", tmp_path,
        {"query": "probe", "expected": "NONE", "notes": "plugin load"},
        max_turns=4, working_directory=tmp_path,
    )

    assert "--ignore-user-config" not in argv


def test_codex_observable_detects_loaded_plugin_skill_path():
    transcript = json.dumps({
        "type": "item.completed",
        "item": {
            "type": "command_execution",
            "command": "sed -n 1,240p /tmp/cache/loom/loom-workflow/1.0.0/skills/distill-sessions/SKILL.md",
        },
    })

    observable = loom_firing_harness._normalize_observable("codex", transcript)

    assert observable["fired"] == "loom-workflow:distill-sessions"


def test_comparison_verdict_reports_tokens_without_treating_cost_as_behavior_change():
    baseline = {
        "expected": "loom-code:brainstorming",
        "observable": {
            "fired": "loom-code:brainstorming", "result_subtype": "completed",
            "tool_sequence": ("Skill",), "tokens": {"input_tokens": 100},
        },
    }
    candidate = {
        "expected": "loom-code:brainstorming",
        "observable": {
            "fired": "loom-code:brainstorming", "result_subtype": "completed",
            "tool_sequence": ("Skill",), "tokens": {"input_tokens": 60},
        },
    }

    assert loom_firing_harness._comparison_verdict(
        [(baseline, candidate), (baseline, candidate)]
    ) == "PASS"


def test_comparison_verdict_refuses_conflicting_difference_groups():
    def run(fired):
        return {
            "expected": "loom-code:brainstorming",
            "observable": {
                "fired": fired, "result_subtype": "completed", "tool_sequence": (),
            },
        }

    exact = run("loom-code:brainstorming")
    miss = run(None)
    over = run("loom-code:other")
    assert loom_firing_harness._comparison_verdict(
        [(exact, miss), (exact, miss), (miss, exact), (miss, exact)]
    ) == "INCONCLUSIVE"
    assert loom_firing_harness._comparison_verdict(
        [(exact, miss), (exact, miss), (exact, over)]
    ) == "INCONCLUSIVE"


def test_shipped_corpus_validates():
    """F2: EVERY shipped firing corpus parses and validates cleanly.

    The file list is ENUMERATED from the corpus directory, never hard-coded:
    a hard-coded tuple silently under-covers when a corpus is added, and
    reads as complete while doing so. research-asks.jsonl was validated by
    nothing for exactly that reason — a bogus skill id in it passed the
    whole suite.

    Each corpus must:
    parse via `parse_corpus`, have >= 8 entries, produce zero
    self-containedness warnings (trap #2 — no context-less fragments),
    and every `expected` value must be a well-formed "<plugin:skill>" id
    or the literal "NONE".
    """
    repo_root = Path(__file__).resolve().parents[2]
    corpus_dir = repo_root / "docs" / "loom" / "firing-corpus"
    corpora = sorted(corpus_dir.glob("*.jsonl"))
    assert len(corpora) >= 4, (
        f"expected at least the 4 shipped corpora in {corpus_dir}, "
        f"found {[c.name for c in corpora]}"
    )
    for path in corpora:
        name = path.name
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
            # WHY resolvability, not just shape: the corpus is the grading
            # oracle, and `_family()` keys on the plugin prefix. A retired
            # plugin id keeps its colon, so a shape-only check stays green
            # while a CORRECT fire grades MISS — the oracle inverts silently.
            # The 6->2 merge left 28 such records passing this assertion.
            if expected != "NONE":
                assert expected in _installed_skill_ids(repo_root), (
                    f"{name}: expected {expected!r} names no installed skill — "
                    "a renamed or retired id makes the oracle grade correct "
                    "fires as MISS"
                )
