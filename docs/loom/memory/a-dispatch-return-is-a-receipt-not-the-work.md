---
name: a-dispatch-return-is-a-receipt-not-the-work
description: An Agent dispatch returns an acknowledgement immediately and the child's real output arrives later as a separate notification, so a subagent that fans work out and then ends its own turn hands the parent that receipt — text like "I'll wait for their completion notifications" — as if it were the task's result; observed 3x in one session, and the guard is an explicit no-fan-out line in the dispatch packet
type: gotcha
origin: branch plan-field-microstructure (2026-08-19) — T14's implementer returned early three times; the harness fact was re-probed live the same day
---

Dispatching an agent returns two things at two different moments. The call
itself returns only an acknowledgement — an id and a note that the agent is
working in the background. The child's actual output arrives later, as a
separate notification. Both facts were re-probed live on 2026-08-19: a
`general-purpose` subagent dispatched a trivial child, received the
acknowledgement synchronously with no result in it, and got the child's real
answer only in a later notification event.

An agent that mistakes the first for the second ends its turn there. Its final
text becomes its return value, so the parent receives a sentence like *"I'll
wait for their completion notifications"* in the slot where the work belongs.
Nothing errors, no child is lost, and the parent sees a well-formed report of
a task that was never done. This happened three times in one session, to the
same task, until the fan-out was forbidden outright.

**Why:** the failure is invisible from both ends. The parent gets a fluent
report and has no signal distinguishing it from a real one; the children
finish correctly and write real output that nobody reads. The delegation looks
completed precisely because every individual step succeeded — the only broken
link is that the intermediate agent stopped between them. And an agent under a
"return conclusions, not file dumps" instruction is already primed to return
something short, which is what a receipt looks like.

**How to apply:** put an explicit no-fan-out line in the dispatch packet of any
worker expected to do the work itself — *do this task yourself; do not
dispatch sub-agents* — rather than relying on the worker to wait correctly.
When a returned result reads like a status update rather than an artifact (it
promises, plans, or reports waiting, and cites no `file:line` and no concrete
output), treat it as a non-return: re-dispatch with the no-fan-out line, or
take the task over inline. Never write it into the ledger as done. If a nested
panel is genuinely wanted, the parent dispatches the panel as siblings itself
— related: [[skill-in-subagent-loses-internal-orchestration]] (whose original
"subagents have no Agent tool" mechanism is corrected there; this entry is the
ground its recommendation now rests on).
