---
name: 2026-08-07-plan-time-complexity-budget-fields
description: writing-plans could record a per-task complexity budget (new abstractions / new files) for reviewers to check overshoot
status: open
blocked: waiting on the deletion-first review dimension demonstrably failing to catch over-engineering across two or more arcs
origin: 2026-08-07 family complexity audit (docs/loom/audits/2026-08-07-family-complexity-audit.md, item E2)
start: the deletion-first review dimension (audit item E1) demonstrably fails to catch over-engineering — complexity findings recur across two or more arcs despite it
---

Research grounding: autoregressive models optimize local coherence and
nothing tracks accumulated complexity at inference time, which argues
for a generation-time anchor, not just post-hoc review. The candidate
mechanism: writing-plans records per-task expected new-abstraction and
new-file counts; the reviewer flags overshoot. Budget must be counted in
abstractions/interfaces, never LOC — this repo has pinned LOC as a wrong
proxy (gate on task kind, not size).

Parked behind E1 deliberately: legislate the minimal form first
(review dimension riding existing rounds), escalate to plan-time budget
fields only on evidence that the minimal form is insufficient.
writing-plans is itself a complexity hotspot; adding fields to it needs
that evidence.
