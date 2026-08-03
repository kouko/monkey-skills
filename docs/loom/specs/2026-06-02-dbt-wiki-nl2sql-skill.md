# Brief — dbt-wiki：NL2SQL 消費端（A. runtime consumer + B. portable packager）

- **Date**: 2026-06-02
- **Topic**: dbt-wiki-nl2sql-skill
- **Stage**: brainstorming → (next) writing-plans（預期拆 part-1 = A、part-2 = B）
- **North star**: 把整理出來的 wiki 內容做成「能有效回答商業邏輯問題的 text-to-SQL」。本 brief 是消費端——把已完成的知識底料（v2.1.0：知識層 + 關係圖 + metric 欄位卡）變成真正會「NL → SQL」的東西。
- **User goal（本 session 鎖定）**：最終產物要可攜、給沒有 dbt-wiki 的人獨立使用（→ B）；但 A 有早期測試/baseline 價值 → **A、B 都要做，A 先**。

---

## Problem

（Axis 1 — JTBD）

**When** 一個分析師/工程師面對一個 dbt 專案、想用白話問一個**商業邏輯問題**（"上個月每家店的線上 GMV 是多少？"），**I want** 一個工具讀懂這個專案的業務知識（實體、指標、關係、預物化欄位）並直接給我**正確、可跑的 SQL**，**so I can** 不必先讀 200 個 model 的 SQL、也不必自己拼 join/grain/欄位。

兩個層次的 JTBD：
- **A（runtime consumer）**：在「有 dbt-wiki 的 repo 內」當下問→當下生 SQL。價值：閉環跑起來、可量測 baseline、早期測試 wiki 到底有沒有幫助。
- **B（packager）**：把 wiki「編譯」成一個**自包含、可散布的 NL2SQL skill**，交給**沒有 dbt-wiki、沒有 dbt 專案**的人也能用（例如交付給業務團隊 / 別的 repo）。價值：可攜、產品化。

研究（vault 2026-06-01 + 本次 Axis-4）：text-to-SQL 主流架構 = 把 schema 拆成語意實體 → 檢索相關子集 → 動態 few-shot → schema-linking → 生 SQL。**關鍵洞察：dbt-wiki 的知識庫本身就已經是「schema 拆成語意實體 + summary + 關係圖」**——RASL/Pinterest 用 vector DB 建的東西，dbt-wiki 用 markdown + 分層檢索已經有了。所以 A 可重用 `query` 的分層檢索，**不需要自建 vector DB**。

## Users

（Axis 2）

- **A 的使用者**：已經跑過 `dbt-wiki:init` 的工程師/分析師，repo 內有 `.dbt-wiki/` + 有 dbt 專案的 `manifest.json`。要的是「問→可跑 SQL」。
- **B 產出物的使用者**：**沒有** dbt-wiki plugin、可能沒有 dbt 專案、可能不會寫 SQL 的人（業務、PM、別團隊）。他們拿到的是一個獨立 skill bundle，問白話→得 SQL，無需安裝 dbt-wiki 或持有 manifest。
- **B 的操作者**：擁有 wiki 的工程師，定期 `build` 出 bundle 交付。
- **共同約束**：dbt-wiki 是 local-only、**永不連 warehouse、永不執行 SQL**（SCHEMA「What dbt-wiki NEVER does」, `SCHEMA.md:722-727`）。所以**驗證只能是靜態的**（sqlglot parse + manifest schema 存在性檢查），不能靠執行回饋自我修正。

## Smallest End State

（Axis 3 — 最小可 ship 增量 = A；B 為已承諾的第二增量）

**A（part-1，最小閉環）= 新 sibling skill `dbt-wiki:to-sql`**（暫名）：
1. NL 商業問題 → 用 `query` 的分層檢索挑出相關 entities/metrics（含**欄位卡映射**）/concepts/關係邊（+ evidence schema 欄位型別）。
2. 組 prompt：schema-linking（業務詞→實體欄位）+ 欄位卡（預物化變體→`model.column`，直接 SELECT）+ 關係圖 join-path。
3. 生 SQL。
4. **靜態驗證**：sqlglot parse 通過 + 引用到的 table/column 存在於 manifest（catalog.json 在的話加型別檢查）。
5. 回傳 SQL + 引用的知識頁 + 驗證結果（pass / 哪裡對不上）。
6. **v1 = zero-shot baseline**（no few-shot examples），但 prompt 預留 few-shot slot。

**B（part-2，可攜封裝）= 新 skill `dbt-wiki:pack-sql-skill`**（暫名）：
- 讀 `.dbt-wiki/` → 產出一個**自包含 Anthropic SKILL.md bundle**：凍結的 schema 卡（實體欄位字典 + 欄位卡映射）+ 關係圖 + gold examples（若有）+ A 的生成 prompt 邏輯，**不依賴** dbt-wiki plugin / dbt 專案 / manifest。
- bundle 帶 `manifest_sha` + build 日期 + staleness 註記（快照，wiki 變動需 rebuild）。
- 產出物本身能獨立「NL → SQL」（靜態驗證受限：無 manifest 時退化為 sqlglot parse-only + 對 bundle 內凍結 schema 檢查）。

**驗收（A）**：給定一個有 `.dbt-wiki/` + manifest 的 fixture 專案 + 一個商業問題，`to-sql` 能產出 sqlglot-parse 通過、且 table/column 都存在於 manifest 的 SQL，並列出引用知識頁。
**驗收（B）**：`pack-sql-skill` 能產出一個 SKILL.md bundle，該 bundle 在**移除 dbt-wiki/dbt 專案**的環境下仍能對 bundle 內凍結 schema 生出 parse-通過的 SQL。

## Current State Evidence

（觸碰/擴充既有 skill，必填；皆實讀引用）

- **Forward（現有 happy path）**：`query` 接 NL 問題 → 分類 K1–K3（語意）/ C1–C11（結構）→ 分層檢索（summary frontmatter → full page, `query/SKILL.md:127-171`）→ 合成「答案」+ 引用 → 選擇性存 synthesis（`query/SKILL.md:178-300`）。**缺口**：query 停在「解釋」，**從不生成可跑 SQL**。A 重用其檢索骨架、新增 SQL 生成 + 靜態驗證的輸出契約。
- **Reverse（SSOT / 資料流向）**：dbt-wiki **無 distribute.py**（獨立 plugin）。`.dbt-wiki/` 由 `init`（Phase A evidence + Phase B knowledge）產生、`query`/`refresh` 消費。A 像 query 一樣**唯讀消費** `.dbt-wiki/`。**B 是第一個會「寫到 `.dbt-wiki/` 之外」的 dbt-wiki skill**（產出 bundle 到使用者指定路徑）——需明確其輸出邊界（落使用者私有 repo，per 資料治理護欄）。
- **Error / 一致性路徑**：`query` 有 drift check（`manifest_sha` vs 快照, `query/SKILL.md:54-65, 242-251`）。A 沿用：驗證對「當前 manifest」，drift 時加 caveat。B 的 bundle 是**凍結快照** → 必須帶 build-time `manifest_sha` + staleness 註記（沿用 synthesis 的 stale 契約形狀）。
- **Data 來源**：A 檢索輸入 = entities / metrics（**含本次剛 ship 的 `## Materialized Columns` 欄位卡**）/ concepts / `relationships` 邊 + evidence schema（`columns[].type`，catalog.json 在則為真型別, `SCHEMA.md:374-407`）。驗證用 `sqlglot`（**已是 dep**，init extraction 用之, `skills/init/assets/extract_column_lineage.py`）+ manifest。
- **Boundary（硬護欄）**：dbt-wiki **NEVER 連 warehouse / 執行 SQL / 連外部 API**（`SCHEMA.md:722-727`）。⇒ A/B 產 SQL **但不執行**；驗證 = 靜態（sqlglot parse + manifest/凍結 schema 存在性），**不做** execution-based 自我修正（那要連 warehouse，屬 dbt-wiki 核心邊界外的可選 producer，如同 log-mining）。真實 SQL/客戶名/輸出落使用者私有 repo（Block 8 治理）。

**Evidence paths appendix**：
- `dbt-wiki/skills/query/SKILL.md`（54-65, 116-171, 178-300）
- `dbt-wiki/skills/init/assets/SCHEMA.md`（232-289 metric+欄位卡頁型, 374-407 evidence 欄位, 722-727 NEVER）
- `dbt-wiki/skills/init/references/distill-metrics.md`（§5b 欄位卡 = A 的關鍵 schema-linking 輸入）
- `dbt-wiki/skills/init/assets/extract_column_lineage.py`（sqlglot 既有用法）

## Decision

**做**：
- **A = 新 sibling skill `dbt-wiki:to-sql`**（不塞進 `query` 的新 class——輸出契約不同：可跑 SQL + 靜態驗證 + 預留 few-shot，混入會讓 query 膨脹且職責不純）。重用 query 分層檢索；pipeline = 檢索→組 prompt（schema-link + 欄位卡 + join-path）→生 SQL→靜態驗證（sqlglot + manifest）→回傳 SQL+引用+驗證。**v1 zero-shot**，prompt 內建 few-shot slot。
- **B = 新 skill `dbt-wiki:pack-sql-skill`**：wiki →自包含 SKILL.md bundle（凍結 schema 卡 + 關係圖 + examples〔若有〕+ 生成 prompt），帶 manifest_sha + staleness。B 重用 A 的 prompt/生成邏輯（A 是核心，B 把 A 的 runtime「快照凍結」成可攜產物）。
- **A 先、B 後**：A 是 B 的前提（B 封裝的就是 A 的能力）+ A 給可量測 baseline 來驗證 wiki 有效、進而指導 B 的設計。

**不做（v1）**：
- **gold examples 的生成**：v1 A = zero-shot baseline（只設計 slot）。理由：(a) 給乾淨 baseline 量測 examples 的 +44.9pp 增益；(b) gold-example 生成 pipeline 是另一個已寫好的獨立 brief（`2026-06-02-dbt-wiki-gold-example-bank.md`，增強 L1）；(c) 最小終態。**← 此 scope 決策在 checkpoint 請你確認/否決（見 Open Questions OQ1）。**
- **execution-based 驗證 / 連 warehouse**：違反 dbt-wiki 核心邊界，屬可選外部 producer。
- **vector DB / embedding 檢索**：dbt-wiki 的 markdown 分層檢索已覆蓋，YAGNI。

**為何不塞進 query**：query 的契約是「解釋 + 引用 + 選擇性存 synthesis」；NL2SQL 的契約是「可跑 SQL + 靜態驗證 + few-shot」。兩者輸出形狀、驗證需求、未來演化（examples/log）都不同 → 獨立 skill（compose），避免把 query 變成 god-skill（complect）。

## Out of Scope

- gold-example bank 的生成/挑選（增強 L1，獨立 brief；A 只留 slot）。
- log-mined examples（增強 L2，可選，需真實 log）。
- 連 warehouse / 執行 SQL / execution-accuracy 自我修正迴圈。
- vector DB / embedding-based 檢索。
- 真實 SQL/客戶資料進 public repo（治理硬護欄）。
- 多方言 SQL 生成最佳化（v1 跟隨 manifest 的 adapter 方言；跨方言移植延後）。

## Alternatives Considered

（Axis 4 — research-grounded）

1. **RAG + vector DB schema retrieval**（RASL [arXiv 2507.23104]、Pinterest OpenSearch）— [Amazon Science RASL](https://assets.amazon.science/1b/95/8f62e89647348f4c4836f6c3040d/rasl-retrieval-augmented-schema-linking-for-massive-database-text-to-sql.pdf)、[Algomatic context-engineering JA](https://tech.algomatic.jp/entry/2026/01/28/190559)
   - Pros：超大 schema（數十萬表）可擴展；動態 few-shot 檢索。
   - Cons：要 embedding 基建；**dbt-wiki 已用 markdown 分層檢索達成等效「schema 拆語意實體 + summary」**——重複造輪。
   - 結論：採用其「檢索→few-shot→schema-link→生成」**架構**，但檢索層重用 dbt-wiki 既有分層機制，不引 vector DB。
2. **塞進現有 `query` skill 當新 query class** — 最少新檔。
   - Pros：重用最大化、單一入口。
   - Cons：輸出契約/驗證/演化都不同 → query 變 god-skill；違反 design-is-taking-apart。
   - 結論：否決，獨立 sibling skill。
3. **直接做 B、跳過 A** — 一步到位可攜產物。
   - Pros：少一個 skill。
   - Cons：沒有 baseline 量測、沒有早期測試迴圈、B 要凍結的「A 的邏輯」還沒驗證 → 高風險。user 也明確要 A 的早期測試價值。
   - 結論：否決，A 先。
4. **few-shot from start vs zero-shot baseline first**（SAFE-SQL [arXiv 2502.11438]、OpenSearch-SQL [arXiv 2502.14913]）— [SAFE-SQL](https://arxiv.org/pdf/2502.11438)
   - SAFE-SQL/研究：few-shot 例子是最大準確度槓桿（user 研究 +44.9pp）。
   - 但：gold-example pipeline 是獨立工程；zero-shot 先給可量測 baseline。
   - **My take**：**A v1 = zero-shot baseline，examples 設計成 slot、緊接著做**——理由：乾淨 baseline 才量得出 examples 的增益；examples 生成已有獨立 brief。Conditional reversal：若你的優先是「一上線就要最高準確度、可接受更大 v1」→ 把 gold-example 生成併進 part-1。**（OQ1 待你定）**

## What Becomes Obsolete

（Axis 5）

- 幾乎純新增（兩個新 skill）。
- `query` 的 K-class「解釋指標」與 A 的「生 SQL」相鄰但不重疊——但需在 router/README 明確兩者分工（query=理解資料、to-sql=產查詢），避免使用者混淆/觸發錯 skill。
- 若 A 證明有效，先前手寫「讀 wiki 自己拼 SQL」的人工流程變過時。
- 純增量是 flag：但此處有外部需求驅動（user 北極星），非 YAGNI。

## Open Questions

- **OQ1（scope）— ✅ LOCKED 2026-06-02**：A v1 = **zero-shot baseline**（不含 gold examples，prompt 留 few-shot slot）。examples 生成緊接著做、為獨立增量（已有 `2026-06-02-dbt-wiki-gold-example-bank.md` brief）。→ part-1 = A zero-shot；part-1 不含 examples 工程。
- **OQ2（B 設計，part-2 才需鎖）**：bundle 內要凍結「全部知識頁」還是「壓縮子集 + 按需」？可攜性 vs bundle 大小 vs 涵蓋率的取捨——part-2 brainstorm 再深入（可能需 dogfood A 的檢索命中率來指導）。
- **OQ3（命名）**：`to-sql` / `ask-sql` / `nl2sql`；`pack-sql-skill` / `export-sql-skill`。writing-plans 前定即可。
- **OQ4（驗證強度）**：靜態驗證之外，要不要「可選」掛 execution 驗證（透過使用者自備的 warehouse 連線，**作為 dbt-wiki 核心外的 opt-in producer**，類比 log-mining）？預設不做；記為未來增強。
