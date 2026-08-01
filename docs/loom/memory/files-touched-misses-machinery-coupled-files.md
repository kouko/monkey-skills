---
name: files-touched-misses-machinery-coupled-files
description: A plan task's `Files touched` reliably names what the task is ABOUT and misses what it is mechanically COUPLED to — guard tests pinning the state the change alters, an SSOT sitting behind a functional copy, a manifest mirror a hook enforces; three of seven tasks in one plan under-declared this way, and that field is the only oracle authorizing parallel dispatch
type: gotcha
origin: branch docs-reuse-adequacy-brief-and-backlog (loom-code 0.43.0, 2026-08-01) — three independent instances in one plan, each surfaced by a different mechanism
---

Three tasks in one plan declared `Files touched` sets their commits then
exceeded. The misses look unrelated until you line them up:

| task | undeclared file | what actually coupled it |
|---|---|---|
| T3 | `test_plan_obligation_sweep.py`, `test_sdd_review_weight_marker.py` | both pin the state the change alters (a max-check-number guard, a `checks_passed` denominator) |
| T4 | `domain-teams/…/spec-consistency.md` | the named path was a **functional copy**; the SSOT lives elsewhere and `distribute.py` regenerates the copy |
| T6 | `loom-code/.codex-plugin/plugin.json` | a `PostToolUse` hook blocks the sibling manifest's edit until the mirror is regenerated |

None of the three appears in its task's own description. None is enforced by
its task's own tests — T4's would have passed while CI's separate drift job
failed, and T6's edit was refused outright by a hook. Each was found by a
different accident: an implementer volunteering the deviation, a hook blocking,
and a manual diff of declared-versus-actual.

**Why:** `Files touched` is not decoration — it is the disjointness oracle that
authorizes parallel dispatch at all. An oracle that is right two times in three
is not an oracle. In this plan no collision occurred, but only because the
undeclared files happened not to overlap between the concurrently-running tasks.

**How to apply:** when writing `Files touched`, the description names what the
task is *about*; then ask separately what the change is *coupled to* by
machinery — which guard tests pin the state you are altering, whether the file
you named is a functional copy with an SSOT elsewhere (check `distribute.py`'s
ROUTE table), and whether a hook or drift test enforces a mirror of it. And
after the task commits, diff `git show --stat <sha>` against the declared field:
that comparison is mechanical, needs no judgement, and would have caught all
three of these. Related: [[parallel-implementers-shared-tree-need-index-race-guard]]
(the sibling failure — same wave, the git index rather than the declaration).
