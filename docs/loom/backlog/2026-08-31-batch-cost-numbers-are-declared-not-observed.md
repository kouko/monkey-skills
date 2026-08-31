---
name: 2026-08-31-batch-cost-numbers-are-declared-not-observed
description: task_batch_replay.py compares declared review_dispatches/review_rounds numbers typed into JSON, not anything the harness observed, so compare PASSes on an unfalsifiable input
status: open
origin: 2026-08-31 — independent adversarial audit of main 96a56d8b (loom-code 0.106.0) after PR #767; finding F10, declined from the batch-review-hardening arc (docs/loom/specs/2026-08-31-batch-review-hardening.md §Out of Scope)
start: event — the next batch pilot is run, or the 10→2 number is cited as evidence outside its plan
---

`loom-code/scripts/task_batch_replay.py` reads `review_dispatches` and
`review_rounds` as plain numbers typed into a JSON file; nothing in the
pipeline observes an actual dispatch or counts an actual review round.
`compare` PASSes whenever the candidate's declared number is lower than
the baseline's declared number, which is true by construction for any
input someone chooses to type in — the check cannot fail on a dishonest
or mistaken input, only on an honest one that happens to be worse.

The 2026-08-31 pilot's headline number (10 dispatches down to 2) is a
concrete instance, not just a hypothetical: it is n=1, its baseline
includes NEEDS_REVISION re-review cycles while the candidate arc passed
on the first try, and nothing in the pilot record distinguishes "the
mechanism is better" from "this one run got lucky." Citing 10→2 as
evidence for the mechanism, rather than as one data point about one run,
overstates what was measured.

A rigorous measurement needs harness-emitted counts (the dispatch and
review-round totals come from the orchestrator's own log, not typed
JSON), at least 5 batches, and at least one reopen cycle exercised on
both the baseline and candidate arms so the comparison isn't
first-try-vs-retried by construction.
