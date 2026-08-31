---
name: 2026-08-31-packet-identity-binds-whole-plan-text
description: A sealed ReviewPacket's source_digest covers the entire plan file, so any ledger flip on a NON-member task between `packet` and `apply-result` invalidates the packet and the receipt binding refuses — correct but a trap for an orchestrator running other waves concurrently
status: open
origin: 2026-08-31 — first live batch checkpoint on the batch-review-hardening plan (Decision Log DL-3 there): the orchestrator flipped T4/T5 to done and T7 to claimed while the apply-result-binding batch (T1–T3) was under review; apply-result refused with "packet_identity does not match the rebuilt packet"
start: event — the next time apply-result refuses on packet_identity drift with every member sha unchanged, or when the batch-eligibility nudge entry (2026-08-31-batch-eligibility-should-push-toward-batching) is picked up, since wider batches make concurrent non-member ledger flips more likely
---

`build_packet` derives `source_digest` from the whole plan text and folds it
into the packet identity; `record-dispatch` stores that identity; the
receipt binding shipped in the hardening arc compares it at apply time.
Every part is right on its own — the plan is the execution authority, and a
changed plan must not be finalized against an old receipt. The trap is what
counts as "changed": a `Status:` line on a task outside the batch is
irrelevant to the reviewed bytes, yet it moves the digest, so an orchestrator
that keeps other waves moving while a batch is out for review gets a refusal
whose message points at identity, not at the ledger flip that caused it.

Two shapes for a fix, neither chosen: (a) narrow the digest to the batch's
execution projection plus its members' task blocks, so non-member ledger
lines cannot perturb it — smallest change, but the projection must then be
proven to cover everything the reviewer's verdict depended on; (b) keep the
whole-plan digest and make the refusal message name the plan lines that
differ from the sealed text, so the orchestrator can see it was a ledger
flip and re-seal with confidence. (b) is the honest floor even if (a) is
adopted. Until either lands, the operating rule is: from `packet` to
`apply-result`, the plan file is frozen.
