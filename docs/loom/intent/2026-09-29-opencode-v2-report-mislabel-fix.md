# OpenCode v2 acceptance report suite-label fix
originator: kouko
kind: engineering
needs-design: no — internal documentation wording fix only; no user-facing interface surface
status: confirmed 2026-09-29
publication: automatic — authorized 2026-09-29 by kouko

## Problem
The scalar-reverify episode ended NON_CONVERGENT because the acceptance test report's A1 section labels the loader-only suite (506 tests) as the "complete package suite" when the full `scripts/ -q` suite passes 698. The product fix itself (7de9eb66c) was reviewed and passed by both vendors; only this one documentation label is wrong.

## Proposed outcome
The acceptance test report's A1 line states the correct suite identity and count, so the report no longer mislabels a subset suite as the full suite.

## Acceptance
1. `docs/loom/2026-09-29-opencode-v2-scalar-reverify/acceptance-test-report.md` A1 no longer calls the 506-loader-suite the "complete package suite"; it either names it as the loader-specific suite (506) or reports the full suite (698).
2. A fresh closing-review episode returns no NEEDS_REVISION for the report-wording change.
3. No other functional content changes.

## Constraints
- Same branch (feat/2026-09-29-opencode-v2-plugin-compat).
- No rework of the reviewed loader fix (7de9eb66c) or probe programs.
- Keep the report in Traditional Chinese.

## Out of scope
- Any change to loader code, tests, or adversarial programs.

## Open questions
- none
