---
name: 2026-08-13-a-widened-field-grammar-has-no-mechanical-consumer-enumeration
description: the consumer census a plan owes when it widens a field's grammar is performed from memory, so it misses consumers nobody thought of — the same arc missed one consumer its own brief named first, then missed three more of the same class in a second file set; the field-value-microstructure arc (2026-08-19) is a worked instance of the census done in the "Reverse" line of a brief's Current State Evidence
status: open
origin: brief-item-addressability arc (2026-08-13) — two independent misses of one class; the practice exists as prose in docs/loom/memory but has no enumeration step
start: next arc that widens or narrows a value grammar in a loom contract file, or the next touch of writing-plans' plan-document-reviewer prompt
---

The arc widened `Brief item covered` to accept two new referent forms. It owed
every consumer of that field's grammar either a task or a recorded reason it
needed none. It did the census, and did it well in part — it checked
`plan_card.py`, found the field is read as an opaque string, and correctly
recorded "no change needed".

It then missed consumers **twice**:

1. `plan-document-reviewer-prompt.md`, whose Check 3 enumerates accepted
   referent kinds — the consumer the brief's own `## Users` section named
   FIRST. Found mid-arc by an implementer who happened to open the file.
2. `writing-plans/README.md` and its `.ja` / `.zh-TW` siblings, still calling
   the field quote-only. Found at whole-branch review, by the docs arm, in
   files outside its own dispatched scope.

Both were caught, so nothing shipped wrong. The cost was rounds, and the
second miss happened **after** the arc had already written the memory entry
warning about exactly this class
(`docs/loom/memory/widening-a-value-grammar-needs-a-consumer-census-at-plan-time.md`).
A practice that its own author re-violates within one arc is not a practice
problem; it is a missing mechanism.

**Why prose does not hold here.** The census asks the author to recall every
file that reads a field. Recall is the wrong instrument: the miss is silent
(no gate fires, the widened value is legal in the SSOT and simply gapped
downstream), and the tell is subtle — a downstream gate rejecting the new
value reads as a defect in the value rather than as evidence about the gate,
so fixing the symptom removes the signal.

**Candidate mechanism.** At plan time, for any task changing what a field may
legally contain, run a grep for the field's own name across the repo's
contract surfaces and paste the hit list into the plan, one line per hit:
task, or reason it needs none. The list is derived, not remembered, so a
consumer that exists cannot be absent from it. Start the sweep from the
brief's `## Users` — a stakeholder the brief names is a consumer the plan owes
an answer about, and that is precisely where miss (1) sat.

Open sub-question, not yet decided: whether this is a plan-document-reviewer
check (blocks on a missing census table) or an authoring instruction in
`plan-format.md` (visible, unenforced). The reviewer-check version is
mechanically verifiable and therefore preferred, but it needs a definition of
"contract surface" that does not turn into a repo-wide grep on every plan.

Related: [[2026-08-13-a-plan-can-dispatch-a-task-whose-acceptance-depends-on-an-unresolved-open-question]]
(the sibling plan-time gate proposed from the same arc's evidence).

## Worked instance (2026-08-19, field-value-microstructure arc)

This entry's start condition — "next arc that widens or narrows a value
grammar in a loom contract file" — fired: the arc at
`docs/loom/plans/2026-08-19-field-value-microstructure.md` widens the
`Description`/`Goal`/`Acceptance.RED`/`Acceptance.GREEN` field grammar
(BI-1, BI-2, BI-6). Its brief's Current State Evidence section derived,
rather than recalled, the hit list this backlog entry's "Candidate
mechanism" proposed: a `Reverse` line naming `plan-format.md` as the
grammar's SSOT, restated by `writing-plans/README.md` and its `.ja` /
`.zh-TW` mirrors, and graded by `plan-document-reviewer-prompt.md`
Checks 3, 7, 16, 17, 18 — each hit then got its own plan task (Task 7 =
`plan-format.md`, Task 9 = the three README mirrors, Task 10 = the
reviewer-prompt check). No consumer in that list was found late or
missed; the census ran at brief-authoring time, not per-task. The open
sub-question this entry left unresolved (reviewer-check vs authoring
instruction) is still unresolved — this instance used a brief-time
prose enumeration, not a mechanical grep gate.
