# Brief — dbt-wiki 知識主體化重設計（v2.0）

- **Date**: 2026-06-01
- **Topic**: 把 dbt-wiki 從「資源類型蒸餾」改造成「知識主體蒸餾」
- **Current version**: dbt-wiki 1.3.0（SCHEMA 標記 frozen for v1.x → 本次為 **v2.0** breaking + migration）
- **Stage**: brainstorming brief → 待 user 簽核 → writing-plans

---

## Problem
（Axis 1 — JTBD）

> 當我（或團隊的分析師）要理解、分析一個 dbt 專案處理的資料時，我要的是**圍繞「資料代表什麼意義」組織的蒸餾知識**——業務實體、指標、業務概念、資料領域——而不是圍繞 dbt 的物件類型（model / source / macro）。這樣我不必逆向閱讀 SQL 與 DAG，就能理解這份資料在講什麼、進而分析它。

核心轉變：**dbt 物件類型從「蒸餾的主體」降級為「支撐知識的證據」**。知識是主角，結構血緣是它的腳註。

## Users
（Axis 2 — job story）

- **主要**：資料分析師 / BI / 想理解資料的工程師。「當我接手或查詢一個不熟的 dbt 專案，我想用業務語言（churn 是什麼、哪些實體跟營收有關、這個指標怎麼算）查到答案，而不必先讀 200 個 model 的 SQL，這樣我能更快開始分析。」
- **次要**：dbt 開發者本人，用知識層做 onboarding 文件 / 跨團隊溝通的語意對照。
- **既有工具與限制**：手上有 dbt 專案（`manifest.json` + compiled SQL + schema.yml）；可能有也可能沒有 dbt Semantic Layer（MetricFlow metrics）；本機 LLM-driven skill，無法連 warehouse / dbt Cloud。

## Smallest End State
（Axis 3 — 最小可交付）

最小但仍解決 JTBD 的版本：

1. **SCHEMA v2.0** — 定義知識層頁型 + 證據層 + migration note。
2. **init 兩階段**：Phase A 機械建證據層（現有 pipeline，搬到 `_evidence/`）→ Phase B **新增** LLM 蒸餾知識層（至少 `entities/` + `metrics/` + `concepts/`），每頁引用證據層。
3. **query 加語意問句類別**（「churn 是什麼意思」「哪些實體跟營收有關」「解釋這個指標」），結構類問句改讀證據層。
4. **refresh** 機械刷新證據層（核心不變）+ 把受影響的知識頁標 stale（沿用現有 syntheses stale 機制）。

**可延後到 fast-follow（不在最小範圍）**：`domains/` 維度、ingest 寫進知識頁、完整語意問句 taxonomy、dbt Semantic Layer 深度整合。

> 註：因 SCHEMA frozen-for-v1.x，任何頁型變更都強制 v2.0 + migration，所以「最小」仍必含 SCHEMA + init + query + refresh 四處；ingest 與 domains 可獨立後續。

## Current State Evidence
（觸碰既有程式碼，必填）

- **Forward（進入點 / 控制流）**：4 個 skill 各有 trigger（`skills/{init,refresh,ingest,query}/SKILL.md` frontmatter）。init 管線 Step 0→6（`skills/init/SKILL.md`，Step 6 生成 index/lineage 在 `:599-608`）。
- **Reverse（SSOT / 誰擁有什麼）**：
  - 頁面格式 SSOT = `skills/init/assets/SCHEMA.md`（`:49` Directory Layout、`:68-71` Page Types、`:70+` model frontmatter）；標記 **frozen for v1.x**（`SCHEMA.md:1-6`），重大改動須 v2.0 + migration script。
  - 生成權責：init 全量生成、refresh 增量、ingest 只碰 `## User Notes`、query 唯讀。
  - 權威來源 = `target/manifest.json` + compiled SQL（不可變的 `dbt/` 源層，SCHEMA `:11-18`）。
  - **無 `distribute.py`/sync 腳本**——dbt-wiki 是自包含 plugin，無 code-team 式 SSOT 分發；證據層直接由 init/refresh 寫。
- **Error / edge**：sqlglot parse 失敗 → `columns_extracted_via: failed`（頁仍建、欄位 sources 空，`init:494-495`）；`manifest_sha` drift 偵測（query Step 0 / refresh Step 1）；orphan 不硬刪、archive 到 `_archive/<date>/`（refresh Step 5）。
- **Data（資料形狀）**：manifest + sqlglot + schema.yml → model frontmatter（`SCHEMA.md:70-145`：materialization / columns[].sources / depends_on / feeds_into）。recursive column lineage JSONL（`init:526-534`）。
- **Boundary（邊界）**：dbt-wiki = STRUCTURE+LINEAGE vs repo-wiki = WHY（`SCHEMA.md:31-39`）；dbt-wiki 絕不寫 `.dbt-wiki/` + `CLAUDE.md` 以外、絕不連 warehouse / dbt Cloud（各 skill Rules 段）。

**Evidence paths appendix**：
- `dbt-wiki/skills/init/assets/SCHEMA.md`
- `dbt-wiki/skills/init/SKILL.md`
- `dbt-wiki/skills/refresh/SKILL.md`
- `dbt-wiki/skills/query/SKILL.md`
- `dbt-wiki/skills/ingest/SKILL.md`

## Decision
（要建什麼 / 不建什麼 / 為什麼）

採 **雙層架構（user 已簽核）**：

- **知識層（主體，LLM 蒸餾）** — `entities/`、`metrics/`、`concepts/`（最小）+ `domains/`（後續）。LLM 讀 SQL + 欄名 + schema.yml description + 血緣，蒸餾業務意義；每頁以 markdown link 引用證據層頁面（仿 Obsidian wiki references→entities 模式）。
- **證據層（支撐，機械萃取，降級）** — 現有 `models/ sources/ macros/ seeds/ snapshots/ tests/ exposures/` 搬到 `_evidence/` 之下，manifest + sqlglot + `manifest_sha` drift **完整保留**（這是現有核心價值，也是蒸餾的最佳原料，不丟）。`lineage.md`、`syntheses/` 保留。

不建：真正的 RDF/ontology graph store；不連 warehouse / dbt Cloud；不取代 dbt Semantic Layer（**若專案有 MetricFlow metrics，metrics/ 維度應 ingest 它當權威輸入，不重推**）；不碰 `.repo-wiki/`。

**知識維度集合（✅ LOCKED 2026-06-01）— 三維 + typed links**：

| 維度 | 放什麼 | 來源訊號 | 對應產業概念 |
|---|---|---|---|
| `entities/` | 業務物件（Customer, Order, Subscription）；跨 stg→int→mart 多 model。**欄位段含白話欄位字典（glossary 併此，不另開）** | model 命名族、grain、欄位語意、血緣聚類 | Ontology concepts |
| `metrics/` | 業務指標（MRR, churn, LTV）：定義＋算法白話＋caveats＋來源 model | 聚合 SQL、MetricFlow metrics（若有）、mart 欄位 | Semantic / Metrics Layer |
| `concepts/` | SQL 裡編碼、不屬單一實體的橫切業務規則（「活躍客戶＝近 90 天有單」、財年、狀態列舉） | CASE/WHERE 語意、schema.yml description | Business Glossary（抽象詞） |
| `domains/`（後續，非首版） | 主題領域 landscape（finance / marketing / product），彙整實體+指標+概念 | dbt groups / mart 子資料夾 / tags | Data domain / 子領域導覽 |

**維度間關聯 = typed links（graph，非巢狀）**：每頁一個 `## Relationships` 段（或 frontmatter `related:`），LLM 從血緣＋SQL 語意推出有類型的邊：entity↔entity（join key / depends_on）、metric→entity（衡量對象 / GROUP BY grain）、metric→concept（算法依賴）、concept→entity/metric（規則套用）、任何知識頁→`_evidence/`（證據引用）。這層 typed-link 即產業講的輕量 ontology / knowledge graph。

**不獨立成維度（當頁內段落）**：`glossary`（欄位白話意義長在 entity 頁欄位段 + 生成 `glossary.md` 索引）、`data-quality`（entity/metric 頁的 caveats / 測試覆蓋段，資料來自證據層 dbt tests）。理由：關聯已由 typed link 承載，多開資料夾只會製造 routing 歧義與 drift。

## Alternatives Considered
（Axis 4 — WebSearch EN+JA，已執行）

業界把「關於資料的知識」分層，三條成熟路線：

1. **機械爬取型 Data Catalog**（Atlan / DataHub / OpenMetadata）— 自動爬 dbt models 生 metadata + lineage。**Pros**：自動、永遠新。**Cons**：語意淺、停在「結構」（=現在的 dbt-wiki）。
2. **人工策展 Business Glossary + Ontology**（Actian / data.world）— 詞彙表 + 概念關係。**Pros**：語意深、可概念搜尋。**Cons**：人工成本高、易過時。
3. **AI 輔助語意蒸餾**（dbt「Ask dbt」、AI semantic search）— LLM 讀專案自動生語意。**Pros**：自動 + 深語意。**Cons**：非決定性、可能出錯、freshness 需另設機制。

**My take（given context）**：
- **Recommend：路線 3（AI 蒸餾）疊在路線 1（機械證據）之上** = 本 brief 的雙層設計。理由：LLM-driven skill 的獨門優勢正是「讓機器讀 SQL+血緣自動產出業務意義」，補上機械爬取做不到、人工策展太貴的中間地帶；保留路線 1 當證據層則守住決定性血緣。
- **Conditional reversal**：若日後要對接企業級治理 / 跨工具一致性，再考慮把 `metrics/` 導出成真正的 semantic layer 規格（MetricFlow / cube）而非只是知識頁。
- EN/JA 一致（無分歧）：兩語都把 catalog（發現）/ glossary（詞義）/ semantic layer（指標算法）/ ontology（關係）分層，且都點名 AI 輔助為新興中間地帶。

來源：[Atlan dbt-data-catalog](https://atlan.com/dbt-data-catalog/)、[DataHub ontology-vs-semantic-layer](https://datahub.com/blog/ontology-vs-semantic-layer/)、[Actian business-glossary](https://www.actian.com/data-intelligence/business-glossary/)、[getdbt semantic-layer](https://www.getdbt.com/discover/understanding-the-semantic-layer)、[NTT DATA セマンティックレイヤー](https://www.nttdata.com/jp/ja/trends/data-insight/2024/0912/)、[Hakky dbt データカタログ](https://book.st-hakky.com/data-platform/data-catalog-and-dbt-usage)。

## What Becomes Obsolete
（Axis 5 — 同個 PR 內處理）

- **定位語句** `dbt-wiki = STRUCTURE + COLUMN LINEAGE`（`SCHEMA.md:35`）→ 改成「= 資料的語意知識，由結構證據支撐」。同步改 repo-wiki coexistence 段（`SCHEMA.md:31-39`）：repo-wiki=WHY（決策）vs dbt-wiki=WHAT-the-data-means（語意），仍互補、交叉連結。
- **index.md 純結構分組**（tier/materialization/tag/group，`init:603-608`）→ 改成知識優先索引（by domain / entity / metric），結構分組降級進證據層索引。
- **query C1–C11 即全部分類**（`query:115-125`）→ 結構類保留但成少數，語意類問句領頭。
- **頂層 `.dbt-wiki/models/`**（`SCHEMA.md:57,71`）→ 搬到 `_evidence/models/`（migration script 處理既有使用者）。
- **「dbt-wiki 純機械、零判斷」的賣點敘述**（各 README / SKILL 描述）→ 改成「證據層機械、知識層 AI 蒸餾」雙重敘事。

## Out of Scope

- 真正的 graph database / RDF / SPARQL。
- 連接 warehouse、dbt Cloud、catalog.json 即時欄位型別（維持現有 Phase 2+ optional）。
- 取代或實作 dbt Semantic Layer（只 ingest 既有 MetricFlow，不產生 MetricFlow）。
- 改動 `.repo-wiki/` 任何內容。
- `domains/` 維度、ingest→知識頁、refresh 自動重蒸全形、完整語意 query taxonomy（**全列 fast-follow，不在 MVP 首個 PR**）。
- migration / 佈局偵測 / git mv / 跨位置 User Notes 保留（clean-break，永不做）。

## Open Questions

1. ~~知識維度集合~~ **✅ LOCKED**：三維 `entities/metrics/concepts` + typed-link `## Relationships`；glossary/data-quality 當頁內段落不另開；`domains/` 後續。
2. ~~migration 策略~~ **✅ LOCKED**：**clean break，不寫 migration**。v2.0 直接重建，砍掉佈局偵測 / `git mv` 搬遷 / 跨位置 User Notes 保留邏輯（YAGNI — plugin 早期無滿載部署）。唯一護欄：init 偵測到 v1.x `.dbt-wiki/` 且含 User Notes 時**印一次警告**（不保留、建議先備份），非遷移邏輯。
3. ~~知識層 freshness~~ **✅ LOCKED — 自動重蒸餾（精確版 B）**：refresh 用既有 **manifest diff（Step 2 比對 columns/depends_on/materialization/raw_code md5）精確抓 modified models** → **只對這些 model 背後的知識頁自動 re-distill**（不碰未變頁 → 無多餘 git 抖動，動到的頁是真語意變、diff 合法）→ 重蒸頁可隨改動 model 的 PR 一起 commit，frontmatter 記 `last_changed_by: <commit/PR>` provenance。**不採 git-diff 偵測**（粗、漏上游 var/macro/source 傳播、誤判純 refactor）；不採「每次全量重蒸」（成本/抖動）。成本 = 該次 PR 改動量，通常小。
   - 知識頁 frontmatter 需記 `derived_from: [evidence model uids]`，refresh 據此判定哪些知識頁受影響（重用 syntheses affected_models 重疊邏輯，方向相同）。
4. ~~首個 v2.0 範圍切分~~ **✅ LOCKED — MVP**：首個 PR = **SCHEMA v2.0 + init（Phase A 證據 + Phase B 蒸餾）+ query（語意問句）+ thin refresh（證據刷新 + 標 stale，先不自動重蒸）**。理由：知識蒸餾品質是最高風險的未驗證新核心（蒸餾引擎在 init、其餘消費它），先最小投資驗證品質。
   - **Fast-follow（不在 MVP）**：refresh 自動重蒸（第 3 項全形）→ ingest→知識頁 → `domains/` 維度。
   - 注意：第 3 項鎖定的 freshness model（自動重蒸）為**最終形態**；MVP 先出 thin refresh（flag-stale）當踏腳石，自動重蒸排 fast-follow（複用 init 蒸餾引擎 + refresh 既有 manifest diff，屆時增量接線）。
