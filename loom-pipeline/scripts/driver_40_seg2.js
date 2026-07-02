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
        verdict: 'UNRESOLVED',
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
