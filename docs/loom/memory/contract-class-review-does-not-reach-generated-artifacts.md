---
name: contract-class-review-does-not-reach-generated-artifacts
description: A clause added to docs-reviewer's dimensions binds only where its scope contract lets it look — since the 0.75.0 contract-class narrowing, record-class docs/** (generated briefs/plans/specs) exit review scope before dimension evaluation runs, so a template-contract enforcement clause reaches the template files themselves but never the instances writers generate from them; instance-level gating needs its own check in the reviewer that actually reads instances (for plans: plan-document-reviewer)
type: gotcha
origin: feat/visualization-trigger-layer (2026-08-11) — T5 code-quality reviewer caught the plan's own Notes overstating docs-reviewer coverage ("the loop for plans is covered at branch time"), corrected in the plan's Decision Log
---

The visualization arc wired "diagram slot absent / unjustified N/A" into
docs-reviewer's omission dimension and recorded "the loop for plans is
covered at branch time by docs-reviewer" as the reason a
plan-document-reviewer check could stay deferred debt. The reviewer's
own scope contract falsifies that: record-class `docs/**` files are
excluded before dimensions evaluate, so the new clause fires on
contract-class template files only — a generated plan skipping its
`## Task-flow diagram` slot is never seen by docs-reviewer at all.

**Why:** a dimension edit feels global because the dimension table reads
global, but jurisdiction is decided upstream by the scope contract.
Adding enforcement text to a reviewer that never opens the target
artifact class is enforcement theater for that class.

**How to apply:** before citing reviewer X as the feedback loop for
artifact class Y, check X's scope/exclusion rules actually admit Y.
For generated plan instances the admitting reviewer is
plan-document-reviewer (a slot-presence check there is the open debt
this entry tracks); for generated briefs/specs, no automated reader
currently admits them — writer-side template obligation is the only
layer, so weigh that when deciding whether a deferred check is safe
debt.
