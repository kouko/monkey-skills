"""Structural + behavioral tests for driver_60_ledger.js — the ledger module
of the build-assembled Workflow driver (see
docs/loom/plans/2026-07-03-loom-pipeline-conductor.md Task 12). Source-only:
the concat-build lands in a later task, so `test_ledger_fields` checks the
module in isolation via `node --check` plus grep-asserts on the required
contract surface (LEDGER, recordLedger, renderLedger, writeLedger, the
ledger path, G5 per-judge section, the 3 intervention buckets, the G2
critic-found metric, and the "checkpointed" closing line). The remaining
test is behavioral: it concatenates the module source with a `node -e`
probe (mirroring test_pipeline_driver_runstation.py's pattern) to exercise
recordLedger's fail-loud validation and renderLedger's real output.

The 3 intervention buckets mirror
docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md's
"intervention ledger — 25 raw entries, triaged into three buckets" section:
A. Driver/harness gaps, B. Genuine human gates, C. Capability gaps.
"""
import subprocess
from pathlib import Path

MODULE_PATH = Path(__file__).parent / "driver_60_ledger.js"


def test_ledger_fields():
    # @req: REQ-LOOM-PIPELINE-LEDGER-1
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"

    source = MODULE_PATH.read_text(encoding="utf-8")

    # node --check must pass (valid JS syntax, no runtime execution)
    result = subprocess.run(
        ["node", "--check", str(MODULE_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"node --check failed: {result.stderr}"

    # cross-module contract surface (segment modules call these verbatim)
    assert "const LEDGER" in source, "missing LEDGER array declaration"
    assert "function recordLedger" in source, "missing recordLedger declaration"
    assert "function renderLedger" in source, "missing renderLedger declaration"
    assert "async function writeLedger" in source, "missing writeLedger declaration"

    # ledger file path: <projectPath>/docs/loom/<changeId>/pipeline-ledger.md
    assert "docs/loom/" in source, "missing docs/loom/ path segment"
    assert "pipeline-ledger.md" in source, "missing pipeline-ledger.md filename"

    # driver never writes files directly — writeLedger must dispatch a
    # station agent (the ambient `agent` primitive), same convention as
    # driver_20_runstation.js's typeof-guarded ambient budget primitive
    assert "typeof agent" in source, (
        "writeLedger must fail loud via a typeof-guarded ambient `agent` "
        "primitive rather than writing files itself"
    )

    # G5: per-judge panel verdicts section marker (every individual judge's
    # verdict, not just aggregates)
    assert "G5" in source, "missing G5 per-judge section marker"

    # interventions: 3-bucket list mirroring the dogfood report's buckets
    assert "Driver/harness gaps" in source, "missing bucket A marker"
    assert "Genuine human gates" in source, "missing bucket B marker"
    assert "Capability gaps" in source, "missing bucket C marker"

    # G2: critic-found metric + false-positive placeholder
    assert "Critic-found rows" in source, "missing G2 critic-found metric line"
    assert "Later rejected by human: TBD" in source, (
        "missing G2 'Later rejected by human: TBD' placeholder line"
    )

    # G6: honest "checkpointed, not durable" closing line
    assert "checkpointed run — resume via journal + resumeFromRunId" in source, (
        "missing G6 checkpointed closing line"
    )

    # no forbidden non-deterministic tokens (concat-chain rule, inherited)
    for token in ["Date.now(", "Math.random(", "new Date()"]:
        assert token not in source, f"forbidden token present: {token}"


def test_ledger_record_and_render_behavioral():
    # @req: REQ-LOOM-PIPELINE-LEDGER-1
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"
    source = MODULE_PATH.read_text(encoding="utf-8")

    harness = source + "\n" + (
        "(() => {\n"
        "  // 1. malformed entry (missing verdict) must throw\n"
        "  let threw = false;\n"
        "  try {\n"
        "    recordLedger({ station: 'design-critic', judge: 'lens-a11y' });\n"
        "  } catch (e) {\n"
        "    threw = true;\n"
        "    console.error('MALFORMED_THREW: ' + e.message);\n"
        "  }\n"
        "  if (!threw) {\n"
        "    console.error('FAIL: malformed entry did not throw');\n"
        "    process.exit(1);\n"
        "  }\n"
        "\n"
        "  // 1b. the REAL mistake a segment module can make: spreading a\n"
        "  // STATION result (station+verdict+summary, NO judge/role) — the\n"
        "  // exact shape the seg1<->ledger integration break shipped. Must throw.\n"
        "  let stationSpreadThrew = false;\n"
        "  try {\n"
        "    recordLedger({ station: 'principles', verdict: 'adopted', summary: 'ok', artifacts: [], interventions: [] });\n"
        "  } catch (e) {\n"
        "    stationSpreadThrew = true;\n"
        "    console.error('STATION_SPREAD_THREW: ' + e.message);\n"
        "  }\n"
        "  if (!stationSpreadThrew) {\n"
        "    console.error('FAIL: station-spread entry without judge/role did not throw');\n"
        "    process.exit(1);\n"
        "  }\n"
        "\n"
        "  // 2. valid entry must be accepted\n"
        "  recordLedger({ station: 'design-critic', judge: 'lens-a11y', verdict: 'PASS_WITH_NOTES' });\n"
        "  if (LEDGER.length !== 1) {\n"
        "    console.error('FAIL: valid entry not recorded, LEDGER.length=' + LEDGER.length);\n"
        "    process.exit(1);\n"
        "  }\n"
        "\n"
        "  // 3. renderLedger with a minimal stationResults array\n"
        "  const args = {\n"
        "    changeId: 'toy-change',\n"
        "    projectPath: '/tmp/toy-project',\n"
        "    budgets: { run: 500000, perStation: { design: 40000 } },\n"
        "    budgetSpent: 12345,\n"
        "  };\n"
        "  const stationResults = [\n"
        "    { station: 'design', verdict: 'PASS', validator_exit: 0, summary: 'ok', interventions: [] },\n"
        "  ];\n"
        "  const out = renderLedger(args, stationResults);\n"
        "  if (typeof out !== 'string' || !out.includes('checkpointed')) {\n"
        "    console.error('FAIL: renderLedger output missing checkpointed wording');\n"
        "    process.exit(1);\n"
        "  }\n"
        "  if (!out.includes('| design |')) {\n"
        "    console.error('FAIL: renderStationTable did not honor the station field, got:\\n' + out);\n"
        "    process.exit(1);\n"
        "  }\n"
        "  console.log('OK');\n"
        "  process.exit(0);\n"
        "})();\n"
    )
    result = subprocess.run(
        ["node", "-e", harness], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, (
        f"behavioral probe failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "MALFORMED_THREW" in result.stderr, (
        "expected recordLedger to throw on the malformed entry"
    )
    assert "OK" in result.stdout


def test_interventions_attributed_by_station_field():
    """Whole-branch review 🔴: renderInterventionBuckets read station.name,
    which no producer sets (they all set .station) — every intervention
    rendered as [unknown]. Pin the fix: a real producer-shaped station
    result must attribute its intervention by its .station value.

    # @req: REQ-LOOM-PIPELINE-LEDGER-3
    """
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"
    source = MODULE_PATH.read_text(encoding="utf-8")

    harness = source + "\n" + (
        "(() => {\n"
        "  const stationResults = [\n"
        "    { station: 'spec-validator', verdict: 'NEEDS_REVISION', interventions: [\n"
        "      { bucket: 'B', text: 'Decisions section absent', critic_found: false },\n"
        "    ] },\n"
        "  ];\n"
        "  const args = { changeId: 'c1', projectPath: '/tmp/x', budgets: { run: 1, perStation: {} } };\n"
        "  const out = renderLedger(args, stationResults);\n"
        "  if (out.includes('[unknown]')) {\n"
        "    console.error('FAIL: intervention attributed to [unknown]');\n"
        "    process.exit(1);\n"
        "  }\n"
        "  if (!out.includes('[spec-validator]')) {\n"
        "    console.error('FAIL: intervention not attributed to its station');\n"
        "    process.exit(1);\n"
        "  }\n"
        "  console.log('OK');\n"
        "})();\n"
    )
    import subprocess as sp
    result = sp.run(["node", "-e", harness], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, (
        f"attribution probe failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_g2_metric_counts_nested_critic_found_interventions():
    """G2 fix: nothing populates top-level LEDGER entry.critic_found — the
    seg2/seg3 schemas nest critic_found inside stationResults[].interventions[]
    items. renderG2Metric must count THAT, not the always-empty top-level
    field, so 'Critic-found rows' stops being structurally dead.

    # @req: REQ-LOOM-PIPELINE-LEDGER-2
    """
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"
    source = MODULE_PATH.read_text(encoding="utf-8")

    harness = source + "\n" + (
        "(() => {\n"
        "  const stationResults = [\n"
        "    { name: 'spec-critic-nfr-security', verdict: 'NEEDS_REVISION', interventions: ["
        "        { bucket: 'B', text: 'missing rate-limit NFR', critic_found: true },\n"
        "        { bucket: 'A', text: 'not critic-found', critic_found: false },\n"
        "    ] },\n"
        "    { name: 'spec-critic-missing-object', verdict: 'NEEDS_REVISION', interventions: ["
        "        { bucket: 'C', text: 'missing scheduler actor', critic_found: true },\n"
        "    ] },\n"
        "  ];\n"
        "  const out = renderLedger({ changeId: 'toy-change' }, stationResults);\n"
        "  if (!out.includes('Critic-found rows: 2')) {\n"
        "    console.error('FAIL: expected \"Critic-found rows: 2\" in rendered ledger, got:\\n' + out);\n"
        "    process.exit(1);\n"
        "  }\n"
        "  console.log('OK');\n"
        "  process.exit(0);\n"
        "})();\n"
    )
    result = subprocess.run(
        ["node", "-e", harness], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, (
        f"behavioral probe failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "OK" in result.stdout
