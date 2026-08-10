---
name: 2026-08-10-plan-document-reviewer-misrouted-as-agent-type
description: writing-plans' self-review wording led a cold operator to look up plan-document-reviewer in the agent registry, find nothing, and substitute docs-reviewer with the wrong checklist for 3 rounds — field incident in an external consumer repo
status: OPEN
origin: 2026-08-10 review-cost discussion — diagnosed from the consumer repo's session transcripts (kumiko, private; disclosed per committed-docs precedent)
start: next touch of loom-code/skills/writing-plans/SKILL.md §Self-review, or the next reported plan-gate misroute — whichever comes first
---

- Start: next touch of loom-code/skills/writing-plans/SKILL.md §Self-review, or the next reported plan-gate misroute — whichever comes first

- Origin: 2026-08-10 review-cost discussion — diagnosed from the consumer repo's session transcripts (kumiko, private; disclosed per committed-docs precedent)

- The defect: `plan-document-reviewer` is a PROMPT FILE
  (`writing-plans/references/plan-document-reviewer-prompt.md`) dispatched
  via a generic subagent — it is NOT a registered agent type. The
  §Self-review wording ("dispatch … as an evaluator subagent") does not
  say this explicitly, so a cold operator in an external consumer repo
  looked for an agent TYPE named plan-document-reviewer, found none in
  the registry, and substituted the `docs-reviewer` agent — which reviewed
  the plan with the prose-5-dimension checklist for 3 rounds. Wrong
  checklist → wrong findings → convergence cap → the user had to ratify
  PASS by fiat with round-3's fix never reviewed.

- Why it matters: every round of a wrong-checklist review is pure waste
  that still costs a full dispatch, and the failure mode ends in a fiat
  PASS — the exact outcome the gate exists to prevent.

- Fix sketch (one sentence + maybe a pin): §Self-review states
  explicitly that plan-document-reviewer is a prompt file for a
  general-purpose subagent, never an agent-registry lookup, and that no
  other reviewer agent may substitute; a cold-reader probe (haiku)
  verifies the routing per the institution's prompt-text quality floor.

- Evidence pointers (private repo, session-level): the consumer repo's
  Part-4 plan records the 3 proxy rounds and the fiat close in its plan
  header notes.
