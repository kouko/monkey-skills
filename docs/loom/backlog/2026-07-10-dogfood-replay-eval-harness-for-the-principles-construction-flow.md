---
name: 2026-07-10-dogfood-replay-eval-harness-for-the-principles-construction-flow
description: Dogfood replay/eval harness for the principles construction flow
status: open
origin: 2026-07-10 cold-operator dogfood close-out discussion — the user asked whether human-run dogfood records can become automated test / iteration material. Three human-grounded seeds already exist: pip-note-app (paper run, `docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/`), quote-tool (simulated-user Target B, `docs/loom/dogfood/2026-07-10-weak-model-dual-dogfood/`), and meeting-transcriber (live cold-operator run — structured seed + verbatim transcript in `docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/` `seed.md` / `transcript.md`).
start: several rounds of real L1/L2 data accumulated, or a regression suspicion the manual loop is too slow to chase.
---

- Start: several rounds of real L1/L2 data accumulated, or a regression
  suspicion the manual loop is too slow to chase.
- Origin: 2026-07-10 cold-operator dogfood close-out discussion — the
  user asked whether human-run dogfood records can become automated
  test / iteration material. Three human-grounded seeds already exist:
  pip-note-app (paper run,
  `docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/`), quote-tool
  (simulated-user Target B,
  `docs/loom/dogfood/2026-07-10-weak-model-dual-dogfood/`), and
  meeting-transcriber (live cold-operator run — structured seed +
  verbatim transcript in
  `docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/`
  `seed.md` / `transcript.md`).
- 2026-07-10 matrix update: a 5-seed synthetic corpus now exists
  (`docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/`, input +
  grader-only oracle pairs) and its first 6-run matrix is graded
  (`docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/matrix-results.md`).
  Two residuals from that run — prose-named stack/canon → Anchors drops
  (5/6 artifacts) and the seed-walk self-report being observably FALSE
  (seed5) — are now covered mechanically; see the 2026-07-11 update
  below.
- 2026-07-11 update: L1 (regression matrix Workflow,
  `.claude/workflows/principles-replay-matrix.js`) and L2 (mechanical
  traceability gate,
  `loom-product-principles/scripts/check_seed_traceability.py`) shipped
  on branch `feat-principles-replay-loop-l1-l2`, closing both residuals
  above. Design SSOT: `docs/loom/specs/2026-07-10-principles-replay-loop.md`
  (§Level 1, §Level 2).
- 2026-07-12 update: the mechanical seed-coverage gate shipped (PR #545)
  — drafting agent authors `seed-inventory.md` at reading time, the
  PIPELINE runs `check_seed_traceability.py` (headless: matrix courier;
  interactive: SKILL.md Step 8), verbatim miss list feeds ONE fix-agent
  round. Acceptance 4/18 (22%) → 8/12 (67%); the fix round cleared
  43/43 caught misses (baseline:
  `docs/loom/dogfood/2026-07-12-mechanical-seed-gate-baseline/`). The
  residual failure class is now inventory OMISSIONS at
  extraction-at-reading time — displaced upstream, not eliminated.
  Inventory quality is the current improvement frontier (recorded
  next-arc candidate: independent second extraction agent diffed against
  the first, or extraction-checklist emphasis on deferred/stance items;
  re-trigger: omission failures capping the pass-rate in future runs).
- What: Level 3 — the autonomous improvement loop (matrix → grade →
  implementer proposes a SKILL.md fix → review → re-run) — is now
  BUILT: `.claude/workflows/principles-improve-loop.js` (saved workflow
  `principles-improve-loop`), brief SSOT
  `docs/loom/specs/2026-07-11-principles-replay-l3-loop.md`. Design
  history remains at `docs/loom/specs/2026-07-10-principles-replay-loop.md`
  §Level 3 — do not restate it here. `skill-dev-toolkit:skill-tuning`
  remains the candidate variant-diversification engine, deliberately
  NOT wired in yet. Re-evaluation note (2026-07-12): its recorded
  re-trigger (single-fixer plateau — per the L3 brief's §Decision) was
  formally MET on 2026-07-11 (L3 run2 hit the plateau brake after
  consecutive rejected rounds,
  `docs/loom/dogfood/2026-07-11-l3-loop-run2/`), but the plateau's
  underlying failure class was resolved by the mechanical seed-coverage
  gate (PR #545), not by fixer diversification — so meeting the trigger
  does NOT activate this entry; it needs a NEW plateau observed on
  post-gate L3 runs before wiring in. Two
  still-unbuilt reuse tiers from the original
  discussion remain adjacent open ideas, not folded into L1/L2/L3:
  simulated-user replay (answer-bank + correction-events from the
  transcripts driving a simulated user that injects recorded
  corrections) and judge rubric (the graded reports' 5 criteria +
  B1-B6/F1-F7 findings as labeled ground truth for an LLM judge).
  Division of labor, agreed with the user: mechanical/regression
  coverage goes automatic; NEW failure-mode discovery and taste calls
  stay human — simulated users are systematically agreeable and miss
  owner-only corrections (ground truth lives with the human; both
  live runs proved read-back catches what simulation would wave
  through). When a SECOND station ships a headless/seeded mode,
  promote the seed-traceability invariant from product-principles
  SKILL.md to a family-shared convention (n=1 today, deliberately
  station-local). Calibration DONE 2026-07-11 (3 matrix runs, 18
  artifacts, stable-fragment + `|`-alternative tokens; committed
  baseline: `docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/calibration-baseline-2026-07-11.md`).
  Grade-courier robustness (stage-throw guard) shipped 2026-07-11 on
  branch `feat-replay-matrix-stage-guard` — both stage bodies in
  `principles-replay-matrix.js` now catch stage errors into degraded
  failed rows instead of `pipeline()` dropping the seed to null. The
  other harness next-touch candidate, anchor-match precision
  (`check_seed_traceability.py` restricting anchor match to the
  first/canon-name cell), is DEFERRED — see
  `docs/loom/specs/2026-07-11-replay-matrix-stage-guard.md` §Companion
  decision for the reason (n=1 observed false-negative, under-report-only,
  no mechanical rule yet separates it from a reproduced true positive);
  revisit when L1 data shows drop-signal distortion attributable to it.
