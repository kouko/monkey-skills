"""Behavioral contract for deterministic Task Batch Review replay evidence."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).with_name("task_batch_replay.py")


def _load():
    spec = importlib.util.spec_from_file_location("task_batch_replay", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


replay = _load()


def _corpus() -> dict:
    return {
        "schema": "task-batch-replay-corpus/v1",
        "authorization": {
            "authorized": True,
            "source": "explicit-local-fixture",
        },
        "cases": [
            {
                "case_id": "eligible-capability",
                "task_ids": ["T1", "T2"],
                "requirements": ["REQ-1", "REQ-2"],
                "known_defects": [],
                "required_package_gates": ["package"],
                "expected_candidate_path": "eligible_batch",
                "expected_fallback_causes": [],
            },
            {
                "case_id": "invalid-boundary",
                "task_ids": ["T3", "T4"],
                "requirements": ["REQ-3", "REQ-4"],
                "known_defects": [],
                "required_package_gates": ["package"],
                "expected_candidate_path": "individual_fallback",
                "expected_fallback_causes": ["invalid_boundary"],
            },
            {
                "case_id": "known-defect",
                "task_ids": ["T5", "T6"],
                "requirements": ["REQ-5", "REQ-6"],
                "known_defects": ["DEFECT-1"],
                "required_package_gates": ["package"],
                "expected_candidate_path": "eligible_batch",
                "expected_fallback_causes": [],
            },
        ],
    }


def _case(
    case_id: str,
    *,
    dispatches: int,
    rounds: int = 1,
    fallback_causes: list[str] | None = None,
    false_scope_expansions: list[str] | None = None,
    detected_known_defects: list[str] | None = None,
    requirements: tuple[str, ...],
    elapsed_work_ms: int = 100,
    maximum_aggregate_diff_bytes: int = 10,
    package: str = "PASS",
) -> dict:
    return {
        "case_id": case_id,
        "review_dispatches": dispatches,
        "review_rounds": rounds,
        "fallback_causes": fallback_causes or [],
        "false_scope_expansions": false_scope_expansions or [],
        "detected_known_defects": detected_known_defects or [],
        "elapsed_work_ms": elapsed_work_ms,
        "maximum_aggregate_diff_bytes": maximum_aggregate_diff_bytes,
        "requirement_to_tests": {
            requirement: [f"test_{requirement.lower()}"]
            for requirement in requirements
        },
        "package_gates": {"package": package},
        "batch_reopens": 0,
    }


def _results(corpus: dict) -> tuple[dict, dict]:
    identity = replay.corpus_identity(corpus)
    baseline = {
        "schema": "task-batch-replay-result/v2",
        "provenance": "observed",
        "corpus_identity": identity,
        "branch": "baseline-branch",
        "cases": [
            _case("eligible-capability", dispatches=4, requirements=("REQ-1", "REQ-2")),
            _case("invalid-boundary", dispatches=4, requirements=("REQ-3", "REQ-4")),
            _case(
                "known-defect",
                dispatches=4,
                detected_known_defects=["DEFECT-1"],
                requirements=("REQ-5", "REQ-6"),
            ),
        ],
    }
    candidate = {
        "schema": "task-batch-replay-result/v2",
        "provenance": "observed",
        "corpus_identity": identity,
        "branch": "candidate-branch",
        "cases": [
            _case("eligible-capability", dispatches=2, requirements=("REQ-1", "REQ-2")),
            _case(
                "invalid-boundary",
                dispatches=4,
                fallback_causes=["invalid_boundary"],
                requirements=("REQ-3", "REQ-4"),
            ),
            _case(
                "known-defect",
                dispatches=2,
                detected_known_defects=["DEFECT-1"],
                requirements=("REQ-5", "REQ-6"),
            ),
        ],
    }
    return baseline, candidate


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


# @req: REQ-111
def test_baseline_candidate_comparison_is_same_corpus_and_safety_gated(
    tmp_path: Path,
) -> None:
    corpus = _corpus()
    baseline, candidate = _results(corpus)

    report = replay.compare(corpus, baseline, candidate)
    assert report["schema"] == "task-batch-replay-report/v1"
    assert report["verdict"] == "PASS"
    assert report["corpus_identity"] == replay.corpus_identity(corpus)
    assert report["case_ids"] == [
        "eligible-capability", "invalid-boundary", "known-defect"
    ]
    for lane in ("baseline", "candidate"):
        metrics = report[lane]
        assert set(metrics) == {
            "review_dispatches",
            "review_rounds",
            "fallback_causes",
            "false_scope_expansion",
            "escaped_known_defects",
            "elapsed_work_ms",
            "maximum_aggregate_diff_bytes",
            "requirement_to_test_traceability",
            "package_gates",
        }
    assert report["baseline"]["review_dispatches"] == 12
    assert report["candidate"]["review_dispatches"] == 8
    assert report["candidate"]["fallback_causes"] == {"invalid_boundary": 1}
    assert report["candidate"]["escaped_known_defects"] == []
    assert report["safety_regressions"] == []
    assert report["cost_attribution"] == {
        "eligible_batch": {
            "baseline_review_dispatches": 8,
            "candidate_review_dispatches": 4,
            "saved_review_dispatches": 4,
        },
        "individual_fallback": {
            "baseline_review_dispatches": 4,
            "candidate_review_dispatches": 4,
            "saved_review_dispatches": 0,
        },
    }

    bad = json.loads(json.dumps(candidate))
    bad["cases"][2]["detected_known_defects"] = []
    defect_report = replay.compare(corpus, baseline, bad)
    assert defect_report["verdict"] == "FAIL"
    assert "escaped_known_defect:known-defect:DEFECT-1" in defect_report["safety_regressions"]

    bad = json.loads(json.dumps(candidate))
    bad["cases"][0]["requirement_to_tests"]["REQ-2"] = []
    trace_report = replay.compare(corpus, baseline, bad)
    assert trace_report["verdict"] == "FAIL"
    assert "traceability_regression:eligible-capability:REQ-2" in trace_report["safety_regressions"]

    bad = json.loads(json.dumps(candidate))
    bad["cases"][0]["false_scope_expansions"] = ["scope-outside-task"]
    scope_report = replay.compare(corpus, baseline, bad)
    assert scope_report["verdict"] == "FAIL"
    assert "false_scope_expansion:eligible-capability:scope-outside-task" in scope_report["safety_regressions"]

    bad = json.loads(json.dumps(candidate))
    bad["cases"][0]["package_gates"]["package"] = "FAIL"
    gate_report = replay.compare(corpus, baseline, bad)
    assert gate_report["verdict"] == "FAIL"
    assert "package_gate_failure:eligible-capability:package" in gate_report["safety_regressions"]

    dispatch_only = json.loads(json.dumps(candidate))
    dispatch_only["cases"][2]["detected_known_defects"] = []
    assert sum(row["review_dispatches"] for row in dispatch_only["cases"]) < 12
    assert replay.compare(corpus, baseline, dispatch_only)["verdict"] == "FAIL"

    no_saving = json.loads(json.dumps(candidate))
    no_saving["cases"][0]["review_dispatches"] = 6
    no_saving["cases"][2]["review_dispatches"] = 2
    no_saving_report = replay.compare(corpus, baseline, no_saving)
    assert no_saving_report["candidate"]["review_dispatches"] == 12
    assert no_saving_report["verdict"] == "FAIL"
    assert no_saving_report["cost_regressions"] == [
        "no_review_dispatch_reduction",
        "no_eligible_batch_dispatch_reduction",
    ]

    mismatched = json.loads(json.dumps(candidate))
    mismatched["corpus_identity"] = "0" * 64
    with pytest.raises(replay.ReplayInputError, match="corpus identity"):
        replay.compare(corpus, baseline, mismatched)

    missing_case = json.loads(json.dumps(candidate))
    missing_case["cases"].pop()
    with pytest.raises(replay.ReplayInputError, match="case IDs"):
        replay.compare(corpus, baseline, missing_case)

    # One documented-style command consumes only explicit local inputs and
    # returns machine-readable PASS/FAIL with distinct schema-error status.
    corpus_path = tmp_path / "authorized-corpus.json"
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    _write(corpus_path, corpus)
    _write(baseline_path, baseline)
    _write(candidate_path, candidate)
    command = [
        sys.executable,
        str(SCRIPT),
        "compare",
        "--corpus", str(corpus_path),
        "--baseline", str(baseline_path),
        "--candidate", str(candidate_path),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["verdict"] == "PASS"

    _write(candidate_path, dispatch_only)
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    assert completed.returncode == 1
    assert json.loads(completed.stdout)["verdict"] == "FAIL"

    candidate_path.write_text("not-json", encoding="utf-8")
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "candidate" in completed.stderr and "invalid JSON" in completed.stderr

    candidate_path.unlink()
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "candidate" in completed.stderr and "cannot read" in completed.stderr

    unauthorized = json.loads(json.dumps(corpus))
    unauthorized["authorization"]["authorized"] = False
    with pytest.raises(replay.ReplayInputError, match="explicit authorization"):
        replay.compare(unauthorized, baseline, candidate)

    open_schema = json.loads(json.dumps(corpus))
    open_schema["private_session_path"] = "/not-an-authorized-field"
    with pytest.raises(replay.ReplayInputError, match="closed schema mismatch"):
        replay.compare(open_schema, baseline, candidate)


def _run_cli(
    tmp_path: Path, corpus_text: str, baseline_text: str, candidate_text: str
) -> subprocess.CompletedProcess[str]:
    corpus_path = tmp_path / "corpus-malformed.json"
    baseline_path = tmp_path / "baseline-malformed.json"
    candidate_path = tmp_path / "candidate-malformed.json"
    corpus_path.write_text(corpus_text, encoding="utf-8")
    baseline_path.write_text(baseline_text, encoding="utf-8")
    candidate_path.write_text(candidate_text, encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "compare",
            "--corpus", str(corpus_path),
            "--baseline", str(baseline_path),
            "--candidate", str(candidate_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


# @req: REQ-111
def test_malformed_types_paths_and_duplicate_keys_fail_closed(tmp_path: Path) -> None:
    corpus = _corpus()
    baseline, candidate = _results(corpus)

    malformed_path = json.loads(json.dumps(corpus))
    malformed_path["cases"][0]["expected_candidate_path"] = []
    with pytest.raises(replay.ReplayInputError, match="expected_candidate_path"):
        replay.compare(malformed_path, baseline, candidate)

    malformed_gate = json.loads(json.dumps(candidate))
    malformed_gate["cases"][0]["package_gates"]["package"] = []
    with pytest.raises(replay.ReplayInputError, match="package_gates.package"):
        replay.compare(corpus, baseline, malformed_gate)

    malformed_root_key = json.loads(json.dumps(corpus))
    malformed_root_key[1] = "not-a-string-key"
    with pytest.raises(replay.ReplayInputError, match="object keys must be strings"):
        replay.compare(malformed_root_key, baseline, candidate)

    malformed_trace_key = json.loads(json.dumps(candidate))
    trace = malformed_trace_key["cases"][0]["requirement_to_tests"]
    trace[1] = trace.pop("REQ-1")
    with pytest.raises(replay.ReplayInputError, match="object keys must be strings"):
        replay.compare(corpus, baseline, malformed_trace_key)

    malformed_gate_key = json.loads(json.dumps(candidate))
    gates = malformed_gate_key["cases"][0]["package_gates"]
    gates[1] = gates.pop("package")
    with pytest.raises(replay.ReplayInputError, match="object keys must be strings"):
        replay.compare(corpus, baseline, malformed_gate_key)

    # Every measured review relation is closed: zero/zero means no review;
    # otherwise each round owns at least one dispatch.
    for field_values in (
        (1, 0),
        (0, 1),
        (1, 2),
    ):
        incoherent = json.loads(json.dumps(baseline))
        incoherent["cases"][0]["review_dispatches"] = field_values[0]
        incoherent["cases"][0]["review_rounds"] = field_values[1]
        with pytest.raises(replay.ReplayInputError, match="review measurement"):
            replay.compare(corpus, incoherent, candidate)

    eligible_incoherent = json.loads(json.dumps(candidate))
    eligible_incoherent["cases"][0]["review_dispatches"] = 1
    eligible_incoherent["cases"][0]["review_rounds"] = 0
    eligible_incoherent["cases"][0]["fallback_causes"] = ["invalid_boundary"]
    with pytest.raises(replay.ReplayInputError, match="review measurement"):
        replay.compare(corpus, baseline, eligible_incoherent)

    eligible_fallback = json.loads(json.dumps(eligible_incoherent))
    eligible_fallback["cases"][0]["review_rounds"] = 1
    with pytest.raises(replay.ReplayInputError, match="eligible Batch"):
        replay.compare(corpus, baseline, eligible_fallback)

    eligible_zero = json.loads(json.dumps(candidate))
    eligible_zero["cases"][0]["review_dispatches"] = 0
    eligible_zero["cases"][0]["review_rounds"] = 0
    with pytest.raises(replay.ReplayInputError, match="positive review evidence"):
        replay.compare(corpus, baseline, eligible_zero)

    fallback_extra = json.loads(json.dumps(candidate))
    fallback_extra["cases"][1]["fallback_causes"] = [
        "invalid_boundary", "verification_failure"
    ]
    with pytest.raises(replay.ReplayInputError, match="exactly match"):
        replay.compare(corpus, baseline, fallback_extra)

    fallback_missing = json.loads(json.dumps(candidate))
    fallback_missing["cases"][1]["fallback_causes"] = []
    with pytest.raises(replay.ReplayInputError, match="exactly match"):
        replay.compare(corpus, baseline, fallback_missing)

    raw_corpus = json.dumps(corpus)
    raw_baseline = json.dumps(baseline)
    raw_candidate = json.dumps(candidate)
    duplicate_root = raw_corpus.replace(
        '"schema": "task-batch-replay-corpus/v1"',
        '"schema": "task-batch-replay-corpus/v1", '
        '"schema": "task-batch-replay-corpus/v1"',
        1,
    )
    duplicate_requirement = raw_candidate.replace(
        '"REQ-1": ["test_req-1"]',
        '"REQ-1": ["test_req-1"], "REQ-1": ["test_req-1"]',
        1,
    )
    duplicate_gate = raw_candidate.replace(
        '"package": "PASS"',
        '"package": "PASS", "package": "PASS"',
        1,
    )
    for malformed_label, expected_error, corpus_text, candidate_text in (
        (
            "corpus",
            "expected_candidate_path",
            json.dumps(malformed_path),
            raw_candidate,
        ),
        (
            "candidate",
            "package_gates.package",
            raw_corpus,
            json.dumps(malformed_gate),
        ),
        (
            "candidate",
            "review measurement",
            raw_corpus,
            json.dumps(eligible_incoherent),
        ),
        ("corpus", "duplicate JSON object key", duplicate_root, raw_candidate),
        (
            "candidate",
            "duplicate JSON object key",
            raw_corpus,
            duplicate_requirement,
        ),
        (
            "candidate",
            "duplicate JSON object key",
            raw_corpus,
            duplicate_gate,
        ),
    ):
        completed = _run_cli(
            tmp_path, corpus_text, raw_baseline, candidate_text
        )
        assert completed.returncode == 2
        assert completed.stdout == ""
        assert "Traceback" not in completed.stderr
        assert malformed_label in completed.stderr
        assert expected_error in completed.stderr


# @req: REQ-111
def test_fallback_cost_cannot_create_or_hide_batch_savings(tmp_path: Path) -> None:
    corpus = _corpus()
    baseline, candidate = _results(corpus)

    for dispatches in (1, 5):
        mismatched = json.loads(json.dumps(candidate))
        mismatched["cases"][0]["review_dispatches"] = 4
        mismatched["cases"][1]["review_dispatches"] = dispatches
        mismatched["cases"][2]["review_dispatches"] = 4
        with pytest.raises(replay.ReplayInputError, match="fallback review cost"):
            replay.compare(corpus, baseline, mismatched)

        completed = _run_cli(
            tmp_path,
            json.dumps(corpus),
            json.dumps(baseline),
            json.dumps(mismatched),
        )
        assert completed.returncode == 2
        assert completed.stdout == ""
        assert "Traceback" not in completed.stderr
        assert "fallback review cost" in completed.stderr

    mismatched_rounds = json.loads(json.dumps(candidate))
    mismatched_rounds["cases"][1]["review_rounds"] = 2
    with pytest.raises(replay.ReplayInputError, match="fallback review cost"):
        replay.compare(corpus, baseline, mismatched_rounds)

    baseline_without_review = json.loads(json.dumps(baseline))
    baseline_without_review["cases"][1]["review_dispatches"] = 0
    baseline_without_review["cases"][1]["review_rounds"] = 0
    with pytest.raises(replay.ReplayInputError, match="baseline.*positive"):
        replay.compare(corpus, baseline_without_review, candidate)

    no_eligible_saving = json.loads(json.dumps(candidate))
    no_eligible_saving["cases"][0]["review_dispatches"] = 4
    no_eligible_saving["cases"][2]["review_dispatches"] = 4
    report = replay.compare(corpus, baseline, no_eligible_saving)
    assert report["verdict"] == "FAIL"
    assert report["cost_attribution"]["eligible_batch"] == {
        "baseline_review_dispatches": 8,
        "candidate_review_dispatches": 8,
        "saved_review_dispatches": 0,
    }
    assert "no_eligible_batch_dispatch_reduction" in report["cost_regressions"]

    # The authorized representative remains the positive proof: fallback cost
    # is identical while all savings come from eligible Batch cases.
    passing = replay.compare(corpus, baseline, candidate)
    assert passing["verdict"] == "PASS"
    assert passing["cost_attribution"]["individual_fallback"][
        "saved_review_dispatches"
    ] == 0
    assert passing["cost_attribution"]["eligible_batch"][
        "saved_review_dispatches"
    ] > 0


def _single_case_corpus() -> dict:
    corpus = _corpus()
    corpus["cases"] = corpus["cases"][:1]
    return corpus


def _log_line(branch: str, sha: str) -> str:
    return json.dumps(
        {
            "schema": "review-dispatch-log/v1",
            "recorded_at": "2026-08-31T05:26:11+00:00",
            "branch": branch,
            "reviewed_sha": sha,
            "plugin_version": "0.107.1",
        },
        sort_keys=True,
    )


_SHA_A = "a" * 40
_SHA_B = "b" * 40


def _observe_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    log = tmp_path / "review-dispatches.jsonl"
    log.write_text(
        "\n".join(
            [
                _log_line("b", _SHA_A),
                _log_line("b", _SHA_A),
                _log_line("other", _SHA_B),
                _log_line("b", _SHA_B),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    _write(receipts / "one.json", {"schema": "batch-dispatch-receipt-v1", "applied_action": "reopen"})
    _write(receipts / "two.json", {"schema": "batch-dispatch-receipt-v1", "applied_action": "finalize"})
    _write(receipts / "three.json", {"schema": "batch-dispatch-receipt-v1"})
    corpus = tmp_path / "corpus.json"
    _write(corpus, _single_case_corpus())
    return log, receipts, corpus


# No registered REQ-id names the observe subcommand in this dispatch; tag omitted.
def test_observe_counts_dispatches_rounds_and_reopens_from_log_and_receipts(
    tmp_path: Path,
) -> None:
    log, receipts, corpus = _observe_fixture(tmp_path)
    out = tmp_path / "result.json"
    code = replay.main(
        [
            "observe",
            "--log", str(log),
            "--branch", "b",
            "--corpus", str(corpus),
            "--out", str(out),
            "--receipts", str(receipts),
        ]
    )
    assert code == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["schema"] == "task-batch-replay-result/v2"
    assert result["provenance"] == "observed"
    assert result["corpus_identity"] == replay.corpus_identity(_single_case_corpus())
    (case,) = result["cases"]
    assert case["case_id"] == "eligible-capability"
    assert case["review_dispatches"] == 3
    assert case["review_rounds"] == 2
    assert case["batch_reopens"] == 1
    # v2 keeps the whole v1 case shape underneath the observed counts.
    assert set(case) == replay._RESULT_CASE_KEYS | {"batch_reopens"}


# No registered REQ-id names the observe subcommand in this dispatch; tag omitted.
def test_observe_refuses_malformed_log_and_summarizes_without_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    log, receipts, corpus = _observe_fixture(tmp_path)
    out = tmp_path / "result.json"

    # `--receipts` omitted -> batch_reopens is 0, never guessed.
    assert replay.main(
        ["observe", "--log", str(log), "--branch", "b", "--corpus", str(corpus), "--out", str(out)]
    ) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["cases"][0]["batch_reopens"] == 0
    out.unlink()

    # `--summary` prints exactly the close-out line and writes no result file.
    assert replay.main(
        ["observe", "--log", str(log), "--branch", "b", "--receipts", str(receipts), "--summary"]
    ) == 0
    assert capsys.readouterr().out == "observed reviewer fan-outs: 3 (rounds 2, batch reopens 1)\n"
    assert not out.exists()

    # Zero matching lines on an existing log -> the zero line; absent log -> N/A, exit 0.
    assert replay.main(["observe", "--log", str(log), "--branch", "nobody", "--summary"]) == 0
    assert capsys.readouterr().out == "observed reviewer fan-outs: 0 (rounds 0, batch reopens 0)\n"
    assert replay.main(
        ["observe", "--log", str(tmp_path / "missing.jsonl"), "--branch", "b", "--summary"]
    ) == 0
    assert capsys.readouterr().out == "observed reviewer fan-outs: N/A — no dispatch log\n"

    # A malformed line refuses, naming its line number.
    bad = tmp_path / "bad.jsonl"
    bad.write_text(_log_line("b", _SHA_A) + "\n" + '{"schema": "x"}' + "\n", encoding="utf-8")
    with pytest.raises(replay.ReplayInputError, match="line 2"):
        replay.read_dispatch_log(bad)
    assert replay.main(["observe", "--log", str(bad), "--branch", "b", "--summary"]) == 2
    assert "line 2" in capsys.readouterr().err

    # A multi-case corpus cannot receive single-case attribution.
    multi = tmp_path / "multi.json"
    _write(multi, _corpus())
    assert replay.main(
        ["observe", "--log", str(log), "--branch", "b", "--corpus", str(multi), "--out", str(out)]
    ) == 2
    assert "exactly one case" in capsys.readouterr().err

    # `read_dispatch_log` is the module's only reader of the log: observe sees its view.
    monkeypatch.setattr(
        replay, "read_dispatch_log", lambda path: [json.loads(_log_line("b", _SHA_B))]
    )
    assert replay.main(["observe", "--log", str(log), "--branch", "b", "--summary"]) == 0
    assert capsys.readouterr().out == "observed reviewer fan-outs: 1 (rounds 1, batch reopens 0)\n"


def _v1_results(corpus: dict) -> tuple[dict, dict]:
    """The declared v1 pilot shape: hand-typed counts under `mode`, no provenance."""
    baseline, candidate = _results(corpus)
    declared = []
    for mode, result in (("individual", baseline), ("batch", candidate)):
        cases = [
            {key: value for key, value in case.items() if key != "batch_reopens"}
            for case in result["cases"]
        ]
        declared.append(
            {
                "schema": "task-batch-replay-result/v1",
                "mode": mode,
                "corpus_identity": result["corpus_identity"],
                "cases": cases,
            }
        )
    return declared[0], declared[1]


# No registered REQ-id in this dispatch (plan carries none); tag omitted.
def test_compare_refuses_declared_v1_results(tmp_path: Path) -> None:
    corpus = _corpus()
    baseline, candidate = _results(corpus)
    v1_baseline, v1_candidate = _v1_results(corpus)

    # The historical pilot shape (contract-repair-post-v3 Task 17) is refused
    # by name: hand-typed numbers can no longer produce a PASS.
    with pytest.raises(replay.ReplayInputError) as refused:
        replay.compare(corpus, v1_baseline, candidate)
    assert "baseline.schema" in str(refused.value)
    assert "task-batch-replay-result/v1" in str(refused.value)
    with pytest.raises(replay.ReplayInputError, match="candidate.schema"):
        replay.compare(corpus, baseline, v1_candidate)

    # A v2 file whose provenance is not "observed" is refused naming the value.
    declared = json.loads(json.dumps(candidate))
    declared["provenance"] = "declared"
    with pytest.raises(replay.ReplayInputError) as refused:
        replay.compare(corpus, baseline, declared)
    assert "candidate.provenance" in str(refused.value)
    assert "declared" in str(refused.value)

    # A v2-schema file with no provenance at all is refused on provenance, not
    # on a generic closed-schema mismatch.
    unprovenanced = json.loads(json.dumps(baseline))
    del unprovenanced["provenance"]
    with pytest.raises(replay.ReplayInputError, match="baseline.provenance"):
        replay.compare(corpus, unprovenanced, candidate)

    # CLI: the v1 pilot files exit 2 with the same refusal on stderr.
    completed = _run_cli(
        tmp_path, json.dumps(corpus), json.dumps(v1_baseline), json.dumps(v1_candidate)
    )
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "Traceback" not in completed.stderr
    assert "baseline.schema" in completed.stderr
    assert "task-batch-replay-result/v1" in completed.stderr


# No registered REQ-id in this dispatch (plan carries none); tag omitted.
def test_compare_accepts_two_observe_written_results(tmp_path: Path) -> None:
    log, receipts, corpus_path = _observe_fixture(tmp_path)
    corpus = _single_case_corpus()
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    # Baseline branch "b": 3 dispatches over 2 rounds; candidate "other": 1/1.
    assert replay.main(
        ["observe", "--log", str(log), "--branch", "b",
         "--corpus", str(corpus_path), "--out", str(baseline_path)]
    ) == 0
    assert replay.main(
        ["observe", "--log", str(log), "--branch", "other",
         "--corpus", str(corpus_path), "--out", str(candidate_path),
         "--receipts", str(receipts)]
    ) == 0

    report = replay.compare(
        corpus,
        json.loads(baseline_path.read_text(encoding="utf-8")),
        json.loads(candidate_path.read_text(encoding="utf-8")),
    )
    assert report["verdict"] == "PASS"
    assert report["baseline"]["review_dispatches"] == 3
    assert report["candidate"]["review_dispatches"] == 1
    assert report["cost_attribution"]["eligible_batch"]["saved_review_dispatches"] == 2
    # Unmeasured fields stay unmeasured: no gate verdict is invented either way.
    assert report["safety_regressions"] == []
    assert report["candidate"]["package_gates"] == {"eligible-capability": {}}
