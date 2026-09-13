---
name: using-loom-workflow
description: |
  Route broad Loom workflow-tool requests to the right skill. Use when the request spans tools or the right workflow skill is unclear.
---

# Using loom-workflow

Select the matching skill below and read its full `SKILL.md` before acting.
Directly named skills remain directly invocable; this router is optional.
The selected skill owns its procedure, permissions, and output contract.

| Request | Load |
|---|---|
| Judge a proposal, choose what to keep, or assess a simpler implementation | [critique](../critique/SKILL.md) |
| Explain how documented reasoning reached a conclusion, or request a CoT diagram | [cot-explain](../cot-explain/SKILL.md) |
| Write, edit, or review dbt + Redshift model style and structure | [dbt-model-style](../dbt-model-style/SKILL.md) |
| Open, advance, resume, or assess a persistent Outcome Map across sessions | [decision-map](../decision-map/SKILL.md) |
| Mine past agent sessions or skill-activation telemetry for improvement evidence | [distill-sessions](../distill-sessions/SKILL.md) |
| Commit, create/merge a PR, or recall a decision bound to Git history | [git-memory](../git-memory/SKILL.md) |
| Explicitly invoke `goal-create` by name for a session goal or repository purpose | [goal-create](../goal-create/SKILL.md) |
| Save state for another session or resume a saved HANDOFF | [handoff](../handoff/SKILL.md) |
| Ask for a second opinion from another model, higher effort, or another vendor | [independent-advisor](../independent-advisor/SKILL.md) |
| Remember, recall, reconcile, or forget a durable repository lesson; or a task needs a prior lesson | [loom-memory](../loom-memory/SKILL.md) |
| Re-orient within this conversation: 'where were we', '剛剛講到哪', '振り返り' | [recap-state](../recap-state/SKILL.md) |

Do not select `goal-create` from an inferred need or an unnamed goal request.
Changing a critique lens selects `critique`; changing who answers selects
`independent-advisor`. A built-in `/recap` away-summary is not `recap-state`.
Simple factual or function-state questions need no workflow skill, and general
diagrams do not select `cot-explain`. A single implementation change belongs
to an available Loom lifecycle station, not `decision-map`; this toolbox
does not supply intent, spec, plan, build, review, or ship procedures.
