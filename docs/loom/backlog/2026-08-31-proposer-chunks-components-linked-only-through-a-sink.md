---
name: 2026-08-31-proposer-chunks-components-linked-only-through-a-sink
description: propose_review_batches.py (and the simulation it reproduces) splits a connected component into cap-4 chunks in topological order, so tasks whose only link is a shared sink (the version-bump task everything depends on) get proposed as one batch — the −60% figure and the `--check` reason-line demands both inherit that
status: open
origin: 2026-08-31 — Task 12 pilot of the batch-review-measurement-and-nudge arc: on its own 12-task plan the proposer produced [1,2,3,4] [5,6,7,8] [9,10,11] + [12], while the plan's three declared batches follow direct edges; seven `Not batched because` lines were owed, most for pairs with no direct edge and different Modules
start: event — when the first arc after this one runs `--check` and finds itself writing "only transitively connected through the version-bump sink" more than twice, or before re-sizing the cap or edge rule from the simulation
---

Variant C's edge rule is sound per pair (same lane AND (direct edge OR same
Module)), but components are formed by transitive closure and then cut by
cap in topological order, so a sink task that depends on everything glues
the plan into one component and the cut pairs tasks that share nothing but
that sink. The simulation's own `noshare_c` column (34% of proposed batches
share no file) is the same effect measured. The honest count of "pairs the
rule itself endorses" is smaller than the −60% headline.

Candidate fix: chunk by direct-edge adjacency — a batch must be a connected
subgraph under the pair rule (every member has a direct edge or same Module
with at least one other member), and sinks with more than N incoming
edges are excluded from clustering (release administration is never
review-batched anyway). Re-run the simulation with that rule before
changing the constants; record the new per-plan column beside
`fanouts_c_module_cap4`.
