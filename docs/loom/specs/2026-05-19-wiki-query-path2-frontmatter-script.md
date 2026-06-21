# wiki-query Path 2 — frontmatter script as Tier 1 entry

Brainstorming brief produced 2026-05-19; consumes upstream research [`research/2026-05-18 LLM wiki index 過大問題`](../../../../../../kouko-obsidian-vault/research/) (vault-internal) and the A+B→Path 2 pivot history in the same vault.

## Problem

`wiki/index.md` 已 286 行 / 33KB / ~8K tokens，每次 `wiki-query` Tier 1 全讀。Karpathy 三層架構原意是 cheaper tier 先行，但 index.md 線性膨脹後 Tier 1 反而比 Tier 2 貴 — 設計被自己破壞。每次 `wiki-ingest` append 1-15 行讓問題持續成長。

**JTBD**：當 kouko 問 wiki 一個問題、wiki 已有相關 page 時，要拿到「ranked candidates 含 summary」而不是付 8K tokens 讀整本目錄。

## Users

- **唯一使用者**：kouko 在自己的 `kouko-obsidian-vault` 上跑 `/wiki-query`
- **規模**：285 wiki pages（entities 44 / concepts 59 / references 172 / skills 8 / journal 2）；references 線性增長
- **既有條件**：每頁 frontmatter 已含 `summary ≤200 chars`（[`page-format.md:18`](../../../obsidian/skills/wiki-ingest/references/page-format.md#L18) 規定）+ `tags` + `type`；vault 內 5 個 wiki-* skill + 1 個 Tier 0 hot cache 已 work

## Smallest End State

1. 新增 `obsidian/skills/wiki-query/scripts/query-frontmatter.py` ~80 行 stdlib Python
2. 改寫 [`obsidian/skills/wiki-query/SKILL.md:26-37`](../../../obsidian/skills/wiki-query/SKILL.md#L26-L37) STEP 2（讀 index.md → 呼叫 script）
3. [`obsidian/skills/wiki-ingest/SKILL.md:253-255`](../../../obsidian/skills/wiki-ingest/SKILL.md#L253-L255) STEP 4e 改成「加 stale banner，停止 append」
4. [`obsidian/skills/wiki-query/SKILL.md:16`](../../../obsidian/skills/wiki-query/SKILL.md#L16) Pre-flight 第 3 點：`wiki/index.md` empty 改檢查「frontmatter 是否有 summary」或乾脆刪除此檢查

不做：A 分片 / 條目瘦身 / 向量索引 / PageRank / `.query-cache.json` / 多 vault override env var。

## Current State Evidence

- **Forward**（被 query 入口）：[`wiki-query/SKILL.md:30`](../../../obsidian/skills/wiki-query/SKILL.md#L30) `Read wiki/index.md` — 唯一 Tier 1 入口，要拔掉
- **Reverse**（誰維護 index.md）：[`wiki-ingest/SKILL.md:253-255`](../../../obsidian/skills/wiki-ingest/SKILL.md#L253-L255) STEP 4e 每次 ingest append；wiki-cross-linker 未驗證是否掃 index.md（plan 階段確認）
- **Data**（candidate 來源）：[`wiki-ingest/references/page-format.md:18`](../../../obsidian/skills/wiki-ingest/references/page-format.md#L18) `summary: "≤200 chars single-line summary used by tiered retrieval"`；同檔 L263 明文「frontmatter.summary only — across all matching pages」— Path 2 直接吃這個欄位
- **Boundary**（既有腳本慣例）：[`wiki-ingest/scripts/scan-vault.sh + select-batch.py`](../../../obsidian/skills/wiki-ingest/scripts/) — 證明 skill 內 `scripts/` 是 wiki-* 家族既定 pattern；新 script 跟進
- **Error**（fallback 路徑）：retrieval-tiers.md（[`wiki-query/references/retrieval-tiers.md`](../../../obsidian/skills/wiki-query/references/retrieval-tiers.md)）定義 Tier 契約，需同步更新

Evidence paths appendix：
- `obsidian/skills/wiki-query/SKILL.md`
- `obsidian/skills/wiki-query/references/retrieval-tiers.md`
- `obsidian/skills/wiki-ingest/SKILL.md`
- `obsidian/skills/wiki-ingest/references/page-format.md`
- `obsidian/skills/wiki-ingest/scripts/`（pattern 範本）

## Decision

實作 Path 2：新增 `query-frontmatter.py` 取代 index.md 作為 LLM Tier 1 入口，採以下 5 個操作層決議：

| # | 議題 | 決議 | 理由 |
|---|------|------|------|
| Q1 | keyword 抽取 | wiki-query agent (LLM) 抽 keyword list 傳入 script；SKILL.md 加 prompt | query understanding 是 LLM cheap zone；CJK / 混合語言意圖最準 |
| Q2 | type filter | Script `--type` 為 optional；LLM 只在明確指涉時加 hint，否則跨類 top-K | YAGNI；錯推成本小；LLM 自判斷比硬規則好 |
| Q3 | multilingual 比對 | `unicodedata.normalize('NFKC', s).lower()` + Python `in` substring | 同 ripgrep 家族 literal substring；285 頁 false positive 罕見；不引入 tokenizer 依賴 |
| Q4 | script 位置 | skill 內 `obsidian/skills/wiki-query/scripts/` | 跟 wiki-ingest scripts/ 同 pattern；skill 自包含；跨 vault 一致行為 |
| Q5 | index.md 退役 | 保留檔案 + 加 stale banner + wiki-ingest STEP 4e 停止 append | 避免維護一個 LLM 不讀的檔；保留 Obsidian 端歷史快照 |

**實作技術選擇**：純 Python（stdlib only），單檔約 80 行；不引入 ripgrep / yq / PyYAML 等外部依賴。

**Why not A+B**：每 wiki page 的 frontmatter 已含 `summary` 為 Tier 1.5 設計（page-format.md L18 + L263），index.md 在重複 frontmatter 資料；A 分片 + B 瘦身只是優化「中間那一站」，Path 2 直接拿掉那一站。

## Out of Scope

### 本 PR 不做

- A 分片 / B 條目瘦身（決策推理史保留於 vault `research/2026-05-18 wiki-index 結構化重構方案 A+B 組合.md`）
- 向量索引 / BM25 hybrid / GraphRAG
- PageRank on wikilink graph
- `.query-cache.json` mtime-based 快取
- 多 vault override 機制
- migration script 把 index.md 內容反向同步回 frontmatter（frontmatter 早就 source-of-truth）
- v1.0 不做並行化 — `ThreadPoolExecutor` 等並行 I/O 列為下方 future trigger

### Future triggers（記錄於此避免遺忘）

| 觸發條件 | 升級項目 |
|---------|---------|
| cold scan 實測 >200ms | 加 `ThreadPoolExecutor(max_workers=8)` 包檔案讀取（+5 行） |
| wiki 規模 >1000 頁 或 scan >500ms | 評估 `.query-cache.json` mtime-based 或 ripgrep pre-filter |
| LLM 反映 false positive 頻繁 | 評估 CJK tokenizer（jieba/lindera） |
| recall 良好但 precision 差 | 評估 wikilink graph PageRank 排序 |
| 語意 query 比例 >30% | 評估 sqlite-vec 嵌入索引 |

## Alternatives Considered

### 系統層（macro）

8 種業界做法定位詳見 vault [`research/2026-05-18 LLM wiki index 過大問題-業界做法調查.md`](../../../../../../kouko-obsidian-vault/research/)：親子分片 / 條目壓縮 / BM25+向量 / Composable Retrieval / GraphRAG / 記憶階層化 / 演算法重要性 / 用戶側 ignore。Path 2 對應「條目壓縮」極限版（拿掉中間站、直接用 frontmatter）。

A+B 路線推理史詳見 vault [`research/2026-05-18 wiki-index 結構化重構方案 A+B 組合.md`](../../../../../../kouko-obsidian-vault/research/)。被否決原因：page-format.md L18 + L263 已規定 `summary` 為 Tier 1.5 設計，A+B 在優化重複資料的中間檔。

### 實作層（micro）— 為什麼純 Python 不選 ripgrep

| 選項 | 機制 | 拒絕原因 |
|------|------|---------|
| **A: 純 ripgrep + jq + bash pipeline** | `rg -l` 找候選 → `yq` 抽 summary → `jq` 排序 | rg 無法表達 field-weighted scoring；多步 pipeline 脆弱；無單一 source of truth |
| **B: ripgrep + Python hybrid** | rg 做 candidate pre-filter，Python parse + score | cold scan 200→80ms gain 被 LLM round-trip ~3s 完全淹沒；新增外部依賴破壞 skill 自包含；不符 wiki-ingest scripts/ 既有純 stdlib pattern |
| **C: 純 Python（採用）** | stdlib only，single file | 寫一次解所有事；單檔可審；無外部依賴 |

### 並行化選項

| 選項 | 為何不在 v1.0 | 觸發條件 |
|------|--------------|---------|
| `ThreadPoolExecutor` | 285 檔 / LLM 是 10-50x 慢，gain 不可見 | cold scan >200ms |
| `ProcessPoolExecutor` | spawn cost > work cost；永遠不適用此規模 | — |
| `asyncio + aiofiles` | 額外依賴；ThreadPool 已足夠 | — |

## What Becomes Obsolete

| 移除/變更 | 同 PR 處理 |
|----------|-----------|
| [`wiki-query/SKILL.md:30`](../../../obsidian/skills/wiki-query/SKILL.md#L30) 「Read wiki/index.md」 | ✅ STEP 2 重寫一起改 |
| [`wiki-ingest/SKILL.md:253-255`](../../../obsidian/skills/wiki-ingest/SKILL.md#L253-L255) STEP 4e append 邏輯 | ✅ 改 banner 模式 |
| [`wiki-query/SKILL.md:16`](../../../obsidian/skills/wiki-query/SKILL.md#L16) Pre-flight 「index.md empty 須先 ingest」 | ✅ 改檢查 summary 存在 或移除 |
| [`wiki-query/references/retrieval-tiers.md`](../../../obsidian/skills/wiki-query/references/retrieval-tiers.md) Tier 1 契約 | ✅ 同步更新 |
| `wiki/index.md` 既有檔案 | ❌ 保留作為 Obsidian 端歷史快照（Q5 決議） |
| wiki-cross-linker 對 index.md 的掃描（若有） | ⚠️ plan 階段確認，必要時同 PR |
| wiki-lint L08 frontmatter completeness | ⚠️ Path 2 下 `summary` 缺失成為 Tier 1 隱形 — 升級為 hard error（同 PR 或 follow-up） |

## Open Questions

無未決事項。5 個操作層 Q 全部 resolved（見 §Decision 表格）；3 個 plan-stage 確認項移至 ⚠️ flagged 行（wiki-cross-linker 掃描範圍 / wiki-lint L08 升級時機 / Pre-flight 第 3 點如何改寫）。

---

**下一站**：`writing-plans` 切原子任務。
