"""Structural + behavioral tests for driver_90_main.js — the FINAL module in
the build-assembled Workflow driver (see
docs/loom/plans/2026-07-03-loom-pipeline-conductor.md Task 13): the segment
dispatcher (mainDispatch) plus the top-level execution statements that are
the actual Workflow-script entry point.

SYNTAX-CHECK CHOICE: this file, in isolation, ends with a top-level `await`
+ a bare top-level `return` — valid ONLY inside a module top-level body
(ESM) or an async function body, never in a bare CommonJS script parse (a
throwaway-file spike confirmed: `node --check` fails on top-level `await`
when no `export`/`import` token appears anywhere in the file, exactly the
shape of this module in isolation). The REAL assembled asset
(build_driver.py's concatenated output, already exercised by
test_pipeline_driver_build.py) is auto-detected as ESM because
driver_00_header.js's `export const meta = ...` appears earlier in the same
concatenated file — so this exact top-level shape is proven syntactically
valid there. This test therefore WRAP-CHECKS driver_90_main.js's syntax in
isolation (wraps its full body text in `async function __wrap() { ... }`
before `node --check`) rather than asserting a raw isolated `node --check`
on this file alone — mirroring how the landed loom-pipeline-dogfood
Workflow script's own top-level `await`/`return` pattern only parses inside
a module or async-function context.
"""
import re
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
MODULE_PATH = SCRIPTS_DIR / "driver_90_main.js"
GUARD_PATH = SCRIPTS_DIR / "driver_10_guard.js"
RUNSTATION_PATH = SCRIPTS_DIR / "driver_20_runstation.js"
SEG2_PATH = SCRIPTS_DIR / "driver_40_seg2.js"
LEDGER_PATH = SCRIPTS_DIR / "driver_60_ledger.js"

TOP_LEVEL_MARKER = "// ---- top-level execution"


def test_segment_routing():
    # @req: REQ-LOOM-PIPELINE-MAIN-1
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"
    source = MODULE_PATH.read_text(encoding="utf-8")

    # -- wrap-checked syntax (see module docstring above) --
    wrapped = "async function __wrap() {\n" + source + "\n}\n"
    wrap_path = SCRIPTS_DIR / "_tmp_wrapcheck_driver_90_main.js"
    wrap_path.write_text(wrapped, encoding="utf-8")
    try:
        result = subprocess.run(
            ["node", "--check", str(wrap_path)], capture_output=True, text=True
        )
        assert result.returncode == 0, f"wrap-checked node --check failed: {result.stderr}"
    finally:
        wrap_path.unlink(missing_ok=True)

    # public dispatcher name exactly mainDispatch
    assert "async function mainDispatch(" in source

    # routes to all three segments
    assert "runSegment1(" in source
    assert "runSegment2(" in source
    assert "runSegment3(" in source

    # guardArgs called before routing
    guard_idx = source.index("guardArgs(")
    seg1_idx = source.index("runSegment1(args)")
    assert guard_idx < seg1_idx, "guardArgs must run before segment routing"

    # every segment run renders + writes the ledger (not just segment 3)
    assert "renderLedger(" in source
    assert "writeLedger(" in source

    # default-branch throws (defense in depth — guardArgs already restricts
    # segment to {1,2,3})
    assert "throw new Error" in source

    # run summary fields: machine-readable, relayed by the entry skill
    for field in ["segment", "stations", "verdicts", "budget"]:
        assert re.search(rf"\b{field}\b", source), f"run summary must expose `{field}`"

    # budget.spent() read wrapped in the same typeof-guard convention as
    # driver_20_runstation.js / driver_60_ledger.js
    assert (
        "typeof budget !== 'undefined'" in source
        or 'typeof budget !== "undefined"' in source
    )

    # the station-collapse LOOM-SIMPLIFY marker's ceiling event was THIS
    # task (a task editing driver_30/40/50 to attach a real station field to
    # every STATION result) — it must be gone now that the upgrade executed.
    assert "LOOM-SIMPLIFY" not in source, (
        "the station-identification LOOM-SIMPLIFY marker must be removed — "
        "its ceiling event (a task attaching real station names in "
        "driver_30/40/50) is this very change"
    )

    # budget-scope comment: spent() is THIS INVOCATION's turn-scoped count,
    # not a cumulative cross-run total — grounded in the Workflow tool's
    # budget primitive docs (shared per-turn pool across the main loop and
    # all workflows); a resumed run starts a fresh turn count.
    assert "turn-scoped" in source, (
        "missing the budget-scope comment above the summary's budget field"
    )
    assert "resumeFromRunId" in source, (
        "the budget-scope comment must call out that a resumed run starts a "
        "fresh turn count"
    )

    # top-level execution: bare top-level await + return, mirroring the
    # landed loom-pipeline-dogfood Workflow script's own top-level shape
    assert TOP_LEVEL_MARKER in source
    assert re.search(r"^const \w+ = await mainDispatch\(args\)", source, re.MULTILINE)
    assert re.search(r"^return \w+", source, re.MULTILINE)

    # NO LEDGER / recordLedger DECLARATION here — declared only in
    # driver_60_ledger.js.
    assert not re.search(r"\b(function|const|let|var)\s+recordLedger\b", source), (
        "driver_90_main.js must not DECLARE recordLedger"
    )
    assert not re.search(r"\b(const|let|var)\s+LEDGER\b", source), (
        "driver_90_main.js must not DECLARE LEDGER"
    )

    # self-contained: no imports, no non-deterministic clock/random tokens
    assert "import " not in source
    assert "require(" not in source
    for token in ["Date.now(", "Math.random(", "new Date()"]:
        assert token not in source, f"forbidden token present: {token}"


def test_segment2_routing_behavioral():
    """Execution-level probe: concatenate driver_10 (guardArgs) + driver_20
    (runStation/RALLY_CAP) + driver_40 (runSegment2) + driver_60
    (LEDGER/recordLedger/renderLedger/writeLedger) with driver_90_main.js's
    FUNCTION DEFINITIONS ONLY. Its trailing top-level `await
    mainDispatch(args); return` statements are stripped before concatenation
    (split on TOP_LEVEL_MARKER) — those two bare statements only parse
    inside a module/async-function top level, and re-executing them via
    `node -e` would immediately try to read a Workflow-provided `args`
    global with no runtime behind it. Calling `mainDispatch()` ourselves
    from inside our own async IIFE below exercises the identical routing
    logic without that fragility — the documented fallback the task brief
    allows when driving the literal top-level statements is too brittle.

    Stubs `agent` with a canned station-result shape (mirrors
    test_pipeline_driver_seg2.py's own behavioral-probe stub) and drives
    mainDispatch({segment: 2, ...}) end to end, proving it completes and
    returns a summary with segment: 2 plus populated stations/budget AND a
    `verdicts` POSITIONAL ARRAY of {station, verdict} with >=4 entries whose
    station names are real (non-'unknown') and distinct — the fix for the
    reviewer-found bug where unnamed STATION results collapsed onto a single
    'unknown' key in an object map, silently dropping every verdict but the
    last.

    # @req: REQ-LOOM-PIPELINE-MAIN-1
    """
    main_source = MODULE_PATH.read_text(encoding="utf-8")
    assert TOP_LEVEL_MARKER in main_source, (
        "driver_90_main.js must carry the top-level-execution boundary "
        "comment this test splits on"
    )
    main_defs_only = main_source.split(TOP_LEVEL_MARKER, 1)[0]

    combined_source = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (GUARD_PATH, RUNSTATION_PATH, SEG2_PATH, LEDGER_PATH)
    ) + "\n" + main_defs_only

    harness = combined_source + "\n" + (
        "var budget = { spent: () => 42, remaining: () => 999999 };\n"
        "async function agent(prompt, opts) {\n"
        "  return {\n"
        "    verdict: 'PASS_WITH_NOTES',\n"
        "    artifacts: ['/tmp/x/proposal.md'],\n"
        "    validator_exit: 0,\n"
        "    interventions: [],\n"
        "    summary: 'stub-' + (opts && opts.label),\n"
        "  };\n"
        "}\n"
        "function phase(title) {}\n"
        "function log(msg) {}\n"
        "async function parallel(fns) { return Promise.all(fns.map((fn) => fn())); }\n"
        "\n"
        "(async () => {\n"
        "  const summary = await mainDispatch({\n"
        "    segment: 2, changeId: 'c1', projectPath: '/tmp/x',\n"
        "    skillsRoot: '/tmp/skills',\n"
        "    budgets: { run: 500000, perStation: { spec: 100000, critic: 100000, validator: 100000 } },\n"
        "    models: {},\n"
        "  });\n"
        "\n"
        "  if (summary.segment !== 2) {\n"
        "    console.error('FAIL: expected segment 2, got ' + summary.segment);\n"
        "    process.exit(1);\n"
        "  }\n"
        "  if (!Array.isArray(summary.stations) || summary.stations.length < 4) {\n"
        "    console.error('FAIL: expected >=4 stations, got ' + JSON.stringify(summary.stations));\n"
        "    process.exit(1);\n"
        "  }\n"
        "  if (!Array.isArray(summary.verdicts) || summary.verdicts.length < 4) {\n"
        "    console.error('FAIL: expected verdicts ARRAY with >=4 entries, got ' + JSON.stringify(summary.verdicts));\n"
        "    process.exit(1);\n"
        "  }\n"
        "  var seenStations = {};\n"
        "  for (var vi = 0; vi < summary.verdicts.length; vi++) {\n"
        "    var entry = summary.verdicts[vi];\n"
        "    if (!entry || typeof entry.station !== 'string' || entry.station === 'unknown' || entry.station === '') {\n"
        "      console.error('FAIL: verdicts[' + vi + '] missing a real station name: ' + JSON.stringify(entry));\n"
        "      process.exit(1);\n"
        "    }\n"
        "    if (seenStations[entry.station]) {\n"
        "      console.error('FAIL: duplicate station name in verdicts array: ' + entry.station);\n"
        "      process.exit(1);\n"
        "    }\n"
        "    seenStations[entry.station] = true;\n"
        "    if (typeof entry.verdict === 'undefined') {\n"
        "      console.error('FAIL: verdicts[' + vi + '] missing verdict field: ' + JSON.stringify(entry));\n"
        "      process.exit(1);\n"
        "    }\n"
        "  }\n"
        "  if (!summary.budget || summary.budget.run !== 500000 || summary.budget.spent !== 42) {\n"
        "    console.error('FAIL: expected budget {run:500000, spent:42}, got ' + JSON.stringify(summary.budget));\n"
        "    process.exit(1);\n"
        "  }\n"
        "\n"
        "  console.log('OK');\n"
        "  process.exit(0);\n"
        "})().catch((e) => {\n"
        "  console.error('UNCAUGHT: ' + e.message);\n"
        "  process.exit(1);\n"
        "});\n"
    )

    result = subprocess.run(
        ["node", "-e", harness], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, (
        f"behavioral probe failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "OK" in result.stdout
