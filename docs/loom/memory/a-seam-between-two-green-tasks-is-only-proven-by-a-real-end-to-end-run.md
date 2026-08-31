---
name: a-seam-between-two-green-tasks-is-only-proven-by-a-real-end-to-end-run
description: When a feature's value is a PATH through several tasks (a CLI over a sealed library, a plan ledger writer, a checker), each task's per-task review and green suite prove only that task's assumption of the seam — the first real run on real inputs is where the path breaks; budget one end-to-end dogfood task on real artifacts (not synthetic fixtures) into the plan before declaring the path shipped
type: practice
origin: contract-repair-post-v3 (2026-08-31) — the batch-review adapter (R7) passed per-task triads, then the first real `packet` run on the arc's own plan refused at three seams none of which were in the adapter: the projection validator accepted only REQ- referents while plan-format admits quotes/BI ids; plan_card wrote short SHAs while the sealed chain demands 40-hex; apply-result never wrote the ledger. R11 added T14–T17 and the pilot (T17) measured dispatches 10 → 2 only after those landed
---

Task Batch Review shipped in #766 with every task green and per-task
reviewed, and no real plan could reach its batch path. The adapter arc
that repaired it (R7–R9) also passed every per-task triad — and its
first `batch_review_cli.py packet` on a real plan was refused. All three
causes lived in files no adapter task touched: `review_batch.py:1261`
wanted `REQ-` prefixes, `plan_card.py` accepted short SHAs, and
`apply-result` printed a resolution it never wrote back.

The pattern: a per-task RED/GREEN pins that task's reading of the seam;
a synthetic fixture built by the same author encodes the same reading.
Two green tasks agree on nothing until something runs the producer's
bytes through the consumer's parser on a real artifact.

What to do: when the deliverable is a path, the plan carries one task
whose GREEN is "the path runs end to end on this repo's own live
artifact" — here, the arc's own plan and batch. That task is the pilot,
not an afterthought; put it after the seam fixes and let its RED be the
refusal you actually observed.
