---
name: 2026-08-31-proposer-is-near-variant-c-not-variant-c
description: propose_review_batches.py reproduces the simulation's fanouts_c_module_cap4 on 178 of 254 monkey-skills plans, diverges on 5 (e.g. 2026-08-11-review-cost-reduction 6 vs 7) and refuses 71 pre-DAG-grammar plans the simulation's lenient parser accepted — the docstring's "changing the rule invalidates the record's numbers" claims an equivalence the branch pinned on one plan
status: open
origin: 2026-08-31 — whole-branch review arm A of the batch-review-measurement-and-nudge arc ran the shipped proposer over every CSV row (Task 7 pins only 2026-07-13-us-sec-financial-table-xval.md)
start: event — before the edge rule or the cap is re-sized from the simulation, or when the sink-chunking entry (2026-08-31-proposer-chunks-components-linked-only-through-a-sink) is picked up — both change the clustering and need a corpus-wide oracle first
---

The five divergent plans are the diagnostic: the simulation's parser
(`docs/loom/dogfood/2026-08-31-batch-knob-simulation.py`) normalises
`Module` and reads `Dependencies` leniently, while the proposer reads
through `check_review_batches.py`'s closed grammar. Where they disagree,
one of them is mis-reading a real plan. A parametrized test over the CSV
(`fanouts_c_module_cap4` per row, skipping refused plans with the refusal
reason recorded) makes the equivalence claim checkable and turns the 5
divergences into named cases to resolve — either the simulation is re-run
with the oracle's parser (then the record's numbers move) or the proposer
gains the lenient read for pre-batch-era plans. Until then the docstring
should say "sized from", not "reproduces".
