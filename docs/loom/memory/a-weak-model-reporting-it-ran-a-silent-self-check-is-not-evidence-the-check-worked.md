---
name: a-weak-model-reporting-it-ran-a-silent-self-check-is-not-evidence-the-check-worked
description: A prose instruction telling a weak model to silently run a self-check before returning buys behavioral compliance (the agent says it swept and can describe the sweep) but not the outcome (the defect the sweep targets is still shipped) — the two are decoupled, so a self-reported silent check cannot be trusted as a gate and a visible/verbalized form does not fix it either
type: practice
origin: 2026-09-01 — prose-edit self-sweep arc, two blind A/B rounds (silent vs none; silent vs written checklist) over 24 drafts; Arm-B agents confirmed they ran rule 14's sweep (6/8, describing the grep) yet those same drafts still shipped stale-neighbour defects, and the written-checklist variant scored no better than silent (n=2, variance-dominated); results in docs/loom/dogfood/2026-09-01-prose-selfsweep-ab/
---

Rule 14 told the implementer to silently sweep for stale restatements
before returning. The agents complied behaviorally — they said they ran
the grep, named what they searched — and still left the dependent
sentences stale. Making the checklist *written* rather than silent did
not close the gap: whether a draft caught the defect turned on whether
that agent happened to reason about semantic dependents, which neither
output form forced.

**Why:** "the agent reports it did X" and "X actually changed the
outcome" are independent for a weak model executing a prose instruction.
It can pattern-complete a plausible account of a sweep it did not
really perform, or perform a shallow literal version that misses the
target. So a self-reported self-check — silent OR verbalized — cannot
be trusted as a gate, and its behavioral fidelity is not evidence of
effect. (Compounds with [[a-name-grep-cannot-see-a-rename-written-as-prose]]:
a clean grep is necessary, never sufficient.)

**How to apply:** Do not treat "agent self-checked" as a quality gate,
and do not measure a self-check by whether the agent says it ran. Judge
it by an EXTERNAL check of the outcome (a reviewer, or a mechanical
gate on the artifact), or by a blind A/B on the shipped defect count —
never by the agent's own report. When an A/B on such an instruction
comes back null, the null is about the instruction's effect, not proof
the agents skipped it — they may have run it and still missed.
