export const meta = {
  name: 'principles-replay-matrix',
  description: 'L1 regression matrix for loom-product-principles: fans out one haiku headless replay per seed to a sandbox, then grades each artifact mechanically (validator + seed-traceability checker; no LLM self-report anywhere in the verdict path) and returns a per-seed pass table + overall pass-rate. Eval semantics over non-deterministic replays — never wired into CI.',
  phases: [
    { title: 'Replay' },
    { title: 'Grade' },
  ],
}

// Workflow runtime contract (grounded in .claude/workflows/code-toolkit-sweep.js
// + loom-pipeline/scripts/driver_00_header.js + driver_10_guard.js — the only
// in-repo Workflow scripts): no non-deterministic timestamp/random calls
// anywhere — a Workflow run can be paused and RESUMED from a journal, and
// any of those would produce a different value on resume than on the
// original pass, silently desyncing this script from what was journaled.
// Every label this script needs (`runLabel`) comes in via `args`, the
// Workflow-provided ambient global (never generated inline).

const ROOT = '/Users/kouko/GitHub/monkey-skills'
const SEED_CORPUS_DIR = `${ROOT}/docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus`
const COLD_OPERATOR_SEED = `${ROOT}/docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/seed.md`
const SKILL_MD = `${ROOT}/loom-product-principles/skills/product-principles/SKILL.md`

const DEFAULT_SEEDS = [
  { id: 'seed1', input: `${SEED_CORPUS_DIR}/seed1-input.md`, oracle: `${SEED_CORPUS_DIR}/seed1-oracle.md` },
  { id: 'seed2', input: `${SEED_CORPUS_DIR}/seed2-input.md`, oracle: `${SEED_CORPUS_DIR}/seed2-oracle.md` },
  { id: 'seed3', input: `${SEED_CORPUS_DIR}/seed3-input.md`, oracle: `${SEED_CORPUS_DIR}/seed3-oracle.md` },
  { id: 'seed4', input: `${SEED_CORPUS_DIR}/seed4-input.md`, oracle: `${SEED_CORPUS_DIR}/seed4-oracle.md` },
  { id: 'seed5', input: `${SEED_CORPUS_DIR}/seed5-input.md`, oracle: `${SEED_CORPUS_DIR}/seed5-oracle.md` },
  // cold-operator: the SAME file is both the §Seed input and the §Oracle —
  // a living doc (calibrated in #532), not a synthetic corpus pair.
  { id: 'cold-operator', input: COLD_OPERATOR_SEED, oracle: COLD_OPERATOR_SEED },
]

// --- args guard (fail-loud; no silent improvisation) ------------------------
//
// `args` is the Workflow-provided ambient global (see driver_10_guard.js's
// guardArgs for the pattern this mirrors, incl. the harness sometimes
// delivering args as a JSON STRING rather than an object).

let runArgs = args
if (typeof runArgs === 'string') {
  try {
    runArgs = JSON.parse(runArgs)
  } catch (e) {
    throw new Error(
      'principles-replay-matrix: args arrived as a non-JSON string (' +
      runArgs.slice(0, 80) + '...). Refusing to guess.'
    )
  }
}
if (runArgs === null || typeof runArgs !== 'object' || Array.isArray(runArgs)) {
  throw new Error(
    'principles-replay-matrix: expected an args object, received ' + String(runArgs) + '.'
  )
}
if (typeof runArgs.runLabel !== 'string' || runArgs.runLabel === '' || runArgs.runLabel === 'undefined') {
  throw new Error(
    'principles-replay-matrix: args.runLabel (non-empty string) is required — ' +
    'timestamps/labels must come in via args; this script never generates its own timestamp.'
  )
}
// runLabel becomes a path segment (sandboxDir/runLabel/seed.id/...) AND is
// interpolated into the grading courier's Bash instructions below — allow-list
// rather than deny-list, mirroring loom-pipeline/scripts/driver_10_guard.js's
// changeId guard: only [A-Za-z0-9._-] is safe in both positions. A deny-list
// (reject "/" and "..") lets shell-metacharacter labels like "foo$(x)" through;
// an allow-list closes that hole by construction.
const RUN_LABEL_ALLOWED_PATTERN = /^[A-Za-z0-9._-]+$/
if (!RUN_LABEL_ALLOWED_PATTERN.test(runArgs.runLabel)) {
  throw new Error(
    'principles-replay-matrix: args.runLabel must match ' + RUN_LABEL_ALLOWED_PATTERN +
    ' (letters, digits, dot, underscore, hyphen only) — received ' +
    JSON.stringify(runArgs.runLabel) + '.'
  )
}
if (typeof runArgs.sandboxDir !== 'string' || runArgs.sandboxDir.charAt(0) !== '/') {
  throw new Error(
    'principles-replay-matrix: args.sandboxDir must be an absolute path string ' +
    '(received ' + JSON.stringify(runArgs.sandboxDir) + ').'
  )
}
// sandboxDir is ALSO interpolated into the SAME grading courier's Bash
// instructions as runLabel (it composes artifactPath/gradeTxtPath below) —
// a leading-'/' check alone lets a value like "/tmp/x;evil" through. Apply
// the same allow-list per path segment (split on '/', drop the leading
// empty segment produced by the leading '/', reject empty inner segments).
const sandboxDirSegments = runArgs.sandboxDir.split('/').slice(1)
for (const segment of sandboxDirSegments) {
  if (segment === '' || !RUN_LABEL_ALLOWED_PATTERN.test(segment)) {
    throw new Error(
      'principles-replay-matrix: args.sandboxDir must be an absolute path whose ' +
      'every segment matches ' + RUN_LABEL_ALLOWED_PATTERN + ' (letters, digits, ' +
      'dot, underscore, hyphen only, no empty segments) — offending segment ' +
      JSON.stringify(segment) + ' in ' + JSON.stringify(runArgs.sandboxDir) + '.'
    )
  }
}

let seedPairs = DEFAULT_SEEDS
if (runArgs.seeds !== undefined) {
  if (!Array.isArray(runArgs.seeds) || runArgs.seeds.length === 0) {
    throw new Error(
      'principles-replay-matrix: args.seeds, when provided, must be a non-empty ' +
      'array of seed ids drawn from: ' + DEFAULT_SEEDS.map((s) => s.id).join(', ')
    )
  }
  const known = DEFAULT_SEEDS.map((s) => s.id)
  const unknown = runArgs.seeds.filter((id) => known.indexOf(id) === -1)
  if (unknown.length > 0) {
    throw new Error(
      'principles-replay-matrix: args.seeds has unknown id(s): ' + unknown.join(', ') +
      ' — known ids: ' + known.join(', ')
    )
  }
  seedPairs = DEFAULT_SEEDS.filter((s) => runArgs.seeds.indexOf(s.id) !== -1)
  log(
    `args.seeds narrows this run to ${seedPairs.length}/${DEFAULT_SEEDS.length} seeds ` +
    `(${seedPairs.map((s) => s.id).join(', ')}) — full 6-seed regression coverage is ` +
    'NOT exercised this pass.'
  )
}

// --- schemas ------------------------------------------------------------

const REPLAY_SCHEMA = {
  type: 'object',
  required: ['artifactPath'],
  properties: {
    artifactPath: { type: 'string' },
    notes: { type: 'string' },
  },
}

const GRADE_SCHEMA = {
  type: 'object',
  required: ['validatorExit', 'checkerExit', 'checkerMisses', 'gradeTxtPath', 'artifactPath'],
  properties: {
    validatorExit: { type: 'number' },
    checkerExit: { type: 'number' },
    checkerMisses: { type: 'array', items: { type: 'string' } },
    gradeTxtPath: { type: 'string' },
    artifactPath: { type: 'string' },
  },
}

// --- pipeline -------------------------------------------------------------

phase('Replay')

const results = await pipeline(
  seedPairs,
  // REPLAY STAGE — one haiku headless replay per seed, written to a
  // per-seed sandbox path. No cross-seed barrier (pipeline runs each
  // seed's Replay->Grade independently).
  (seed) => {
    const artifactPath = `${runArgs.sandboxDir}/${runArgs.runLabel}/${seed.id}/PRINCIPLES.md`
    log(`replay:${seed.id}: dispatching headless replay (haiku) -> ${artifactPath}`)
    return agent(
      `You are replaying the loom-product-principles \`product-principles\` skill in its "Headless / seeded mode" — no user is available; this is an on-demand regression replay, not a live authoring session.

STEPS:
1. Read ${SKILL_MD} in full (the whole file — its "## Headless / seeded mode" section is the exact procedure to follow; earlier sections define the artifact contract it references, incl. references/principles-rules.md's — check: marker rule).
2. Read the seed input at ${seed.input} as the run-input seed (its "## Seed" section is the material to feed as user-stated verbatim; everything else in that file is not seed content).
3. Execute the skill's headless/seeded procedure against that seed exactly as written: pick canon candidates and stances yourself (agent-decided answers), walk the seed item-by-item post-draft per the seed-traceability invariant (no silent drops), and mark every agent-decided choice with the literal \`(agent-decided)\` marker at end-of-line per the skill's contract. If the seed is genuinely too thin to ground a North Star, write that refusal as the file's content instead of a normal artifact — never fabricate one.
4. Write the resulting artifact via the Write tool to this EXACT absolute path: ${artifactPath}
5. Do NOT run the validator or the traceability checker yourself — a separate Grade stage does that mechanically. Do NOT self-report pass/fail; an operator self-report has already been proven false once on this seed corpus.

Return the artifact path you wrote.`,
      { model: 'haiku', phase: 'Replay', label: `replay:${seed.id}`, schema: REPLAY_SCHEMA }
    )
  },
  // GRADE STAGE — a courier only: runs the two deterministic scripts and
  // returns their raw exit codes + stderr. The SCRIPT (not the agent)
  // computes pass/fail below from those exit codes alone — no LLM opinion
  // anywhere in the verdict path. Artifact + grade.txt paths are returned
  // so any caller can re-run both scripts on disk to independently
  // re-verify a courier's claim.
  async (replay, seed) => {
    const artifactPath = replay && replay.artifactPath
    const gradeTxtPath = `${runArgs.sandboxDir}/${runArgs.runLabel}/${seed.id}/grade.txt`
    if (!artifactPath) {
      log(`grade:${seed.id}: Replay stage produced no artifactPath — recording as a hard miss.`)
      return {
        seedId: seed.id,
        pass: false,
        validatorExit: null,
        checkerExit: null,
        misses: ['replay: no artifact produced'],
        artifactPath: null,
        gradeTxtPath: null,
      }
    }
    log(`grade:${seed.id}: dispatching grading courier -> ${gradeTxtPath}`)
    const g = await agent(
      `You are a GRADING COURIER. Run EXACTLY these two commands via Bash from the repo root ${ROOT}, and nothing else — do not open or read the artifact yourself, do not form an opinion about correctness, do not run any script other than these two:

1. python3 loom-product-principles/scripts/validate_principles_output.py ${artifactPath}
2. python3 loom-product-principles/scripts/check_seed_traceability.py ${artifactPath} ${seed.oracle}

Save the raw stdout+stderr and exit code of BOTH commands, clearly labeled per command, to this exact path via the Write tool: ${gradeTxtPath}

Return: validatorExit (command 1's exit code, a number), checkerExit (command 2's exit code, a number), checkerMisses (every stderr line command 2 printed, each already in \`<class>: <token>\` form — empty array when checkerExit is 0), gradeTxtPath (the path you wrote), artifactPath (echo back ${artifactPath}).`,
      { phase: 'Grade', label: `grade:${seed.id}`, schema: GRADE_SCHEMA }
    )
    if (!g) {
      log(`grade:${seed.id}: grading courier produced no result — recording as a hard miss.`)
      return {
        seedId: seed.id,
        pass: false,
        validatorExit: null,
        checkerExit: null,
        misses: ['grade: courier produced no result'],
        artifactPath,
        gradeTxtPath: null,
      }
    }
    const pass = g.validatorExit === 0 && g.checkerExit === 0
    log(`grade:${seed.id}: validatorExit=${g.validatorExit} checkerExit=${g.checkerExit} -> ${pass ? 'PASS' : 'FAIL'}`)
    return {
      seedId: seed.id,
      pass,
      validatorExit: g.validatorExit,
      checkerExit: g.checkerExit,
      misses: g.checkerMisses || [],
      artifactPath: g.artifactPath,
      gradeTxtPath: g.gradeTxtPath,
    }
  }
)

const rows = results.filter(Boolean)
const passCount = rows.filter((r) => r.pass).length
const passRate = rows.length ? passCount / rows.length : 0

log(
  `principles-replay-matrix complete: ${rows.map((r) => `${r.seedId}=${r.pass ? 'PASS' : 'FAIL'}`).join(', ')} ` +
  `— pass-rate ${(passRate * 100).toFixed(1)}% (${passCount}/${rows.length}). ` +
  'Eval semantics (pass-rate over non-deterministic replays) — this is not a CI gate; ' +
  're-run the two scripts on disk against each row\'s artifactPath/gradeTxtPath to ' +
  'independently re-verify.'
)

return { runLabel: runArgs.runLabel, rows, passRate }
