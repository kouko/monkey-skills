# Preserve the controlled docs-review experiment
originator: kouko
kind: engineering
needs-design: no — this preserves internal experiment records and changes no interface
evidence: [docs/loom/2026-09-10-docs-review-controlled-evidence/evidence/]
status: confirmed 2026-09-10
publication: automatic — authorized 2026-09-10 by kouko

## Problem
The earlier docs-review experiment was built against a retired Loom workflow. Its controlled evidence is still useful, but publishing the old branch would restore runner and storage code that current Loom deliberately removed.

## Proposed outcome
Publish a current-Loom, evidence-only record of the fixed-corpus Luna experiment, preserving the prompt, raw inputs and outputs, repeats, human oracle, metrics, and revision attribution without restoring a production runner.

## Acceptance
1. A clean checkout contains the fixed corpus, prompt, raw Luna inputs and outputs, repeat runs, human oracle, metrics, and revision attribution needed to audit the experiment.
2. The recorded metrics can be recomputed from the preserved evidence and match the published values.
3. The conclusion distinguishes whether cost in this narrow corpus came mainly from initial-draft quality or from review, and states the experiment's limits.
4. The change adds no production runner or reusable experiment store and does not modify dbt-redshift or `.transactions/`.

## Constraints
- Preserve the original experiment records byte-for-byte where practical and record their source revision.
- Keep Luna, the fixed corpus, and the prompt fixed; do not substitute a newer model or rerun with changed inputs.
- Treat this as a controlled internal experiment, not a production-grade benchmark or general performance claim.
- Public references to `openai.com` are allowed for this cycle; privacy policy changes belong to a later change.
- Do not read or modify `.transactions/`.
- Do not modify or run inside the dbt-redshift environment.

## Out of scope
- Production runner, generalized experiment framework, or reusable evidence store.
- Changes to review prompts, corpus selection, or model choice.
- Merge of the pull request.
- A new privacy policy.

## Open questions
- none
