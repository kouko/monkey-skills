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
