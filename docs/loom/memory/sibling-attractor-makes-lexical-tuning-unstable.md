---
name: sibling-attractor-makes-lexical-tuning-unstable
description: When a slimmed description regresses because a SIBLING skill's description attracts its queries (cross-family first-fire), restoring partial keyword thickness does not clear the attractor — it only moves WHICH record loses (measured: 170-char lost zh+en, 217-char candidate recovered en but newly lost ja); the only measured-stable states are the full pre-slim description or fixing the attractor side — revert fully per the A/B bar, don't tune mid-band
type: gotcha
origin: description-token-economy Task 8 post-merge A/B + remedy experiment (2026-07-14), evidence in docs/skill-dogfood/2026-07-14-description-token-economy/ab-results.md §remedy-experiment
---

user-insights' description was slimmed 899→170 chars. The post-merge A/B
showed 2/3 of its probe queries first-firing loom-pipeline:loom-memory
instead — loom-memory's pre-existing "check prior experience before loom
work" clause out-attracted the thinned description for "research user
needs before we design" phrasings. A targeted 217-char restore (keyword
thickness back, in-band) was cache-experimented: it recovered the en
record but the ja record NEWLY flipped to loom-memory — net still 1/3.
Only the full 899-char revert restores the measured-baseline behavior.

**Why:** routing is a RELATIVE contest between descriptions. Near a
semantic attractor, mid-band keyword tuning shifts the loss around
instead of eliminating it; each tuning round costs a live probe run and
converges nowhere.

**How to apply:** when an A/B regression's mechanism is sibling
attraction (MISS records first-fire a specific other skill), skip
lexical tuning: either revert the slimmed description fully (the pin's
remedy — guaranteed-baseline) or treat the ATTRACTOR side as the fix
surface (qualify its clause) with a two-sided guard re-run. Budget one
experiment at most before reverting.
