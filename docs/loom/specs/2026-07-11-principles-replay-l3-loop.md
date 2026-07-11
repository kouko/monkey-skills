# Brief: principles replay loop — Level 3 autonomous improvement loop

- Date: 2026-07-11
- Upstream design SSOT: `docs/loom/specs/2026-07-10-principles-replay-loop.md`
  §Level 3 — the four guardrails (held-out seeds / one-invariant +
  word-budget brake / plateau detection / no auto-merge) are DEFINED there
  and not restated here; this brief binds them to concrete mechanics.
- Re-trigger condition ("several rounds of real L1/L2 data") met: committed
  baseline `docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/calibration-baseline-2026-07-11.md`
  (18 artifacts, 3 runs × 6 seeds).

## Design-side on-ramp

N/A — loom-internal eval/tooling infrastructure (precedent:
`2026-07-11-escalation-interface-contracts.md` "N/A — loom-internal").

## Problem

The principles station has a measured dominant failure class — prose-named
stack/canon items dropping from `## Anchors` (14/18 baseline artifacts) —
and a proven-exhausted manual remedy path (prose hardening plateaued in 3
live rounds; SSOT §inputs). Today, improving the station means a human
proposes a SKILL.md change, re-runs the matrix, and re-grades by hand —
slow enough that regression suspicions go unchased. The job: close that
loop mechanically — an unattended propose→verify→record loop that surfaces
only *verified* improvement proposals for human review, and **stops itself
when it is not working** instead of accumulating patches.

Expectation-setting (honest): the dominant failure class may be beyond
prose fixes — the SSOT records the prose ceiling. L3's value is systematic
exploration WITH disciplined stopping; a first invocation that ends in
"plateau → route to mechanical remedy / human" is the guardrails working,
not the loop failing.

## Users

- **The maintainer (kouko)** — invokes on demand (after a station behavior
  change, or when drop-signal accumulates); reviews the loop's proposal
  branch as PR reviewer (guardrail 4: the human is the only merger).
- **Future maintainer sessions** — read the round ledger + Decision
  Log-shaped entries to see what was tried, accepted, and rejected, without
  replaying the runs.

## Smallest End State

One new saved Workflow script `.claude/workflows/principles-improve-loop.js`
that, in a single on-demand invocation:

1. **Seed split (guardrail 1)** — committed config: held-out =
   cold-operator (the only human-grounded seed) + seed5; visible =
   seed1–seed4. Held-out seeds and their oracles are never passed to any
   fixer-facing stage. Framing per research: at n=6 the held-out set is a
   **regression smoke test, not a statistical guarantee**.
2. **Baseline** — nests the existing matrix by name
   (`workflow('principles-replay-matrix', …)` → `{runLabel, rows, passRate}`)
   on visible seeds, ×2 runs, aggregated **per seed** (never a single
   scalar).
3. **Fixer stage** — one agent proposes ONE fix per round: a single named
   invariant + a concrete edit to the station's prompt-artifact file(s).
   Input = failing rows + current SKILL.md + failure-class description;
   **never the oracle files** (oracle-overfit guard).
4. **Verify (two-stage accept, per GEPA)** — apply the edit in an isolated
   copy; re-run visible matrix; a win = **no visible seed worse AND ≥1
   seed better**; a win must **reproduce on a confirmation re-run**, then
   pass the held-out smoke (no held-out seed newly failing) before being
   recorded as accepted.
5. **Brakes (guardrails 2+3)** — mechanical word-cap check (reject any
   edit pushing SKILL.md past 4,500 words; currently 2,351); hard cap 3
   rounds per invocation (shipped systems all use fixed budgets); plateau
   early-exit = 2 consecutive rounds with no accepted proposal.
6. **Output (guardrail 4)** — round ledger (imitating
   `loom-pipeline/scripts/driver_60_ledger.js` `recordLedger`), accepted
   edits committed on the arc branch with Decision Log-shaped entries
   (shape: `writing-plans/references/plan-format.md` §Decision Log), and a
   final report file. The loop never merges and never pushes.

Ships with: static guard tests (null-guard / await-in-try / arg
allow-list, per `docs/loom/memory/workflow-agent-results-and-courier-args-need-guards.md`),
a dry-parse test, and one live smoke invocation before close-out.

## Current State Evidence

- **Forward** — L3 invokes the matrix as a saved workflow:
  `.claude/workflows/principles-replay-matrix.js:2` (meta name),
  `:151-256` (per-seed pipeline), `:272` (return `{runLabel, rows, passRate}`);
  args allow-listed `:57-97`, optional `seeds` narrowing `:100-120`.
- **Reverse** — verdict path is purely mechanical: `pass = validatorExit===0
  && checkerExit===0` (`principles-replay-matrix.js:233`); checker CLI +
  exit codes 0/1/2 (`loom-product-principles/scripts/check_seed_traceability.py:227-234`, `:48-50`).
- **Error** — stage-guard precedent at `principles-replay-matrix.js:158,173,196,246`
  (async try/catch with await inside — #535); guard obligations memory
  cited above.
- **Data** — grader contract `docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/README.md:12-16`;
  demote-on-reproduction policy `:25-36`; seed provenance `:18-23`
  (seed1-5 synthetic; cold-operator human-grounded, separate folder);
  baseline table `calibration-baseline-2026-07-11.md:16-35`.
- **Boundary** — station SKILL.md at 2,351/4,500 words (cap
  `scripts/check-skill-structure.py:298` CHK-SKL-010); BACKLOG harness
  entry `docs/loom/BACKLOG.md:46`, L3 pointer `:76-81`; Decision Log
  consumers exist (`plan-format.md`, `kickoff-briefing.md:84`).

## Alternatives Considered (Axis 4 — WebSearch, EN+JA)

Four shipped approaches surveyed: **DSPy MIPROv2** (staged minibatch/full
eval; needs ~50+ val examples), **GEPA** (two-stage accept + per-instance
Pareto tracking; arXiv 2507.19457), **Microsoft PromptWizard** (small-data
20-50 examples, hard 3-5 iteration caps), **JA practitioner line**
(Insight Edge / PFN: measure judge non-determinism, aggregate multiple
runs before trusting a delta). Adopted: GEPA's two-stage accept +
per-seed tracking; PromptWizard's hard round cap; JA multi-run
aggregation. Honest gaps the research surfaced: **no shipped system
validates a held-out split at n=6** (hence smoke-test framing), and **no
shipped system uses plateau-stopping** (all fixed budgets) — our plateau
brake is extra conservatism on top of the cap, not a substitute.
Reversal: if the corpus reaches ~20+ seeds, flip to a real train/held-out
split with staged evaluation. (Sources: dspy.ai/api/optimizers/MIPROv2;
arxiv.org/abs/2507.19457; github.com/microsoft/PromptWizard;
techblog.insightedge.jp/entry/llm-as-a-judge-determinism;
tech.preferred.jp/ja/blog/prompt-tuning.)

## Decision

Build `.claude/workflows/principles-improve-loop.js` as one saved
Workflow script that composes the existing L1 matrix via nested
`workflow()` calls, implements the four SSOT guardrails with the three
research-grounded acceptance mechanics above, and outputs a
human-reviewable proposal branch + ledger + report. We will NOT build:
checker first-cell precision (separately DEFERred with its own
re-trigger), loop-driven oracle/corpus edits (demote-on-reproduction
stays human-executed), CI wiring (eval semantics, per SSOT), or
`skill-tuning` variant diversification (re-trigger: single-fixer
plateaus and diversification is needed).

## Out of Scope

- Checker first-cell anchor precision (DEFERred —
  `2026-07-11-replay-matrix-stage-guard.md` §Companion decision).
- Any loop-initiated edit to seed oracles or the corpus README.
- CI / per-push wiring of the loop or the matrix.
- `skill-dev-toolkit:skill-tuning` integration (recorded re-trigger above).
- Auto-merge / auto-push of proposals (SSOT guardrail 4).
- Behavior changes to `principles-replay-matrix.js` beyond what nested
  invocation requires (ideally zero).

## Open Questions

- **Held-out composition** (chosen: cold-operator + seed5) — cold-operator
  is the only human-grounded seed so it must be unseen; seed5 shows
  run-to-run variance (PASS r2, fail r1/r3) making regressions visible.
  This half of the call is partly arbitrary (seed4 would also serve);
  cost of change = one config line.
- **Isolation mechanics for fixer edits** (worktree vs sandbox copy) —
  plan-stage decision; must not touch the operator's working tree.
- **Cost envelope** — worst case ≈ 3 rounds × (2 baseline + 1 verify +
  1 confirm + 1 held-out) matrix runs ≈ ~50-60 haiku replays per
  invocation. Cheap in model terms; flagged for operator awareness.
