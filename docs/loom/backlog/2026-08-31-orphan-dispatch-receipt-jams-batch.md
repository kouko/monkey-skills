---
name: 2026-08-31-orphan-dispatch-receipt-jams-batch
description: A duplicate receipt with result_applied false for the same batch blocks record-dispatch forever, and the flag is unsigned so hand-editing it unblocks a re-send
status: open
origin: 2026-08-31 — independent adversarial audit of main 96a56d8b (loom-code 0.106.0) after PR #767; finding F7, declined from the batch-review-hardening arc (docs/loom/specs/2026-08-31-batch-review-hardening.md §Out of Scope)
start: event — the next time record-dispatch is refused by a sibling receipt in a live batch
---

`_sibling_unapplied_receipt` in `loom-code/scripts/batch_review_cli.py` scans
the whole receipt directory for any receipt matching the current batch
whose `result_applied` is still `false`. That is the intended guard against
a second concurrent dispatch, but it has no notion of which receipt is the
live one: a duplicate or stale receipt for the same batch — left behind by
a crash, a retry, or an orphaned dispatch that was never going to be
applied — blocks every future `record-dispatch` call for that batch
indefinitely. `apply-result` only flips the one receipt path it is given,
so it cannot clear a sibling it doesn't know about.

The flag is plain JSON with no integrity check, so the same defect cuts
both ways: hand-editing a stale receipt's `result_applied` to `true`
silently unblocks a re-send, with nothing recording that the flip was
manual rather than earned by an actual apply.

Candidate fix: on `apply-result`, flip every same-batch sibling receipt,
not just the one path passed in, and have the jam's refusal message name
the specific blocking file's path so a human can decide whether to
apply it too.
