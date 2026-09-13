# Normalize cross-model probe prose
originator: maintenance-loop
kind: engineering
needs-design: no — repairs an evidence assertion without changing any user-facing surface or behavior
evidence: [docs/loom/2026-09-12-host-aware-cross-model-review-language/evidence/probes/test_host_aware_cross_model_review.py]
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
The final verification rejects correct review guidance when Markdown wraps a sentence across lines. This blocks the completed cross-model review change even though the underlying wording and package tests are correct.

## Proposed outcome
Make prose checks ignore harmless whitespace wrapping while preserving exact checks for the one-column table and its surrounding blank lines.

## Acceptance
1. The cross-model adversarial check passes when required prose is wrapped across Markdown lines and still rejects missing or changed required wording.
2. The table structure and surrounding blank-line contract remain byte-exact.
3. Closing review can generate a matching attestation for the completed branch.

## Constraints
- Do not change user-facing review behavior or wording.
- Do not weaken exact validation of the Markdown table layout.
- Keep the repair limited to the existing committed adversarial program and its review evidence.

## Out of scope
- Redesigning the finalizer or its execution order.
- Changing cross-model selection, ask, suggest, or fixed-tool behavior.

## Open questions
- none
