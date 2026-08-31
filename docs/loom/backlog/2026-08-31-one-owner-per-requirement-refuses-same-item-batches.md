---
name: 2026-08-31-one-owner-per-requirement-refuses-same-item-batches
description: batch_review_cli.py packet refuses a Review Batch whose members cite the same Brief item ("ownership proof contains duplicate requirement authority"), so the module rule that pushes same-module dependency chains into one batch collides with the one-owner-per-requirement ownership proof — the planner must split the item into per-task clauses by hand
status: open
origin: 2026-08-31 — batch-review-measurement-and-nudge arc, sealing batch `proposer` (Tasks 7/8/9, all `Brief item covered: BI-3`); resolved in-arc by citing BI-3 clauses verbatim per task (plan-format referent kind (a)), recorded in that plan's Notes
start: event — the next plan where propose_review_batches.py proposes a batch whose members share one BI-/REQ- id, or when 2026-08-30-task-review-packets-lack-requirement-ownership is picked up (same ownership model)
---

The ownership proof in `review_batch.py` requires every owned requirement
in a batch to have exactly one owner (`len(set(requirements)) !=
len(requirements)` → refused). That is the right invariant for the
per-task packets it was written for, but a brief item like BI-3 naturally
spans a proposer script, its `--check` mode and the prose that names them —
three tasks, one module, one item. The module rule (this arc) clusters
exactly those tasks, and the ownership proof then refuses the batch at
`packet` time, after `ready` and `check_review_batches.py` both said yes
(the same shape as 2026-08-31-batch-ready-accepts-what-packet-refuses).

Two candidate fixes: (a) let `check_review_batches.py` refuse the duplicate
at plan time with a message naming the clause split (cheap, moves the error
to the author); (b) treat a shared item inside one batch as jointly owned —
the batch's verdict question is already one end-to-end question, so joint
ownership is what the reviewer answers anyway. (a) is the floor; (b) needs
the attribution rule in `_classify_findings` to accept a multi-owner
finding.
