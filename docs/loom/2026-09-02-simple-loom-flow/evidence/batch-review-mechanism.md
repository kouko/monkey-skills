# Evidence inventory — SDD "Review Batch" path

## A. What it does (plain English, cited to SKILL.md)

1. A plan's tasks each carry a `Review disposition`: `individual` or
   `batch(<id>)`; a Review Batch groups tasks that share a review lane
   (loom-code/skills/subagent-driven-development/SKILL.md:117-124,
   loom-code/skills/writing-plans/SKILL.md:116-120).
2. Every new SDD run must first run `check_review_batches.py` against the
   unchanged plan; any missing/duplicate/contradictory disposition, invalid
   Batch, or non-zero checker exit refuses the plan outright, zero side
   effects (SKILL.md:117-124).
3. Per task: implementer runs, then for a Batch-disposition task SDD skips
   the individual reviewer step and instead parks the task at
   `implemented(<sha>)`, waiting for the rest of its Batch (SKILL.md:145,
   189-200).
4. Once every member of a "ready group" is `implemented`, SDD re-runs the
   checker, issues a sealed `ExecutionAuthorityProjection`, builds a
   `SafeResolutionReceipt` from the resolved test command's real output
   (never plan prose), and only then materializes an immutable
   `ReviewPacket` (SKILL.md:201-215).
5. The executable form is `batch_review_cli.py`'s four subcommands: `ready`
   (checker-gated), `packet` (materialize sealed Packet), `record-dispatch`
   (write the dispatch receipt), `apply-result` (feed verdicts through
   `resolve_aggregate_review`) (SKILL.md:216-234).
6. One reviewer fan-out is dispatched for the whole Batch (never per
   member); lane rules mirror the individual path (full / prose /
   record-narrowed) (SKILL.md:235-244).
7. `apply-result` output maps to exactly three outcomes: `finalize` (every
   member `implemented→done`), `reopen` (owners of a finding go back to
   `pending`, non-owners stay `implemented`), or `individual_fallback`
   (zero Batch ledger mutation, falls back to the existing per-task
   reviewer loop) (SKILL.md:253-259).
8. `--receipt` is the idempotency record — a second `apply-result` for the
   same Batch is refused, and a crash after the ledger write recovers from
   it (SKILL.md:231-234).
9. A Batch whose boundary is invalid/ambiguous/can't close in this window
   never becomes "individual fallback" by timeout — there is no timeout,
   size limit, or setting; it takes the ordinary individual loop with a
   fresh per-task packet (SKILL.md:193-200).
10. After every Batch reaches `finalize` (or falls back to individual),
    the run proceeds unconditionally to whole-branch review via
    `finishing-a-development-branch` (SKILL.md:264-267).

## B. Size

### Script LOC (`wc -l`)

| Script | LOC |
|---|---|
| review_batch.py | 1490 |
| batch_review_cli.py | 970 |
| propose_review_batches.py | 301 |
| check_review_batches.py | 550 |
| task_batch_replay.py | 719 |
| live_gate_station_receipt.py | 187 |
| **Total (6 dedicated scripts)** | **4217** |
| plan_card.py (whole file, batch is a subset — 69 of its lines mention "batch") | 1510 (whole file) |

### Test LOC (`wc -l`)

| Test file | LOC |
|---|---|
| test_batch_review_cli.py | 1771 |
| test_check_review_batches.py | 522 |
| test_finishing_batch_review_contract.py | 105 |
| test_live_gate_station_receipt.py | 238 |
| test_packet_validate_stations.py | 210 |
| test_plan_card_batch_states.py | 843 |
| test_propose_review_batches.py | 290 |
| test_review_batch_resolution.py | 516 |
| test_review_batch.py | 824 |
| test_sdd_batch_result_contract.py | 59 |
| test_subagent_driven_development_batch_review.py | 552 |
| test_task_batch_replay.py | 785 |
| test_writing_plans_batch_nudge_contract.py | 78 |
| test_writing_plans_review_batches.py | 132 |
| **Total** | **6925** |

### Prose word counts

- SDD SKILL.md, whole file: 4304 words (`wc -w`).
- SDD SKILL.md batch-describing span (lines 189–267, "Batch review
  checkpoint" through the closed result mapping): **705 words**.
- `references/conditional-operations.md` §Batch review and individual
  fallback (lines 96–205): **918 words**. (No file dedicated solely to the
  batch path exists — it is a section inside a shared references file.)
- `writing-plans/references/plan-format.md` §Review Batches (lines
  395–480 span, incl. Field-value grammar example carried in the same
  span): **1074 words**; the heading also recurs as an empty template
  placeholder at plan-format.md:643 (no additional prose).
- No `references/` file in either skill is dedicated exclusively to the
  batch mechanism — it is threaded through SKILL.md and
  conditional-operations.md/plan-format.md alongside non-batch material.

### Named terms introduced (23 counted)

Review Batch, Review disposition (`individual`/`batch(<id>)`),
`ReviewPacket`, `ExecutionAuthorityProjection`, `SafeResolutionReceipt`,
`source_digest`, dispatch receipt, `apply-result`, `record-dispatch`,
`resolve_aggregate_review`, `finalize`, `reopen`, `individual_fallback`,
`wait_refuse`, ownership proof / "one owner per requirement",
`Not batched because` (plan field), `Oversized because` (plan field),
`Aggregate verification`, member SHA / `implemented(<sha>)` /
`done(<sha>)`, Batch-ready window, packet identity, `applied_action`
(receipt field, v0.108.0), `task-batch-replay-result/v2` schema.

## C. Adoption

`grep -rl "^## Review Batches" docs/loom/plans/` → **14 of 268** plan
files (5.2%) carry the section heading, all dated 2026-08-24 to
2026-09-01:

- docs/loom/plans/2026-08-24-cross-host-review-gate-hardening.md
- docs/loom/plans/2026-08-24-cross-host-review-gate-hardening-part-2.md
- docs/loom/plans/2026-08-24-cross-host-review-gate-hardening-part-3.md
- docs/loom/plans/2026-08-24-review-binding-remediation.md
- docs/loom/plans/2026-08-30-task-batch-review.md
- docs/loom/plans/2026-08-31-adversarial-audit-station.md
- docs/loom/plans/2026-08-31-batch-review-hardening.md
- docs/loom/plans/2026-08-31-batch-review-measurement-and-nudge.md
- docs/loom/plans/2026-08-31-contract-repair-post-v3.md
- docs/loom/plans/2026-08-31-decision-map-script-cleanup.md
- docs/loom/plans/2026-08-31-goal-create-stop-when.md
- docs/loom/plans/2026-08-31-loom-code-script-helper-extraction.md
- docs/loom/plans/2026-09-01-loom-design-script-hygiene.md
- docs/loom/plans/2026-09-01-prose-edit-self-sweep.md

Of these, plans that show an actually *resolved* (not just declared)
Batch — a `### Review Batch: <id>` block plus a finalize/reopen/receipt
marker in the plan body:

- 2026-08-30-task-batch-review.md — `### Review Batch: sdd-review-loop` (line 265)
- 2026-08-31-goal-create-stop-when.md — `### Review Batch: shape-prose` (line 196), resolved `finalize` with recorded verdicts (line 212) and an observed-fan-out reconciliation (line 215)
- 2026-08-31-decision-map-script-cleanup.md — 3 named batches (symlink-guard, reclaim-prose, backlog-entries; lines 332/339/346)
- 2026-09-01-loom-design-script-hygiene.md — 2 named batches (queue-split, backlog-store; lines 226/233)
- 2026-09-01-prose-edit-self-sweep.md — 3 tasks declared `batch(prose-artifacts)` then **abandoned to individual fallback** (line 210, "Zero eligible Batches")
- 2026-08-31-adversarial-audit-station.md — Task 16 documents a live batch `station-prose` reopen/finalize misclassification bug hit in production (line 444)

The other 8 of the 14 plans (cross-host-review-gate-hardening x3,
review-binding-remediation, batch-review-hardening,
batch-review-measurement-and-nudge, contract-repair-post-v3,
loom-code-script-helper-extraction) carry the `## Review Batches`
heading as an empty/near-empty section — these plans are about *building*
the batch mechanism itself, not consumers of it; no `### Review Batch:`
member block or resolution marker found in them.

## D. Measured benefit (every number found, with source and population)

- **10→2 dispatches** — docs/loom/backlog/2026-08-31-batch-cost-numbers-are-declared-not-observed.md:14-17 — the 2026-08-31 pilot's headline number; the entry itself states it is **n=1, not harness-observed** (typed JSON, not counted), baseline included NEEDS_REVISION re-review cycles the candidate didn't hit, and explicitly warns against citing it as evidence of the mechanism (status: closed with the caveat recorded, not solved).
- **2060 → 1638 fan-outs, −20.5%** — docs/loom/dogfood/2026-08-31-batch-knob-simulation.md:35 — `fanouts_now → fanouts_k2`, file-overlap-gated same-module clustering, capped. Population: **283 historical plans, simulated/replayed retroactively** — "2060 is currently fully unbatched" (line 44), i.e. this is a simulation over plans that were never actually batched, not a real before/after.
- **2060 → 565, −72.6%** — same file, line 37 — `fanouts_k2_loose` (dependency + file-overlap loosened), same simulated population.
- Overall table (line 187): 283 plans, 2060 baseline fan-outs → K=2..5 caps giving 17.8%–19.9% reduction, "17 plans at cap" etc. — same simulation, not live.
- monkey-skills-only (254 plans): 1821 → 17.6–19.5% (line 188). 6 application repos (29 plans): 239 → 18.8–22.2% (line 189).
- "-50% requires" variants A–D (lines 215-217): further simulated edge-definition variants, same historical-replay method, capped at K=4.
- **Observed fan-outs 7 vs planned 4** — docs/loom/plans/2026-08-31-goal-create-stop-when.md:215 — one real plan, `task_batch_replay.py observe` verbatim count: 1 batch fan-out + 3 individual fan-outs + whole-branch + 2 individual packets for T4/T5 = 7, against a plan of 4 — the one live-plan number found where batching under-delivered relative to its own plan.
- No other real (non-simulated, harness-observed) before/after dispatch-count numbers were found for any of the other 13 adopting plans; several (prose-edit-self-sweep) show batches abandoned to individual fallback with zero savings realized.

## E. Incidents and open debt

### Backlog entries (batch/packet/receipt)

| Entry | Status | One-line |
|---|---|---|
| 2026-08-06-same-type-dispatch-batching-cache-experiment | closed | cache-TTL batching theory unproven in local test; not about Review Batch mechanism specifically (subagent dispatch caching) |
| 2026-08-28-live-gate-post-fix-packet-source-undefined | closed | live-gate convergence loop references an undefined post-fix packet source; recorded as non-gating debt |
| 2026-08-30-task-review-packets-lack-requirement-ownership | **open** | per-task review packets can't distinguish owned vs later-task requirements |
| 2026-08-31-batch-cost-numbers-are-declared-not-observed | closed | `task_batch_replay.py compare` PASSes on unfalsifiable typed-in numbers, not harness-observed counts; flags the 10→2 pilot number as overstated (n=1) |
| 2026-08-31-batch-eligibility-should-push-toward-batching | closed | batch eligibility only refuses, never nudges toward batching — plans drift to individual review |
| 2026-08-31-batch-queue-split | closed | unrelated loom-design script (`batch_queue.py`, 1369 lines) — module-cohesion issue, not the SDD Review Batch mechanism |
| 2026-08-31-batch-ready-accepts-what-packet-refuses | **open** | `ready`/`check_review_batches.py` pass plans that `packet` later refuses at dispatch time, with opaque errors landing on the wrong actor |
| 2026-08-31-one-owner-per-requirement-refuses-same-item-batches | **open** | ownership-proof rule collides with the module-batching rule when tasks share one Brief item — planner must hand-split items |
| 2026-08-31-orphan-dispatch-receipt-jams-batch | **open** | a duplicate unsigned receipt with `result_applied: false` permanently blocks `record-dispatch` until hand-moved |
| 2026-08-31-packet-identity-binds-whole-plan-text | **open** | sealed Packet's `source_digest` covers the ENTIRE plan file, so any unrelated ledger write between `packet` and `apply-result` invalidates it — hit live on the batch-review-hardening plan itself (DL-3) |

Backlog totals: **10 entries** naming batch/packet/receipt; **5 open**, 5 closed (2 of the 5 closed are adjacent, not core: cache-experiment and batch-queue-split).

### Memory entries (docs/loom/memory/)

| Entry | One-line |
|---|---|
| a-batch-reopen-of-every-member-was-classified-as-finalize | `plan_card.py` classified reopen-of-every-member as finalize (key-set heuristic bug); live production incident |
| a-record-class-prose-batch-cannot-resolve-through-the-batch-cli | all-record-class prose batch has no CLI path, must fall back to individual |
| a-review-batch-needs-one-owner-per-requirement | packet refuses same-Brief-item members; workaround = cite clauses verbatim per task |
| a-sealed-review-packet-freezes-the-whole-plan-file-until-apply-result | whole-plan digest freeze; recovery = re-seal/re-record/rebind |
| batch-agents-under-report-what-they-deleted | 12 batch agents removed 38 assertions, reported 27; 14 removals killed a live invariant, suite stayed green |
| deletion-task-review-packet-fails-the-cat-file-existence-check | deletion-only tasks can't satisfy the `cat-file -e` existence check by construction |
| hold-every-plan-write-while-a-review-packet-is-sealed | packet freeze hit 4 times in one run; each re-record hit the orphan-receipt trap too |

7 memory entries, all describing incidents/gotchas encountered while operating the mechanism (none report a clean win).

### CHANGELOG fix releases (loom-code)

| Version | One-line |
|---|---|
| 0.105.1 | fail-closed Task Batch Review — original ship (Review Batches derivable, SDD validates/materializes/dispatches, replay tooling compares costs) |
| 0.106.0 | `batch_review_cli.py` adapter added — single assembly-free execution path; review debt cleared |
| 0.107.0 | Batch review hardening — F1/F5/F6 etc. fixed (receipt binding, missing-commit detection); F7/F9/F10 declined → filed as backlog |
| 0.107.1 | hotfix — `batch_review_cli.py` subprocess argv UTF-8-under-C-locale bug |
| 0.108.0 | Batch review measurement + batching nudge — `observe`/`compare` v2, `propose_review_batches.py`, `Not batched because`/`Oversized because` fields |

5 versions in a row (0.105.1→0.108.0) were dedicated batch-mechanism releases, several explicitly fixing bugs found by adversarial audit of the immediately preceding release.

## F. Totals table

| Metric | Value |
|---|---|
| Scripts LOC (6 dedicated files) | 4217 |
| Test LOC (14 dedicated test files) | 6925 |
| Prose words (SDD SKILL.md batch span + conditional-operations.md batch span + plan-format.md Review Batches span) | 705 + 918 + 1074 = **2697** |
| Named terms introduced | 23 |
| Plans adopted (`## Review Batches` present) | 14 / 268 (5.2%) |
| Plans with a real resolved Batch (not just the empty heading) | 6 / 268 (2.2%) — one of the 6 (prose-edit-self-sweep) resolved to abandonment/individual fallback |
| Real-plan (non-simulated) dispatch saving citable | **None found net-positive**: the only harness-observed real-plan number (goal-create-stop-when, D) shows 7 actual fan-outs against a plan of 4 (worse, not better); the only "win" number (10→2) is explicitly flagged by its own backlog entry as n=1, unfalsifiable-by-construction, and not to be cited as mechanism evidence |
| Simulated-benefit numbers | 2060→1638 (−20.5%) to 2060→565 (−72.6%) fan-outs over 283 historically-replayed (never actually batched) plans |
| Backlog entries open | 5 (of 10 total naming batch/packet/receipt) |
| Backlog entries closed | 5 |
| Memory (incident) entries | 7, all gotchas/bugs, zero reporting a clean win |
| Dedicated fix releases | 5 (0.105.1, 0.106.0, 0.107.0, 0.107.1, 0.108.0) |

Could not find: a references/ file dedicated solely to the batch
mechanism (it is threaded through shared files); any harness-emitted
(not hand-typed) dispatch-count comparison on a real plan; any adoption
data past 2026-09-01 (repo history for the mechanism spans exactly
2026-08-24 to 2026-09-01, ~8 days).
