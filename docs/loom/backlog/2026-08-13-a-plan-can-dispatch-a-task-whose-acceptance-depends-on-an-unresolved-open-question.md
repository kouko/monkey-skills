---
name: 2026-08-13-a-plan-can-dispatch-a-task-whose-acceptance-depends-on-an-unresolved-open-question
description: nothing stops a plan from dispatching a task whose acceptance criteria depend on a question the plan itself records as unresolved, so a known-undecided fork ships as implemented behaviour and surfaces as a whole-branch finding instead of a planning decision
status: closed
origin: brief-item-addressability arc (2026-08-13) — the arc's only 🔴 was a fork the plan had written down as an open question and deferred to review
start: next touch of writing-plans' plan-document-reviewer prompt, or the next arc whose plan carries a non-empty Open Questions section
---

The arc's single 🔴 was not something the plan failed to anticipate. The plan
**named it, wrote it down, and dispatched anyway**: whether a change-folder
join key (referent kind (b)) should be legal in brief mode was recorded as an
open question, with the decision deferred to review.

It then shipped as behaviour — brief mode rejected the kind — and was found by
whole-branch review, which reproduced it live and ruled the shipped behaviour a
defect. Worse, the arc's own edits are what made it reachable: before this
branch, CLI mode-exclusivity hid the case; this branch's new "brief mode fires
change-folder or not" sentence removed the hiding.

**The gap.** `writing-plans` supports an `## Open Questions` section and
`brainstorming` routes unresolved axes into it. Nothing anywhere checks whether
an open question is **load-bearing for a task's acceptance**. An open question
about naming or a future extension is harmless to carry. An open question about
what a value legally means is a task's acceptance criterion in disguise, and
carrying it means the implementer picks silently.

**Candidate mechanism, cheap and mechanical.** A plan-document-reviewer check:
for each entry under `## Open Questions`, does any task's `Acceptance` (RED or
GREEN) depend on its answer? If yes, that task may not dispatch until the
question is resolved — resolve it, or split the task so the undecided half is
out of scope. This is enumerable from the plan text alone; it needs no
judgment about the question's importance, only about whether a task's
acceptance references its subject.

**Why this is higher-leverage than the alternative considered.** The
alternative raised at close-out was a pre-dispatch dialogue between the plan
author and the implementer, with the implementer asking clarifying questions.
Evaluated against this arc's four planning defects, that dialogue would have
caught **one** — this one — and missed the other three, because those were
omissions rather than ambiguities (see
[[2026-08-13-a-widened-field-grammar-has-no-mechanical-consumer-enumeration]]):
the implementer cannot ask about a consumer it does not know exists, and the
one genuinely ambiguous item here is exactly the one the plan had already
written down. The dialogue also conflicts with SDD's per-task scope — an
implementer sees one task, and asking it to interrogate the whole plan
re-widens the context the design deliberately narrows, at N-tasks × rounds of
cost. Recorded so the option does not need re-deriving next time it is raised.

The narrower rule reaches the same defect at a fraction of the cost, and does
it at plan time rather than at review time.

**Shipped.** The open-question dispatch gate arc
(`feat/open-question-dispatch-gate`) landed the plan schema's fill-or-declare
`## Open Questions` slot, the `check_open_questions.py` scanner, and the
plan-document-reviewer's Check 18 — the section-existence + false-N/A gate
that catches a plan claiming "no unresolved question" while its own body shows
one. A load-bearing-for-acceptance open question is now blocked at plan-write
and at branch close-out, not deferred to whole-branch review.
