---
type: delivery
status: claimed
claim: codex, 2026-08-31
graduated-from: null
brief: docs/loom/specs/2026-08-31-docs-review-baseline.md
---

交付第一個可重算的 historical replay baseline：以凍結 corpus、人工 oracle、
弱模型 economy cohorts 與不可變 run/report records，量出 finding rate、
false-alarm rate、repeat agreement、可觀測時間／usage，以及缺陷來源能否被
證據歸因。此票綁定既有 change-folder
`docs/loom/2026-08-31-docs-review-baseline/`，結果必須明示三種文件的 case
coverage 與不足，不把 hard-case corpus 當成日常平均。

成功判準：validated spec 的 active scenarios 全部有可執行驗證；至少一個
真實 historical case 可端到端產生 immutable partial-or-full metric report；
Claude Code 與 Codex economy cohorts 的 scored/invalid/unavailable populations
分開呈現；任何不足被送回 Map fog，而不是由工具自行補答案。
