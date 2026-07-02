// loom-pipeline driver — MAIN dispatch module (concat order: driver_90_*).
//
// CONCAT CONTRACT: see driver_00_header.js. This is the LAST module in
// filename order — build_driver.py concatenates driver_NN_*.js files
// 00 < 10 < 20 < 30 < 40 < 50 < 60 < 90, so every function declaration from
// every earlier module (guardArgs, runSegment1/2/3, renderLedger,
// writeLedger, runStation, recordLedger, ...) is already hoisted into scope
// by the time this file's own top-level statements run. THIS FILE is where
// the assembled Workflow script's execution actually starts.
//
// CROSS-MODULE CONTRACT (pinned):
// - guardArgs(args) — driver_10_guard.js
// - runSegment1(args) / runSegment2(args) / runSegment3(args) —
//   driver_30_seg1.js / driver_40_seg2.js / driver_50_seg3.js
// - renderLedger(args, stationResults) + writeLedger(args, stationResults) —
//   driver_60_ledger.js
// - Workflow runtime globals used below (available at actual Workflow run
//   time only, NOT when this file is checked/tested in isolation): `agent`,
//   `phase`, `log`, `budget`, `args`.
//
// SYNTAX-CHECK NOTE: the top-level statements at the bottom of this file
// (top-level `await` + a bare top-level `return`) are only valid JS inside
// a module top-level body (ESM) or an async function body — NOT in a bare
// CommonJS script parse. The ASSEMBLED asset (build_driver.py's
// concatenated output) is auto-detected as ESM by Node because
// driver_00_header.js's `export const meta = ...` appears earlier in the
// same concatenated file, so `node --check` on the assembled asset passes
// (already exercised by test_pipeline_driver_build.py). This module's own
// dedicated test (test_pipeline_driver_main.py) therefore wrap-checks this
// file's syntax in isolation (wraps its body in `async function __wrap() {
// ... }` before invoking `node --check`) rather than asserting a raw
// isolated `node --check` — mirroring the working top-level shape found in
// the landed loom-pipeline-dogfood Workflow script (top-level await, final
// bare `return {...}`), which this file's own top-level statements copy.

// ---- mainDispatch: segment router + run-summary builder --------------------

// mainStationLabel(stationResult) — prefers the real `station` field every
// segment module (driver_30/40/50) now attaches at each STATION-result push/
// construction site; falls back to `.name` (driver_60_ledger.js's own
// renderStationTable reads the identical `s.station || s.name` order) and
// finally 'unknown' as a defensive floor that should never fire in practice.
function mainStationLabel(stationResult) {
  return (stationResult && (stationResult.station || stationResult.name)) || 'unknown'
}

// mainBuildVerdicts(stationResults) — POSITIONAL array of {station, verdict},
// one entry per STATION result, in call order. Replaces a prior
// name-keyed-object shape that silently collapsed same-named (or unnamed,
// i.e. every entry before this fix) stations onto one key — a later
// station's verdict overwrote an earlier one's, losing data. An array never
// collapses: every station's verdict survives regardless of name collisions.
function mainBuildVerdicts(stationResults) {
  return (stationResults || []).map((s) => ({
    station: mainStationLabel(s),
    verdict: s && s.verdict,
  }))
}

// mainDispatch(args) — guard, route to the segment named by args.segment,
// render + write the ledger for EVERY segment (not just segment 3), then
// return the machine-readable run summary the entry skill relays.
async function mainDispatch(args) {
  // guardArgs returns the validated args — and may have PARSED them from a
  // JSON string (harness stringification, observed live wf_e96f6d0d-140);
  // everything below must use the returned object, not the raw input.
  args = guardArgs(args)

  // Live finding wf_ff22820b-61d: budget.spent() is TURN-scoped (shared
  // pool across the main loop and all workflows this turn), so comparing
  // it raw against args.budgets.run is apples/oranges. Capture a baseline
  // here and report THIS RUN's delta everywhere (summary + ledger).
  const runSpentBaseline =
    typeof budget !== 'undefined' && typeof budget.spent === 'function'
      ? budget.spent()
      : null

  let stationResults
  if (args.segment === 1) {
    stationResults = await runSegment1(args)
  } else if (args.segment === 2) {
    stationResults = await runSegment2(args)
  } else if (args.segment === 3) {
    stationResults = await runSegment3(args)
  } else {
    // guardArgs already restricts segment to {1, 2, 3} — this branch is
    // defense in depth and should never fire in a real run.
    throw new Error(
      'mainDispatch: fail-loud: unexpected args.segment ' + JSON.stringify(args.segment) +
      ' — guardArgs should already have rejected this.'
    )
  }

  // Thread this run's spend into the ledger (renderBudgetSection reads
  // args.budgetSpent; 'n/a' when the budget primitive is unavailable).
  if (runSpentBaseline !== null && typeof budget !== 'undefined') {
    args.budgetSpent = budget.spent() - runSpentBaseline
  }
  const ledgerMarkdown = renderLedger(args, stationResults)
  log(`segment ${args.segment}: ledger rendered (${ledgerMarkdown.length} chars)`)
  await writeLedger(args, stationResults)

  const runSpent =
    runSpentBaseline !== null && typeof budget !== 'undefined'
      ? budget.spent() - runSpentBaseline
      : null

  return {
    segment: args.segment,
    stations: (stationResults || []).map(mainStationLabel),
    verdicts: mainBuildVerdicts(stationResults),
    budget: {
      run: args.budgets.run,
      // `spent` is THIS RUN's delta of the turn-scoped budget.spent()
      // pool (baseline captured at dispatch start) — comparable against
      // args.budgets.run, unlike the raw turn total. A resumed run
      // (resumeFromRunId) starts a fresh count.
      spent: runSpent,
    },
  }
}

// ---- top-level execution -----------------------------------------------------
//
// Workflow scripts run top-level statements in an async context; `args` is
// the Workflow-provided global (see driver_10_guard.js's guardArgs, which
// this dispatches into first). Mirrors the landed loom-pipeline-dogfood
// Workflow script's own top-level shape: top-level `await`, then a bare
// final `return` — the mechanism by which a Workflow script produces its
// result value.

const runSummary = await mainDispatch(args)
return runSummary
