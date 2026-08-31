# Batching-knob simulation over historical loom plans (read-only)

Script: `batch_knob_sim.py` (stdlib only). Per-plan rows: `per_plan.csv`.
No repo file was modified — this is pure analysis over `docs/loom/plans/*.md`
across 7 repos.

## What was measured

- **fanouts_now** — today's reviewer fan-out: one reviewer-dispatch per
  non-mechanical task not in a declared batch, plus one per declared batch.
  (Mechanical tasks self-check — no reviewer fan-out.)
- **Knob ① `nudge_pairs`** — ordered dependency pairs (A→B) with same review
  lane and ≥1 shared touched file, not already co-batched. Each is a
  candidate "you two could batch — justify why not" nudge a plan author
  would have to answer at plan time.
- **Knob ② `fanouts_k2`** — cluster non-mechanical tasks into connected
  components by (dependency edge ∧ same lane ∧ file overlap); count of
  components = simulated fan-out. `fanouts_k2_loose` drops the file-overlap
  requirement (dependency + same lane only) — an upper bound on how far
  clustering could go if file identity weren't required.

## Totals

| repo | plans | tasks | mechanical | fanouts_now | fanouts_k2 | fanouts_k2_loose | nudge_pairs |
|---|---:|---:|---:|---:|---:|---:|---:|
| monkey-skills | 254 | 1875 | 47 | 1821 | 1454 | 464 | 411 |
| kumiko-zaiku-app-icons | 15 | 137 | 0 | 137 | 87 | 30 | 56 |
| meeting-emo-transcriber | 4 | 28 | 0 | 28 | 28 | 28 | 0 |
| reading-list-summarize-scraper | 5 | 39 | 0 | 39 | 38 | 22 | 1 |
| youtube-summarize-scraper | 2 | 12 | 0 | 12 | 9 | 2 | 4 |
| redshift-comment-mcp | 2 | 9 | 0 | 9 | 8 | 5 | 1 |
| intellij-dbtree | 1 | 14 | 0 | 14 | 14 | 14 | 0 |
| **TOTAL** | **283** | **2114** | **47** | **2060** | **1638** | **565** | **473** |

- **fanouts_now → fanouts_k2**: 2060 → 1638, a **20.5% reduction** (file-overlap-gated
  clustering — the conservative knob).
- **fanouts_now → fanouts_k2_loose**: 2060 → 565, a **72.6% reduction** (dependency +
  lane only, no file-overlap gate — the aggressive upper bound; batches this
  loose would likely mix unrelated concerns just because they're sequenced).
- **nudge_pairs (knob ①)**: 473 ordered pairs across the corpus would each have
  demanded a written "why not batch" justification at plan time.
- **fanouts_now already includes existing batching**: this corpus has only 7
  batch-era plans (0.2.6.b batch schema), so nearly all of `fanouts_now`'s
  2060 is currently fully unbatched — the reduction above is almost entirely
  *new* clustering, not double-counting existing batches.

## largest_component distribution

- Plans with a clustered batch ≥4 tasks: **36** of 283.
- Plans with a clustered batch ≥6 tasks: **17** of 283.
- **127 of 283 plans are unchanged by knob ②** (fanouts_k2 == fanouts_now) —
  mostly small plans (1-3 tasks, already disjoint files) or plans predating
  the `Dependencies` field (see Coverage below), where there is nothing to
  cluster.

Batch size matters for review quality: a 13- or 14-task cluster (see example 1
below) is arguably too large for one reviewer pass to hold in their head —
the knob's raw fan-out number understates the trade-off; a size cap (e.g.
"split any component >6") would keep most of the benefit while avoiding
oversized batches. Of the 36 plans with a ≥4 cluster, 17 reach ≥6 and the
remaining 19 sit at exactly 4-5.

## Top 10 plans by biggest absolute fanout saving (fanouts_now − fanouts_k2)

| plan | fanouts_now | fanouts_k2 | saving | largest cluster | nudge_pairs |
|---|---:|---:|---:|---:|---:|
| monkey-skills/2026-08-30-outcome-map-v3.md | 26 | 9 | 17 | 13 | 17 |
| monkey-skills/2026-07-13-us-sec-financial-table-xval.md | 17 | 3 | 14 | 14 | 14 |
| monkey-skills/2026-07-12-us-sec-narrative.md | 12 | 1 | 11 | 12 | 13 |
| monkey-skills/2026-07-16-operational-kpi-quarterly.md | 18 | 8 | 10 | 7 | 11 |
| kumiko-zaiku-app-icons/2026-08-18-axonometric-perspective-and-grounded-slats.md | 16 | 6 | 10 | 11 | 13 |
| monkey-skills/2026-07-03-loom-pipeline-v1-1-batch-mode.md | 13 | 4 | 9 | 10 | 10 |
| monkey-skills/2026-07-18-loop-convergence-fixes.md | 21 | 14 | 7 | 6 | 8 |
| monkey-skills/2026-08-30-backlog-map-boundary-v2.md | 14 | 7 | 7 | 4 | 7 |
| monkey-skills/2026-07-14-operational-kpi-bitemporal-store.md | 8 | 2 | 6 | 7 | 7 |
| monkey-skills/2026-07-14-operational-kpi-review-queue.md | 7 | 1 | 6 | 7 | 11 |

## 3 concrete examples (sanity-check the clustering against real content)

**1. `monkey-skills/2026-07-13-us-sec-financial-table-xval.md`** (17 → 3
fanouts). Tasks 3-16 (14 tasks, the CLI/report skeleton plus every matcher
rule built on it) all edit the same two files —
`investing-toolkit/skills/analysis-xval/scripts/xval_compute.py` +
its test file — building up one cross-validation matcher one rule at a time
(non-dimensional match → dimensional match → unmatched routing →
divergence bands → scale/rounding tolerance → restatement signal →
decimal-disagreement → high-alert surfacing → citations), each declaring
`Task N-1 completes first`. A second, separate 2-task cluster is Tasks 1-2
(the Source A extractor, its own file); Task 17 (the SKILL.md doc) stands
alone — 14 + 2 + 1 = 17 tasks in 3 clusters. This is the clearest "should
obviously batch" case: one module, one linear TDD chain, same reviewer
context needed for every step. Today it's 17 separate reviewer dispatches;
the plan's own `## Notes` explicitly says flipping any task's Files-touched
to avoid the shared file would violate its own pairwise-disjointness check —
the plan author already knew these were coupled.

**2. `monkey-skills/2026-08-30-outcome-map-v3.md`** (26 → 9 fanouts).
`loom-workflow/skills/decision-map/scripts/map_store.py` is a hub file:
Tasks 2, 3, 4, 5, 6, 7, 12, 14, 16, 18, 19, 20, 21 all touch it (directly or
transitively via `Dependencies`), clustering into one 13-task component.
Three smaller clusters form around the plan's other store modules —
`delivery_evidence.py` (Tasks 8, 9, 15), `map_transaction.py` (Tasks 10, 13,
24), and `migrate_map_v3.py` (Tasks 11, 17) — leaving 5 tasks unclustered.
This is a schema-migration plan where most of the work is incremental
invariants on one store module — a textbook batching candidate, though at
13 tasks its largest cluster is also the corpus's best argument for the
size-cap caveat above.

**3. `kumiko-zaiku-app-icons/2026-08-18-axonometric-perspective-and-grounded-slats.md`**
(16 → 6 fanouts, largest cluster 11: Tasks 1, 2, 3, 5, 6, 7, 8, 9, 15, 16, and
one more). Tasks 1/6/7/8/9 all add assertions to the same
`tests/test_render_blender_smoke.py` acceptance-line file, Tasks 1/3/5
each pin one SSOT row in `docs/loom/design-log.md`, and Task 15 (paper
sinking into the floor) touches both `paper.py` and `depths.py` — the
files three earlier tasks already own — chaining the whole camera/floor/paper
rework into one component. Same shape as example 1, different domain
(rendering geometry vs. financial cross-validation), confirming this isn't
an artifact of one plan author's style. The plan's own Notes section
independently reaches the same conclusion by hand: it flags only 5 of 16
tasks as parallel-safe, explicitly because the rest share
`design-log.md` or the smoke-test file.

## Parse coverage (honest accounting)

- **295** `docs/loom/plans/*.md` files found across the 7 repos (worktree
  duplicates excluded — `find` was scoped to each repo's canonical
  `docs/loom/plans/` directory only, `maxdepth 1`).
- **283 parsed** (had ≥1 `## Task N` heading and ≥1 task survived parsing)
  and are in `per_plan.csv` / the totals above.
- **12 skipped**, all for the same reason: **no `## Task N` heading** —
  these are genuinely pre-schema free-form plans (checklists, "## Tasks
  (atomic, TDD each)" prose sections, or a `superpowers:`-era format
  predating this repo's `writing-plans` schema entirely — e.g.
  `reading-list-summarize-scraper/2026-03-28-*.md`, a file-map + prose
  plan with no per-task field blocks at all). Nothing was force-fit; these
  simply carry no `Files touched` / `Dependencies` grammar to simulate over.
  List: `2026-07-04-loom-code-mechanical-gates.md`,
  `2026-07-06-gate-friction-pack.md`, `2026-07-06-loom-code-router-card-slim.md`,
  `2026-07-07-loom-user-communication-overhaul.md`,
  `2026-07-12-verdict-layer-defenses.md`, `2026-07-18-knowledge-triage-three-buckets.md`,
  `2026-08-16-loom-design-merge-plan.md` (monkey-skills);
  `2026-04-04-phase1-foundation.md`, `2026-04-07-sherpa-sidecar-refactor.md`,
  `2026-05-05-speaker-id-improvements.md` (meeting-emo-transcriber);
  `2026-03-29-exclude-availability-filter.md` (youtube-summarize-scraper);
  `2026-05-14-model-card-column-scroll.md` (intellij-dbtree).
- **2114 tasks parsed** across the 283 plans (47 mechanical, excluded from
  fan-out per the brief).
- **14 of 283 parsed plans carry a parser warning** (partial-field
  degradation, not exclusion) — 150 field-level warnings total, concentrated
  in the corpus's oldest plans (`meeting-emo-transcriber`'s 4 earliest plans,
  `reading-list-summarize-scraper`'s founding plan, `intellij-dbtree`'s ELK
  migration, a handful of `monkey-skills` plans from 2026-07). These
  predate the `Files touched` / `Dependencies` field grammar entirely (an
  even older "checkbox + file-map table" style, or a plan whose fields use
  different labels). The parser's fallback is conservative in the safe
  direction: a task missing `Dependencies` is treated as **no dependency
  edges** (never over-clustered), and a task missing `Files touched` is
  treated as **empty file set** (never a false file-overlap match) — so
  these plans undercount knob ② benefit rather than overclaim it. This is
  also most of why `meeting-emo-transcriber` and `intellij-dbtree` show
  `fanouts_k2 == fanouts_now` for their whole repo total: their plans
  predate the field grammar this simulation depends on, not because those
  plans truly have zero batching opportunity.
- **7 of 283 plans are "batch-era"** (carry a `Review disposition` field or
  a `## Review Batches` section) — matches the brief's ballpark of 6.
  `fanouts_now` already nets out their existing batches, so the reduction
  numbers above are not double-counting knob ② against work already batched
  by hand.
- Task-ID grammar is **not restricted to integers** — this corpus uses
  letter/mixed IDs (`5a`, `F3`, `D1`, `A1`) in some plans; the parser
  treats task IDs as opaque tokens throughout, so dependency-edge matching
  works identically for numeric and non-numeric IDs.

## Knob ② with a batch-size cap (K = 3, 4, 5, 6)

Same strict (file-overlap-gated) connected components as `fanouts_k2` above,
but each component is now split into batches of **at most K tasks**, filled
in topological order over in-cluster dependency edges only (so a batch never
contains a task whose in-cluster dependency lands in a later batch — chunking
a valid topo order sequentially guarantees this by construction). New CSV
columns: `fanouts_k2_cap3` .. `fanouts_k2_cap6`. "Plans still at the cap" =
plans whose largest uncapped component is ≥ K (i.e. would still produce at
least one full-size K batch after splitting).

| group | fanouts_now | K=3 | K=4 | K=5 | K=6 |
|---|---:|---:|---:|---:|---:|
| **Overall** (283 plans) | 2060 | 1694 (17.8%, 75 plans at cap) | 1668 (19.0%, 36 at cap) | 1659 (19.5%, 21 at cap) | 1651 (19.9%, 17 at cap) |
| **monkey-skills** (254 plans) | 1821 | 1500 (17.6%, 66 at cap) | 1476 (18.9%, 29 at cap) | 1469 (19.3%, 14 at cap) | 1465 (19.5%, 12 at cap) |
| **6 application repos combined** (29 plans) | 239 | 194 (18.8%, 9 at cap) | 192 (19.7%, 7 at cap) | 190 (20.5%, 7 at cap) | 186 (22.2%, 5 at cap) |

Each cell is total fan-outs (% reduction vs `fanouts_now`, plans that would
still produce at least one full K-size batch). The reduction curve is nearly
flat from K=4 onward (18.9% → 19.5% overall) and tops out just under the
uncapped `fanouts_k2` ceiling of 20.5% — most of knob ②'s benefit is
already captured by K=4, and a cap this low costs almost nothing in
review-load reduction while directly bounding the largest-cluster concern
raised above (the outcome-map-v3 and xval examples' 13-14-task clusters
would become 3-4 batches of ≤5 each at K=5).

## What it takes to reach -50% (three more aggressive edge definitions, cap K=4)

kouko asked what -50% would require. Four variants, all capped at K=4 except
D (kept at K=6 as the strict-clustering reference point from the section
above): **(A) loose** = dependency edge AND same lane, no file gate;
**(B) wave** = same dependency-depth level AND same lane, regardless of
edges/files ("review each wave as one batch"); **(C) module** = same lane
AND (dependency edge OR shared `Module` field value), file gate replaced by
Module equality; **(D) strict/cap6** = this doc's existing file-gated
knob ② from the section above, unchanged, included only for scale
reference. New CSV columns: `fanouts_a_loose_cap4`, `fanouts_b_wave_cap4`,
`fanouts_c_module_cap4`, `fanouts_d_strict_cap6`, `noshare_a/b/c/d`.

| group | fanouts_now | A loose (cap4) | B wave (cap4) | C module (cap4) | D strict (cap6) |
|---|---:|---:|---:|---:|---:|
| **Overall** (283) | 2060 | 835 (−59.5%) | 1104 (−46.4%) | 813 (−60.5%) | 1651 (−19.9%) |
| **monkey-skills** (254) | 1821 | 710 (−61.0%) | 983 (−46.0%) | 689 (−62.2%) | 1465 (−19.5%) |
| **6 app repos** (29) | 239 | 125 (−47.7%) | 121 (−49.4%) | 124 (−48.1%) | 186 (−22.2%) |

**Answer: A and C both clear -50% overall** (and on monkey-skills alone);
**B clears it only on the 6 app repos**, not overall. D (this doc's earlier
recommendation) does not get close.

**No-shared-file batch counts (proxy for "unrelated tasks merged"), overall
n=283:** A=272 of 835 batches (32.6%) share no file with any other member;
B=459 of 1104 (41.6%); C=279 of 813 (34.3%); **D=0 of 1651 (0%)**. Reading
-50% off A or C means roughly **1 in 3 resulting batches would pair tasks
that touch zero files in common** — B is worse (2 in 5); D stays clean only
because it never breaks the file-overlap requirement that defined its
clusters in the first place. -50% is reachable, but not for free: A/C buy
it by admitting same-Module-or-same-wave grouping that ~a third of the time
produces a batch with no shared-file evidence a reviewer could point to.
