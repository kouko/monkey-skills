---
name: 2026-08-24-planning-file-boundaries-vs-data-flow-boundaries
description: decide when loom plans should split work by files versus packet and contract data flow
status: open
origin: cross-host review-gate hardening part 2 and part 3 replanning
start: discuss before the next loom planning task after the current cross-host review-gate hardening arc
---

This is the highest-priority planning discussion after the current arc. Compare
two task-boundary strategies:

- File boundaries: low merge-conflict risk and easy parallel dispatch, but can
  hide semantic dependencies when a shared packet, function contract, or
  terminal invariant crosses callers.
- Data-flow boundaries: make producer→consumer ownership and end-to-end
  acceptance explicit, but can create broader tasks and reduce apparent
  parallelism.

Use the current cross-host review-gate work as the first case study. Decide a
mixed rule: identify shared inputs/outputs, their producers and consumers, and
one end-to-end acceptance path before marking file-disjoint tasks independent.
Record whether this belongs in brainstorming, writing-plans, or the
plan-document-reviewer gate, and define a small mechanical check if one has a
clear owner.
