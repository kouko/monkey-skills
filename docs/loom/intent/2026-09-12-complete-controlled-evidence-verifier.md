# Complete the controlled evidence verifier
originator: kouko
kind: engineering
needs-design: no — this hardens an internal evidence check and changes no interface
evidence: [docs/loom/2026-09-10-docs-review-controlled-evidence/evidence/]
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
The controlled docs-review evidence is ready, but its required integrity probe checks only part of the published record. The prior closing Review therefore ended without an attestation or pull request.

## Proposed outcome
Complete the evidence-local verifier so an independent run detects changes to the fixed inputs, every published metric, the source lineage, and the human-adjudication boundary, then repeat closing Review under a fresh episode.

## Acceptance
1. The verifier independently pins and checks the approved input and prompt SHA-256 values rather than trusting only an adjacent mutable manifest.
2. The verifier recomputes every published aggregate and per-run rate, agreement value, elapsed total, and token total from the raw runs and oracle.
3. The verifier validates the corpus source blobs and both old-to-rebased lineage mappings with independently pinned identifiers.
4. Real mutation cases demonstrate that changing a fixed input, metric, run observation, or adjudication makes verification fail.
5. The completed branch remains evidence-only, does not restore a production runner or reusable store, and does not modify dbt-redshift or `.transactions/`.

## Constraints
- Preserve the fixed corpus, Luna runs, prompt, raw input and output, human oracle, metrics semantics, and revision attribution already recorded.
- Keep the verifier stdlib-only and scoped to this one experiment record.
- Do not rerun Luna or change the experiment population.
- Do not read or modify `.transactions/`.
- Do not modify or run inside the dbt-redshift environment.
- Publish only through non-forced Loom Ship after a fresh Review passes; merge remains separate.

## Out of scope
- Production runner, generalized benchmark framework, or reusable evidence store.
- Changes to the current Loom checker inconsistency.
- New experiment results or a new privacy policy.
- Merge of the pull request.

## Open questions
- none
