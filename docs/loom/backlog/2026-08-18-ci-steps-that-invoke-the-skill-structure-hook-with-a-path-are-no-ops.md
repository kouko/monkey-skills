---
name: 2026-08-18-ci-steps-that-invoke-the-skill-structure-hook-with-a-path-are-no-ops
description: `.claude/hooks/validate-skill-folder-structure.sh` reads its target from the stdin PostToolUse JSON and ignores argv, so every CI step written as `bash <hook> <path>` (tsundoku-ci.yml today) exits 0 without checking — replace those steps with `python3 scripts/check-skill-structure.py <plugin>` and add the missing plugins to the structure scan
status: OPEN
origin: 2026-08-18 think-orbit Part 1 close-out — the same dead step was found in think-orbit-ci.yml (fixed there, eece4620) and traced to tsundoku-ci.yml; memory entry skill-folder-structure-hook-reads-stdin-json-and-ignores-argv
start: next touch of tsundoku-ci.yml or of skill-structure.yml's plugin list — a tiny surgical PR
---

- Start: next touch of tsundoku-ci.yml or of skill-structure.yml's plugin list — a tiny surgical PR
- Evidence: think-orbit CI commit eece4620 (hook step → checker); memory
  `docs/loom/memory/skill-folder-structure-hook-reads-stdin-json-and-ignores-argv.md`.
