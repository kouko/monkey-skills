---
name: a-sealed-review-packet-freezes-the-whole-plan-file-until-apply-result
description: A batch ReviewPacket's identity digests the ENTIRE plan file, so any write to the plan between `packet` and `apply-result` — a `claimed`/`done` flip on a task outside the batch, a Decision Log line — changes the rebuilt identity and the receipt binding refuses with "packet_identity does not match the rebuilt packet"; freeze the plan from `packet` to `apply-result`, and if it moved, re-seal, re-record, and rebind the unchanged reviewer results — never edit the receipt
type: gotcha
origin: batch-review-hardening (2026-08-31) — the first live run of the receipt-bound apply-result refused twice on this exact shape (orchestrator flipped T4/T5/T7 ledger lines and then committed DL-3 while the T1–T3 batch was out for review); member shas were identical both times
---

The sealing is right: the plan is the execution authority, and a plan that
changed must not be finalized against a receipt issued for the old one. The
trap is what "changed" covers. `build_packet` folds a digest of the whole
plan text into the packet identity; `record-dispatch` stores that identity;
apply-time binding compares it. A `Status:` line on a task outside the batch
is irrelevant to the reviewed bytes but moves the digest all the same, and
the refusal names identity drift, not the ledger flip that caused it.

Recognise it by: `apply-result` exits 1 with `action: null` and the reason
"packet_identity does not match the rebuilt packet; re-send the dispatch",
while every member's `implemented(<sha>)` is unchanged and `ready` still
says true.

Correct path: from `packet` to `apply-result`, do not write the plan — run
other waves' ledger flips before sealing or after applying. If it already
moved: run `packet` again (new identity), move the old receipt OUT of the
`--out` directory (any receipt-shaped JSON there, including a `tee`'d copy
of record-dispatch's own stdout, counts as an unapplied sibling and blocks
the re-send), `record-dispatch` again, rewrite `packet_identity` in the
reviewer result file to the new identity, then `apply-result`. Rebinding is
honest only when member shas and sealed bytes are identical; otherwise the
reviewers must re-review.
