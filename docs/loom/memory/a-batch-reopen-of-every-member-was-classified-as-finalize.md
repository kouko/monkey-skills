---
name: a-batch-reopen-of-every-member-was-classified-as-finalize
description: plan_card.py derived a batch transition's direction from which KEYS changed between the ledger and the replacement dict (set(replacements) == members), not from what the VALUES changed TO — a full-membership REOPEN (every member's status moved backward) touches exactly the same key set as a full-membership finalize, so the heuristic misclassified the first live full reopen as a finalize and the batch was unrecoverable until fixed
type: gotcha
origin: adversarial-audit-station arc, docs/loom/plans/2026-08-31-adversarial-audit-station.md — first live full-membership reopen (station-prose batch, 2026-08-31), fixed at d1fa5e07
---

`plan_card.py`'s batch-transition classifier compared the SET of task
keys being written against the batch's member set to decide whether a
ledger write was a "finalize" (all members done) or a partial update.
That comparison is blind to direction: reopening every member of a
batch back to `claimed`/`pending` writes the identical key set as
finalizing every member to `done`. The classifier had no signal that
distinguished "these values all became done" from "these values all
became not-done" — it only ever asked "did every member's key appear
in this write." The first time a real batch needed a full reopen (not
a partial one), it was silently recorded as a finalize and the batch
became stuck: the ledger said done, apply-result refused to re-run,
and there was no clean path back except a manual fix, landed at
d1fa5e07. The unit-test fixture that exercised the classifier carried
the same key-set heuristic baked into its expected behavior, so it
could not have caught this — it was testing the bug's own assumption.

**Why:** a batch operation's meaning lives in the VALUES the write
moves fields to, not in which fields the write touches — two opposite
transitions (finalize-all, reopen-all) are indistinguishable by key
membership alone, and any classifier that only diffs key sets will
alias them.

**How to apply:** derive transition direction (finalize vs reopen)
from the values being written (old status → new status per member),
never from `set(new_keys) == member_set`. When a test fixture mints
authority for a classifier under test, pass the intended direction
into the fixture explicitly rather than letting the fixture re-derive
it the same way production code does — otherwise the fixture and the
bug share the same blind spot.
