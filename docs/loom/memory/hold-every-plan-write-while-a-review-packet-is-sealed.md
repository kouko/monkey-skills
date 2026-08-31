---
name: hold-every-plan-write-while-a-review-packet-is-sealed
description: A sealed batch ReviewPacket's identity digests the WHOLE plan file, so any other write to the plan between `packet` and `apply-result` — a claim flip, a Notes line — forces a re-seal + re-record + rebind of the unchanged reviewer results; on this arc it happened FOUR times in one run, and each re-record hit a second trap — an orphan superseded receipt (result_applied false) left in the scan directory blocks the re-send until moved out; apply-result also refuses while ANY batch member on the plan is still not implemented
type: gotcha
origin: adversarial-audit-station arc, docs/loom/plans/2026-08-31-adversarial-audit-station.md — backlog entries 2026-08-31-packet-identity-binds-whole-plan-text and 2026-08-31-orphan-dispatch-receipt-jams-batch (both start events fired on this arc)
---

This generalizes the identity-binding gotcha already recorded in
`a-sealed-review-packet-freezes-the-whole-plan-file-until-apply-result.md`:
the trap did not resolve to a one-time recognize-and-fix, it recurred
FOUR times across one arc, because the orchestrator kept needing to
write the plan (other waves' ledger flips, Decision Log lines) while a
batch was still out for review. Each recurrence forced the same
recovery: re-seal (`packet`, new identity), `record-dispatch` again,
rewrite `packet_identity` in the reviewer result file, then
`apply-result`. A second, distinct trap compounds it: re-running
`record-dispatch` after a prior attempt leaves the SUPERSEDED receipt
(the one whose `result_applied` is still false) sitting in the scan
directory, and the tooling treats any receipt-shaped JSON there —
including a `tee`'d copy of a previous `record-dispatch`'s own
stdout — as an unapplied sibling and refuses the re-send; recovery is
moving the stale receipt out of the scan directory before retrying.
Separately, `apply-result` also refuses outright while ANY member of
the batch (not just the one being applied) is still not implemented on
the plan.

**Why:** the packet's identity is the whole-plan digest by design (the
plan IS the execution authority), so it cannot be scoped to only the
reviewed bytes without losing that guarantee — but nothing in the tool
chain queues concurrent plan writes, so every unrelated write during a
review window collides with it, and every collision recovery path has
its own second-order trap (orphan receipts, all-members-implemented).

**How to apply:** treat "a batch is sealed for review" as a lock on the
whole plan file — queue every other ledger/Notes write until that
batch's `apply-result` lands, rather than writing opportunistically and
re-sealing reactively. Expect the re-seal to be needed and script it
(re-`packet`, re-`record-dispatch`, rewrite `packet_identity`,
`apply-result`) rather than treating each occurrence as a fresh
incident. Before re-`record-dispatch`, clear superseded receipts from
the scan directory. Do not attempt `apply-result` on one member while
any sibling member of the same batch is still unimplemented.
