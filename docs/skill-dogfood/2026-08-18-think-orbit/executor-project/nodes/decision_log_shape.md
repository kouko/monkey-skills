---
id: decision_log_shape
type: FACT
seq: 7
summary: plan 的 Decision Log 每條只有「選了什麼、因為什麼、改動成本」，沒有指向前提的欄位
status: current
source: sources/part1-decision-log.md（Part 1 plan §Decision Log，行 377–388）
quote: "3. chose author-named node ids over title-derived slugs because derived slugs collide silently — cost-of-change: the day you want auto-naming, this choice costs a naming step in the SKILL, not a data migration"
inputs: []
---
十條 Decision Log 全是同一句型：chose X because Y — cost-of-change Z。它是純文字清單，沒有 id，也沒有可被機器解析的 ref。這代表就算 render 現在就能接，這條載體目前也沒有東西可以餵。
