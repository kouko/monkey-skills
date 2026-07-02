// GENERATED FILE — do not edit; built by loom-pipeline/scripts/build_driver.py from driver_NN_*.js sources.
// Rebuild: python3 loom-pipeline/scripts/build_driver.py

// loom-pipeline driver — HEAD module (concat order: driver_00_*).
//
// CONCAT CONTRACT:
// This file is the head of the assembled Workflow driver asset. The build
// script (loom-pipeline/scripts/build_driver.py, a later task) concatenates
// every `loom-pipeline/scripts/driver_NN_<concern>.js` module IN FILENAME
// ORDER (NN ascending) into ONE self-contained script:
//   loom-pipeline/skills/using-loom-pipeline/assets/loom-pipeline.js
// That assembled asset is the only thing the Workflow tool ever runs.
//
// Rules every module in this concat chain must honor (this file included):
// - NO `import`/`export ... from` of other modules — Workflow scripts cannot
//   import; the entire driver must be one flat, self-contained file after
//   concatenation. (`export const` at top level is fine — it is how the
//   Workflow harness reads `meta` back out of the assembled script.)
// - NO non-deterministic calls: no `Date.now()`, no `Math.random()`, no
//   argless `new Date()`. A Workflow run can be paused and RESUMED from a
//   journal; any of these produce a different value on resume than they did
//   on the original pass, silently desyncing station logic from what was
//   journaled. If a timestamp is genuinely needed, it must be threaded in
//   as an explicit input, never generated inline.
// - Args parsing / validation is NOT this module's job — driver_10_guard.js
//   (a separate task) owns the fail-loud input-contract guard.

export const meta = {
  name: 'loom-pipeline',
  description: 'Deterministic conductor for the loom principles→design→spec→code pipeline',
  phases: [
    { title: 'Principles + Design', detail: 'product-principles (idempotent adopt-if-valid) → design-system + interaction-flows → design-critic panel gate' },
    { title: 'Spec', detail: 'spec-expansion → completeness-critic panel gate → validator exit-0 hard gate' },
    { title: 'Code', detail: 'writing-plans + SDD triad (implementer/spec-reviewer/code-quality-reviewer) under TDD → whole-branch code-reviewer → conditional ui-verification' },
  ],
}

// driver_10_guard.js — fail-loud input contract for the loom-pipeline driver.
//
// F4 (2026-07-03 dogfood): a resumed run rendered every args template slot as
// the literal string "undefined". Ground rules said "make the smallest
// reasonable assumption and proceed" — every station obeyed, intelligently
// and disastrously, and the pipeline silently drifted onto the wrong
// product. guardArgs() closes that hole: any required input that is
// missing, null, empty, or the literal string "undefined" throws instead of
// letting the run improvise.
//
// Self-contained: no imports, no Date.now/Math.random/argless new Date.
// Concatenated after driver_00_header.js in the build; must also parse
// standalone (`node --check`).

function guardArgs(args) {
  var FAIL_LOUD_NOTICE =
    "fail-loud: refusing to improvise missing inputs — no filesystem " +
    "hunting, no substitute seeds; the run FAILS rather than guessing.";
  var REQUIRED_FIELDS = ["segment", "changeId", "projectPath", "budgets", "models"];

  if (args === null || args === undefined || typeof args !== "object") {
    throw new Error(
      "guardArgs: expected an args object, received " + String(args) + ". " +
      FAIL_LOUD_NOTICE
    );
  }

  for (var i = 0; i < REQUIRED_FIELDS.length; i++) {
    var field = REQUIRED_FIELDS[i];
    var value = args[field];
    var isMissing =
      value === undefined ||
      value === null ||
      value === "" ||
      value === "undefined";
    if (isMissing) {
      throw new Error(
        'guardArgs: required input "' + field + '" is missing or invalid ' +
        "(received " + JSON.stringify(value) + "). " + FAIL_LOUD_NOTICE
      );
    }
  }

  // resumeRunId is optional, but the F4 leak was a literal "undefined"
  // string regardless of whether the field was required — guard it too.
  if (
    Object.prototype.hasOwnProperty.call(args, "resumeRunId") &&
    args.resumeRunId === "undefined"
  ) {
    throw new Error(
      'guardArgs: optional input "resumeRunId" leaked the literal string ' +
      '"undefined" (received "undefined"). ' + FAIL_LOUD_NOTICE
    );
  }

  // skillsRoot is optional at this guard layer (only segment 2 needs it —
  // driver_40_seg2.js throws its own fail-loud error when it is missing
  // there); when present it gets the same F4 "undefined"-string leak guard
  // as resumeRunId, plus an absolute-path shape check like projectPath.
  if (Object.prototype.hasOwnProperty.call(args, "skillsRoot")) {
    if (args.skillsRoot === "undefined") {
      throw new Error(
        'guardArgs: optional input "skillsRoot" leaked the literal string ' +
        '"undefined" (received "undefined"). ' + FAIL_LOUD_NOTICE
      );
    }
    if (typeof args.skillsRoot !== "string" || args.skillsRoot.charAt(0) !== "/") {
      throw new Error(
        'guardArgs: "skillsRoot", when present, must be an absolute path ' +
        'starting with "/" (received ' + JSON.stringify(args.skillsRoot) + "). " +
        FAIL_LOUD_NOTICE
      );
    }
  }

  if (args.segment !== 1 && args.segment !== 2 && args.segment !== 3) {
    throw new Error(
      'guardArgs: "segment" must be one of 1, 2, 3 (received ' +
      JSON.stringify(args.segment) + "). " + FAIL_LOUD_NOTICE
    );
  }

  if (typeof args.projectPath !== "string" || args.projectPath.charAt(0) !== "/") {
    throw new Error(
      'guardArgs: "projectPath" must be an absolute path starting with "/" ' +
      "(received " + JSON.stringify(args.projectPath) + "). " + FAIL_LOUD_NOTICE
    );
  }

  // changeId becomes a path segment (docs/loom/<changeId>/...) — allow-list
  // rather than deny-list: only [A-Za-z0-9._-] is safe there. A deny-list
  // (reject "/" and "..") lets shell-metacharacter ids like "foo$(x)"
  // through; an allow-list closes that hole by construction.
  var CHANGE_ID_ALLOWED_PATTERN = /^[A-Za-z0-9._-]+$/;
  if (!CHANGE_ID_ALLOWED_PATTERN.test(args.changeId) || args.changeId.indexOf("..") !== -1) {
    throw new Error(
      'guardArgs: "changeId" must match ' + CHANGE_ID_ALLOWED_PATTERN +
      " (letters, digits, dot, underscore, hyphen only; no \"..\") " +
      "(received " + JSON.stringify(args.changeId) + "). " + FAIL_LOUD_NOTICE
    );
  }

  return args;
}

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

// loom-pipeline driver — segment 1 module (concat order: driver_30_*).
//
// CONCAT CONTRACT: see driver_00_header.js. Self-contained — no imports, no
// Date.now/Math.random/argless new Date. `node --check` must pass on this
// file standalone (the build script concatenates it after driver_00_header.js
// / driver_10_guard.js / driver_20_runstation.js in Task 14).
//
// CROSS-MODULE CONTRACT (pinned — other modules are being written
// concurrently; see docs/loom/plans/2026-07-03-loom-pipeline-conductor.md
// Task 9):
// - Consumes runStation / stablePrefixDispatch / makeStationResult /
//   RALLY_CAP from driver_20_runstation.js (already landed).
// - Consumes recordLedger(entry) / LEDGER from driver_60_ledger.js (Task 12,
//   concurrent) — DECLARED THERE, NOT HERE. This module must never declare
//   LEDGER or recordLedger itself (would collide at concat time).
// - Public entry point name is exactly `runSegment1` — driver_90_main.js
//   (Task 13) routes `args.segment === 1` to it.
// - Workflow runtime globals used here (available at actual Workflow run
//   time only, NOT under `node --check`): agent, phase, log, budget, args.

// ---- Segment 1: Principles + Design ----------------------------------------

// Verbatim copy of driver_00_header.js meta.phases[0].title. Kept as a
// literal (not read from the header file at runtime — this module has no
// import/require of sibling modules) but the RED test cross-checks it
// against the header source so drift fails loud in CI rather than silently.
const SEGMENT_1_PHASE_TITLE = 'Principles + Design'

// ---- principles station (idempotent adopt-if-valid) ------------------------

// Structural validity check for an ALREADY-FETCHED PRINCIPLES.md text blob.
// This module has no filesystem access of its own (Workflow scripts do not
// import fs) — the station agent reads the file with its own tools and
// reports the text back; this helper is the shared adopt-vs-generate rule
// both the station prompt and any future programmatic check apply. A valid
// PRINCIPLES.md carries a north-star statement plus at least one principle
// with a falsifiable "— check:" clause (product-principles' own contract).
function isPrinciplesStructurallyValid(text) {
  if (!text) return false
  var hasNorthStar = /north.?star/i.test(text)
  var hasFalsifiableCheck = /[—-]\s*check:/i.test(text)
  return hasNorthStar && hasFalsifiableCheck
}

const PRINCIPLES_STABLE_PREAMBLE = [
  'STATION: principles (idempotent adopt-if-valid gate).',
  'Check whether <projectPath>/docs/loom/PRINCIPLES.md already exists.',
  '- If it exists AND is structurally valid (a north-star statement plus at',
  '  least one principle carrying a falsifiable "— check:" clause): ADOPT it',
  '  as-is. Do NOT rewrite it. Your STATION verdict summary must say the file',
  '  was adopted, not authored (cost-cut intervention, not a fresh artifact).',
  '  Include a `principles_text_head` field in your structured summary with',
  '  the first ~80 lines of the file, verbatim, so the driver can re-verify',
  '  the adopt decision against the real file content rather than trusting',
  '  your self-report alone.',
  '- Otherwise: load the `loom-product-principles:product-principles` skill',
  '  via the Skill tool and follow it faithfully to generate PRINCIPLES.md.',
  '  Do NOT improvise principles outside the skill — fail-loud per the guard',
  '  doctrine; no ad hoc constitution invented on the station\'s own judgment.',
].join('\n')

function buildPrinciplesThunk(projectPath, agentOpts) {
  return async () => {
    const payload = [
      `Project path: ${projectPath}`,
      `Artifact under check: ${projectPath}/docs/loom/PRINCIPLES.md`,
    ].join('\n')
    const prompt = stablePrefixDispatch(PRINCIPLES_STABLE_PREAMBLE, payload)
    return agent(prompt, agentOpts)
  }
}

// reconcilePrinciplesAdoption(principlesResult) — wires
// isPrinciplesStructurallyValid against the ACTUAL PRINCIPLES.md content
// instead of leaving it a dead helper. The principles station's stable
// preamble (above) instructs the agent to report the fetched file's text
// head (first ~80 lines, field `principles_text_head`) whenever it claims to
// ADOPT. If the station claims adopt but the reported text head fails the
// shared structural rule, do not trust the self-report: downgrade to
// NEEDS_REVISION and record an intervention — falling through as if the
// file needed generation, rather than silently accepting an invalid adopt.
function reconcilePrinciplesAdoption(principlesResult) {
  const claimsAdopted = /adopt/i.test((principlesResult && principlesResult.summary) || '')
  if (!claimsAdopted) return principlesResult
  const textHead = principlesResult && principlesResult.principles_text_head
  if (isPrinciplesStructurallyValid(textHead)) return principlesResult
  return Object.assign({}, principlesResult, {
    verdict: 'NEEDS_REVISION',
    interventions: (principlesResult.interventions || []).concat([
      {
        kind: 'decision',
        description: 'principles station claimed ADOPT but the reported PRINCIPLES.md text head fails the structural adopt-rule (north-star + falsifiable "— check:" clause) — treated as a generation gap, not a silently-accepted adopt',
        agent_fallback: 'verdict overridden to NEEDS_REVISION rather than trusting the adopt claim; a human or re-run should regenerate PRINCIPLES.md',
      },
    ]),
  })
}

// ---- design station ----------------------------------------------------------

const DESIGN_STABLE_PREAMBLE = [
  'STATION: design generators.',
  'Load `loom-interface-design:design-system` and',
  '`loom-interface-design:interaction-flows` via the Skill tool and follow',
  'both faithfully to produce <projectPath>/docs/loom/DESIGN.md and the',
  'per-change <projectPath>/docs/loom/<changeId>/ui-flows.md. Every emitted',
  'artifact MUST carry a Decisions section (what / why / rejected',
  'alternatives) — absence is a G3 finding, not silently accepted.',
  'AFTER writing both artifacts, Read each file back from disk (not from',
  'memory) and check whether it actually contains a Decisions heading. In',
  'your structured summary, include one machine-parsable line per artifact',
  'in the exact form `DECISIONS_SECTION: present` or',
  '`DECISIONS_SECTION: absent` — computed against the real file content you',
  'just read, never a self-reported guess.',
].join('\n')

function buildDesignThunk(projectPath, changeId, critique, agentOpts) {
  return async () => {
    const payload = [
      `Project path: ${projectPath}`,
      `Change id: ${changeId}`,
      critique
        ? `CRITIC FINDINGS TO ADDRESS (augment, do not rewrite):\n${critique}`
        : '',
    ].filter(Boolean).join('\n')
    const prompt = stablePrefixDispatch(DESIGN_STABLE_PREAMBLE, payload)
    return agent(prompt, agentOpts)
  }
}

// ---- design-critic panel (writer!=judge, SCRIPT-layer fan-out) --------------

// Distinct lens personas dispatched as SEPARATE fresh-context agent() calls
// — the writer!=judge structural requirement lives HERE at the script
// layer, never folded into one station agent grading its own draft. Each
// entry becomes its own agent() call site (loop below), never a shared
// context across lenses.
const DESIGN_CRITIC_LENSES = [
  {
    name: 'render-state-completeness',
    persona: 'a confused first-time user hunting for the empty/loading/error/success render-state variants',
  },
  {
    name: 'dead-end-and-exit',
    persona: 'a 3am on-call engineer hunting for dead-ends and missing exit/undo affordances',
  },
]

function buildCriticLensPrompt(projectPath, changeId, lens) {
  return [
    "You are a fresh-context lens-critic on the loom-interface-design:design-critic panel.",
    'Load the `loom-interface-design:design-critic` skill via the Skill tool',
    '(and its references/design-heuristics.md) and follow it faithfully.',
    `Lens: ${lens.name}. Persona: ${lens.persona}.`,
    `Artifacts under critique: ${projectPath}/docs/loom/DESIGN.md and ${projectPath}/docs/loom/${changeId}/ui-flows.md.`,
    'Tag every critic-originated addition as critic-found in place — never',
    "overwrite the writer's content, only augment it.",
    'Return exactly ONE two-valued verdict token: PASS_WITH_NOTES or',
    'NEEDS_REVISION (never a bare PASS).',
    'FINAL ACTION CONTRACT (hard requirement): your FINAL action must be the',
    'StructuredOutput call — do not end on a prose message.',
  ].join('\n')
}

// INVARIANT: no naked agent() calls in segment modules — every dispatch
// site in this file (principles / design / each critic lens) is wrapped by
// runStation() so the watchdog, token budget, and recovery ladder apply
// uniformly. A hung lens must not hang the segment.
function buildCriticLensThunk(projectPath, changeId, lens, agentOpts) {
  return async () => {
    const prompt = buildCriticLensPrompt(projectPath, changeId, lens)
    return agent(prompt, agentOpts)
  }
}

// runDesignCriticPanel — dispatches each lens through runStation('design-critic',
// thunk, {...}) (see INVARIANT above), then pushes EACH judge's individual
// verdict to the ledger (G5: per-judge verdicts, not one folded panel
// verdict). Returns the array of per-lens verdict results so the caller can
// decide whether to loop back.
async function runDesignCriticPanel(projectPath, changeId, round, budgets, models) {
  const perStation = budgets.perStation || {}
  const verdicts = []
  for (const lens of DESIGN_CRITIC_LENSES) {
    const thunk = buildCriticLensThunk(projectPath, changeId, lens, {
      label: `design-critic:${lens.name} r${round}`,
      phase: SEGMENT_1_PHASE_TITLE,
      model: models['design-critic'],
    })
    const result = await runStation('design-critic', thunk, {
      tokenCap: perStation['design-critic'],
    })
    recordLedger({ station: `design-critic:${lens.name}`, judge: lens.name, ...result })
    verdicts.push({ lens: lens.name, ...result })
  }
  return verdicts
}

function panelNeedsRevision(verdicts) {
  return verdicts.some((v) => v.verdict === 'NEEDS_REVISION')
}

function collectCritique(verdicts) {
  return verdicts
    .filter((v) => v.verdict === 'NEEDS_REVISION')
    .map((v) => `[${v.lens}] ${v.summary || ''}`)
    .join('\n')
}

// ---- G3: Decisions-section presence check -----------------------------------

// This check does NOT grade the design station's self-reported prose summary
// against a heading regex — that would just trust the writer's own blurb
// (false-positive or false-pass either way). Instead the design station's
// stable preamble (above) instructs the agent to Read each emitted artifact
// back from disk AFTER writing it and report a machine-parsable
// `DECISIONS_SECTION: present` or `DECISIONS_SECTION: absent` line, computed
// against the real file content. This script only PARSES that field from
// the station's structured summary and gates on it.

// parseDecisionsSectionField(summary) — extracts the DECISIONS_SECTION
// token's value from the design station's structured summary, or null if
// the field is missing entirely.
function parseDecisionsSectionField(summary) {
  if (typeof summary !== 'string') return null
  const match = summary.match(/DECISIONS_SECTION:\s*(present|absent)/i)
  return match ? match[1].toLowerCase() : null
}

function checkDecisionsSection(designResult) {
  const field = parseDecisionsSectionField(designResult && designResult.summary)
  if (field === 'present') return null
  return {
    kind: 'missing-info',
    description: 'design station reported DECISIONS_SECTION: absent (or omitted the field) for its emitted artifacts — G3 check',
    agent_fallback: 'recorded as an intervention on the design STATION result rather than silently accepted',
  }
}

// ---- runSegment1 --------------------------------------------------------------

// runSegment1(args) — principles (idempotent adopt-if-valid) -> design ->
// design-critic panel (writer!=judge, rally-capped) -> G3 Decisions check.
// Returns an array of STATION results.
async function runSegment1(args) {
  phase('Principles + Design')

  const { projectPath, changeId, budgets = {}, models = {} } = args
  const perStation = budgets.perStation || {}
  const stations = []

  // -- principles station --
  const principlesThunk = buildPrinciplesThunk(projectPath, {
    label: 'principles',
    phase: SEGMENT_1_PHASE_TITLE,
    model: models.principles,
  })
  const principlesResult = reconcilePrinciplesAdoption(
    await runStation('principles', principlesThunk, {
      tokenCap: perStation.principles,
    })
  )
  recordLedger({ station: 'principles', role: 'station', ...principlesResult })
  principlesResult.station = 'principles'
  stations.push(principlesResult)

  // -- design + design-critic panel, rally-capped --
  let critique = null
  let designResult = null
  let panelVerdicts = []
  let unresolved = true

  for (let round = 1; round <= RALLY_CAP; round++) {
    const designThunk = buildDesignThunk(projectPath, changeId, critique, {
      label: `design r${round}`,
      phase: SEGMENT_1_PHASE_TITLE,
      model: models.design,
    })
    designResult = await runStation('design', designThunk, {
      tokenCap: perStation.design,
    })
    recordLedger({ station: `design r${round}`, role: 'station', ...designResult })
    designResult.station = `design r${round}`
    stations.push(designResult)

    panelVerdicts = await runDesignCriticPanel(projectPath, changeId, round, budgets, models)

    if (!panelNeedsRevision(panelVerdicts)) {
      unresolved = false
      break
    }
    critique = collectCritique(panelVerdicts)
  }

  if (unresolved) {
    // rally cap exhausted, still NEEDS_REVISION — fail-loud, not a silent
    // accept: surface the unresolved gap as its own STATION-shaped record.
    const unresolvedResult = makeStationResult({
      verdict: 'NEEDS_REVISION',
      artifacts: [],
      validator_exit: -1,
      interventions: [
        {
          kind: 'decision',
          description: `design-critic panel still NEEDS_REVISION after ${RALLY_CAP} rounds — a human would arbitrate`,
          agent_fallback: 'proceeded with the flagged draft; surfaced unresolved rather than silently accepting it',
        },
      ],
      summary: `design-critic rally cap (${RALLY_CAP}) exhausted, unresolved`,
    })
    unresolvedResult.station = 'design-critic'
    stations.push(unresolvedResult)
  }

  // -- G3: Decisions-section presence check on the (final) design artifacts --
  const missingDecisions = checkDecisionsSection(designResult)
  if (missingDecisions && designResult) {
    designResult.interventions = (designResult.interventions || []).concat(missingDecisions)
  }

  return stations
}

// loom-pipeline driver — segment-2 module (concat order: driver_40_*).
//
// CONCAT CONTRACT: see driver_00_header.js. This module is self-contained —
// no imports, no non-deterministic clock/random reads inline.
//
// Implements pipeline segment 2 (docs/loom/plans/2026-07-03-loom-pipeline-conductor.md
// Task 10): spec-expansion (writer, seeded from segment-1 artifact PATHS) →
// completeness-critic panel (script-layer fan-out, >=2 fresh-context lenses,
// RALLY_CAP loop-back, G5 per-judge ledger) → hard validator gate
// (validate_spec_output.py exit 0, no adopt-anyway) → G3 Decisions-section
// presence check.
//
// Depends on runStation / stablePrefixDispatch / makeStationResult /
// RALLY_CAP from driver_20_runstation.js and on recordLedger() declared in
// driver_60_ledger.js (Task 12, concurrent) — both are REFERENCED here,
// never declared, per the cross-module contract.

// Local STATION result schema for this segment's agent() dispatches — named
// uniquely (SEG2_ prefix) because every driver_NN_*.js module concatenates
// into ONE script scope; a same-named top-level `const` declared by a
// sibling segment module would be a SyntaxError at build time.
const SEG2_STATION_SCHEMA = {
  type: 'object',
  required: ['verdict', 'artifacts', 'validator_exit', 'interventions', 'summary'],
  properties: {
    verdict: { type: 'string', description: 'PASS_WITH_NOTES | NEEDS_REVISION | DONE | FAIL' },
    artifacts: { type: 'array', items: { type: 'string' }, description: 'absolute paths written' },
    validator_exit: { type: 'integer', description: 'exit code of the station validator; -1 if none ran' },
    interventions: {
      type: 'array',
      description: 'every point where a human would normally act',
      items: {
        type: 'object',
        // Shape matches driver_60_ledger.js's renderInterventionBuckets()
        // reader exactly: iv.bucket (one of the 3 INTERVENTION_BUCKETS
        // keys, 'A'|'B'|'C') + iv.text. critic_found flags an item a
        // critic LENS surfaced (vs. a mechanical check like the G3
        // Decisions-heading gate below).
        required: ['bucket', 'text'],
        properties: {
          bucket: { type: 'string', description: "A | B | C — see driver_60_ledger.js's INTERVENTION_BUCKETS" },
          text: { type: 'string' },
          critic_found: { type: 'boolean', description: 'true when a critic lens (not a mechanical check) surfaced this gap' },
        },
      },
    },
    summary: { type: 'string' },
  },
}

// Two lenses from loom-spec/skills/completeness-critic/SKILL.md's fixed
// panel (load-bearing order #1 and #3), dispatched as SEPARATE fresh-context
// agent() calls at the SCRIPT layer — not delegated to the skill's own
// internal fan-out. Fresh context per lens is the mechanism that
// decorrelates the critics (SKILL.md "Fresh context per lens...").
const SEG2_CRITIC_LENSES = [
  {
    name: 'nfr-security',
    persona: 'malicious user / 3am on-call ops',
    focus: 'NFR / security — security, performance/latency, privacy, compliance, a11y, i18n, observability',
  },
  {
    name: 'missing-object-actor',
    persona: 'competitor probing edges',
    focus: 'Missing object / actor — every object the seed implies, every actor (human roles, external systems, schedulers, the anonymous/unauthenticated user)',
  },
]

// G3 rationale-travels-with-artifact (docs/loom/plans/2026-07-03-loom-pipeline-conductor.md
// Task 10 §Decision): loom-spec's real proposal.md templates carry NO
// "## Decisions" heading — it is introduced HERE, by this pipeline's own
// instruction to the writer, never assumed from loom-spec's template.
// seg2ValidatorPreamble's presence check below only makes sense because
// this preamble asks for the section first.
function seg2SpecPreamble(changeDir, seg1Paths, round, critique) {
  const lines = [
    `STATION: spec-expansion (writer)${
      round > 1
        ? ` — revision round ${round}. Address the critic findings below; augment the draft, do not rewrite it.`
        : '.'
    }`,
    'Load the loom-spec:spec-expansion skill via the Skill tool and execute it faithfully.',
    'Seed inputs are given as PATHS ONLY (delegation contract) — read each file yourself; do NOT expect their content inlined in this prompt:',
    `- principles: ${seg1Paths.principles}`,
    `- design: ${seg1Paths.design}`,
    `- ui-flows: ${seg1Paths.uiFlows}`,
    `Produce the change-folder at ${changeDir} (proposal.md + specs/<capability>/spec.md).`,
    'Include a "## Decisions" section in proposal.md: decisions made + why + rejected alternatives (G3 rationale-travels-with-artifact — this heading is required by THIS instruction, not assumed from loom-spec\'s own template).',
  ]
  if (critique) {
    lines.push(`CRITIC FINDINGS TO ADDRESS:\n${critique}`)
  }
  return lines.join('\n')
}

function seg2CriticPreamble(lens, changeDir, round) {
  return [
    `STATION: completeness-critic — lens "${lens.name}" (writer≠judge, fresh context), round ${round}.`,
    `Read loom-spec:completeness-critic SKILL.md for the full panel contract, then apply ONLY this lens: ${lens.focus}`,
    `Persona: ${lens.persona}.`,
    `Draft under critique: ${changeDir} (proposal.md + specs/).`,
    "Write back any critic-found gaps per the skill (provenance-tagged, never overwrite the writer's content), then emit the skill's two-valued §Verdict (PASS_WITH_NOTES | NEEDS_REVISION) as `verdict`.",
  ].join('\n')
}

function seg2ValidatorPreamble(changeDir, validatorScript) {
  return [
    'STATION: spec validator gate.',
    `Run via Bash: python3 ${validatorScript} ${changeDir}`,
    'Report the REAL exit code you observed as `validator_exit` — never assert exit 0 without having actually run the command.',
    `G3: also check ${changeDir}/proposal.md for a "## Decisions" section (decisions made + why + rejected alternatives — required by seg2SpecPreamble's own instruction to the writer, not assumed from loom-spec's template). If it is ABSENT, add one entry to \`interventions\` as {bucket: 'B', text: '<name the gap>'} — a human should supply the missing rationale; do not fabricate a Decisions section just to satisfy this check.`,
  ].join('\n')
}

async function runSegment2(args) {
  const changeId = args.changeId
  const projectPath = args.projectPath
  const budgets = args.budgets || {}
  const perStation = budgets.perStation || {}
  const models = args.models || {}

  if (typeof args.skillsRoot !== 'string' || args.skillsRoot === '') {
    throw new Error(
      'runSegment2: segment 2 requires args.skillsRoot to locate the loom-spec validator — refusing to guess.'
    )
  }
  const validatorScript = args.skillsRoot + '/loom-spec/scripts/validate_spec_output.py'

  const results = []
  const changeDir = `${projectPath}/docs/loom/${changeId}`
  const seg1Paths = {
    principles: `${projectPath}/docs/loom/PRINCIPLES.md`,
    design: `${projectPath}/docs/loom/DESIGN.md`,
    uiFlows: `${changeDir}/ui-flows.md`,
  }

  phase('Spec')

  let critique = null

  for (let round = 1; round <= RALLY_CAP; round++) {
    const specResult = await runStation(
      'spec',
      () =>
        agent(
          stablePrefixDispatch(seg2SpecPreamble(changeDir, seg1Paths, round, critique), `changeId=${changeId}`),
          { label: `spec r${round}`, phase: 'Spec', schema: SEG2_STATION_SCHEMA, model: models.spec || 'sonnet' }
        ),
      { tokenCap: perStation.spec }
    )
    recordLedger({ station: `spec r${round}`, role: 'writer', ...specResult })
    specResult.station = 'spec'
    results.push(specResult)

    // ---- completeness-critic panel: script-layer fan-out, >=2 fresh lenses
    const lensResults = []
    for (const lens of SEG2_CRITIC_LENSES) {
      const lensResult = await runStation(
        'spec-critic',
        () =>
          agent(
            stablePrefixDispatch(seg2CriticPreamble(lens, changeDir, round), `changeId=${changeId}, round=${round}`),
            {
              label: `spec-critic-${lens.name} r${round}`,
              phase: 'Spec',
              schema: SEG2_STATION_SCHEMA,
              model: models.critic || 'sonnet',
            }
          ),
        { tokenCap: perStation.critic }
      )
      // G5: per-judge verdict recorded to the ledger, one entry per lens.
      recordLedger({ station: 'spec-critic', judge: lens.name, round, ...lensResult })
      lensResult.station = `spec-critic:${lens.name}`
      results.push(lensResult)
      lensResults.push(lensResult)
    }

    const anyNeedsRevision = lensResults.some((r) => r.verdict === 'NEEDS_REVISION')
    if (!anyNeedsRevision) break

    critique = lensResults
      .filter((r) => r.verdict === 'NEEDS_REVISION')
      .map((r) => r.summary)
      .join('\n')

    if (round === RALLY_CAP) {
      const unresolved = makeStationResult({
        verdict: 'NEEDS_REVISION',  // same token seg1 uses for rally-cap exhaustion — one vocabulary
        interventions: [
          {
            bucket: 'B',
            text: `completeness-critic panel still NEEDS_REVISION after ${RALLY_CAP} rounds — human would arbitrate (agent fallback: proceeded to the validator gate with the flagged draft)`,
          },
        ],
        summary: `spec-critic loop cap hit (RALLY_CAP=${RALLY_CAP}) — unresolved, failing loud in the segment result`,
      })
      recordLedger({ station: 'spec-critic-gate', role: 'panel', ...unresolved })
      unresolved.station = 'spec-critic'
      results.push(unresolved)
    }
  }

  // ---- validator gate: hard, no adopt-anyway ------------------------------
  const validatorResult = await runStation(
    'spec-validator',
    () =>
      agent(stablePrefixDispatch(seg2ValidatorPreamble(changeDir, validatorScript), `changeId=${changeId}`), {
        label: 'spec-validator',
        phase: 'Spec',
        schema: SEG2_STATION_SCHEMA,
        model: models.validator || 'sonnet',
      }),
    { tokenCap: perStation.validator }
  )
  recordLedger({ station: 'spec-validator', role: 'validator', ...validatorResult })
  validatorResult.station = 'validator'
  results.push(validatorResult)

  if (validatorResult.validator_exit !== 0) {
    throw new Error(
      `runSegment2: spec validator gate FAILED (exit ${validatorResult.validator_exit}) — segment 2 fails loud, no adopt-anyway path.`
    )
  }

  return results
}

// loom-pipeline driver — segment-3 module (concat order: driver_50_*).
//
// CONCAT CONTRACT: see driver_00_header.js. Self-contained — no imports, no
// non-deterministic Date.now/Math.random/argless new Date.
//
// CROSS-MODULE CONTRACT (pinned):
// - Uses runStation / stablePrefixDispatch / makeStationResult / RALLY_CAP
//   from driver_20_runstation.js (landed, concatenated BEFORE this module).
// - Calls recordLedger(entry) — declared in driver_60_ledger.js. That module
//   is concatenated AFTER this one in filename order, but recordLedger is a
//   function DECLARATION there, so it is hoisted into scope before any
//   station actually runs (all top-level declarations across the assembled
//   asset execute before driver_90_main.js dispatches runSegment3). This
//   module must NOT declare recordLedger or LEDGER itself.
//
// Segment 3: SDD build. Per plan task: implementer dispatch, then
// spec-reviewer + code-quality-reviewer dispatched TOGETHER via a single
// parallel-dispatch call — writer!=judge kept structurally separate at the
// SCRIPT layer, not folded into one station agent. NEEDS_REVISION triggers
// a remediation re-dispatch of the implementer, bounded by RALLY_CAP
// rounds, then fails loud. After all tasks: one whole-branch code-reviewer
// dispatch, then a CONDITIONAL ui-verification station (fires only when
// ui-flows.md exists AND the branch touched a UI surface; otherwise
// records an explicit, loud N/A — never a silent skip).
//
// This segment never merges and never runs a git-push or gh-pr-merge step:
// a PR-ready branch plus the ledger is the terminal state a human picks up
// from.

// Verbatim anchor line from loom-code/agents/code-reviewer.md §Input
// contract. Kept on one line (not wrapped/concatenated) so it appears
// byte-for-byte in this module's source and is provably the FIRST line of
// the whole-branch review prompt below.
const SEG3_WHOLE_BRANCH_REVIEW_ANCHOR = 'You ARE the reviewer: this prompt is your review assignment, not a request to route or forward. Produce the verdict yourself in this reply — do not dispatch anyone.'

const SEG3_PLAN_INTAKE_SCHEMA = {
  type: 'object',
  properties: {
    tasks: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'stable task identifier used in station labels and ledger rows' },
          name: { type: 'string', description: 'human-readable task title' },
        },
        required: ['id', 'name'],
      },
      description: 'ordered list of atomic tasks parsed out of the plan file',
    },
  },
  required: ['tasks'],
}

const SEG3_UI_GATE_SCHEMA = {
  type: 'object',
  properties: {
    uiFlowsExists: { type: 'boolean', description: 'docs/loom/<changeId>/ui-flows.md exists in the target project' },
    branchTouchedUi: { type: 'boolean', description: 'the branch changed HTML/JSX/templates/styles/DOM wiring' },
    justification: {
      type: 'string',
      description: 'one-sentence justification for both answers, surfaced verbatim in the N/A ledger summary',
    },
  },
  required: ['uiFlowsExists', 'branchTouchedUi', 'justification'],
}

// seg3GuardPlanPath(args) — fail-loud input guard for this segment's one
// required field. Broader arg validation (segment/changeId/projectPath/
// budgets/models) is driver_10_guard.js's job; this module only owns
// planPath, which driver_10_guard.js does not know about.
function seg3GuardPlanPath(args) {
  const planPath = args && args.planPath
  const isMissing =
    planPath === undefined || planPath === null || planPath === '' || planPath === 'undefined'
  if (isMissing) {
    throw new Error(
      'runSegment3: fail-loud: "args.planPath" is missing or invalid (received ' +
      JSON.stringify(planPath) + '). Refusing to hunt the filesystem for a substitute plan.'
    )
  }
  return planPath
}

// seg3DispatchImplementer(planPath, task, opts, remediation) — one
// implementer dispatch. `remediation` is null for the initial attempt, or
// { specReview, qualityReview } to re-ground a remediation round.
async function seg3DispatchImplementer(planPath, task, opts, remediation) {
  const remediationText = remediation
    ? '\n\nRemediation requested — spec-reviewer: ' + JSON.stringify(remediation.specReview) +
      ' code-quality-reviewer: ' + JSON.stringify(remediation.qualityReview)
    : ''

  const prompt = stablePrefixDispatch(
    'You are the loom-pipeline segment-3 implementer for one SDD task, under the TDD iron law.',
    `Plan: ${planPath}\nTask: ${JSON.stringify(task)}${remediationText}`
  )

  const label = remediation
    ? `seg3-implementer-${task.id}-remediation`
    : `seg3-implementer-${task.id}`

  return runStation(
    label,
    () => agent(prompt, { agentType: 'loom-code:implementer', model: opts.models && opts.models.code }),
    { budget: opts.budget, tokenCap: opts.tokenCap }
  )
}

// seg3RunReviewRound(planPath, task, implementerResult, round, reviewOpts) —
// one remediation round: dispatch spec-reviewer + code-quality-reviewer IN
// PARALLEL against the implementer's artifact, then record both individual
// verdicts to the ledger (G5). Extracted out of seg3RunTaskTriad to keep
// that function under the house function-length ceiling
// (naming-and-functions.md).
async function seg3RunReviewRound(planPath, task, implementerResult, round, reviewOpts) {
  const reviewerPrompt = stablePrefixDispatch(
    'You are a loom-pipeline segment-3 reviewer for one SDD task artifact.',
    `Plan: ${planPath}\nTask: ${JSON.stringify(task)}\nArtifact: ${JSON.stringify(implementerResult)}`
  )

  const [specReview, qualityReview] = await parallel([
    () => runStation(
      `seg3-spec-reviewer-${task.id}-r${round}`,
      () => agent(reviewerPrompt, { agentType: 'loom-code:spec-reviewer', model: reviewOpts.models && reviewOpts.models.review }),
      { budget: reviewOpts.budget, tokenCap: reviewOpts.tokenCap }
    ),
    () => runStation(
      `seg3-code-quality-reviewer-${task.id}-r${round}`,
      () => agent(reviewerPrompt, { agentType: 'loom-code:code-quality-reviewer', model: reviewOpts.models && reviewOpts.models.review }),
      { budget: reviewOpts.budget, tokenCap: reviewOpts.tokenCap }
    ),
  ])

  const specVerdict = specReview && specReview.verdict
  const qualityVerdict = qualityReview && qualityReview.verdict

  // G5: every INDIVIDUAL judge's verdict, not a station aggregate — one
  // recordLedger() call per reviewer (driver_60_ledger.js's recordLedger
  // requires {station, judge-or-role, verdict}; it fails loud on anything
  // less, so a missing verdict throws here rather than recording silently).
  recordLedger({ station: `seg3-task-${task.id}`, judge: 'spec-reviewer', verdict: specVerdict, round })
  recordLedger({ station: `seg3-task-${task.id}`, judge: 'code-quality-reviewer', verdict: qualityVerdict, round })

  return {
    specReview,
    qualityReview,
    needsRevision: specVerdict === 'NEEDS_REVISION' || qualityVerdict === 'NEEDS_REVISION',
  }
}

// seg3RunTaskTriad(planPath, task, codeOpts, reviewOpts) — implementer, then
// spec-reviewer + code-quality-reviewer IN PARALLEL, looped up to RALLY_CAP
// remediation rounds. Returns a STATION result on PASS; throws (fail loud)
// if NEEDS_REVISION survives all rounds. `codeOpts` carries the implementer's
// budgets.code token cap; `reviewOpts` carries the reviewers' budgets.perStation.review
// cap — kept separate so a heavier code cap never leaks into judgment-only
// dispatches (G1 per-station granularity).
async function seg3RunTaskTriad(planPath, task, codeOpts, reviewOpts) {
  let implementerResult = await seg3DispatchImplementer(planPath, task, codeOpts, null)

  for (let round = 0; round <= RALLY_CAP; round++) {
    const { specReview, qualityReview, needsRevision } =
      await seg3RunReviewRound(planPath, task, implementerResult, round, reviewOpts)

    if (!needsRevision) {
      const triadResult = makeStationResult({
        verdict: 'PASS',
        artifacts: [implementerResult, specReview, qualityReview],
        summary: `task ${task.id}: implementer + triad passed after ${round} remediation round(s)`,
      })
      triadResult.station = `seg3-task-${task.id}`
      return triadResult
    }

    // Intentional asymmetry vs seg1's design-critic loop: unreviewable CODE
    // stops the line (throw) here, whereas seg1 lets an imperfect DESIGN
    // draft ride forward with a flagged intervention after RALLY_CAP.
    if (round === RALLY_CAP) {
      throw new Error(
        `runSegment3: fail-loud: task ${task.id} exhausted RALLY_CAP (${RALLY_CAP}) remediation ` +
        `rounds with NEEDS_REVISION still outstanding (spec=${specReview && specReview.verdict}, ` +
        `quality=${qualityReview && qualityReview.verdict})`
      )
    }

    implementerResult = await seg3DispatchImplementer(planPath, task, codeOpts, { specReview, qualityReview })
  }
}

// seg3RunWholeBranchReview(opts) — one code-reviewer dispatch over the
// cumulative branch diff. The prompt's FIRST line is the verbatim
// "You ARE the reviewer" anchor (stablePrefixDispatch appends the payload
// AFTER the preamble, never before it — see driver_20_runstation.js).
async function seg3RunWholeBranchReview(opts) {
  const prompt = stablePrefixDispatch(
    SEG3_WHOLE_BRANCH_REVIEW_ANCHOR,
    ['### Branch', opts.branch || '', '### Diff scope', opts.diffScope || ''].join('\n')
  )

  const review = await runStation(
    'seg3-whole-branch-review',
    () => agent(prompt, { agentType: 'loom-code:code-reviewer', model: opts.models && opts.models.review }),
    { budget: opts.budget, tokenCap: opts.tokenCap }
  )

  const result = makeStationResult({
    verdict: review && review.verdict,
    artifacts: [review],
    summary: 'whole-branch code-reviewer verdict for the cumulative branch diff',
  })
  result.station = 'seg3-whole-branch-review'
  return result
}

// seg3CheckUiVerificationGate(projectPath, changeId, probeOpts) — a
// fact-only station (no filesystem primitive exists at this layer; every
// read routes through agent()) that reports whether BOTH conditional-gate
// conditions hold, mirroring the D8 principles-conformance conditional
// pattern. `probeOpts` carries the small dedicated cap for fact-only probe
// stations (see runSegment3).
async function seg3CheckUiVerificationGate(projectPath, changeId, probeOpts) {
  return runStation(
    'seg3-ui-verification-gate-check',
    () => agent(
      stablePrefixDispatch(
        'Check the two ui-verification gate conditions and report facts only, no judgment.',
        [
          `Project path: ${projectPath}`,
          `Change id: ${changeId}`,
          `Check 1: does docs/loom/${changeId}/ui-flows.md exist under the project path?`,
          'Check 2: did this branch touch a UI surface (HTML/JSX/templates/styles/DOM wiring)?',
          'Check 3: in one sentence, justify both answers above — this justification is quoted ' +
            'verbatim in the N/A ledger summary when the gate does not fire.',
        ].join('\n')
      ),
      { model: probeOpts.models && probeOpts.models.review, schema: SEG3_UI_GATE_SCHEMA }
    ),
    { budget: probeOpts.budget, tokenCap: probeOpts.tokenCap }
  )
}

// seg3RunUiVerification(projectPath, changeId, probeOpts, reviewOpts) —
// CONDITIONAL station. Fires only when both gate conditions hold; otherwise
// records a loud N/A (never a silent skip) quoting the probe's OWN
// justification instead of a hardcoded string — makes the ledger auditable.
async function seg3RunUiVerification(projectPath, changeId, probeOpts, reviewOpts) {
  const gate = await seg3CheckUiVerificationGate(projectPath, changeId, probeOpts)
  const uiFlowsExists = !!(gate && gate.uiFlowsExists)
  const branchTouchedUi = !!(gate && gate.branchTouchedUi)
  const justification = (gate && gate.justification) || ''

  if (!uiFlowsExists || !branchTouchedUi) {
    const naResult = makeStationResult({
      verdict: 'N/A',
      summary: `ui-verification: N/A — ${justification}`,
    })
    naResult.station = 'seg3-ui-verification'
    return naResult
  }

  const verification = await runStation(
    'seg3-ui-verification',
    () => agent(
      stablePrefixDispatch(
        'Load the loom-code:ui-verification skill and drive the real rendered app through every state ui-flows.md enumerates.',
        [
          `Project path: ${projectPath}`,
          `Change id: ${changeId}`,
          `ui-flows.md path: docs/loom/${changeId}/ui-flows.md`,
        ].join('\n')
      ),
      { model: reviewOpts.models && reviewOpts.models.review }
    ),
    { budget: reviewOpts.budget, tokenCap: reviewOpts.tokenCap }
  )

  const result = makeStationResult({
    verdict: verification && verification.verdict,
    artifacts: [verification],
    summary: 'ui-verification: drove the ui-flows.md-enumerated states against the real rendered app',
  })
  result.station = 'seg3-ui-verification'
  return result
}

// runSegment3(args) — segment-3 entry point: SDD build + whole-branch
// review + conditional ui-verification. Never merges, never pushes.
async function runSegment3(args) {
  phase(meta.phases[2].title)

  const planPath = seg3GuardPlanPath(args)
  const { projectPath, changeId, branch, diffScope, budget, models = {}, budgets = {} } = args

  // Per-station-family token caps (G1): the implementer writes code and
  // gets the code cap; both reviewers and the whole-branch code-reviewer
  // are judgment-only and share the review cap; plan-intake and the
  // ui-gate check are fact-only probes and get a small dedicated cap.
  // Canonical budgets shape: { run, perStation: { <stationName>: <cap> } }.
  const perStation = budgets.perStation || {}

  // Explicit family-constant fallbacks (STATION_TOKEN_BUDGETS.code / .review)
  // instead of runStation's own name-keyed STATION_TOKEN_BUDGETS[name]
  // lookup: seg3's station labels are dynamic per-task strings (e.g.
  // "seg3-implementer-T1"), which never match a STATION_TOKEN_BUDGETS key,
  // so an omitted perStation cap would silently fall through to runStation's
  // generic 20000 default instead of the code/review family's real cap.
  const codeOpts = { budget, models, tokenCap: perStation.code || STATION_TOKEN_BUDGETS.code }
  const reviewOpts = { budget, models, tokenCap: perStation.review || STATION_TOKEN_BUDGETS.review }
  const probeOpts = { budget, models, tokenCap: perStation.probe || STATION_TOKEN_BUDGETS.probe }

  const planIntake = await runStation(
    'seg3-plan-intake',
    () => agent(
      stablePrefixDispatch(
        'You are the loom-pipeline segment-3 plan-intake station: read the plan file and return its ordered task list as structured output.',
        `Plan path: ${planPath}`
      ),
      { model: models.review, schema: SEG3_PLAN_INTAKE_SCHEMA }
    ),
    probeOpts
  )
  const tasks = (planIntake && planIntake.tasks) || []

  if (!tasks.length) {
    throw new Error(
      `runSegment3: fail-loud: plan-intake at "${planPath}" returned zero tasks — refusing to silently skip the SDD build`
    )
  }

  // Fail loud on any id-less task — the schema's required: ['id', 'name']
  // should already stop the agent from omitting it, but this defensive
  // check catches a non-conforming StructuredOutput call before it produces
  // "seg3-task-undefined" labels/ledger rows. Never improvise a substitute
  // id.
  tasks.forEach((task, index) => {
    const id = task && task.id
    if (id === undefined || id === null || id === '') {
      throw new Error(
        `runSegment3: fail-loud: plan-intake task at index ${index} is missing "id" — refusing to invent a substitute id`
      )
    }
  })

  const results = []
  for (const task of tasks) {
    results.push(await seg3RunTaskTriad(planPath, task, codeOpts, reviewOpts))
  }

  results.push(await seg3RunWholeBranchReview({ branch, diffScope, budget: reviewOpts.budget, models: reviewOpts.models, tokenCap: reviewOpts.tokenCap }))
  results.push(await seg3RunUiVerification(projectPath, changeId, probeOpts, reviewOpts))

  return results
}

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

// Render-layer tolerance is intentional (contrast recordLedger's fail-loud):
// the ledger is the run's evidence trail — one mis-tagged bucket must land
// visibly in "Unbucketed", never crash the render and destroy the trail.
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
      const label = '[' + (station.station || station.name || 'unknown') + '] ' + (iv && iv.text ? iv.text : JSON.stringify(iv))
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
  guardArgs(args)

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

  const ledgerMarkdown = renderLedger(args, stationResults)
  log(`segment ${args.segment}: ledger rendered (${ledgerMarkdown.length} chars)`)
  await writeLedger(args, stationResults)

  return {
    segment: args.segment,
    stations: (stationResults || []).map(mainStationLabel),
    verdicts: mainBuildVerdicts(stationResults),
    budget: {
      run: args.budgets.run,
      // `spent` is THIS INVOCATION's turn-scoped output-token count — per
      // the Workflow tool's budget primitive docs, budget.spent() counts
      // output tokens spent THIS TURN across the main loop and all
      // workflows (a shared per-turn pool), not a cumulative cross-run
      // total. A resumed run (resumeFromRunId) starts a fresh turn count;
      // cross-invocation cost lives in the per-segment ledgers instead.
      spent: typeof budget !== 'undefined' ? budget.spent() : null,
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

