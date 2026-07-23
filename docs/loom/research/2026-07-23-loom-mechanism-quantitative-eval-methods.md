# Quantitative Evaluation of Agent-Scaffold Mechanisms — Industry Survey + loom Seed Inventory

Research date: 2026-07-23. Method: one focused WebSearch agent (EN+JP, 28 tool
uses) over agent-scaffold evaluation literature, plus one read-only inventory
agent over this repo's `docs/loom/dogfood/` + `docs/loom/audits/` (28 records,
every record classified). Purpose: ground a future arc that measures, with
objective metrics, whether EACH CHANGE to the loom-* mechanism made it better
than the previous version — per-change regression measurement, not a one-shot
academic evaluation.

## Bottom line

The industry has no off-the-shelf score for "is this bespoke gated pipeline
good"; what it has is three experimental designs — **fixed-model ablation**
(lock the LLM, vary only the scaffold), **cost-controlled Pareto comparison**,
and **RCT** — of which only the first fits the per-change purpose. A
TDD-enforcing, review-gated, multi-role dev pipeline has NO dedicated
literature as a category (verified absence, not assumed). The strongest causal
result in the whole field is negative and cautionary: METR's RCT found
experienced devs 19% SLOWER with AI tools while self-reporting 20% faster —
subjective impressions of mechanism value are inadmissible; only measurement
counts. This repo already holds a working prototype of the right design
(`principles-replay-matrix`) and ~30 seed-grade raw materials for extending it
to loom-code.

## Industry methods (9, all source-verified)

| Method | What it measures | Scaffold isolation | Bespoke-usable? |
|---|---|---|---|
| [HAL — Holistic Agent Leaderboard](https://arxiv.org/abs/2510.11977) | success + $/token + behavior logs | model × scaffold × benchmark full grid (21,730 rollouts); cost-controlled Pareto frontiers | ✅ open harness |
| [Harness-disclosure protocol](https://arxiv.org/abs/2605.23950) | harness-vs-model variance decomposition | shows harness-induced variance can EXCEED model-induced (rank reversals) | ✅ explicitly for in-house |
| [Fixed-LLM scaffold-evolution study](https://arxiv.org/abs/2607.03691) | resolve-rate across 35 harness releases | model locked, only scaffold version varies — **the design that matches our purpose** | ✅ portable to own version history |
| [METR RCT](https://arxiv.org/abs/2507.09089) | real task completion time | true RCT (16 devs × 246 real issues) | design portable; heavyweight |
| [Agentless controlled comparison](https://arxiv.org/abs/2407.01489) | resolve rate + cost, same LLM | fixed pipeline vs open agent loop — pipeline won at 1/N cost | ✅ gate-vs-no-gate pattern |
| [AgentSpec module ablation](https://arxiv.org/html/2606.14674v1) | marginal contribution of single modules | each module independently on/off | ✅ closest to "which gate earns its keep" |
| [CLEAR enterprise framework](https://arxiv.org/abs/2511.14136) | Cost/Latency/Efficacy/Assurance/Reliability + 8-run consistency | CLEAR score correlates 0.83 with production success (accuracy-only: 0.41) | ✅ closest scorecard for gated pipelines |
| [SWE-bench leaderboard dissection](https://arxiv.org/abs/2506.17208) | submission profiling | ❌ confirms leaderboards do NOT attribute scaffold vs model | ❌ |
| [DORA 2025/2026 AI-expanded](https://dora.dev/insights) | delivery + stability + AI Code Share etc. | longitudinal survey; self-reported "attribution gap" | org-level only |

Verified specifics:
- (a) SWE-bench-style leaderboards do not separate scaffold vs model
  attribution; HAL is the one infrastructure built to close that gap.
- (b) METR RCT headline: randomized AI-allowed devs were **19% slower** on
  real issues despite forecasting 24% and self-reporting 20% faster.
- (c) HAL reports cost-controlled Pareto frontiers as a default output.
- (d) No 2025–2026 paper evaluates a TDD-enforcing / review-gated /
  multi-role dev pipeline as a named category — AgentSpec (module ablation)
  and CLEAR (enterprise scorecard) are the two nearest neighbors.
- (e) DORA added AI metrics but cannot attribute output to agents; SPACE's
  AI-era adaptation is nominal (most studies use ≤3 of its 5 dimensions).

Field gaps (explicit): no ablation-grade study isolates a review-gate/TDD
mechanism's marginal contribution; no public method evaluates bespoke
frameworks against a no-scaffold baseline off-the-shelf — you must run the
fixed-model pattern yourself. "Does more process machinery help" is
empirically open even at the base case.

## The design this repo aligns on (per-change regression measurement)

Five elements, all instantiated already by `principles-replay-matrix`
(workflow `.claude/workflows/principles-replay-matrix.js`; design SSOT
`docs/loom/specs/2026-07-10-principles-replay-loop.md`):

1. Fix the task set, model tier (haiku — weak tier exposes ambiguous skill
   text), and effort; the ONLY variable is the skill version.
2. Mechanical grading — verdicts from exit codes only, no LLM self-report
   anywhere in the verdict path.
3. Paired per-seed win/loss/tie tables, not aggregate scores alone.
4. n≥2 replicates per seed; a regression is a shift beyond the noise band
   (CLEAR's run-consistency dimension).
5. Red/green discipline: the failure a change targets enters the corpus as a
   new seed (RED before the change), and the change is "effective" iff the
   new seed flips GREEN with zero old-seed regressions.

Per-change scorecard: seeds flipped green / seeds flipped red / pass-rate
delta vs noise band / token-cost delta.

Scope honesty — what this measures and what it does not: mechanical replay
guards the FLOOR (structure present, known failure modes not recurring). It
does not measure the CEILING (is a principle truly falsifiable, is a memo
insightful) — quality judgment stays with low-frequency blind A/B
(`skill-dev-toolkit:skill-tuning`), rubric scoring (`skill-judge`), and human
read; each discovered quality failure ratchets the floor upward by becoming a
new mechanical seed after the fact. Goodhart guard: periodically dilute the
corpus with fresh real-world failures so wording cannot overfit the suite.

## Seed inventory for extending to loom-code (2026-07-23 scan)

28 dogfood/audit records classified (READY = input + checkable expectations
both recoverable; PARTIAL = reconstruction needed; NARRATIVE-ONLY = prose
lesson, not replayable): **9 READY / 10 PARTIAL / 10 NARRATIVE-ONLY** (class
tallies sum to 29 over 28 records — one cross-plugin record is
double-classified)
(loom-code proper: 2 READY + 3 PARTIAL; cross-plugin READY records cover it
further).

Top seed sources for a loom-code matrix, in order:

1. `docs/loom/audits/2026-07-16-loom-weak-model-behavioral-audit.md` — **26
   ready-made (skill, probe prompt, pass-criterion) rows** covering every
   loom-code skill; alone seeds most of a first matrix.
2. `docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md` — pinned commit
   diff + 5 disk-verifiable ground-truth findings at pinned commits (line
   anchors on a subset); the only git-checkable
   REVIEW-QUALITY oracle on record.
3. `docs/loom/firing-corpus/*.jsonl` — routing/triggering seeds already in
   seed+oracle shape; reuse, don't rebuild.
4. `docs/loom/audits/2026-07-20-loom-mechanism-weakness-audit.md` §5 — the
   self-mint-a-waiver-under-pressure probe (haiku fails, sonnet holds): a
   sharp gate-integrity seed.
5. `docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md` F4 — the
   "undefined" template-args derail; input-contract-guard seed (fixture needs
   rebuilding).

Implication for arc scope: the corpus does not need authoring from scratch —
the arc reduces to (i) normalizing ~26+ existing probes into seed/oracle file
pairs, (ii) assembling the grading workflow by copying the replay-matrix
pattern, (iii) wiring loom-code's existing mechanical gates (validators, gate
markers, living-spec checker) as graders. BACKLOG entry: §"loom-code replay
matrix — per-change objective regression measurement". Related standing note:
the principles-station BACKLOG entry already reserves "promote the
seed-traceability invariant to a family-shared convention when a SECOND
station ships a headless/seeded mode" — that trigger fires if this arc ships.

## Sources

Survey agent (EN+JP WebSearch, 2026-07-23): arXiv 2510.11977, 2605.23950,
2607.03691, 2507.09089, 2407.01489, 2606.14674, 2511.14136, 2506.17208;
dora.dev/insights; metr.org/blog/2025-07-10. Inventory agent: read-only scan
of `docs/loom/dogfood/` (20 records) + `docs/loom/audits/` (8 records),
2026-07-23.
