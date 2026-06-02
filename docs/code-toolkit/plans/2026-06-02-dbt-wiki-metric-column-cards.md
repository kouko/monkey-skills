# Plan: dbt-wiki metric 欄位卡（materialized-metric column cards）

**Source brief**: docs/code-toolkit/specs/2026-06-02-dbt-wiki-metric-column-cards.md
**Total tasks**: 4
**Critical-path depth**: 3 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-02)

> **Nature**: 純 spec/markdown 編修，無對應 code 測試（dbt-wiki pytest 只覆蓋 Python extraction scripts）。
> 每個 task 的 acceptance 是 **RED diagnostic**（grep 該規則/區段不存在 → 編修後存在）+ reviewer 語意一致性確認。
> User 拍板：**只放 body 表格**，零 frontmatter 結構塊。觸碰檔僅 `SCHEMA.md` + `distill-metrics.md`；query/refresh/init 泛型載入、零強制改動（OQ1 顯式指引延後）。

---

## Task 1 — SCHEMA knowledge-metric 加 optional `## Materialized Columns` 區段定義

- **Description**: 在 `assets/SCHEMA.md` 的 `### knowledge-metric` body sections 區塊（現有 Definition / Calculation / Caveats / Relationships / Evidence），加入一個 **optional** 的 `## Materialized Columns` 區段定義：說明「僅當 metric 被預先物化成 mart 欄位時出現」，內容為一張 markdown 表格，列「期間/區隔變體 → 實體 `model.column` + grain」，供 text-to-SQL 直接 SELECT。明確標註 body-only（不進 frontmatter）、不破壞「一個 metric 一頁」原則。
- **Module**: `dbt-wiki/skills/init/assets/SCHEMA.md`
- **Files touched**: `dbt-wiki/skills/init/assets/SCHEMA.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md`（232-261 knowledge-metric 段）
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-02-dbt-wiki-metric-column-cards.md`
- **Acceptance**:
  - **RED**: `grep -c "Materialized Columns" dbt-wiki/skills/init/assets/SCHEMA.md` 在 knowledge-metric 段回 0（區段未定義）
  - **GREEN**: knowledge-metric body sections 含 `## Materialized Columns` optional 區段定義，標明「僅物化 metric 出現」+ 表格欄位（變體 → `model.column` + grain）+ body-only；SCHEMA「frozen for v2.x，只允許 wording 澄清」的精神以**新增 optional 區段**方式相容（不改既有必備區段語意）
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "`assets/SCHEMA.md`（knowledge-metric 頁型 SSOT）：加一個 optional `## Materialized Columns` 區段定義（僅在 metric 被物化成欄位時出現）"

## Task 2 — distill-metrics 加物化偵測 gate + 訊號清單

- **Description**: 在 `references/distill-metrics.md` 的 SQL-derivation 分支（§3）加一個新子節（如 §3c「物化偵測」）：判斷 metric 的變體是否已是**預物化的實體欄位**（值已算好、query 時直接 SELECT、不需再 GROUP BY），給出可測試的啟發式訊號清單（mart/reporting 層、欄位名期間後綴 `_mtd`/`_ytd`/`_mom`/`_l30d` 等森林、schema.yml 描述該欄位為 measure 值、一行一 entity/period grain 已聚合）並明確與「一般 fct 表仍需 query 時聚合」的邊界區隔。命中 → 路由到欄位卡輸出（§Task 3 定義）；未命中 → 維持既有公式/§5 fallback 路徑。
- **Module**: `dbt-wiki/skills/init/references/distill-metrics.md`
- **Files touched**: `dbt-wiki/skills/init/references/distill-metrics.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/references/distill-metrics.md`（107-153 §3 SQL-derivation、41-47 §1 期間變體、201-217 §5 fallback）
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-02-dbt-wiki-metric-column-cards.md`
- **Acceptance**:
  - **RED**: distill-metrics.md §3 無「物化偵測」子節 / 無「預物化欄位 vs 仍需聚合」判準（grep「物化」「materializ」在 §3 範圍回 0 命中）
  - **GREEN**: §3 含物化偵測子節 + 啟發式訊號清單 + 與一般 fct 的邊界區隔 + 命中/未命中分流敘述（命中→欄位卡、未命中→公式/§5）
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "新增『物化偵測』判斷：這個 metric 的變體是否已是預物化的實體欄位（值已算好、query 時直接 SELECT、不需再聚合）？"

## Task 3 — distill-metrics 加 `## Materialized Columns` 輸出規格 + 調整 Calculation 敘述

- **Description**: 在 `references/distill-metrics.md` 加「欄位卡輸出規格」：當物化偵測命中，metric 頁額外產出 `## Materialized Columns` body 表格（變體維度 → 實體 `model.column` + grain），並把 `## Calculation`（§5 周邊）調整為「對物化 metric：值已預先算好，直接 SELECT 對應欄位」+ 指向該表。納入**欄位森林壓縮規則**：欄位遵循規則命名模式（如 `gmv_{period}_{segment}`）時，表格捕捉「模式 + 維度允許值清單」而非逐列 100 列；僅命名不規則時逐欄列舉。表格欄名/區段名須與 Task 1 在 SCHEMA 定義的一致。
- **Module**: `dbt-wiki/skills/init/references/distill-metrics.md`
- **Files touched**: `dbt-wiki/skills/init/references/distill-metrics.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/references/distill-metrics.md`（176-217 §4-5 Calculation+fallback）
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md`（Task 1 新增的 `## Materialized Columns` 定義 — 確保命名一致）
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-02-dbt-wiki-metric-column-cards.md`
- **Acceptance**:
  - **RED**: distill-metrics.md 無 `## Materialized Columns` 輸出區段規格 / 無欄位森林命名模式壓縮規則（grep 回 0）
  - **GREEN**: distill-metrics.md 含欄位卡輸出規格（表格欄位定義 + 變體→`model.column`+grain）+ 命名模式壓縮規則 + Calculation 對物化 metric 改為「直接 SELECT 預建欄位」敘述；區段名/欄名與 SCHEMA（Task 1）一致
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false  # 與 Task 2/4 同檔（distill-metrics.md）；且須對齊 Task 1 的 SCHEMA 區段名（doc-mirrors-doc）
- **Brief item covered**: "是 → 額外產出一個 `## Materialized Columns` body 區段：一張 markdown 表格，列『期間/區隔變體 → 實體 model.column + grain』；`## Calculation` 改寫為『值已預先算好，直接 SELECT 對應欄位』" + "大欄位森林用維度化/命名模式壓縮，避免 100 列爆炸"

## Task 4 — distill-metrics 加物化 metric worked example + 更新 §11 decision-rule 表

- **Description**: 在 `references/distill-metrics.md` 加一個物化 metric 的完整 worked example（GMV 期間變體欄位森林風格：合成 evidence，產出含 `## Materialized Columns` 映射表的完整 metric 頁；不得含任何真實客戶名/真實 SQL），並更新 §11「Summary of Decision Rules」表，新增一列明確分流：「metric 變體已物化成欄位 → 走欄位卡（§Task 3 區段）」vs「非物化純聚合/window → 走 §5 散文 fallback」，避免兩路徑語意重疊漂移（Axis 5）。
- **Module**: `dbt-wiki/skills/init/references/distill-metrics.md`
- **Files touched**: `dbt-wiki/skills/init/references/distill-metrics.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/references/distill-metrics.md`（348-438 §10 既有 worked example、442-458 §11 decision-rule 表）
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-02-dbt-wiki-metric-column-cards.md`
- **Acceptance**:
  - **RED**: distill-metrics.md 無物化 metric worked example / §11 表無「物化→欄位卡 vs 非物化→公式」分流列（grep 回 0）；example 不得出現真實客戶名
  - **GREEN**: distill-metrics.md 含一個物化 metric 完整 worked example（合成、零真實資料）+ §11 表新增分流列；example 用合成名（如 acme / synthetic store GMV）
- **Dependencies**: Task 3 completes first
- **Independent**: false  # 與 Task 2/3 同檔（distill-metrics.md）；example 須示範 Task 3 定義的輸出格式
- **Brief item covered**: "Worked example：在 distill-metrics.md 加（或擴充）一個物化 metric 的完整範例（如 GMV 期間變體欄位森林）" + Axis 5 "需在 distill-metrics §5 與 §11 decision-rule 表明確分流，避免兩條路徑語意重疊漂移"

## Notes

- **依賴結構**：Task 1（SCHEMA）∥ Task 2（distill 偵測）為同一 dependency level 的兩個 leaf（disjoint files、無語意依賴）→ 兩者皆 `Independent: true`，可並行派遣。Task 3 join 兩者（須對齊 SCHEMA 區段名 + 接 Task 2 的 gate），Task 4 接 Task 3。Critical path = (T1∥T2) → T3 → T4 = **depth 3**。
- **同檔序列化**：Task 2/3/4 皆編修 `distill-metrics.md`，即使無語意依賴也不可並行（同檔寫入）；故 Task 3/4 標 `Independent: false`。唯一可並行的是 Task 1（SCHEMA.md，異檔）對 Task 2。
- **護欄（Block 8）**：所有 worked example / 範例一律合成資料，**絕不**含任何真實客戶名 / 真實 SQL；artifact-only、零 warehouse/log。
- **OQ1（延後）**：query K1/K2 是否加「metric 頁若有 `## Materialized Columns`，text-to-SQL 優先回該映射」的輕量指引 — 不在本 plan，泛型載入已涵蓋；若 SDD 中確認低成本可作為 fast-follow task 追加。
