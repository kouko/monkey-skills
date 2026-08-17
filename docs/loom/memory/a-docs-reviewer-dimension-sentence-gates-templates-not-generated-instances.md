---
name: a-docs-reviewer-dimension-sentence-gates-templates-not-generated-instances
description: A sentence added to docs-reviewer's omission (or any) dimension row reaches only contract-class `.md` — skill files, references, agents, hooks — because record-class `docs/**` is outside its jurisdiction; it never gates the generated briefs, plans, or specs the sentence is written about, so instance-level enforcement must be a validator or a reviewer that reads instances (plan-document-reviewer, spec validator), and the arc's brief should say which one — recorded twice now (2026-08-11 diagram slot, 2026-08-17 table routing)
type: gotcha
origin: branch loom-doc-container (loom-code 0.85.0, 2026-08-17) — brief Decision, Task 5; precedent docs/loom/plans/2026-08-11-visualization-trigger-layer.md Decision Log 1
---

Both slot arcs added a docs-reviewer omission sentence "so reviewers catch
a missing/false slot" — and both discovered at review time that the
reviewer's scope contract excludes `docs/**`, so the sentence gates the
templates that define the slot, never the briefs/plans/specs that fill
it. The 2026-08-11 arc recorded it as plan Decision Log 1; this arc caught
it at planning and wrote the reach into the brief.

**Why:** the 0.75.0 contract-class narrowing made docs review cheap by
exempting record-class prose; a dimension sentence inherits that scope
whatever it talks about. Instance gating lives elsewhere: the spec
validator (mechanical, at freeze), plan-document-reviewer (reads plan
instances), and human sign-off gates with the adjudication view.

**How to apply:** when a brief proposes "add a docs-reviewer sentence" as
enforcement for a slot, state in the same sentence what gates the
generated instances; if the answer is "nothing mechanical", either add
the instance gate (validator / plan-document-reviewer check) or record it
as debt explicitly — never let the docs-reviewer sentence stand in for
instance enforcement.
