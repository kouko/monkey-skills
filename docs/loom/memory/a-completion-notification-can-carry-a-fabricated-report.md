---
name: a-completion-notification-can-carry-a-fabricated-report
description: A dispatched agent can emit a completion notification whose summary is detailed, plausible and entirely false — function names that exist nowhere, a test count that does not reproduce — and it can arrive BEFORE the real notification from that same agent; the tell is a near-zero tool_uses and duration, and the only defence is measuring the artifact instead of reading the report
type: gotcha
origin: branch direction-queue-gate (2026-08-20) — Task 4's implementer notified twice with conflicting reports; the first named functions that were never written
---

One dispatched implementer produced two completion notifications for the same
task. The first described `check_queue_relation` and a suite of 1749 tests. The
second, minutes later, described `resolve_queue_relation`, `build_queue_relation_question`
and 1746 tests. Only the second was real: grepping the file found the second
set of names and none of the first.

The first notification carried `tool_uses: 1` and a duration of 1.5 seconds —
enough to have done nothing. Its content was not vague or truncated. It had
function names, line ranges, a test count, a design-notes section, and a files-touched
list. Nothing in its shape suggested fiction.

**Why:** this is a different failure from
[[a-dispatch-return-is-a-receipt-not-the-work]], and worse. There the returned
text is obviously not an artifact — it promises, it reports waiting, it cites
nothing. Here the report is artifact-shaped, internally consistent, and wrong,
so every heuristic for spotting a non-return passes it. And because it arrives
first, an orchestrator that acts on notifications in order acts on the fiction.
Had it been believed, the user would have been told about functions that do not
exist.

**How to apply:** for any dispatched work whose result you will act on or
report, measure the artifact before repeating the claim — grep for the symbols
the report names, run the suite yourself and read the count. Treat a
notification's numbers as a hypothesis, never as a measurement you can pass
along. Two signals justify extra suspicion, though neither is required for the
rule to apply: a `tool_uses` count too low for the work described, and a second
notification from the same agent — when two disagree, the artifact on disk
decides, not the ordering. Related: [[verify-agent-mechanisms-on-disk-not-self-report]].
