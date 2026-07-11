---
name: pipeline-enforced-gates-beat-drafter-instructions
description: When a weak-model drafter keeps violating a coverage obligation despite prose instructions, move enforcement into the PIPELINE (harness runs a deterministic checker, verbatim miss list feeds one bounded fix round) — measured 22%→67% pass-rate with the dominant failure class displaced to input-side extraction quality, after three prose-hardening proposals had been mechanically rejected as no-ops
type: practice
origin: branch l3-loop-run-20260711 (2026-07-12) — mechanical seed-gate arc; motivating evidence docs/loom/dogfood/2026-07-11-l3-loop-run2 (L3 plateau) + acceptance docs/loom/dogfood/2026-07-12-mechanical-seed-gate-baseline
---

The principles station's seed-coverage obligation was enforced by prose
("walk the seed item-by-item") and a self-reported check — the L3
improve-loop mechanically rejected three successive prose-hardening
proposals (including one that PRESCRIBED a mechanical grep as prose),
confirming the prose ceiling. Rebuilt as a pipeline gate — the drafting
agent authors an entity inventory at reading time (Write-only), a harness
courier runs the deterministic checker, and the verbatim miss list feeds
ONE bounded fix round — the measured pass-rate went 4/18 (22%) → 8/12
(67%), the fix round cleared 100% of caught misses, and every residual
failure was an inventory omission (extraction-at-reading), a different
and rarer class than the old drop-at-drafting.

**Why:** external mechanical feedback beats self-critique decisively
(CRITIC arXiv 2305.11738; DeepMind 2310.01798 — intrinsic self-correction
degrades accuracy), every shipped system (Aider/Guardrails/Instructor/
ZOZO) enforces validators in pipeline code, and this family's own A/B
evidence shows prose in context moves weak-model behavior 0/2. A
mechanical gate does not just shrink the failure rate — it DISPLACES the
failure class to the gate's own input quality (here: the inventory),
which is where the next improvement round should aim.

**How to apply:** when a drafting-agent obligation keeps failing after
1-2 prose attempts, stop hardening prose. (1) Have the drafter emit a
machine-checkable side artifact at the moment the information is in
front of it (reading time, not recall time); (2) run the deterministic
checker from the HARNESS (workflow courier / orchestrator step), never
as an instruction the drafter must remember; (3) feed the verbatim miss
list to a fresh fix agent, bounded to 1 round (raise toward 3 only on
measured need); (4) measure before/after with the same mechanical
grader, and expect the residual failures to move upstream — plan the
next round against the new class, not the old one.
