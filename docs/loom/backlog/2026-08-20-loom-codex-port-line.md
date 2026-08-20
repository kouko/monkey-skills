---
name: 2026-08-20-loom-codex-port-line
description: loom 機制 Codex 移植線——把 loom-code 目前綁定 Claude Code 的機制搬到 Codex host
status: open
origin: docs/loom/DIRECTION.md `## Later` cleanup（north-star-serves-link 弧，2026-08-20）
start: 下次有 Codex-only 或跨 host 的具體需求出現時，評估是否值得起這條弧
---

loom-code 的多個機制（git-guard、hooks、skill 派工慣例）目前是 Claude Code
專屬設計，Codex 只有部分 shim 或鏡射（例如 on-ramp 弧的 Codex shim、
codex-hooks 鏡射）。這條 Later 項是把「loom 機制系統性移植到 Codex」當成
一條獨立的弧，而不是逐一補丁。

`docs/loom/memory/` 裡已有零星的 Codex 差異紀錄（例如
`feedback_codex_multi_agent_spawns_from_standing_instructions` 這類），下一步
是先盤點現有的 Codex 差異點清單，再決定移植的範圍與順序。
