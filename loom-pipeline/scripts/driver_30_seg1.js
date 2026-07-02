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

// Local station-result schemas (SEG1_ prefix — one concat scope; see
// driver_40_seg2.js's same note). Live finding wf_ff22820b-61d: agent()
// WITHOUT opts.schema returns plain TEXT (the harness only injects the
// StructuredOutput tool when a schema is passed) — spreading that string
// into recordLedger produced indexed-char garbage. Schemas are therefore
// load-bearing, not decoration.
const SEG1_STATION_SCHEMA = {
  type: 'object',
  required: ['verdict', 'artifacts', 'interventions', 'summary'],
  properties: {
    verdict: { type: 'string', description: 'adopted | authored | PASS_WITH_NOTES | NEEDS_REVISION | DONE | FAIL' },
    artifacts: { type: 'array', items: { type: 'string' }, description: 'absolute paths written' },
    validator_exit: { type: 'integer', description: 'validator exit code; -1 if none ran' },
    interventions: {
      type: 'array',
      items: {
        type: 'object',
        required: ['bucket', 'text'],
        properties: {
          bucket: { type: 'string', description: "A | B | C — driver_60_ledger.js INTERVENTION_BUCKETS" },
          text: { type: 'string' },
          critic_found: { type: 'boolean' },
        },
      },
    },
    summary: { type: 'string', description: 'must carry the DECISIONS_SECTION: present|absent token for design' },
    principles_text_head: { type: 'string', description: 'first ~80 lines of PRINCIPLES.md verbatim (adopt/author both)' },
  },
}

const SEG1_CRITIC_SCHEMA = {
  type: 'object',
  required: ['verdict', 'summary'],
  properties: {
    verdict: { type: 'string', description: 'PASS_WITH_NOTES | NEEDS_REVISION — two-valued, no bare PASS' },
    summary: { type: 'string' },
    critic_found_rows: { type: 'integer', description: 'count of critic-found additions made to ui-flows.md' },
    interventions: {
      type: 'array',
      items: {
        type: 'object',
        required: ['bucket', 'text'],
        properties: { bucket: { type: 'string' }, text: { type: 'string' }, critic_found: { type: 'boolean' } },
      },
    },
  },
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
      schema: SEG1_CRITIC_SCHEMA,
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
    schema: SEG1_STATION_SCHEMA,
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
      schema: SEG1_STATION_SCHEMA,
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
