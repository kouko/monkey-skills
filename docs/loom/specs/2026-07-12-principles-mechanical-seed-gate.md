# Brief: principles station — mechanical seed-coverage gate (plateau remedy)

- Date: 2026-07-12
- Motivating evidence: L3 improve-loop plateau — three consecutive rejected
  prose proposals across two runs (`docs/loom/dogfood/2026-07-11-l3-loop-smoke/`,
  `docs/loom/dogfood/2026-07-11-l3-loop-run2/`); run2 round 2 proposed a
  grep-based seed walk AS PROSE and still lost. Dominant failure class:
  prose-named stack/canon → `## Anchors` drop, 14/18 baseline artifacts
  (`calibration-baseline-2026-07-11.md:37-42`).
- Design SSOT lineage: `2026-07-10-principles-replay-loop.md` §Level 3
  guardrail 3 routes a plateau to "mechanical remedies or a human" — this
  arc is that mechanical remedy.

## Design-side on-ramp

N/A — loom-internal infrastructure (standing precedent).

## Problem

The principles station's seed-coverage obligation ("every seed-named
canon/tech lands as an Anchors row") is enforced today by prose
instructions and a self-reported seed walk — and the seed walk self-report
is PROVEN falsifiable (SSOT §inputs), while three L3 rounds proved prose
hardening cannot move the behavior. The job: make seed coverage a
**physical property of the pipeline** — a deterministic checker that the
HARNESS runs (never the drafting model), whose exact miss list feeds one
bounded fix round — so a drafted artifact structurally cannot finalize
with dropped anchors.

## Users

- **Replay/eval operators (headless)** — the L1 matrix; its pass-rate is
  the arc's acceptance instrument.
- **Interactive station sessions** — a strong-model orchestrator running
  `product-principles` for a real product idea; gets the same gate at the
  existing Step 8 validate-then-fix seam.
- **Future L3 loop runs** — a mechanically-gated station raises the
  baseline the fixer must beat.

## Smallest End State

1. **Inventory authoring (drafting agent, Write-only — no Bash needed)**:
   the station's headless flow gains a step — BEFORE drafting sections,
   extract every seed-named entity into `seed-inventory.md` using the
   checker's existing oracle format, keys `named_anchors:` /
   `deferred_items:` ONLY (never `negative:` — its semantics is
   must-be-ABSENT, `check_seed_traceability.py:202-210`). Interactive mode:
   same inventory derived from the user's answers.
2. **Pipeline-enforced check (harness, not model instructions)**:
   - **L1 matrix** (`principles-replay-matrix.js`): the Replay phase gains
     a self-check leg — a Bash courier runs
     `check_seed_traceability.py <draft> <inventory>` (zero script
     changes — parser is source-agnostic, `main` at `:227-248`); on exit 1
     a fix agent receives the VERBATIM miss list and patches additively
     (missing Anchors rows use the existing `(agent-decided)` version
     convention); re-check; **1 fix round now, budget for 3** (shipped
     consensus; reversal recorded below). GRADE stage untouched — it still
     verdicts against the grader-only calibrated oracle, so measurement
     independence holds (inventory ≠ oracle).
   - **Interactive** (`product-principles/SKILL.md` Step 8, :203-222):
     extend the existing validate-then-fix step to also run the checker
     against the session's inventory, exit-0 gated (wording precedent:
     `writing-plans/SKILL.md:216,230`).
3. **Oracle isolation preserved**: no replay/fix/courier prompt may name
   any path under the seed-corpus folder; the inventory lives in the run
   sandbox. Oracles stay grader-only (`corpus README:11-16`).
4. **Acceptance (whole arc)**: ≥2 post-change L1 matrix runs vs the
   committed 4/18 baseline — the dominant failure class must measurably
   shrink (fewer class-D anchor drops per run); no regression on
   deferred-item or negative checks; both L1 runs' reports committed as
   the new baseline.

Ships with: static guard tests for the matrix changes (per the house
conventions and `workflow-agent-results-and-courier-args-need-guards.md`),
pytest coverage for any new helper, dry-parse, and the SKILL.md word cap
respected (2,351/4,500 today).

## Current State Evidence

- **Forward** — station flow steps: Step 5 Write (`SKILL.md:139`,
  Anchors rules :156-181) → Step 6 Read-back (:186) → Step 7 Emit (:196)
  → Step 8 Validate-then-fix (:203-222, validator command :212); headless
  seed walk (the prose step this gate supersedes) at :264-267, grounded
  by the traceability invariant :239-263.
- **Reverse** — checker reuse is zero-change: parser takes two arbitrary
  paths (`check_seed_traceability.py:227-248`), format contract :4-29
  (`;` tokens :91-97, `|` alternatives :103-116); inventory must avoid
  `negative:` (must-be-ABSENT semantics :202-210) and know that
  `deferred_items` requires `— re-trigger:` lines (:163-172) and
  `named_anchors` a non-empty version cell (:179-182).
- **Error** — replay agent currently has NO script access by design
  (matrix `:167-168`, STEP 5 "Do NOT run the validator or the traceability
  checker yourself"); grading courier has Bash (:210-218). The new
  self-check leg therefore lands as a separate courier + fix agent in the
  workflow, not as replay-agent Bash.
- **Data** — seeds at `docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/seed{1..5}-input.md`
  + cold-operator seed (paths pinned in matrix :20-32); seed shape = `## Seed`
  bullet list, CJK content; oracles grader-only (README :11-16).
- **Boundary** — validator enforces structure only (docstring :10-44),
  needs no change; GRADE already measures improvement with zero changes
  (`pass = validatorExit===0 && checkerExit===0`, matrix :233);
  SKILL.md word count 2,351/4,500.

## Alternatives Considered (Axis 4 — WebSearch EN+JA)

Shipped approaches: **Aider** lint/test reflection loop (external checker,
`max_reflections` hardcoded 3), **Guardrails AI** reask loop (validator
outside the model, bounded `num_reasks`), **Instructor** (validation error
fed back verbatim, retries ~3), **ZOZO production pipeline** [JA]
(app-code validation + rejected-value feedback, max 3 retries, errors cut
87%, most fixed in round 1). Evidence answers: (a) external mechanical
feedback beats self-critique decisively (CRITIC arXiv 2305.11738; DeepMind
arXiv 2310.01798 — intrinsic self-correction DEGRADES accuracy); (b) fix
bound = 3 is the shipped consensus, round 1 catches most; (c) honest gap —
no source measures weak-model compliance with "run the validator
yourself", but every shipped system enforces in pipeline code, never in
model instructions ("instruction-based compliance is statistical hope"),
which converges with this family's own 0/2 preload evidence. Rejected
alternatives: SKILL.md-only prose gate (three L3 rounds + (c) refute it);
heuristic entity extraction in the checker (would duplicate what the
drafting agent can author reliably at intake — extraction-at-reading is
the easy half of the task; dropping-at-drafting is the failure).
Reversal: if post-round-1 miss rate stays high, raise the fix bound to 3
BEFORE escalating the drafter tier; if the drafter tier rises to sonnet+,
instruction-based self-run becomes a viable supplement — the harness gate
stays the authority either way.

## Decision

Build the mechanical seed-coverage gate as: inventory authored by the
drafting agent at intake (oracle-format, two keys), checker run by the
PIPELINE (matrix courier headless / Step 8 interactive), verbatim miss
list → one additive fix round, exit-0 gated, oracle isolation intact,
acceptance measured by the L1 matrix against the committed baseline. NOT
building: checker modifications (zero-change reuse), validator changes,
L3 loop changes (it benefits automatically via a raised baseline),
seed-corpus expansion (separate candidate arc), first-cell anchor
precision (own DEFER stands).

## Out of Scope

- Any edit to `check_seed_traceability.py` or `validate_principles_output.py`.
- Any edit to seed oracles / corpus README policy.
- `principles-improve-loop.js` (L3) changes.
- Seed-corpus expansion (n=6 → 20+; separate arc, recorded).
- Interactive-mode UX beyond the Step 8 extension.

## Open Questions

- Inventory file naming/location in interactive mode (headless: run
  sandbox; interactive: alongside the artifact?) — plan-stage decision,
  low cost.
- Whether the fix agent is the SAME replay agent continued or a fresh
  agent fed draft+miss-list — plan-stage; fresh agent matches the
  family's fresh-context conventions and the ZOZO feedback shape.
- Fix bound telemetry: record per-run how many misses round 1 cleared —
  feeds the recorded reversal condition.
