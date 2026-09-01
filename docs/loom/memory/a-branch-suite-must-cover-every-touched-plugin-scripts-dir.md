---
name: a-branch-suite-must-cover-every-touched-plugin-scripts-dir
description: A branch-verify command that covers only the dirs the branch CHANGED is a structural false-green in both directions — it misses touched plugin scripts/ dirs it never loads, and it misses the CONSUMERS of what changed, which by definition live outside the changed tree; enumerate every dir the branch touched AND every dir that imports or loads what it moved, or the aggregate run shares a boundary with the change and no run can cross it
type: practice
origin: 2026-08-15 plain-relay-contract arc — whole-branch review round 1 caught 6 plugin-local test failures (3934cbf2 lockstep cleanup missed 3 dirs); the orchestrator's verify command had returned 1633 passed across the habitual subset, never loading the 3 touched dirs where the breakage lived
---

The loom family ships six plugins, each with its own `scripts/` test
directory. The habitual branch-verify incantation —

  `python3 -m pytest scripts/ loom-code/scripts/ .claude/hooks/`

— covers only three of them (the repo root, loom-code, and hooks). On
the plain-relay-contract branch, the dedup/lockstep cleanup commit
(3934cbf2) updated tests in loom-discovery and loom-code but missed
loom-spec, loom-interface-design, and loom-product-principles. The
orchestrator ran the habitual command, saw 1633 passed, and read it
as green. It was green by omission: the three broken suites were never
collected. The whole-branch code review (round 1) caught the 6
failures by inspecting the actual edited files across all plugins.

The fix is structural, not vigilance-based: the branch-level verify
command MUST enumerate every plugin whose `scripts/` dir the branch
touched. The full 6-plugin surface is —

  loom-code/scripts  loom-discovery/scripts  loom-spec/scripts
  loom-interface-design/scripts  loom-product-principles/scripts
  loom-pipeline/scripts  +  repo scripts/  +  .claude/hooks/

A green number that excludes a touched dir is a structural false-green:
it cannot see the breakage by construction, no matter how carefully it
is read.

**Two facts above went stale and are corrected here (2026-09-01).**
The five sibling plugins named — loom-discovery, loom-spec,
loom-interface-design, loom-product-principles, loom-pipeline — were
merged into a single `loom-design`, so the enumeration is now
`loom-code/scripts`, `loom-design/scripts`, `loom-workflow/scripts`,
repo `scripts/`, and `.claude/hooks/`. And the per-directory
requirement is gone: the basename collision that forced it was fixed
by giving `loom-design/scripts/` a `pytest.ini` with
`--import-mode=importlib` plus a `pythonpath` line, so one invocation
now collects the whole tree.

**The mirror failure, same class, opposite direction (2026-09-01).**
This entry says: cover every dir you CHANGED. That is half the rule. An
arc that split `loom-design/scripts/pipeline/batch_queue.py` verified
with `pytest loom-design/scripts/` and `pytest loom-design/scripts/pipeline/`
— both inside the tree it changed, both green — and shipped two CI-red
failures. Every CONSUMER of a moved module lives outside the tree that
moved it: a loom-code-side test loaded `batch_queue.py` by file path and
died on its new sibling import, and a fingerprint gate hashing the whole
`loom-design/` tree went stale. As the reviewer put it: the aggregate run
and the change had the same boundary, so no run could have crossed it.

So the rule has two halves, and the second is the one that hides: run
every dir the branch TOUCHED, and every dir that IMPORTS OR LOADS what
the branch moved. Find the second set by grepping the whole repo for the
moved module's name — including by-path loads via
`spec_from_file_location`, which no import-graph tool will show you.

Pairs with [[a-per-task-triad-cannot-see-cross-plugin-guard-tests]]:
the per-task triad blindness and the verify-command blindness are two
layers of the same cross-plugin coverage gap — whole-branch review is
the net that catches both.