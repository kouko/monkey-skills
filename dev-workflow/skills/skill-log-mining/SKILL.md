---
name: skill-log-mining
description: >-
  Mine ~/.claude/projects JSONL transcripts plus /insights facets to produce
  edit proposals against existing dev-workflow:* and code-toolkit:* SKILL.md
  files. Use when auditing skill activation telemetry, surfacing missed-trigger
  patterns, or generating data-grounded description / frontmatter / body edit
  proposals for shipped skills. Stub at v0.1; full body lands in Part 3 of the
  v0.1 plan. Do NOT use for creating new skills from scratch (use
  dev-workflow:skill-creator-advance), for taste-driven A/B output tuning (use
  dev-workflow:skill-tuning), or for token / structure refactors of an existing
  skill (use dev-workflow:skill-refactor). 技能ログ採掘・SKILL.md 改善提案・トリガー
  漏れ検出・活性化ログ分析。技能日誌挖掘・SKILL.md 迭代提案・觸發遺漏偵測・啟動日誌分析。
version: 0.1.0
---

# skill-log-mining (v0.1 — in progress)

This skill is being built across 3 parts. The full body lands in Part 3 (Task 11).

See [planning docs](../../../docs/code-toolkit/plans/2026-05-22-skill-log-mining-v0.1-part-1.md) for status.
