// loom-pipeline driver — runStation module (concat order: driver_20_*).
//
// CONCAT CONTRACT: see driver_00_header.js. This module is self-contained —
// no imports, no non-deterministic clock/random reads inline. setTimeout IS
// allowed (used for the wall-clock watchdog below); a scheduled timeout does
// not desync journal replay the way an inline non-deterministic VALUE would.
//
// Supersedes the ad hoc runStation() retry-×2 wrapper from the prior
// loom-pipeline-dogfood driver (session workflows script) with: per-station
// token budget enforcement, a run-level budget floor, a wall-clock watchdog,
// and the AEP-borrowed 4-step recovery ladder (see
// docs/loom/research/2026-07-03-lessons-from-agentic-engineering-patterns.md
// §Borrowed — capped at 4 stages for loom-pipeline, not AEP's 5).

// ---- STATION result schema -------------------------------------------------

function makeStationResult({
  verdict,
  artifacts = [],
  validator_exit = -1,
  interventions = [],
  summary = '',
} = {}) {
  return {
    verdict,
    artifacts,
    validator_exit,
    interventions,
    summary,
  }
}

// ---- constants --------------------------------------------------------------

// Max critic<->writer loop-back rounds. Consumed by later segment modules
// (driver_30_seg1.js design-critic loop, driver_40_seg2.js completeness-critic
// loop) — a station and its critic get at most RALLY_CAP rounds before the
// loop cap fires and the run proceeds with the flagged draft as an
// intervention (decision a human would otherwise arbitrate).
const RALLY_CAP = 2

// Per-station wall-clock watchdog. Generous default: a station may run a
// multi-step skill procedure (reads + subagent dispatch + validator run) —
// 30 minutes gives real headroom before we declare it hung.
const STATION_TIMEOUT_MS = 30 * 60 * 1000

// Per-station default token budgets. Stations that do heavier fan-out
// (critic panels, SDD triads) override these at the call site; this is the
// floor for a single-agent station.
const STATION_TOKEN_BUDGETS = {
  principles: 20000,
  design: 40000,
  'design-critic': 60000,
  spec: 40000,
  'spec-critic': 60000,
  code: 150000,
  review: 60000,
  ledger: 10000,
  'spec-validator': 30000,
  probe: 20000,
}

// ---- stable-prefix dispatch --------------------------------------------------

// stablePrefixDispatch(stablePreamble, payload)
// Returns a single prompt string: a STABLE, cacheable station preamble
// (identical text across rounds/retries so the host can prompt-cache it)
// followed by the per-change payload appended (never prepended — prepending
// would invalidate the cached prefix). The appended contract always ends
// with the StructuredOutput-pinning line: without it, stations tend to end
// on prose and break the orchestrator's parser (F1).
function stablePrefixDispatch(stablePreamble, payload) {
  const contract = [
    payload,
    '',
    'FINAL ACTION CONTRACT (hard requirement): your FINAL action must be the StructuredOutput call — do not end on a prose message.',
  ].join('\n')
  return `${stablePreamble}\n\n${contract}`
}

// ---- recovery ladder ---------------------------------------------------------

// 4-step recovery ladder, attempted once per stage, in order:
//   1. retry-same       — re-run the identical thunk (transient failure)
//   2. re-ground        — re-run with the error text appended to the payload
//   3. fresh-context    — a brand-new agent() dispatch, same contract
//   4. escalate-human   — give up; throw with the full ladder history
const LADDER = ['retry-same', 're-ground', 'fresh-context', 'escalate-human']

// ---- budget resolution + guards ----------------------------------------------

// resolveBudget(name, optsBudget) — resolve the budget primitive for this
// station: opts.budget wins (unit-test injection), else fall back to the
// ambient Workflow global `budget`. The bare identifier is read only behind
// `typeof budget !== 'undefined'` — that guard never throws even when
// `budget` is undeclared anywhere (module-level, standalone `node` load, or
// `node --check`), unlike touching the identifier directly.
//
// Fail loud if neither is available: a station that runs unmetered is worse
// than a station that refuses to run. This shape (budget.spent() /
// budget.remaining()) is grounded in the Workflow tool's budget primitive
// docs and was exercised live in the 2026-07-03 F5 spike (run
// wf_667ec006-ec2) and the loom-pipeline dogfood (source 4a — live
// verification).
function resolveBudget(name, optsBudget) {
  const globalBudget = typeof budget !== 'undefined' ? budget : undefined
  const resolved = optsBudget || globalBudget
  if (!resolved || typeof resolved.spent !== 'function' || typeof resolved.remaining !== 'function') {
    throw new Error(
      `${name}: fail-loud: no budget primitive available — refusing to run unmetered`
    )
  }
  return resolved
}

// checkRunFloor(name, budget, floor) — run-level guard: refuse to start a
// station if the run's remaining budget is already below the floor. Fatal,
// not retryable (marked via err.budgetFatal).
function checkRunFloor(name, budget, floor) {
  const remaining = budget.remaining()
  if (remaining < floor) {
    const err = new Error(
      `${name}: run-level budget guard tripped — remaining ${remaining} below floor ${floor}`
    )
    err.budgetFatal = true
    throw err
  }
}

// checkStationBudget(name, budget, baselineSpent, tokenCap) — cumulative
// per-station token check. IMPORTANT: baselineSpent is captured ONCE at
// runStation start (see below), never re-captured per ladder stage. The
// plan's "budget.spent() delta vs cap" means one delta per STATION across
// the whole ladder — re-baselining per stage would let each stage's own
// delta stay under cap while the station's total blew through it. Fatal,
// not retryable (marked via err.budgetFatal) so the ladder does not advance
// on a budget kill.
function checkStationBudget(name, budget, baselineSpent, tokenCap) {
  const delta = budget.spent() - baselineSpent
  if (delta > tokenCap) {
    const err = new Error(
      `${name}: token budget exceeded — cumulative spend ${delta} over per-station cap ${tokenCap}`
    )
    err.budgetFatal = true
    throw err
  }
}

async function withWatchdog(name, timeoutMs, fn) {
  let timer
  try {
    return await Promise.race([
      fn(),
      new Promise((_, reject) => {
        timer = setTimeout(
          () => reject(new Error(`${name}: station timed out after ${timeoutMs}ms (wall-clock watchdog)`)),
          timeoutMs
        )
      }),
    ])
  } finally {
    clearTimeout(timer)
  }
}

// resolveStageThunk(stage, ctx) — pick the thunk for one ladder stage, or
// return null if the stage is skipped (re-ground/fresh-context with no
// builder supplied — already logged to ctx.history). escalate-human has no
// thunk: it throws, which the runStation loop's own try/catch folds into
// history like any other stage error, then the loop ends and the final
// exhausted-ladder error fires below.
function resolveStageThunk(stage, ctx) {
  const { name, thunk, buildRegroundedThunk, buildFreshContextThunk, lastError, history } = ctx
  if (stage === 'retry-same') {
    return thunk
  }
  if (stage === 're-ground') {
    if (!buildRegroundedThunk) {
      history.push({ stage, skipped: true, reason: 'no re-ground thunk supplied' })
      return null
    }
    return buildRegroundedThunk(lastError ? String(lastError.message || lastError) : '')
  }
  if (stage === 'fresh-context') {
    if (!buildFreshContextThunk) {
      history.push({ stage, skipped: true, reason: 'no fresh-context thunk supplied' })
      return null
    }
    return buildFreshContextThunk()
  }
  // escalate-human: no thunk to run — throw to human with ladder history.
  throw new Error(
    `${name}: exhausted recovery ladder [${history.map((h) => h.stage).join(', ')}] — last error: ${lastError}`
  )
}

// ---- runStation ---------------------------------------------------------------

// runStation(name, thunk, opts) — async wrapper around one station dispatch.
//
// opts:
//   - budget: { spent(): number, remaining(): number } — the Workflow budget
//     primitive (or a compatible shim in tests).
//   - tokenCap: number — this station's token budget (cumulative delta of
//     budget.spent() across the whole call, all ladder stages combined).
//     Falls back to STATION_TOKEN_BUDGETS[name] then a conservative default.
//   - floor: number — run-level remaining-budget floor; if budget.remaining()
//     is already below this before the station starts, fail loud rather than
//     spend into a run that cannot finish.
//   - timeoutMs: per-station watchdog override (defaults to STATION_TIMEOUT_MS).
//   - buildRegroundedThunk(errorText): () => Promise — stage-2 retry, same
//     station with the error text appended to the payload.
//   - buildFreshContextThunk(): () => Promise — stage-3 retry, a brand-new
//     agent() dispatch (fresh context) with the same contract.
async function runStation(name, thunk, opts = {}) {
  const {
    budget: optsBudget,
    tokenCap = STATION_TOKEN_BUDGETS[name] || 20000,
    floor = 0,
    timeoutMs = STATION_TIMEOUT_MS,
    buildRegroundedThunk = null,
    buildFreshContextThunk = null,
  } = opts

  const resolvedBudget = resolveBudget(name, optsBudget)
  checkRunFloor(name, resolvedBudget, floor)
  const baselineSpent = resolvedBudget.spent()

  const history = []
  let lastError = null

  for (const stage of LADDER) {
    try {
      const stageThunk = resolveStageThunk(stage, {
        name,
        thunk,
        buildRegroundedThunk,
        buildFreshContextThunk,
        lastError,
        history,
      })
      if (stageThunk === null) continue

      const result = await withWatchdog(name, timeoutMs, stageThunk)
      checkStationBudget(name, resolvedBudget, baselineSpent, tokenCap)
      return result
    } catch (err) {
      if (err && err.budgetFatal) throw err
      checkStationBudget(name, resolvedBudget, baselineSpent, tokenCap)
      lastError = err
      history.push({ stage, error: String(err && err.message ? err.message : err) })
    }
  }

  throw new Error(
    `${name}: escalate-human — recovery ladder exhausted. History: ${JSON.stringify(history)}`
  )
}
