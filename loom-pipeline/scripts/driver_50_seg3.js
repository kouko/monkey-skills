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

  // LOOM-SIMPLIFY: local `perStation.probe || 20000` fallback instead of a
  // driver_20 STATION_TOKEN_BUDGETS['probe'] entry | ceiling: next time
  // driver_20_runstation.js is edited by any task in this plan | upgrade:
  // add a 'probe' entry to STATION_TOKEN_BUDGETS there and drop this local
  // fallback | ref: Task 11 remediation round, finding 🟡2 (driver_20 is
  // out of scope for this task).
  //
  // Explicit family-constant fallbacks (STATION_TOKEN_BUDGETS.code / .review)
  // instead of runStation's own name-keyed STATION_TOKEN_BUDGETS[name]
  // lookup: seg3's station labels are dynamic per-task strings (e.g.
  // "seg3-implementer-T1"), which never match a STATION_TOKEN_BUDGETS key,
  // so an omitted perStation cap would silently fall through to runStation's
  // generic 20000 default instead of the code/review family's real cap.
  const codeOpts = { budget, models, tokenCap: perStation.code || STATION_TOKEN_BUDGETS.code }
  const reviewOpts = { budget, models, tokenCap: perStation.review || STATION_TOKEN_BUDGETS.review }
  const probeOpts = { budget, models, tokenCap: perStation.probe || 20000 }

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
