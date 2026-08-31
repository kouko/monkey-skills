---
name: 2026-08-31-batch-ready-accepts-what-packet-refuses
description: ready and check_review_batches.py pass plans that packet refuses at dispatch time, with opaque errors that land on whoever runs packet instead of whoever authored the plan
status: open
origin: 2026-08-31 — independent adversarial audit of main 96a56d8b (loom-code 0.106.0) after PR #767; finding F9, declined from the batch-review-hardening arc (docs/loom/specs/2026-08-31-batch-review-hardening.md §Out of Scope)
start: event — the next time packet refuses a plan that ready accepted
---

Two failure modes both pass `check_review_batches.py` and the CLI's
`ready` subcommand (exit 0) but die later in `packet`. First: two batch
members citing the same `Brief item covered` referent — `ready` has no
duplicate-authority check, so `packet` is the first thing to refuse it,
with the message "ownership proof contains duplicate requirement
authority". Second: a member whose `Brief item covered` line reads
`none — <reason>` — legal plan-authoring shorthand for "this task covers
no brief item" — passes `ready` and then dies in `packet` with the
opaque "execution authority member is malformed", giving no hint that
the `none —` form is the cause.

Both failures land on whoever runs `packet` to dispatch the batch, often
a different session than whoever authored the plan and chose the
referents. By the time the error surfaces, tracing it back to the
authoring decision costs a re-read of the whole plan.

Candidate fix: fold both refusals into `ready` or into
`check_review_batches.py`'s validation, so a malformed plan fails at
authoring time, in the authoring session, with the same diagnostic
`packet` would have produced.
