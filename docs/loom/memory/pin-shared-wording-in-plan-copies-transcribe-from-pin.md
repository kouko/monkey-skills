---
name: pin-shared-wording-in-plan-copies-transcribe-from-pin
description: When one wording must ship in N places (a hook card + a SKILL.md SSOT, parallel tasks), PIN the canonical text in the plan's ## Notes and have every task transcribe VERBATIM from the pin — never from each other and never re-derived; the pin survived four review-driven fixups with zero drift on first use, and reviewers can verify each copy character-level against the pin instead of judging semantic closeness between copies
type: practice
origin: feat/mid-task-ask-layered-defense (2026-07-14) — ask-triage card + SDD gate-① arms
---

The layered-defense branch needed the same three-way triage wording in two
sanctioned copies (the L2 hook card and SDD gate ①'s SSOT), built by two
PARALLEL implementers. Instead of task A copying from task B (ordering
dependency) or each re-deriving from the brief (drift), the plan's ## Notes
carried two pinned blocks (§Pinned card text, §Pinned triage arms); each
task's dispatch said "transcribe VERBATIM from the pin". Both per-task
reviewers and the whole-branch reviewer then verified character-level
against the pins — cheap, mechanical, no taste call. Four fixups later
(escape-hatch supplement, sequenced relay) the copies were still
pin-faithful; the supplement pattern (add sentences AFTER the pinned block,
never edit inside it) kept fix flexibility without breaking the contract.

**Why:** shared wording built by parallel workers has no natural SSOT until
merge; copy-from-sibling creates ordering, re-derivation creates drift, and
post-hoc semantic comparison is a judgment call reviewers get wrong.

**How to apply:** when a plan fans one wording into ≥2 files, add a §Pinned
<name> block to the plan's ## Notes, make each consuming task's Description
say "transcribe VERBATIM from the pin", and instruct reviewers to
character-check against the pin. Amendments go AFTER pinned blocks as
supplements — editing inside a pin invalidates every copy's verification.
(Related: [[preamble-wording-is-contract-surface]],
[[assertion-must-encode-the-property-it-claims]].)
