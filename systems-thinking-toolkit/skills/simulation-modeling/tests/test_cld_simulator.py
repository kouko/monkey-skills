"""Tests for cld_simulator.py — analytical-comparison + safety + format.

Run with:
    PYTHONDONTWRITEBYTECODE=1 pytest systems-thinking-toolkit/skills/simulation-modeling/tests/ -v
"""
from __future__ import annotations

import csv
import io
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest


HERE = Path(__file__).parent
SKILL_ROOT = HERE.parent
SCRIPT = SKILL_ROOT / "scripts" / "cld_simulator.py"
EXAMPLES = SKILL_ROOT / "examples"


# Ensure pytest can import the simulator module for direct unit-tests too.
sys.path.insert(0, str(SCRIPT.parent))
import cld_simulator  # noqa: E402  (intentional after sys.path tweak)


def run_simulator(*args: str) -> subprocess.CompletedProcess:
    """Invoke the script as a subprocess. Returns CompletedProcess (no check)."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=env,
    )


def run_csv(spec: str | Path, *extra: str) -> tuple[list[str], list[list[float]]]:
    """Run simulator on a spec, parse CSV from stdout. Returns (header, rows-as-floats)."""
    result = run_simulator(str(spec), "--output", "csv", *extra)
    assert result.returncode == 0, f"simulator failed: {result.stderr}"
    rows = list(csv.reader(io.StringIO(result.stdout)))
    header = rows[0]
    data = [[float(x) for x in r] for r in rows[1:]]
    return header, data


# ---------------------------------------------------------------------------
# Analytical-comparison tests (the v0.10 deliverable's main value-add).
# ---------------------------------------------------------------------------

def test_exponential_growth_matches_analytical():
    """01_exponential_growth: P(t) = P0 * exp(r*t). Euler should match within 5%."""
    spec = EXAMPLES / "01_exponential_growth.json"
    header, data = run_csv(spec)
    final_t, final_p = data[-1]
    P0, r = 100.0, 0.05
    expected = P0 * math.exp(r * final_t)
    err_pct = abs(final_p - expected) / expected * 100
    assert err_pct < 5.0, (
        f"exponential growth Euler error {err_pct:.2f}% exceeds 5% tolerance "
        f"(sim={final_p:.4f}, analytical={expected:.4f})"
    )


def test_goal_seeking_converges_to_target():
    """02_goal_seeking: I(t) → Target exponentially. Final within 1%."""
    spec = EXAMPLES / "02_goal_seeking.json"
    header, data = run_csv(spec)
    final_inventory = data[-1][1]
    target = 100.0
    err_pct = abs(final_inventory - target) / target * 100
    assert err_pct < 1.0, (
        f"goal-seeking convergence error {err_pct:.3f}% exceeds 1% "
        f"(final={final_inventory:.4f}, target={target})"
    )


def test_logistic_s_curve_inflection():
    """03_limits_to_growth: P crosses K/2 at t* = ln((K-P0)/P0)/r. Within 5%."""
    spec = EXAMPLES / "03_limits_to_growth.json"
    header, data = run_csv(spec)
    K = 1000.0
    P0 = 10.0
    r = 0.2
    expected_t = math.log((K - P0) / P0) / r  # ~22.976
    # Find first time P >= K/2.
    cross_t = None
    for t, p in data:
        if p >= K / 2:
            cross_t = t
            break
    assert cross_t is not None, "logistic never crossed K/2 within simulation duration"
    err_pct = abs(cross_t - expected_t) / expected_t * 100
    assert err_pct < 5.0, (
        f"logistic inflection time error {err_pct:.2f}% exceeds 5% "
        f"(sim={cross_t:.3f}, analytical={expected_t:.3f})"
    )


def test_predator_prey_oscillates():
    """04_predator_prey: Rabbits time-series should have >=2 local maxima."""
    spec = EXAMPLES / "04_predator_prey.json"
    header, data = run_csv(spec)
    rabbits = [row[1] for row in data]
    local_maxima = sum(
        1 for i in range(1, len(rabbits) - 1)
        if rabbits[i] > rabbits[i - 1] and rabbits[i] > rabbits[i + 1]
    )
    assert local_maxima >= 2, (
        f"predator-prey expected >=2 local maxima in Rabbits, got {local_maxima}"
    )


# ---------------------------------------------------------------------------
# Safety / error-handling tests.
# ---------------------------------------------------------------------------

def test_malformed_json_fails_cleanly(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{this is not valid json")
    result = run_simulator(str(bad))
    assert result.returncode != 0
    assert "invalid JSON" in result.stderr or "JSON" in result.stderr


def test_missing_spec_file_fails_cleanly(tmp_path):
    result = run_simulator(str(tmp_path / "nonexistent.json"))
    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "no such" in result.stderr.lower()


def test_eval_rejects_imports():
    """Equation `__import__("os").system("ls")` must be rejected at compile, not at eval.

    Rejection can fire via multiple guard rails: outer call's method-chain (attribute),
    inner `__import__` name (underscore), or the call's non-Name func node. Any of
    these is acceptable — what matters is the equation never reaches eval.
    """
    with pytest.raises(cld_simulator.EquationError) as exc:
        cld_simulator.compile_equation('__import__("os").system("ls")')
    msg = str(exc.value).lower()
    assert any(token in msg for token in (
        "underscore", "attribute", "not allowed", "only simple function",
    )), f"unexpected error message: {msg}"


def test_eval_rejects_dunder():
    """Equation `().__class__` must be rejected."""
    with pytest.raises(cld_simulator.EquationError):
        cld_simulator.compile_equation("().__class__")


def test_eval_rejects_bare_dunder_call():
    """Bare `__import__("os")` (no method chain) must trigger the underscore guard."""
    with pytest.raises(cld_simulator.EquationError) as exc:
        cld_simulator.compile_equation('__import__("os")')
    msg = str(exc.value).lower()
    assert "underscore" in msg or "not in safe whitelist" in msg or "not allowed" in msg


def test_eval_rejects_attribute_access():
    """Equation `Population.real` must be rejected (no attribute access in equations)."""
    with pytest.raises(cld_simulator.EquationError) as exc:
        cld_simulator.compile_equation("Population.real")
    assert "attribute" in str(exc.value).lower()


def test_eval_rejects_unknown_function():
    """Equation `eval('1+1')` must be rejected — `eval` not in whitelist."""
    with pytest.raises(cld_simulator.EquationError) as exc:
        cld_simulator.compile_equation("eval('1+1')")
    assert "whitelist" in str(exc.value).lower() or "not in safe" in str(exc.value).lower()


def test_undefined_variable_errors(tmp_path):
    """Equation `0.05 * UndefinedStock` → clean EquationError naming the bad name."""
    spec = {
        "name": "bad",
        "duration": 1,
        "dt": 0.1,
        "stocks": {"X": 1.0},
        "flows": {"F": {"to": "X", "equation": "0.05 * UndefinedStock"}}
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    result = run_simulator(str(p))
    assert result.returncode != 0
    assert "UndefinedStock" in result.stderr or "undefined" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Output format tests.
# ---------------------------------------------------------------------------

def test_csv_output_format(tmp_path):
    """CSV has correct header + row count = duration/dt + 1."""
    spec = {
        "name": "tiny",
        "duration": 1.0,
        "dt": 0.1,
        "stocks": {"X": 1.0},
        "parameters": {},
        "flows": {"F": {"to": "X", "equation": "0.0"}}
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    header, data = run_csv(p)
    assert header == ["time", "X"], f"unexpected CSV header: {header}"
    # duration=1, dt=0.1, expect 1/0.1 + 1 = 11 rows.
    assert len(data) == 11, f"expected 11 rows, got {len(data)}"
    # All X values should remain 1.0 (zero-rate flow).
    assert all(abs(row[1] - 1.0) < 1e-9 for row in data)


def test_ascii_chart_renders(tmp_path):
    """ASCII chart output contains stock name + asterisks."""
    spec = EXAMPLES / "01_exponential_growth.json"
    result = run_simulator(str(spec), "--output", "ascii-chart")
    assert result.returncode == 0
    assert "Population" in result.stdout
    assert "*" in result.stdout


def test_both_output_writes_csv_and_chart(tmp_path):
    """`--output both --out file.csv` writes CSV to file + chart to stdout."""
    spec = EXAMPLES / "01_exponential_growth.json"
    outfile = tmp_path / "out.csv"
    result = run_simulator(str(spec), "--output", "both", "--out", str(outfile))
    assert result.returncode == 0
    assert outfile.exists()
    # CSV file should parse cleanly.
    with outfile.open() as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["time", "Population"]
    assert len(rows) >= 2
    # Chart should be on stdout.
    assert "Population" in result.stdout
    assert "*" in result.stdout


def test_duration_override(tmp_path):
    """--duration overrides the spec value."""
    spec = EXAMPLES / "01_exponential_growth.json"
    header, data = run_csv(spec, "--duration", "10")
    # duration=10, dt=0.1 → 101 rows.
    assert len(data) == 101, f"expected 101 rows, got {len(data)}"
    assert data[-1][0] == pytest.approx(10.0, abs=1e-9)


def test_dt_override(tmp_path):
    """--dt overrides the spec value."""
    spec = EXAMPLES / "01_exponential_growth.json"
    header, data = run_csv(spec, "--duration", "10", "--dt", "1")
    # duration=10, dt=1 → 11 rows.
    assert len(data) == 11, f"expected 11 rows with dt=1, got {len(data)}"


# ---------------------------------------------------------------------------
# Spec validation tests.
# ---------------------------------------------------------------------------

def test_spec_missing_stocks_fails(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"flows": {}}))
    result = run_simulator(str(bad))
    assert result.returncode != 0
    assert "stocks" in result.stderr


def test_spec_flow_references_unknown_stock(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({
        "stocks": {"A": 1.0},
        "flows": {"F": {"to": "Phantom", "equation": "1.0"}}
    }))
    result = run_simulator(str(bad))
    assert result.returncode != 0
    assert "Phantom" in result.stderr or "unknown" in result.stderr.lower()


def test_spec_flow_needs_to_or_from(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({
        "stocks": {"A": 1.0},
        "flows": {"F": {"equation": "1.0"}}
    }))
    result = run_simulator(str(bad))
    assert result.returncode != 0
    assert "to" in result.stderr or "from" in result.stderr


# ---------------------------------------------------------------------------
# Transfer flow (both to and from) sanity test.
# ---------------------------------------------------------------------------

def test_transfer_flow_conserves_total(tmp_path):
    """A flow with both `to` and `from` should conserve total mass."""
    spec = {
        "name": "transfer",
        "duration": 10,
        "dt": 0.1,
        "stocks": {"Source": 100.0, "Sink": 0.0},
        "parameters": {"rate": 0.1},
        "flows": {"Transfer": {
            "to": "Sink", "from": "Source",
            "equation": "rate * Source"
        }}
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    header, data = run_csv(p)
    # Total Source + Sink should remain ~100 throughout (Euler error tiny here).
    for row in data:
        total = row[1] + row[2]
        assert abs(total - 100.0) < 0.01, (
            f"transfer flow violated conservation at t={row[0]}: total={total}"
        )


# ---------------------------------------------------------------------------
# v0.10 hardening — input-bound guards.
# ---------------------------------------------------------------------------

def test_dt_zero_rejected_via_spec(tmp_path):
    """dt=0 in spec must be rejected cleanly (no infinite loop)."""
    spec = {
        "name": "dt-zero", "duration": 10, "dt": 0,
        "stocks": {"X": 1.0}, "flows": {},
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    result = run_simulator(str(p))
    assert result.returncode != 0
    assert "dt" in result.stderr.lower()


def test_dt_zero_rejected_via_cli(tmp_path):
    """dt=0 via --dt flag must be rejected (CLI override path)."""
    spec = {
        "name": "dt-cli", "duration": 10, "dt": 0.1,
        "stocks": {"X": 1.0}, "flows": {},
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    result = run_simulator(str(p), "--dt", "0")
    assert result.returncode != 0
    assert "dt" in result.stderr.lower()


def test_negative_dt_rejected(tmp_path):
    """Negative dt must be rejected (same guard as zero)."""
    spec = {
        "name": "neg-dt", "duration": 10, "dt": -0.1,
        "stocks": {"X": 1.0}, "flows": {},
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    result = run_simulator(str(p))
    assert result.returncode != 0
    assert "dt" in result.stderr.lower()


def test_negative_duration_rejected(tmp_path):
    """Negative duration must be rejected."""
    spec = {
        "name": "neg-dur", "duration": -5, "dt": 0.1,
        "stocks": {"X": 1.0}, "flows": {},
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    result = run_simulator(str(p))
    assert result.returncode != 0
    assert "duration" in result.stderr.lower()


# ---------------------------------------------------------------------------
# v0.10 hardening — Euler discipline (no mid-step cascade).
# ---------------------------------------------------------------------------

def test_circular_stock_reference_uses_step_boundary(tmp_path):
    """Two flows referencing each other's target stock must read OLD values at step
    boundary (forward Euler discipline). Not cascading values from within the step.

    Setup: stock A starts at 10, stock B starts at 0. Flow F1 adds (0.5 * B) to A
    each step; Flow F2 adds (0.5 * A) to B each step. With Euler discipline,
    after step 1 (dt=1.0) using OLD values:
        A_new = 10 + 0.5 * 0   = 10  (read OLD B=0)
        B_new = 0  + 0.5 * 10  = 5   (read OLD A=10)
    Step 2 reads (A=10, B=5):
        A_new = 10 + 0.5*5  = 12.5  (Euler reads OLD B=5)
        B_new = 5  + 0.5*10 = 10
    A non-Euler cascading variant would compute differently.
    """
    spec = {
        "name": "circular",
        "duration": 2.0, "dt": 1.0,
        "stocks": {"A": 10.0, "B": 0.0},
        "flows": {
            "F1": {"to": "A", "equation": "0.5 * B"},
            "F2": {"to": "B", "equation": "0.5 * A"},
        },
        "outputs": ["A", "B"],
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    header, data = run_csv(p)
    # rows: t=0, t=1, t=2
    assert len(data) == 3
    # t=0
    assert abs(data[0][1] - 10.0) < 1e-9 and abs(data[0][2] - 0.0) < 1e-9
    # t=1: per Euler with OLD values
    assert abs(data[1][1] - 10.0) < 1e-9, f"step 1 A expected 10.0, got {data[1][1]}"
    assert abs(data[1][2] - 5.0)  < 1e-9, f"step 1 B expected 5.0, got {data[1][2]}"
    # t=2: per Euler with OLD values from step 1
    assert abs(data[2][1] - 12.5) < 1e-9, f"step 2 A expected 12.5, got {data[2][1]}"
    assert abs(data[2][2] - 10.0) < 1e-9, f"step 2 B expected 10.0, got {data[2][2]}"


def test_multiple_flows_to_same_stock_add(tmp_path):
    """Two inflows to the same stock should produce additive accumulation per step.

    Setup: stock S=0; F1 = constant rate 2.0/time; F2 = constant rate 3.0/time.
    Both target S. After 10 time units, S should be ≈ 50 (= (2+3) * 10).
    """
    spec = {
        "name": "multi-inflow",
        "duration": 10.0, "dt": 0.1,
        "stocks": {"S": 0.0},
        "flows": {
            "F1": {"to": "S", "equation": "2.0"},
            "F2": {"to": "S", "equation": "3.0"},
        },
        "outputs": ["S"],
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    header, data = run_csv(p)
    final_S = data[-1][1]
    assert abs(final_S - 50.0) < 0.01, (
        f"two flows summing to 5.0/time over 10 time should give S=50, got {final_S}"
    )


# ---------------------------------------------------------------------------
# v0.10 hardening — degenerate spec shapes.
# ---------------------------------------------------------------------------

def test_empty_outputs_list_defaults_to_all_stocks(tmp_path):
    """Spec with `outputs: []` should run cleanly and fall back to emitting
    all stocks (treating empty as "not specified" rather than "explicitly empty").

    This documents the UX choice: an empty outputs list is interpreted
    permissively as "no preference, emit everything" rather than restrictively
    as "emit nothing". The reasoning: users who set `outputs: []` almost
    certainly forgot to fill it in; emitting nothing would silently hide all
    simulation results and produce a CSV with only timestamps, which is
    rarely useful.
    """
    spec = {
        "name": "no-outputs",
        "duration": 5.0, "dt": 1.0,
        "stocks": {"X": 1.0, "Y": 2.0},
        "flows": {"F": {"to": "X", "equation": "0.1 * X"}},
        "outputs": [],
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    result = run_simulator(str(p), "--output", "csv")
    assert result.returncode == 0, f"simulator failed: {result.stderr}"
    rows = list(csv.reader(io.StringIO(result.stdout)))
    # Empty outputs → fallback to all stocks (X and Y both present).
    assert rows[0] == ["time", "X", "Y"], f"expected fallback to all stocks, got {rows[0]}"
    assert len(rows) == 7  # t=0 through t=5 inclusive with dt=1
    for row in rows[1:]:
        assert len(row) == 3, f"expected 3-column row, got {row}"


# ---------------------------------------------------------------------------
# v0.10 hardening — Euler accuracy documentation.
# ---------------------------------------------------------------------------

def test_long_duration_euler_drift_documented(tmp_path):
    """Long-run Euler drift on exponential growth: with dt=0.1, error grows
    with duration. Documents the limitation. The test passes if drift is
    bounded under a known threshold; if it ever exceeds the threshold,
    the SKILL.md caveats need updating.
    """
    P0 = 100.0
    r = 0.05
    duration = 200.0
    dt = 0.1
    spec = {
        "name": "long-exp",
        "duration": duration, "dt": dt,
        "stocks": {"P": P0},
        "flows": {"birth": {"to": "P", "equation": f"{r} * P"}},
        "outputs": ["P"],
    }
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    header, data = run_csv(p)
    sim_final = data[-1][1]
    analytical_final = P0 * math.exp(r * duration)
    relative_error = abs(sim_final - analytical_final) / analytical_final
    # At duration=200 with dt=0.1, Euler under-shoots exp by a few %.
    # Documented threshold: 10%. If this ever fails, dt must be reduced
    # OR the SKILL.md caveats need stronger wording.
    assert relative_error < 0.10, (
        f"Euler drift at duration={duration}, dt={dt} is "
        f"{relative_error*100:.2f}% — exceeds documented 10% threshold"
    )


def test_dt_sensitivity_smaller_dt_more_accurate(tmp_path):
    """Smaller dt should produce result closer to analytical solution.

    Same spec, two simulations at dt=1.0 vs dt=0.01. Verify dt=0.01 has
    strictly smaller error against the analytical exp(rt) reference.
    This documents the dt trade-off (smaller = more accurate = slower).
    """
    P0 = 100.0
    r = 0.05
    duration = 50.0
    spec_template = {
        "name": "dt-sens", "duration": duration,
        "stocks": {"P": P0},
        "flows": {"birth": {"to": "P", "equation": f"{r} * P"}},
        "outputs": ["P"],
    }
    analytical = P0 * math.exp(r * duration)

    # Coarse dt=1.0
    spec1 = dict(spec_template); spec1["dt"] = 1.0
    p1 = tmp_path / "coarse.json"; p1.write_text(json.dumps(spec1))
    _, data1 = run_csv(p1)
    err_coarse = abs(data1[-1][1] - analytical)

    # Fine dt=0.01
    spec2 = dict(spec_template); spec2["dt"] = 0.01
    p2 = tmp_path / "fine.json"; p2.write_text(json.dumps(spec2))
    _, data2 = run_csv(p2)
    err_fine = abs(data2[-1][1] - analytical)

    assert err_fine < err_coarse, (
        f"finer dt should produce smaller error: coarse={err_coarse:.3f}, "
        f"fine={err_fine:.3f}"
    )
    # Documented behavior: fine should be at LEAST 10× more accurate than coarse.
    assert err_fine * 10 < err_coarse, (
        f"fine dt error ({err_fine:.4f}) not 10× better than coarse ({err_coarse:.4f})"
    )
