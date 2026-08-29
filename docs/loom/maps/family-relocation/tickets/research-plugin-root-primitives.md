---
type: research
status: closed
claim: kouko-session, 2026-08-29
---

`${CLAUDE_PLUGIN_ROOT}` 與 plugin 機制對「跨 plugin 資源解析」實際支援
到什麼程度？官方文件面（plugin manifest、hooks、skills 的路徑解析規則）
＋已知實測面（本 repo 的 boundary 測試與 codex 鏡射）各說了什麼、缺口
在哪。一份查證報告，供 feasibility 票設定量測基準。

selection-basis: map and ticket both user-named — kouko listed the open items and said 做 research, naming this ticket directly (also the only open research ticket on the map); deep-research authorization granted per-instance by that same message.

## Resolution

Report delivered: docs/loom/research/2026-08-29-plugin-root-primitives.md
(deep-deep-research pipeline: 22 sources, 25 claims adversarially verified,
22 confirmed / 3 killed). Key verified findings: the cache location/layout,
the full CLAUDE_PLUGIN_ROOT expansion matrix, its documented instability
across updates, the path-escape guard blocking static cross-plugin paths,
and an official install-time plugin-dependencies mechanism are ALL now
documented surfaces — but installed_plugins.json (the probe's resolver
oracle, and the only current-enabled-version source) appears nowhere in
official docs (verified negative), and no documented primitive provides
runtime sibling-root discovery on Claude Code (verified negative; the
same absence on Codex is context-tier only). CLAUDE_PLUGIN_DATA is a
documented durable-state alternative worth noting for handshake designs.
Measurement baseline for the feasibility ruling: report §Implications 1-5.
