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
