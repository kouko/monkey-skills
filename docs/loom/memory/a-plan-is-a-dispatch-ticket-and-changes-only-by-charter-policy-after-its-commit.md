---
name: a-plan-is-a-dispatch-ticket-and-changes-only-by-charter-policy-after-its-commit
description: A plan answers "how is the work split and dispatched" for a fresh-context implementer; after the plan commit it changes only through the policies the artifact charter's plan row names (claimed/blocked marks, an appended memory task, an un-landed task replaced or amended with the reason in the commit message, a Questions-asked append) — build diaries, lessons and landed shas have their own homes and a plan that carries them is an inconsistency, never a richer plan
type: practice
sources:
  - resource: 2026-09-05-artifact-charter-boundaries-and-edit-rights — a real 3,945-word plan whose Risks section had grown a dated build diary (41% of the file) and three post-hoc tasks tagged with landed shas; the same template had produced 215-word plans elsewhere
---

Plans from one template ranged from 215 to 3,945 words. The long ones were
not over-planned: they were written back into during build and review — a
dated "LESSON" list under Risks, tasks appended with `landed: <sha>`, design
rationale folded into Risk lines. Nothing said the plan was closed once
committed, so every station treated it as the nearest open notebook.

**Why:** build derives progress from git and resumes a half-built plan by
re-reading it; a diary in the plan is re-read as planning fact. Reviewers
reconcile against the plan as ground truth, so text added after sign-off
silently moves the target. The charter row (`contract/manifest.yaml`,
`artifacts.plan.charter`) names each kind of overflow and where it lives:
behaviour → spec, diary → review.json, lessons → memory, shas → dispatch.

**How to apply:** treat the plan commit as sign-off. After it, edit the plan
only through an `edits_after` policy id and let `plan-edits <change-id>`
recompute the diff; anything else goes to the artifact the charter's
`must_not` column names. When a fact the plan relied on proves wrong, amend
the un-landed task and say so in the commit message — that is a policy, a
diary entry is not.
