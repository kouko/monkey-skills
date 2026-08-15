---
name: dedup-of-one-rule-must-not-strip-a-sibling-rule-in-the-same-paragraph
description: When dedup'ing a rule (replacing an in-place copy with a pointer to an SSOT), a paragraph often holds several distinct rules governed by DIFFERENT upstream sections — replacing the whole paragraph with the pointer strips the siblings that are NOT dedup targets; edit at sentence granularity, leaving the non-dedup rules in place, and keep a guard test that asserts each sibling marker survives
type: gotcha
origin: 2026-08-15 plain-relay-contract arc — T10 (8bc0f516) replaced brainstorming/SKILL.md's fork-guidance paragraph (which held the brief-before-fork trigger, the stakes-first framing, AND the "render ≥2 options as a markdown comparison table" default) with a single dedup pointer; the table-default rule is governed by family-relay.md §Family relay discipline, a different section, and was never a dedup target — it was deleted incidentally; caught by the F1 dogfood guard test in loom-pipeline/scripts/test_family_relay.py
---

A dedup replaces an in-place copy of *one* rule with a pointer to its
SSOT. But the copy often shares a paragraph with sibling rules that
are NOT dedup targets — they are governed by different upstream
sections and must stay. Replacing the whole paragraph with the pointer
strips the siblings along with the target.

On the plain-relay-contract branch, brainstorming/SKILL.md's
fork-guidance paragraph held three distinct rules:

  1. the brief-before-fork trigger (dedup target → SSOT pointer)
  2. the stakes-first framing (dedup target → moved to SSOT)
  3. "render ≥2 options as a markdown comparison table by default"
     (NOT a dedup target — governed by family-relay.md §Family relay
     discipline, a different section)

T10 replaced the whole paragraph with the dedup pointer. Rules 1 and
2 were correctly relocated; rule 3 was deleted incidentally. The F1
dogfood guard (`test_brainstorming_fork_table_default`) asserts the
"markdown comparison table" marker survives in the fork region — it
went RED, but lived in another plugin's test dir so the per-task
triad never ran it (see
[[a-per-task-triad-cannot-see-cross-plugin-guard-tests]]).

Mitigation: dedup at sentence granularity, not paragraph granularity.
Leave each non-dedup sibling rule in place next to the pointer. And
keep (or add) a guard test per sibling marker — a dedup that touches
a paragraph with N rules needs N assertions that the non-target
markers survive, not one assertion that the pointer landed.