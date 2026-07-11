"""Tests for improve_loop_verdict.py — the `compare` and `smoke` verdict
subcommands for the L3 principles-improve-loop (Task 1, brief
docs/loom/specs/2026-07-11-principles-replay-l3-loop.md §Smallest End State
item 4).

Synthetic content only. Fixtures built INLINE (flat-folder rule: no
fixtures/ subdir, no conftest.py — same convention as
test_check_seed_traceability.py).
"""

import json
import subprocess
import sys
from pathlib import Path

from improve_loop_verdict import aggregate_pass_map

SCRIPT = Path(__file__).with_name("improve_loop_verdict.py")


def _write(tmp_path: Path, name: str, rows) -> Path:
    """Write `rows` (a list of row dicts, or a dict with a 'rows' key) as
    JSON to tmp_path/name and return the path."""
    path = tmp_path / name
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


def _run(args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": ""},
    )


# --- compare -----------------------------------------------------------------

def test_compare_accepts_only_no_worse_and_one_better(tmp_path):
    # RED test: `improve_loop_verdict` module is not implemented yet.
    baseline = _write(tmp_path, "baseline.json", [
        {"seedId": "seed1", "pass": True},
        {"seedId": "seed2", "pass": False},
    ])
    candidate = _write(tmp_path, "candidate.json", [
        {"seedId": "seed1", "pass": True},   # unchanged, not worse
        {"seedId": "seed2", "pass": True},   # better
    ])
    proc = _run(["compare", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_compare_rejects_trade_of_one_better_one_worse(tmp_path):
    baseline = _write(tmp_path, "baseline.json", [
        {"seedId": "seed1", "pass": True},
        {"seedId": "seed2", "pass": False},
    ])
    candidate = _write(tmp_path, "candidate.json", [
        {"seedId": "seed1", "pass": False},  # worse
        {"seedId": "seed2", "pass": True},   # better
    ])
    proc = _run(["compare", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 1


def test_compare_rejects_no_change(tmp_path):
    baseline = _write(tmp_path, "baseline.json", [
        {"seedId": "seed1", "pass": True},
        {"seedId": "seed2", "pass": False},
    ])
    candidate = _write(tmp_path, "candidate.json", [
        {"seedId": "seed1", "pass": True},
        {"seedId": "seed2", "pass": False},
    ])
    proc = _run(["compare", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 1


def test_compare_accepts_bare_list_or_rows_wrapped_json(tmp_path):
    # Boundary: a baseline/candidate file may be a bare list OR the full
    # matrix return shape {"runLabel", "rows", "passRate"} — both parse.
    baseline = _write(tmp_path, "baseline.json", {
        "runLabel": "r1",
        "rows": [
            {"seedId": "seed1", "pass": True},
            {"seedId": "seed2", "pass": False},
        ],
        "passRate": 0.5,
    })
    candidate = _write(tmp_path, "candidate.json", [
        {"seedId": "seed1", "pass": True},
        {"seedId": "seed2", "pass": True},
    ])
    proc = _run(["compare", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_compare_malformed_json_exits_2(tmp_path):
    baseline = tmp_path / "baseline.json"
    baseline.write_text("{not valid json", encoding="utf-8")
    candidate = _write(tmp_path, "candidate.json", [{"seedId": "seed1", "pass": True}])
    proc = _run(["compare", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 2


def test_compare_missing_file_exits_2(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    candidate = _write(tmp_path, "candidate.json", [{"seedId": "seed1", "pass": True}])
    proc = _run(["compare", "--baseline", str(missing), "--candidate", str(candidate)])
    assert proc.returncode == 2


def test_compare_seed_set_mismatch_exits_2(tmp_path):
    baseline = _write(tmp_path, "baseline.json", [
        {"seedId": "seed1", "pass": True},
        {"seedId": "seed2", "pass": False},
    ])
    candidate = _write(tmp_path, "candidate.json", [
        {"seedId": "seed1", "pass": True},  # seed2 missing from candidate
    ])
    proc = _run(["compare", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 2


def test_compare_row_missing_required_key_exits_2(tmp_path):
    baseline = _write(tmp_path, "baseline.json", [{"seedId": "seed1"}])  # no "pass"
    candidate = _write(tmp_path, "candidate.json", [{"seedId": "seed1", "pass": True}])
    proc = _run(["compare", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 2


def test_compare_aggregates_multiple_baseline_runs_with_two_flags(tmp_path):
    # Two --baseline flags = 2 baseline runs; ≥1 better still required.
    baseline1 = _write(tmp_path, "b1.json", [{"seedId": "seed1", "pass": False}])
    baseline2 = _write(tmp_path, "b2.json", [{"seedId": "seed1", "pass": False}])
    candidate = _write(tmp_path, "candidate.json", [{"seedId": "seed1", "pass": True}])
    proc = _run([
        "compare",
        "--baseline", str(baseline1), "--baseline", str(baseline2),
        "--candidate", str(candidate),
    ])
    assert proc.returncode == 0, proc.stdout + proc.stderr


# --- aggregate_pass_map (unit-level: documents the "ANY baseline run passed" rule) ---

def test_aggregate_pass_map_seed_passes_if_any_run_passed():
    result = aggregate_pass_map([
        [{"seedId": "s1", "pass": False}],
        [{"seedId": "s1", "pass": True}],
    ])
    assert result == {"s1": True}


def test_aggregate_pass_map_seed_fails_if_no_run_passed():
    result = aggregate_pass_map([
        [{"seedId": "s1", "pass": False}],
        [{"seedId": "s1", "pass": False}],
    ])
    assert result == {"s1": False}


# --- smoke ---------------------------------------------------------------

def test_smoke_passes_when_no_held_out_seed_newly_failing(tmp_path):
    baseline = _write(tmp_path, "baseline.json", [
        {"seedId": "cold-operator", "pass": True},
        {"seedId": "seed5", "pass": False},
    ])
    candidate = _write(tmp_path, "candidate.json", [
        {"seedId": "cold-operator", "pass": True},
        {"seedId": "seed5", "pass": True},  # improvement, not a failure
    ])
    proc = _run(["smoke", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_smoke_fails_and_names_newly_failing_seed(tmp_path):
    baseline = _write(tmp_path, "baseline.json", [
        {"seedId": "cold-operator", "pass": True},
        {"seedId": "seed5", "pass": True},
    ])
    candidate = _write(tmp_path, "candidate.json", [
        {"seedId": "cold-operator", "pass": True},
        {"seedId": "seed5", "pass": False},  # newly failing
    ])
    proc = _run(["smoke", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 1
    assert "seed5" in proc.stdout


def test_smoke_malformed_json_exits_2(tmp_path):
    baseline = tmp_path / "baseline.json"
    baseline.write_text("not json at all", encoding="utf-8")
    candidate = _write(tmp_path, "candidate.json", [{"seedId": "seed5", "pass": True}])
    proc = _run(["smoke", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 2


def test_smoke_seed_set_mismatch_exits_2(tmp_path):
    baseline = _write(tmp_path, "baseline.json", [
        {"seedId": "cold-operator", "pass": True},
        {"seedId": "seed5", "pass": True},
    ])
    candidate = _write(tmp_path, "candidate.json", [
        {"seedId": "cold-operator", "pass": True},  # seed5 missing
    ])
    proc = _run(["smoke", "--baseline", str(baseline), "--candidate", str(candidate)])
    assert proc.returncode == 2
