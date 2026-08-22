---
name: autonomy-needs-a-small-explicit-stop-set
description: Autonomous execution is reliable only when it advances approved bounded work by default and uses one small explicit set of authority and safety stops; duplicate prompts and empty work queues are notifications, not reasons to ask.
type: practice
origin: branch loom-autonomy-defaults (2026-08-22)
---

An agent can keep moving after a bounded plan is approved only when its
default and exceptions are stated together. Advance work that is already
approved and within scope. Stop for ambiguous authority or safety-sensitive
actions such as privacy, merge, deploy, or deletion. Notify rather than ask
when no decision is required, including an empty queue.

**Why:** A flow that asks at every station turns coordination into a hidden
manual queue. A flow with no explicit stops can exceed the authority the user
actually granted.

**How to apply:** Put the same four outcomes at the orchestration boundary:
auto-resolve safe bounded work; notify for low-risk status; ask when authority
or scope is unclear; halt and escalate for defined safety stops. A downstream
skill must honor an authorization already delegated by that boundary instead
of asking for it again.
