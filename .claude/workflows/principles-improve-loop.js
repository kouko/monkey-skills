export const meta = {
  name: 'principles-improve-loop',
  description: 'L3 autonomous improvement loop for loom-product-principles: nests the L1 replay matrix (principles-replay-matrix) on visible seeds, proposes ONE mechanical fixer edit per round, verifies it two-stage (win + confirmation re-run) plus a held-out smoke before accepting, and stops itself on a word-cap or plateau brake. Never merges or pushes — output is a human-reviewable proposal branch + round ledger + report.',
  phases: [
    { title: 'Baseline' },
    { title: 'Fix' },
    { title: 'Verify' },
  ],
}

// Workflow runtime contract (grounded in .claude/workflows/principles-replay-matrix.js
// + code-toolkit-sweep.js + loom-pipeline/scripts/driver_*.js — the only in-repo
// Workflow scripts): no non-deterministic timestamp/random calls anywhere — a
// Workflow run can be paused and RESUMED from a journal, and any of those would
// produce a different value on resume than on the original pass, silently
// desyncing this script from what was journaled. Every label this script needs
// (`runLabel`) comes in via `args`, the Workflow-provided ambient global.

// --- args guard (fail-loud; no silent improvisation; mirrors
// principles-replay-matrix.js :41-98) ----------------------------------------

let runArgs = args
if (typeof runArgs === 'string') {
  try {
    runArgs = JSON.parse(runArgs)
  } catch (e) {
    throw new Error(
      'principles-improve-loop: args arrived as a non-JSON string (' +
      runArgs.slice(0, 80) + '...). Refusing to guess.'
    )
  }
}
if (runArgs === null || typeof runArgs !== 'object' || Array.isArray(runArgs)) {
  throw new Error(
    'principles-improve-loop: expected an args object, received ' + String(runArgs) + '.'
  )
}
if (typeof runArgs.runLabel !== 'string' || runArgs.runLabel === '' || runArgs.runLabel === 'undefined') {
  throw new Error(
    'principles-improve-loop: args.runLabel (non-empty string) is required — ' +
    'timestamps/labels must come in via args; this script never generates its own timestamp.'
  )
}
// runLabel becomes a path segment AND is interpolated into nested-workflow
// runLabels below — allow-list rather than deny-list, mirroring matrix
// :63-76 / driver_10_guard.js's changeId guard: a deny-list lets shell-
// metacharacter labels like "foo$(x)" through; an allow-list closes that
// hole by construction.
const RUN_LABEL_ALLOWED_PATTERN = /^[A-Za-z0-9._-]+$/
if (!RUN_LABEL_ALLOWED_PATTERN.test(runArgs.runLabel)) {
  throw new Error(
    'principles-improve-loop: args.runLabel must match ' + RUN_LABEL_ALLOWED_PATTERN +
    ' (letters, digits, dot, underscore, hyphen only) — received ' +
    JSON.stringify(runArgs.runLabel) + '.'
  )
}
if (typeof runArgs.sandboxDir !== 'string' || runArgs.sandboxDir.charAt(0) !== '/') {
  throw new Error(
    'principles-improve-loop: args.sandboxDir must be an absolute path string ' +
    '(received ' + JSON.stringify(runArgs.sandboxDir) + ').'
  )
}
// sandboxDir is forwarded as-is into the nested principles-replay-matrix
// call's own args (which applies this SAME per-segment allow-list itself)
// — validated here too so a malformed value fails loud at THIS script's
// boundary rather than only inside the nested workflow. A leading-'/'
// check alone would let a value like "/tmp/x;evil" through; apply the
// same allow-list per path segment (split on '/', drop the leading empty
// segment produced by the leading '/', reject empty inner segments).
const sandboxDirSegments = runArgs.sandboxDir.split('/').slice(1)
for (const segment of sandboxDirSegments) {
  if (segment === '' || !RUN_LABEL_ALLOWED_PATTERN.test(segment)) {
    throw new Error(
      'principles-improve-loop: args.sandboxDir must be an absolute path whose ' +
      'every segment matches ' + RUN_LABEL_ALLOWED_PATTERN + ' (letters, digits, ' +
      'dot, underscore, hyphen only, no empty segments) — offending segment ' +
      JSON.stringify(segment) + ' in ' + JSON.stringify(runArgs.sandboxDir) + '.'
    )
  }
}

// maxRounds: optional integer, allow-listed to [1, 2, 3] (default 3) —
// consumed by the round loop (Task 5) and the live-smoke override
// (Task 7 passes maxRounds: 1). Allow-listed against a fixed set rather
// than a min/max range comparison, mirroring this file's other guards.
const MAX_ROUNDS_ALLOWED = [1, 2, 3]
let maxRounds = 3
if (runArgs.maxRounds !== undefined) {
  if (typeof runArgs.maxRounds !== 'number' || MAX_ROUNDS_ALLOWED.indexOf(runArgs.maxRounds) === -1) {
    throw new Error(
      'principles-improve-loop: args.maxRounds, when provided, must be one of ' +
      JSON.stringify(MAX_ROUNDS_ALLOWED) + ' — received ' + JSON.stringify(runArgs.maxRounds) + '.'
    )
  }
  maxRounds = runArgs.maxRounds
}

// --- seed split (guardrail 1) ------------------------------------------------
//
// HELD_OUT = cold-operator (the only human-grounded seed) + seed5 (shows
// run-to-run variance across the calibration baseline, making regressions
// visible) — Decision Log #3, docs/loom/plans/2026-07-11-principles-replay-l3-loop.md.
// Held-out seeds and their oracles must NEVER reach any fixer-facing stage
// (Task 4 enforces this at the prompt-construction boundary).
const ALL_SEED_IDS = ['seed1', 'seed2', 'seed3', 'seed4', 'seed5', 'cold-operator']
const HELD_OUT_SEED_IDS = ['cold-operator', 'seed5']
// VISIBLE is derived by EXCLUSION from ALL_SEED_IDS — never an
// independently hardcoded list that could silently drift out of sync with
// ALL_SEED_IDS/HELD_OUT_SEED_IDS as the corpus grows.
const VISIBLE_SEED_IDS = ALL_SEED_IDS.filter((id) => HELD_OUT_SEED_IDS.indexOf(id) === -1)

// --- Baseline phase -----------------------------------------------------------
//
// Nests the existing L1 matrix by name, x2 runs on VISIBLE seeds only,
// aggregated PER SEED (pass-if-any-pass across the 2 runs) — never a single
// scalar. Every nested-workflow() result is null-guarded: it can resolve to
// null OR throw (docs/loom/memory/workflow-agent-results-and-courier-args-need-guards.md);
// the per-run call is `async` with `return await` INSIDE the try — a sync
// try/catch around a returned promise cannot catch its rejection.

phase('Baseline')

async function runBaselineOnce(label) {
  try {
    return await workflow('principles-replay-matrix', {
      runLabel: `${runArgs.runLabel}-${label}`,
      sandboxDir: runArgs.sandboxDir,
      seeds: VISIBLE_SEED_IDS,
    })
  } catch (e) {
    const message = e && e.message ? e.message : String(e)
    log(`baseline:${label}: nested workflow() threw — recording as a hard miss. (${message})`)
    return null
  }
}

const BASELINE_RUN_COUNT = 2
const baselineRuns = []
for (let i = 1; i <= BASELINE_RUN_COUNT; i++) {
  const label = `baseline${i}`
  const result = await runBaselineOnce(label)
  if (!result) {
    log(`baseline:${label}: nested workflow() returned null/no result — recording as a hard miss.`)
  }
  baselineRuns.push(result)
}

const baselineBySeed = {}
for (const id of VISIBLE_SEED_IDS) {
  baselineBySeed[id] = { seedId: id, pass: false, runs: [] }
}
for (const run of baselineRuns) {
  if (!run || !Array.isArray(run.rows)) {
    log('baseline: skipping a null/malformed nested-workflow result during per-seed aggregation.')
    continue
  }
  for (const row of run.rows) {
    if (!row || !row.seedId || !baselineBySeed[row.seedId]) continue
    baselineBySeed[row.seedId].runs.push(row)
    if (row.pass) baselineBySeed[row.seedId].pass = true
  }
}

const baseline = {
  runLabel: runArgs.runLabel,
  seeds: VISIBLE_SEED_IDS,
  bySeed: baselineBySeed,
}

log(
  'baseline complete: ' +
  Object.keys(baselineBySeed).map((id) => `${id}=${baselineBySeed[id].pass ? 'PASS' : 'FAIL'}`).join(', ')
)

// --- Fix phase (STUB — wired in Task 4: fixer stage) --------------------------

phase('Fix')
log('Fix phase: stub — Task 4 adds the fixer agent (schema-forced ONE-invariant proposal) plus apply/revert couriers.')

// --- Verify phase (STUB — wired in Task 5: round loop) ------------------------

phase('Verify')
log('Verify phase: stub — Task 5 adds the round loop (two-stage accept, brakes, ledger, report).')

// TODO(Task 5): replace this placeholder return with the final
// {runLabel, rounds, accepted, ledger} shape once the round loop lands.
return { runLabel: runArgs.runLabel, maxRounds, baseline }
