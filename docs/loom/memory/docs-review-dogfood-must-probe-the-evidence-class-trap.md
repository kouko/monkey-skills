---
name: docs-review-dogfood-must-probe-the-evidence-class-trap
description: When dogfooding any docs-review contract change, the load-bearing probe is the evidence-class trap — a cold round-2 reviewer whose headline surviving defect is evidence-class must still return a passing verdict (evidence never gates); a misread silently reproduces the 🟡-accumulation loop the class filter exists to kill, and no grep pin can catch it
type: practice
origin: PR feat-requesting-docs-review-skill (loom-code 0.42.0, 2026-07-30) — dogfood record docs/loom/dogfood/2026-07-30-requesting-docs-review-dogfood.md §D3
---

Grep pins verify the aggregation words exist; only a behavioral probe verifies a
cold reviewer APPLIES them when the incentive points the other way. The designed
trap: hand a round-2 reviewer a remediation where an evidence-class finding was
"fixed" by rephrasing in place (defect survives in new words). The correct
output is simultaneously (a) `not-fixed` on that finding, (b) no re-litigation
as a new differently-worded finding, and (c) a PASSING verdict — because
evidence-class findings never feed the gate, even when the surviving defect is
the round's headline. A reviewer that returns NEEDS_REVISION here has silently
reverted to severity-counting, which is the exact 9-round-loop failure mode the
instruction/evidence split shipped to end.

**Why:** The class-filter semantics are the one part of the docs-review design
that is both load-bearing and invisible to string tests — every other duty
(dimensions, scope, cap wording) pins mechanically; this one only fails in
behavior, and its failure mode looks like diligence.

**How to apply:** On every future change to docs-review contracts
(requesting-docs-review, docs-reviewer agent, aggregation wording), re-run the
trap probe from the dogfood record's D3 recipe before ship: round-1 findings
with one evidence-class defect, a remediation that rephrases it in place, one
cold reviewer. Expected: not-fixed + no re-litigation + passing verdict
(strictly PASS when no instruction-🟡 survives). Any other output is a contract
wording defect — fix the wording, not the reviewer.
