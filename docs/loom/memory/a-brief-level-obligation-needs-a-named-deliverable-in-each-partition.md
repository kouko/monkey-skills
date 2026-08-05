---
name: a-brief-level-obligation-needs-a-named-deliverable-in-each-partition
description: A brief-level obligation stated once for the whole arc ("residues + pointers") but not itemized as a named deliverable inside each partition/task ships unmet through every per-task gate — plan review and per-task reviewers verify tasks against their own itemized lists, so an obligation living only at the brief level has no gate that owns it; only a whole-branch pass can catch it, at the most expensive point
type: gotcha
origin: 2026-08-05 extraction-batch arc (PR #652 round 1) via the orchestrator-tree-detach-hardening brief
---

The 0.55.0 extraction batch's brief stated in its Smallest End State
that extracted files get "residues + pointers". Partitions A and B
itemized their pointer lines as explicit deliverables; Partition C
(requesting-docs-review) did not — and passed every per-task gate with
no route to its own design-evidence.md. Three plan-review rounds and six per-task reviewers
passed it, because each verified the itemized lists in front of them;
only a whole-branch docs arm caught the missing pointer, one round
before merge.

**Why:** every gate downstream of the brief verifies against a
partition- or task-scoped list. An obligation that lives only in a
brief-level clause is invisible to all of them — the plan reviewer
checks task-to-brief coverage by item, and a clause covering N
partitions "is covered" as soon as any one partition carries it.

**How to apply:** when freezing a brief, walk each Smallest-End-State
clause and confirm every sub-obligation ("+ pointers", "and tests",
"each with an index line") appears as a NAMED deliverable in every
partition/task it binds — a clause that fans out over N partitions
needs N itemized appearances, not one summary sentence. The
plan-review question is "which task's list carries this?", asked per
partition.
