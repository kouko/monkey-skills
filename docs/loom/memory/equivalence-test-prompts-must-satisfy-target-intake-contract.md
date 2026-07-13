---
name: equivalence-test-prompts-must-satisfy-target-intake-contract
description: A behavioral-equivalence test prompt that violates the target skill's own input contract cannot arbitrate equivalence — it produced a false 3/3 not_equivalent verdict (baseline/candidate each picked different defensible readings of the invalid input); validate prompts against the skill's intake contract first, and confirm any single-run divergence with n≥2 replicates per side before believing it
type: practice
origin: PR (refactor/writing-plans-token-slim) — skill-refactor pilot on writing-plans; evidence: docs/skill-dogfood/2026-07-13-writing-plans-token-refactor/gate-evidence.md
---

During the writing-plans token-refactor equivalence gate, the P3 stress
prompt fed a bare Smallest-End-State list ("Here is the brief: …make the
plan") that did not qualify as a brief under writing-plans' own §When
NOT to Use intake contract. Runs against that input scattered across
three defensible readings (re-derive DAG and ship a plan / refuse via
depth ceiling / refuse via no-brief exemption), and the 3-judge ensemble
returned a unanimous not_equivalent that vanished once the prompt was
fixed to a contract-valid, strictly-sequential brief — round 2 judged
all pairs equivalent, 3/3.

**Why:** an input the skill is contractually allowed to reject does not
pin a single correct behavior, so baseline-vs-candidate divergence on it
measures sampling luck, not the refactor. The false REJECT nearly killed
a sound refactor; conversely the same mechanism could mask a real
regression.

**How to apply:** before trusting any equivalence/dogfood verdict on a
skill, check each test prompt against the target skill's own intake
contract (exemption tables, required input shape) — an invalid prompt is
a test-infra bug, not a behavioral signal. When a divergence does
appear on a non-deterministic scenario, run n≥2 replicates per side
first: a consistent 2-0 vs 0-2 outcome split is evidence, a 1-0 split is
noise. (Related: [[assertion-must-encode-the-property-it-claims]],
[[dogfood-evidence-anchors-shipped-commit]].)
