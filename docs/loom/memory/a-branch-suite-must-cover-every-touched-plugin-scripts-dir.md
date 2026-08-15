---
name: a-branch-suite-must-cover-every-touched-plugin-scripts-dir
description: The habitual branch-verify command (scripts/ loom-code/scripts/ .claude/hooks/) structurally excludes the other loom-* plugin scripts/ dirs — a green 1633 was green only because the broken suites in loom-spec/loom-interface-design/loom-product-principles scripts/ were never loaded; branch-level suite coverage MUST enumerate every plugin whose scripts/ dir the branch touched, not just the CI-gated subset
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

Run per-directory (a single combined run basename-collides on
`test_plugin_manifest.py` / `test_marketplace_entry.py` /
`test_knowledge_triage.py` / `test_mint_critic_verdict.py` — a
pre-existing collection artifact, not a branch defect) and aggregate
the counts. A green number that excludes a touched dir is a
structural false-green: it cannot see the breakage by construction,
no matter how carefully it is read.

Pairs with [[a-per-task-triad-cannot-see-cross-plugin-guard-tests]]:
the per-task triad blindness and the verify-command blindness are two
layers of the same cross-plugin coverage gap — whole-branch review is
the net that catches both.