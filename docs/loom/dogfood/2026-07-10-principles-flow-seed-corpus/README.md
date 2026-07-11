# Seed corpus — loom-product-principles headless seeded-mode replay tests

Synthetic corpus for replay-testing `loom-product-principles:product-principles`
§Headless / seeded mode against its seed-traceability invariant (every seed
item must land as a carrying principle, an `## Anchors` row, an `## Open
Questions` entry, or an explicit out-of-jurisdiction note — never silently
dropped).

5 pairs: `seedN-input.md` (what the replay operator/agent gets — mimics the
real `docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/seed.md`
§Seed structure) + `seedN-oracle.md` (grader-only trap manifest — never shown
to the operator — listing `named_anchors`, `deferred_items`,
`out_of_jurisdiction_bait`, `stances`, `negative`). Grade by checking every
oracle assertion against the produced artifact with the validator + greps;
NEVER trust the operator's own seed-walk self-report (a false "✓" self-report
was observed live in the 2026-07-10 matrix, seed5).

- seed1 B2B incident war-room dashboard (non-head canons; 5-stance single bullet)
- seed2 preschool bedtime-story audio app (2 deferred; canon only in prose)
- seed3 API schema-diff CLI (stack only in idea sentence; mixed traditions)
- seed4 local-first vector sketchbook (mixed traditions; non-head visual canon)
- seed5 full-stack booking SaaS (dual stack in prose; DECIDED-cost anti-trap;
  2 deferred) — authored by the orchestrator, same conventions as seed1-4

## Calibration policy: demote-on-reproduction

A machine `negative:` token is a lossy approximation of "bait accepted" —
under substring semantics, ANY token can in principle be contained in a
natural rejection sentence (negation-superstring). A token stays
machine-checked only until a rejection-mention false positive is OBSERVED
in a run or REPRODUCED mechanically against `check()`; on first such
occurrence it is demoted to a grader-side `# note:` line. Misses are
always human-reviewed (this matrix is an eval, never CI), so a retained
token's residual risk is bounded by that review — this replaces the
too-absolute "nothing stays machine-checked" reading (round-2 cold-operator
run: 8 correction-regression negatives retained, 0 false positives).

Provenance: synthetic, generated 2026-07-10 for the seed-traceability harness
(BACKLOG: "Dogfood replay/eval harness"). First use + results:
`../2026-07-10-principles-flow-cold-operator/matrix-results.md`.
