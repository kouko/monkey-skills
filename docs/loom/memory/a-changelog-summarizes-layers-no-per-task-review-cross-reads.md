---
name: a-changelog-summarizes-layers-no-per-task-review-cross-reads
description: A release note restates every layer's semantics in one place, yet no per-task triad reviews it against those layers — cross-read the changelog at whole-branch time
type: gotcha
origin: decision-map protocol-hardening branch, whole-branch review round 1 (2026-08-29)
---

A CHANGELOG entry is a one-paragraph restatement of semantics that live
in other files — schema references, skill text, code — but the task
that writes it is reviewed only against its own plan block, and no
sibling task's triad ever reads it. On the protocol-hardening branch
this let two inversions ship through nine green per-task verdicts: the
`ratification` field described as recording who ratified (the grammar
layer defines the opposite — a deferred, not-yet-given ratification),
and an upgrade-impact claim ("every existing map remains checker-valid
unmodified") that the reviewer falsified by running the old store
against the new checker.

**Why:** the changelog is most readers' only index into what changed;
an inversion there propagates a wrong mental model even while every
underlying layer is correct, and per-task review structurally cannot
catch it because the defect is disagreement BETWEEN layers, not a wrong
statement within one.

**How to apply:** treat the release note as a cross-layer summary at
whole-branch review time — read each of its semantic claims against the
layer that owns the semantics (schema file, skill text, code), and run
any runnable upgrade-impact claim against a pre-branch store instead of
accepting it as prose.
