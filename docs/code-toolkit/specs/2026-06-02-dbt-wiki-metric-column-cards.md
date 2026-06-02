# Brief — dbt-wiki：metric 欄位卡（materialized-metric column cards）

- **Date**: 2026-06-02
- **Topic**: dbt-wiki-metric-column-cards
- **Stage**: brainstorming → (next) writing-plans → SDD
- **Nature**: artifact-only spec 精修；零 warehouse/log；對已 ship v2.0 distill 規格的增量
- **Background handoff**: `.claude/handoffs/HANDOFF-2026-06-02-005739-dbt-wiki-metric-column-cards.md`
- **North star**: 餵一個對「商業邏輯問題」有效的 text-to-SQL skill。本變更完成 dbt-wiki 最小狀態的最後一塊（知識層 ✅ + 關係圖 ✅ + metric 欄位卡 ⬜）。

---

## Problem

（Axis 1 — JTBD）

**When** dbt 專案把相當比例的 metric **預先物化成 mart 欄位**（如預聚合的月度 GMV：`gmv_mtd` / `gmv_ytd` / `gmv_mom` / 各通路區隔 …，一個 measure 可達數十～上百欄的「欄位森林」），**I want** dbt-wiki 蒸餾出的 metric 頁能直接告訴下游 text-to-SQL skill「哪個業務問題 → 哪個實體 `model.column`」，**so I can** 讓 text-to-SQL 用 **retrieval/mapping**（SELECT 預建欄位）而非重新合成 GROUP BY 聚合——這正是研究證實的最大準確度槓桿。

問題的本質**不是公式**：這些 metric 的值已經算好躺在欄位裡。text-to-SQL 需要的是「business vocabulary（metric + 期間/區隔維度）→ physical `table.column`」的映射。

**研究 grounding（Axis 4，WebSearch EN+JA，已交叉）**：semantic-layer 把業務詞彙映射到實體欄位是 NL→SQL 準確度的主槓桿——dbt 自家 benchmark **16.7% → 83%**（純靠走 semantic-layer 映射）；企業部署 85–95%。欄位卡 = 對沒有 MetricFlow、但有預物化欄位的專案，提供一個**微型 semantic-layer 映射**。

## Users

（Axis 2）

- **直接消費者**：未來的 text-to-SQL skill（cold-start LLM 讀 `.dbt-wiki/metrics/*.md` 來決定 SELECT 哪個欄位）。
- **間接消費者**：分析師 / 工程師透過 `/dbt-wiki:query`（K1「這個指標是什麼」、K2「跟哪些實體有關」）讀 metric 頁。
- **生產者**：`init` 的 Phase B metric distillation（依 `distill-metrics.md` 程序，從 `_evidence/` + manifest.json + sqlglot 蒸餾，零 warehouse 連線）。
- **條件**：多數 dbt-wiki 使用者**沒有** MetricFlow / dbt Semantic Layer（否則走既有 §2b 權威 ingest 分支）；很多人沒有可查 log / 無權限——所以機制只能吃 manifest + compiled SQL。

## Smallest End State

（Axis 3）

在現有 **SQL-derivation 分支（§3）內** 加一個物化偵測子步驟與一個結構化映射輸出區段，**不新增頁型、不改既有「一個 metric 一頁」原則、不碰 frontmatter（user 拍板：只放 body 表格）**：

1. **`distill-metrics.md`（主要修改對象）**：
   - 新增「物化偵測」判斷：這個 metric 的變體是否已是**預物化的實體欄位**（值已算好、query 時直接 SELECT、不需再聚合）？
   - 是 → 額外產出一個 **`## Materialized Columns`** body 區段：一張 markdown 表格，列「期間/區隔變體 → 實體 `model.column` + grain」；`## Calculation` 改寫為「值已預先算好，直接 SELECT 對應欄位」+ 指向該表。
   - 否 → 維持既有公式 / 聚合路徑（§5 fallback 不變）。
   - 大欄位森林用**維度化/命名模式**壓縮，避免 100 列爆炸（見 Decision）。
2. **`assets/SCHEMA.md`（knowledge-metric 頁型 SSOT）**：在 knowledge-metric body sections 加一個 **optional** `## Materialized Columns` 區段定義（僅在 metric 被物化成欄位時出現）。
3. **Worked example**：在 distill-metrics.md 加（或擴充）一個物化 metric 的完整範例（如 GMV 期間變體欄位森林）。

**驗收**：給定一個含預聚合欄位森林的合成 evidence，依新規程能產出含 `## Materialized Columns` 映射表的 metric 頁；非物化 metric 仍走原公式路徑、輸出不變。

## Current State Evidence

（觸碰既有規格，必填；皆實讀引用）

- **Forward（現有 happy path）**：`distill-metrics.md` §3 SQL-derivation 產出 metric 頁（Definition/Calculation/Caveats/Relationships/Evidence）。期間變體**已**被收斂為「ONE page，描述在 `## Calculation` 散文」(`distill-metrics.md:41-47`)；純聚合/window 無公式者走 §5 fallback「描述 aggregation + grain + 期間變體 + 上游定義註記」(`distill-metrics.md:201-217`)。**缺口**：散文描述了「有哪些期間變體」，但沒有給出**變體 → 實體欄位名**的結構化查找；text-to-SQL 仍須猜哪個欄位。
- **Reverse（SSOT 擁有權 / 資料流向）**：dbt-wiki **無 distribute.py / sync 腳本**（非 code-team functional-copy 機制）。頁型 SSOT = `SCHEMA.md` knowledge-metric 段 (`assets/SCHEMA.md:232-261`)；`distill-metrics.md` 是**實作該頁型的程序**。方向：SCHEMA 定義頁型 ← distill-metrics 實作；兩者須同步新增該區段（手動契約，非腳本）。
- **Error / 一致性路徑**：`refresh` 對知識頁的 stale-flag 純靠 `derived_from` glob 重疊 (`skills/refresh/SKILL.md:343-346`)，**不檢查 body 區段清單** → 新增 derived 區段對 refresh 無破壞、無需改 refresh。`query` K1/K2 「載入整個 metric 頁 + 走 `## Relationships`」亦為泛型、**無區段 allowlist** (`skills/query/SKILL.md:127-128`) → 自動吃到新區段。**結論：consumer 端零強制改動**（handoff「須同步 init/query/refresh」的疑慮在實讀後降級為「確認泛型」——已確認）。
- **Data 來源**：欄位卡的 `model.column` 映射資料來自 evidence model 頁的 `columns[]`（實體欄位名 + description + type + sources）(`assets/SCHEMA.md:374-407`)。物化偵測的訊號（mart 層、欄位名期間後綴、值已聚合）由 evidence 頁 + compiled SQL 提供。
- **Boundary（護欄）**：純 manifest.json + sqlglot；零 warehouse / 零 log / 零外部 API（`SCHEMA.md:694-701` What dbt-wiki NEVER does）；artifact-only。真實 SQL / 客戶名 / `.dbt-wiki/` 輸出**絕不**進 public repo（handoff Block 8）。

**Evidence paths appendix**：
- `dbt-wiki/skills/init/references/distill-metrics.md`（41-47, 107-153, 176-217, 442-458）
- `dbt-wiki/skills/init/assets/SCHEMA.md`（232-261, 290-339, 374-407, 658-675, 694-701）
- `dbt-wiki/skills/query/SKILL.md`（127-128, 152）
- `dbt-wiki/skills/refresh/SKILL.md`（343-346, 384-426）
- `dbt-wiki/skills/init/SKILL.md`（691-761 Phase B orchestration，泛型引用 distill-metrics）

## Decision

**做**：在 distill-metrics.md §3（SQL-derivation 分支）加一個**物化偵測子步驟**，命中時為 metric 頁產出一個 **`## Materialized Columns`** body 區段（markdown 表格：變體維度 → 實體 `model.column` + grain），並把 `## Calculation` 調整為「預物化、直接 SELECT」敘述；SCHEMA knowledge-metric 頁型加上該 optional 區段定義；補一個物化 metric 的 worked example。

**不做**：不新增頁型；不破壞「一個 metric 一頁」（§1）；不加 frontmatter 結構塊（user 拍板 body-only，零新增 frontmatter↔body drift 面）；不改 §2b MetricFlow 權威 ingest 分支；不碰 init/query/refresh 的核心邏輯（泛型已涵蓋，至多加一句指引——見 Open Questions）。

**為何 body-only**：(1) 最小終態；(2) 零新增 byte-coupling drift（user 反覆被 frontmatter↔body 三方耦合咬過）；(3) text-to-SQL skill 讀 markdown 即可取用；(4) 符合 v2.0「知識主體、人類可讀」定位。若下游證明需程式化抽取 → 再加 frontmatter（可逆、延後）。

**欄位森林壓縮（Decision C，confident proposal）**：當物化欄位遵循規則命名模式（如 `gmv_{period}_{segment}`），表格捕捉**模式 + 維度允許值清單**（period ∈ {daily, mtd, qtd, ytd, mom, yoy …}、segment ∈ {total, online, …}），而非逐欄列 100 列；僅在命名不規則時才逐欄列舉。理由：對 text-to-SQL，「命名模式 + 維度枚舉」比 100 列更可泛化、頁面更精簡，且與 §1「不 fork 20 個近重複頁」一致。

## Out of Scope

- examples/ gold-example bank（增強 L1，brief 已寫 = handoff P2，獨立 commit）。
- log-mined examples（增強 L2，可選，需真實 log）。
- MetricFlow / Semantic Layer 權威 ingest 分支（§2b 已存在，不動）。
- frontmatter `materialized_columns:` 機器結構塊（延後，下游需求驅動才做）。
- 消費端 text-to-SQL skill 本身（handoff P3 策略題，待定路線圖長度）。
- 任何 warehouse / log / catalog.json 連線（v2.0 仍 artifact-only）。
- v1.x migration（clean-break，不做）。

## Alternatives Considered

（Axis 4 — research-grounded）

1. **走 MetricFlow / Semantic Layer 權威 ingest**（dbt Semantic Layer / Cube / LookML）— [dbt Developer Blog: Semantic Layer vs Text-to-SQL 2026](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026)、[NTT DATA DATA INSIGHT](https://www.nttdata.com/jp/ja/trends/data-insight/2024/0912/)
   - Pros：最高準確度（16.7%→83%）；確定性查詢生成；業界主流方向。
   - Cons：**多數目標使用者沒有 MetricFlow**；本變更的前提正是「metric 已被物化成欄位、無 Semantic Layer」。
   - 結論：已是既有 §2b 分支；本變更是**補上沒有 Semantic Layer 時的等效映射**，非取代。
2. **不做映射、維持 `## Calculation` 散文描述期間變體** — 現狀。
   - Pros：零改動。
   - Cons：text-to-SQL 仍須從散文猜實體欄位名 → schema-linking 負擔留給下游；放棄已知最大槓桿。
3. **frontmatter 結構塊（machine-first）** — 比照現有 `relationships:` 雙寫。
   - Pros：機器可讀性最高，下游可直接 parse。
   - Cons：新增 frontmatter↔body drift 面（user 痛點）；v2.0 定位偏人類可讀。
   - 結論：user 拍板降級為延後增強。

**My take（已採納）**：body-only `## Materialized Columns` 表格（選項對映「只放 body 表格」）。Why：補足無-Semantic-Layer 專案的 schema-linking 映射（最大槓桿）、最小終態、零新增 drift。Conditional reversal：若下游 text-to-SQL skill 證明需穩定程式化抽取 → 加 frontmatter 鏡像（Alternative 3）。

## What Becomes Obsolete

（Axis 5）

- 嚴格說無「程式碼」過時——這是 spec 增量。
- **概念上**：對物化 metric，§5「無公式 fallback」的純散文期間變體描述被 `## Materialized Columns` 結構表**取代/升級**（fallback 仍用於非物化的純聚合/window metric）。需在 distill-metrics §5 與 §11 decision-rule 表明確「物化 → 走欄位卡；非物化純聚合 → 走 §5 散文 fallback」的分流，避免兩條路徑語意重疊漂移。

## Open Questions

- **OQ1（不擋實作）**：query K1/K2 是否要加一句指引「metric 頁若有 `## Materialized Columns`，text-to-SQL 類問題優先回該映射」？泛型載入已涵蓋，但顯式指引可提升下游命中。→ 傾向加一句輕量指引，writing-plans 時定。
- **OQ2（策略，handoff P3）**：`examples/` vs `syntheses/` 是否收斂、消費端 text-to-SQL skill 算不算本專案——皆**不擋本變更**。
- **OQ3**：物化偵測的「值已預聚合、不需再 GROUP BY」訊號邊界（vs 一般 fct 表仍需聚合）——writing-plans 時把判準寫死成可測試的啟發式清單。
