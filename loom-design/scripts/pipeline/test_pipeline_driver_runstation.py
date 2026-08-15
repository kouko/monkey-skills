"""Structural + behavioral tests for driver_20_runstation.js — the
runStation module of the build-assembled Workflow driver (see
docs/loom/plans/2026-07-03-loom-pipeline-conductor.md Task 8). Source-only:
the concat-build lands in Task 14, so `test_ladder_budgets_watchdog_prefix`
checks the module in isolation via `node --check` plus grep-asserts on the
required contract surface (STATION schema, budgets, watchdog, ladder,
stable-prefix dispatch, RALLY_CAP). The remaining tests are behavioral: they
concatenate the module source with a `node -e` probe (mirroring
test_pipeline_driver_guard.py's pattern) to exercise fail-loud budget
resolution, the cumulative per-station cap, and the watchdog under a real
event loop.

The budget.spent()/budget.remaining() shape asserted here is grounded in the
Workflow tool docs and was exercised live in the 2026-07-03 F5 spike (run
wf_667ec006-ec2) and the loom-pipeline dogfood (source 4a — live
verification).
"""
import subprocess
from pathlib import Path

MODULE_PATH = Path(__file__).parent / "driver_20_runstation.js"

LADDER_STAGES = ["retry-same", "re-ground", "fresh-context", "escalate-human"]

STATION_FIELDS = ["verdict", "artifacts", "validator_exit", "interventions", "summary"]


def test_ladder_budgets_watchdog_prefix():
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"

    source = MODULE_PATH.read_text(encoding="utf-8")

    # node --check must pass (valid JS syntax, no runtime execution)
    result = subprocess.run(
        ["node", "--check", str(MODULE_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"node --check failed: {result.stderr}"

    # STATION schema field names all present
    for field in STATION_FIELDS:
        assert field in source, f"STATION schema missing field: {field}"

    # ladder stages named, in order
    positions = [source.index(stage) for stage in LADDER_STAGES]
    assert positions == sorted(positions), (
        f"ladder stages not in declared order: {LADDER_STAGES}"
    )

    # per-station AND run-level budget checks
    assert "budget.spent(" in source, "missing per-station budget.spent() check"
    assert "budget.remaining(" in source, "missing run-level budget.remaining() check"

    # wall-clock watchdog: Promise.race + a timeout constant
    assert "Promise.race" in source
    assert "STATION_TIMEOUT_MS" in source

    # rally cap constant, exported for critic loops, value 2
    assert "RALLY_CAP = 2" in source

    # F1: StructuredOutput-pinning line in the stable-prefix dispatch contract
    assert "your FINAL action must be the StructuredOutput call" in source

    # no forbidden non-deterministic tokens (concat-chain rule, inherited)
    for token in ["Date.now(", "Math.random(", "new Date()"]:
        assert token not in source, f"forbidden token present: {token}"


def test_runstation_fails_loud_without_budget():
    source = MODULE_PATH.read_text(encoding="utf-8")

    harness = source + "\n" + (
        "(async () => {\n"
        "  try {\n"
        "    await runStation('t-station', async () => 'ok', {});\n"
        "    console.error('should have thrown');\n"
        "    process.exit(0);\n"
        "  } catch (e) {\n"
        "    console.error(e.message);\n"
        "    process.exit(1);\n"
        "  }\n"
        "})();\n"
    )
    result = subprocess.run(
        ["node", "-e", harness], capture_output=True, text=True, timeout=10
    )
    assert result.returncode != 0, (
        "runStation must fail loud (non-zero exit) with no opts.budget and no "
        "global budget available"
    )
    assert "fail-loud: no budget primitive available" in result.stderr, (
        f"unexpected error message: {result.stderr!r}"
    )


def test_runstation_cumulative_budget_stops_ladder():
    source = MODULE_PATH.read_text(encoding="utf-8")

    # Mock budget: spent() advances 60 per real thunk invocation. tokenCap is
    # 100, so the cumulative delta breaches on the SECOND real attempt
    # (120 > 100). All three ladder thunks always fail, so without the fix
    # the ladder would ride all the way to escalate-human (4 attempts,
    # spend 240) instead of dying fatally at the breach.
    harness = source + "\n" + (
        "(async () => {\n"
        "  let calls = 0;\n"
        "  const mockBudget = { spent: () => calls * 60, remaining: () => 999999 };\n"
        "  const failingThunk = async () => {\n"
        "    calls++;\n"
        "    throw new Error('functional failure');\n"
        "  };\n"
        "  try {\n"
        "    await runStation('t-station', failingThunk, {\n"
        "      budget: mockBudget,\n"
        "      tokenCap: 100,\n"
        "      buildRegroundedThunk: () => failingThunk,\n"
        "      buildFreshContextThunk: () => failingThunk,\n"
        "    });\n"
        "    console.error('should have thrown');\n"
        "    process.exit(0);\n"
        "  } catch (e) {\n"
        "    console.error(e.message);\n"
        "    console.error('SPENT=' + mockBudget.spent());\n"
        "    process.exit(1);\n"
        "  }\n"
        "})();\n"
    )
    result = subprocess.run(
        ["node", "-e", harness], capture_output=True, text=True, timeout=10
    )
    assert result.returncode != 0, "budget-exceeded must be fatal, not swallowed"
    assert "token budget exceeded" in result.stderr, (
        f"final error must name the budget kill: {result.stderr!r}"
    )

    spent_line = next(
        line for line in result.stderr.splitlines() if line.startswith("SPENT=")
    )
    spent = int(spent_line.split("=", 1)[1])
    assert spent < 180, (
        "ladder must stop AT the cumulative breach (2 attempts = 120 spent), "
        f"not ride through further stages (3 attempts = 180): spent={spent}"
    )


def test_runstation_watchdog_rejects_instead_of_hanging():
    source = MODULE_PATH.read_text(encoding="utf-8")

    harness = source + "\n" + (
        "(async () => {\n"
        "  const neverResolves = () => new Promise(() => {});\n"
        "  try {\n"
        "    await runStation('t-station', neverResolves, {\n"
        "      budget: { spent: () => 0, remaining: () => 999999 },\n"
        "      timeoutMs: 50,\n"
        "    });\n"
        "    console.error('should have thrown');\n"
        "    process.exit(0);\n"
        "  } catch (e) {\n"
        "    console.error(e.message);\n"
        "    process.exit(1);\n"
        "  }\n"
        "})();\n"
    )
    # Outer timeout guard on the probe itself (separate from the in-module
    # STATION_TIMEOUT_MS override) so a watchdog regression fails the test
    # instead of hanging the suite.
    result = subprocess.run(
        ["node", "-e", harness], capture_output=True, text=True, timeout=10
    )
    assert result.returncode != 0, (
        "a thunk that never resolves must reject via the watchdog, not hang"
    )
