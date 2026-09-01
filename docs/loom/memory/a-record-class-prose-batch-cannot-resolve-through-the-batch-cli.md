---
name: a-record-class-prose-batch-cannot-resolve-through-the-batch-cli
description: An all-record-class prose Review Batch has a valid single-arm resolution in the batch library but no path through the batch review CLI, so it must resolve task-by-task through individual review instead
type: gotcha
origin: 2026-09-01 — prose-edit self-sweep arc (docs/loom/plans/2026-09-01-prose-edit-self-sweep.md, DL-2); backlog 2026-09-01-apply-result-cannot-take-record-class-narrowed-arms
---

The prose review lane's library contract accepts a single-arm
(`spec-reviewer` only) resolution when every batch member is
record-class — the docs-reviewer slot is N/A by construction, since a
docs-reviewer correctly refuses to mint a verdict for record-class
files it has no jurisdiction over. But the batch review CLI's
apply-result step computes the expected arm set from the lane alone,
so it demands both arms and cannot consume the single-arm result the
library permits. A second coupling compounds it: the plan-card ledger
refuses a direct `done(<sha>)` write for any task still declared a
batch member, so even the individual-fallback exit is blocked until the
plan's dispositions are amended off the batch.

**Why:** A batch whose members are all under `docs/**` (or any
record-class path) is exactly where batching is cheapest, yet it is the
one shape the CLI cannot close — the saving is lost precisely when a
real defect is found and the arm-narrowing should have applied.

**How to apply:** When a Review Batch's members are all record-class,
do not route it through the batch review CLI. Amend each member's
disposition to individual review up front, dispatch spec-reviewer alone
per task (record the code-quality/docs slot as N/A — record-class
prose), and skip the batch packet entirely. Reserve the batch CLI for
batches with at least one contract-class member.
