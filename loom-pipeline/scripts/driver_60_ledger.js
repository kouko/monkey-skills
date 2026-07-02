// loom-pipeline driver — ledger module (concat order: driver_60_*).
//
// CONCAT CONTRACT: see driver_00_header.js. This module is self-contained —
// no imports, no non-deterministic clock/random reads inline.
//
// This module OWNS the shared ledger primitives the segment modules
// (driver_30_seg1.js, driver_40_seg2.js, driver_50_seg3.js — written
// concurrently) call verbatim:
//   - `LEDGER` (array) + `recordLedger(entry)` — every per-judge panel
//     verdict a segment module produces is pushed here as it happens (G5:
//     the ledger must carry every individual judge's verdict, not just a
//     station's aggregate).
//   - `renderLedger(args, stationResults)` — pure function, returns the full
//     ledger markdown as a string. Renders what it is given; computes
//     nothing time-based (no remaining-budget math, no elapsed-time math).
//   - `writeLedger(args, stationResults)` — dispatches a station agent (via
//     the ambient `agent` primitive) to Write the rendered markdown to
//     <projectPath>/docs/loom/<changeId>/pipeline-ledger.md. The driver
//     itself never writes files directly — same no-direct-fs discipline as
//     every other station in this driver.
//
// Intervention bucket shape mirrors
// docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md's "intervention
// ledger — 25 raw entries, triaged into three buckets" section:
//   A. Driver/harness gaps (automatable — fix the machinery, not the human)
//   B. Genuine human gates (keep a person here)
//   C. Capability gaps (build next)
// Segment modules push interventions as { bucket: 'A'|'B'|'C', text }
// entries onto a station result's `interventions` array.

// ---- LEDGER: per-judge panel verdicts (G5) --------------------------------

const LEDGER = []

// recordLedger(entry) — validates entry has at least {station, judge-or-role,
// verdict}; malformed entries throw (fail-loud, per the pinned cross-module
// contract — a silently-dropped judge verdict would defeat G5's whole point:
// "every individual judge's verdict, not just aggregates").
function recordLedger(entry) {
  if (!entry || typeof entry !== 'object') {
    throw new Error('recordLedger: entry must be an object, received ' + String(entry))
  }
  if (typeof entry.station !== 'string' || entry.station === '') {
    throw new Error(
      'recordLedger: entry.station (non-empty string) is required, received ' + JSON.stringify(entry)
    )
  }
  if (entry.judge === undefined && entry.role === undefined) {
    throw new Error(
      'recordLedger: entry requires a "judge" or "role" field, received ' + JSON.stringify(entry)
    )
  }
  if (typeof entry.verdict !== 'string' || entry.verdict === '') {
    throw new Error(
      'recordLedger: entry.verdict (non-empty string) is required, received ' + JSON.stringify(entry)
    )
  }
  LEDGER.push(entry)
  return entry
}

// ---- interventions: 3-bucket flatten --------------------------------------

const INTERVENTION_BUCKETS = [
  { key: 'A', title: 'A. Driver/harness gaps (automatable — fix the machinery, not the human)' },
  { key: 'B', title: 'B. Genuine human gates (keep a person here)' },
  { key: 'C', title: 'C. Capability gaps (build next)' },
]

function renderInterventionBuckets(stationResults) {
  const buckets = { A: [], B: [], C: [] }
  const unbucketed = []

  ;(stationResults || []).forEach((station) => {
    ;(station.interventions || []).forEach((iv) => {
      const label = '[' + (station.name || 'unknown') + '] ' + (iv && iv.text ? iv.text : JSON.stringify(iv))
      if (iv && Object.prototype.hasOwnProperty.call(buckets, iv.bucket)) {
        buckets[iv.bucket].push('- ' + label)
      } else {
        unbucketed.push('- ' + label)
      }
    })
  })

  const sections = INTERVENTION_BUCKETS.map((b) => {
    const items = buckets[b.key]
    return '### ' + b.title + '\n' + (items.length ? items.join('\n') : '- none')
  })

  if (unbucketed.length) {
    sections.push('### Unbucketed (intervention missing a recognized bucket)\n' + unbucketed.join('\n'))
  }

  return sections.join('\n\n')
}

// ---- per-station verdict table ---------------------------------------------

function renderStationTable(stationResults) {
  const rows = (stationResults || []).map((s) => {
    const validatorExit = s.validator_exit !== undefined ? s.validator_exit : 'n/a'
    return '| ' + (s.station || s.name || 'unknown') + ' | ' + (s.verdict || 'n/a') + ' | ' + validatorExit + ' | ' + (s.summary || '') + ' |'
  })
  if (rows.length === 0) {
    rows.push('| (none) | n/a | n/a | n/a |')
  }
  return ['| Station | Verdict | Validator Exit | Summary |', '|---|---|---|---|'].concat(rows).join('\n')
}

// ---- per-judge panel table (G5) --------------------------------------------

function renderJudgePanelTable() {
  const rows = LEDGER.map((entry) => {
    const role = entry.judge !== undefined ? entry.judge : entry.role
    return '| ' + entry.station + ' | ' + role + ' | ' + entry.verdict + ' |'
  })
  if (rows.length === 0) {
    rows.push('| (none recorded) | n/a | n/a |')
  }
  return ['| Station | Judge/Role | Verdict |', '|---|---|---|'].concat(rows).join('\n')
}

// ---- budget section ---------------------------------------------------------

// renderBudgetSection(args) — renders run cap / spent / per-station caps
// exactly as given on args; computes nothing (no remaining = cap - spent
// math, no elapsed-time math — this module has no clock).
function renderBudgetSection(args) {
  const budgets = (args && args.budgets) || {}
  const runCap = budgets.run !== undefined ? budgets.run : 'n/a'
  const spent = args && args.budgetSpent !== undefined ? args.budgetSpent : 'n/a'
  const perStation = budgets.perStation || {}
  const perStationLines = Object.keys(perStation).map((name) => '  - ' + name + ': ' + perStation[name])

  return [
    '- Run cap: ' + runCap,
    '- Spent: ' + spent,
    '- Per-station caps:',
  ]
    .concat(perStationLines.length ? perStationLines : ['  - (none given)'])
    .join('\n')
}

// ---- G2: critic-found false-positive metric --------------------------------

// The false-positive rate itself cannot be known at render time — it needs a
// human to later judge which critic-found rows were legitimate vs
// over-flagged. This section only emits the raw count plus a TBD placeholder
// for that later human judgment (G2 per the plan).
//
// CONTRACT: critic_found is populated on the NESTED
// stationResults[].interventions[] items (see the segment modules' STATION
// schemas, e.g. driver_40_seg2.js's SEG2_STATION_SCHEMA), never on a
// top-level LEDGER entry — no producer sets LEDGER entry.critic_found, so
// this metric counts only the nested field (the real source).
function renderG2Metric(stationResults) {
  const nestedCount = (stationResults || []).reduce((count, station) => {
    const interventions = (station && station.interventions) || []
    return count + interventions.filter((iv) => iv && iv.critic_found === true).length
  }, 0)
  return ['- Critic-found rows: ' + nestedCount, '- Later rejected by human: TBD'].join('\n')
}

// ---- renderLedger: full markdown ledger ------------------------------------

function renderLedger(args, stationResults) {
  const changeId = (args && args.changeId) || 'unknown-change'

  return [
    '# Pipeline Ledger — ' + changeId,
    '',
    '## Per-Station Verdicts',
    '',
    renderStationTable(stationResults),
    '',
    '## Per-Judge Panel Verdicts (G5)',
    '',
    renderJudgePanelTable(),
    '',
    '## Interventions',
    '',
    renderInterventionBuckets(stationResults),
    '',
    '## Budget',
    '',
    renderBudgetSection(args),
    '',
    '## G2 — Critic False-Positive Metric',
    '',
    renderG2Metric(stationResults),
    '',
    '---',
    '',
    'checkpointed run — resume via journal + resumeFromRunId',
    '',
  ].join('\n')
}

// ---- writeLedger: station-agent write --------------------------------------

// writeLedger(args, stationResults) — the driver never writes files
// directly; a station agent with the Write tool does. Same ambient-global
// discipline as driver_20_runstation.js's `typeof budget !== 'undefined'`
// guard: the `agent` primitive is read only behind a typeof check, which
// never throws even when `agent` is undeclared (module-level, standalone
// `node` load, or `node --check`).
async function writeLedger(args, stationResults) {
  const markdown = renderLedger(args, stationResults)
  const ledgerPath = args.projectPath + '/docs/loom/' + args.changeId + '/pipeline-ledger.md'

  const dispatch = typeof agent !== 'undefined' ? agent : undefined
  if (!dispatch) {
    throw new Error(
      'writeLedger: fail-loud: no station-agent dispatch primitive (`agent`) available — ' +
        'the driver never writes files directly; refusing to write ' + ledgerPath + ' without a station agent'
    )
  }

  const prompt = [
    'You are the ledger-writer station. Use the Write tool to write the',
    'markdown content below, verbatim and unmodified, to this exact path:',
    ledgerPath,
    '',
    'Do not alter, summarize, reformat, or truncate the content. The',
    '---BEGIN CONTENT---/---END CONTENT--- markers below are delimiters only',
    'and are NOT part of the file content.',
    '',
    '---BEGIN CONTENT---',
    markdown,
    '---END CONTENT---',
  ].join('\n')

  return dispatch(prompt, { label: 'ledger-writer' })
}
