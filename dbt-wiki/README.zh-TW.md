# dbt-wiki

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Local-only LLM 可查詢的 dbt 專案**語意知識庫**，採雙層架構：**知識層**（LLM 蒸餾的業務物件／指標／橫切業務規則）由**證據層**（manifest + sqlglot 機械萃取的結構血緣）支撐。Query 用業務語言問「churn 是什麼意思」「哪些實體跟營收有關」「這個指標怎麼算」，以及既有的結構血緣問題——**不需 dbt Cloud、不離開機器**。

**Version**: 2.4.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## 背景

dbt 第一方有 `dbt docs generate`（靜態 HTML 網站），生態裡也有付費工具（dbt Cloud Discovery API、第三方 lineage 平台）。但**對話式 LLM 查 dbt 專案結構**這個 niche 是空的：

- **dbt Cloud Discovery API**——有 metadata，但要付費訂閱
- **dbt docs serve**——HTML 給人看，LLM 沒法直接查
- **`target/manifest.json`**——結構化真實，但 1-50MB；沒 query 介面
- **dbt-mcp 不開 Discovery**——只露 CLI 工具；LLM 要自己解析 `dbt list` stdout
- **通用 code 搜尋（Greptile、Cursor @Codebase）**——懂 code 但不懂 dbt；漏 lineage 與 column 關係

`dbt-wiki` 補上這個缺口：**local-only**、**LLM 可查詢**、以**業務語意為主體**的 dbt 專案知識庫，從 dbt 已產出的 artifact 蒸餾（不打 warehouse、不需付費 Cloud）。知識層（`entities/` / `metrics/` / `concepts/`）讓分析師用業務語言理解資料；證據層（`_evidence/`）保存完整結構血緣做支撐。

## Skills

| Skill | 何時用 | 主要輸入 |
|---|---|---|
| [`/dbt-wiki:init`](skills/init/) | 每專案一次（重跑安全） | `target/manifest.json` + `target/compiled/**/*.sql`（sqlglot column lineage）+ `dbt/models/**/*.sql`（raw — SQL/jinja inline 註解） |
| [`/dbt-wiki:rescan`](skills/rescan/) | `dbt parse` / `compile` / `run` 後 model 有變（便宜、0 LLM） | 對 `manifest_sha` 做 diff，只更新變動證據頁；受影響的知識頁標 stale；保留 user-owned `## User Notes` 段 |
| [`/dbt-wiki:redistill`](skills/redistill/) | rescan 把知識頁標 stale 後，用 LLM 重新對齊語意（使用者觸發） | stale 的 entities/metrics/concepts 頁 + 其 `derived_from` 證據；按 domain 分組，跳過人工認證的 `mature` 頁 |
| [`/dbt-wiki:sync`](skills/sync/) | 「把 wiki 一次弄到最新」一個指令 | 先跑 `rescan`，若知識頁變 stale，再用明確 yes 把關 LLM `redistill` |
| [`/dbt-wiki:ingest`](skills/ingest/) | 想塞 manifest 或 schema.yml 沒有的 context（gotcha、設計理由、ticket 連結） | 自由文字 arg；自動依文中提到的 model / source / macro 名附上 |
| [`/dbt-wiki:query`](skills/query/) | 想問業務語意（「churn 是什麼意思」「哪些實體跟營收有關」）或 dbt 結構 / lineage / 欄位問題時 | 知識層頁（entities / metrics / concepts）+ 相關證據頁；自動偵測 drift |
| [`/dbt-wiki:pack`](skills/pack/) | 想把蒸餾好的知識庫**打包成可攜的 Agent Skill bundle**（`<project>-analytics/`）時。讓另一個 agent 用自己的連倉工具拿這個 bundle 來 grounding、生成、執行 SQL。由專案擁有者執行；emit 出來的 bundle 可放進任何支援 Skills 的 agent。 | frozen 的 `.dbt-wiki/` 知識層（entities / metrics / concepts + 欄位卡 + relationships + value domain）；emit 一個扁平 skill 資料夾（SKILL.md + knowledge/ + references/ + examples/）並附快照註記 |

## 快速上手

1. 從 [monkey-skills marketplace](https://github.com/kouko/monkey-skills) 安裝
2. 以下任一即可 — init 自動偵測：
   - **[uv](https://github.com/astral-sh/uv)**（**推薦** — 自動在 ephemeral env 裝 sqlglot，不污染你的 dbt env）：`brew install uv`（macOS）或 `curl -LsSf https://astral.sh/uv/install.sh | sh`（Linux/macOS）
   - **或** 在 dbt env 用 pip 裝 sqlglot：`pip install 'sqlglot>=25.0'`
3. 在 dbt 專案根目錄：
   ```bash
   dbt parse        # 產生 target/manifest.json
   dbt compile      # 產生 target/compiled/**/*.sql（jinja 已展開；sqlglot 需要這個）
   ```
4. 在 Claude Code：
   ```
   /dbt-wiki:init
   ```
5. 改完 dbt 後：
   ```bash
   dbt parse && dbt compile
   ```
   然後：
   ```
   /dbt-wiki:rescan
   ```
6. （選擇性）塞入 manifest.json / schema.yml 沒有的 tribal knowledge：
   ```
   /dbt-wiki:ingest "fct_orders sort_key 設 (order_date, customer_id) 是因為 Tableau extract join 在這兩欄——見 incident #4521"
   /dbt-wiki:ingest "marts_finance 跑 incremental 前要先 grant analytics_readonly_group 權限"
   ```
7. 問任何問題：
   ```
   /dbt-wiki:query "churn 是什麼意思？"                      # 語意問句 → 知識層 concepts/
   /dbt-wiki:query "哪些實體跟營收有關？"                    # 語意問句 → entities + relationships
   /dbt-wiki:query "MRR 怎麼計算？"                          # 語意問句 → metrics/
   /dbt-wiki:query "fct_orders 依賴什麼？"                   # 結構問句 → 證據層 lineage
   /dbt-wiki:query "rename stg_customers.email 會影響哪些 model？"
   /dbt-wiki:query "fct_orders sort key 為什麼這樣設？"      # 從 ingest 進來的 context 答
   ```

## `init` 產出

init 分兩階段：Phase A 機械建證據層，Phase B LLM 蒸餾知識層。

```
.dbt-wiki/
  SCHEMA.md              # frozen schema (請勿手動編輯)
  index.md               # 知識優先目錄：實體 / 指標 / 概念在前；結構分組降級至 Evidence 區
  log.md                 # append-only 操作記錄
  lineage.md             # 完整 DAG（ASCII tree + adjacency list，來自證據層）
  entities/              # 知識層：業務物件（Customer、Order 等）——LLM 蒸餾
  metrics/               # 知識層：業務指標（MRR、churn 等；MetricFlow 定義為優先輸入）
  concepts/              # 知識層：SQL 裡的橫切業務規則（「活躍客戶」定義、財年等）
  _evidence/
    models/<name>.md     # 每個 model 一份：frontmatter（materialization、欄位含 sqlglot sources、
                         #   depends_on、feeds_into、tests）+ body（description、SQL preview、
                         #   inline SQL/jinja 註解含行號、column chain、user notes）
    sources/<src>__<table>.md  # 每個宣告的 source 一份
    macros/<name>.md     # 每個被 ≥1 model 用的 macro
    seeds/, snapshots/, tests/, exposures/  # 其他 dbt resource
  syntheses/             # 已儲存的查詢結果（query 自動儲存血緣類問句）
  _internal/             # sqlglot 助手等內部腳本
  _archive/<date>/       # rescan 時 orphaned 的頁面（永不硬刪）
```

## 證據層：column-level lineage

知識層的支撐證據。dbt 的 `manifest.json` 給你 **model-level** lineage（`fct_orders` depends on `stg_orders`）但**不給 column-level**（`fct_orders.customer_id` 從 `stg_orders.customer_id` 來）。

證據層用 sqlglot parse `target/compiled/<project>/**/*.sql`（jinja 已被 `dbt compile` 展開）抽出 column-level lineage——這是知識層蒸餾的原料，也是結構問句的真實源：

```yaml
columns:
  - name: customer_id
    description: "FK to dim_customers"
    tests: [not_null]
    sources:
      - "stg_orders.customer_id"
      - "stg_customers.id"  # via COALESCE
```

這解鎖 dbt manifest 答不出的 query：
- `"fct_orders.customer_id 從哪來？"` → 順 compiled SQL 倒推
- `"rename stg_customers.email 會影響哪些 model 的哪些 column？"` → 跨 `columns[].sources` 反向走
- `"哪些 model 用了 ROW_NUMBER() OVER (...)？"` → sqlglot AST 掃
- `"schema.yml 漏寫的 column"` → diff sqlglot SELECT 列 vs schema.yml `columns:`

## 與 [`repo-wiki`](../repo-wiki/) 共存

兩個 plugin 同 repo 安裝會乾淨共存：

- **`.dbt-wiki/`** = **資料的語意意義**（WHAT the data means）——知識層（entities / metrics / concepts，LLM 蒸餾）+ 證據層（manifest + sqlglot 結構血緣）
- **`.repo-wiki/`** = **WHY**（決策、refactor 歷史、tribal knowledge——手動 ingest）

任意交叉連結：
```markdown
<!-- in .dbt-wiki/_evidence/models/fct_orders.md -->
WHY: see [.repo-wiki/sources/2026-04-29-revenue-forecast-...](../.repo-wiki/sources/...)

<!-- in .repo-wiki/entities/DbtModels.md -->
For current dependencies of fct_orders, see [fct_orders](.dbt-wiki/_evidence/models/fct_orders.md)
```

CLAUDE.md drop-in 用不同 marker（`<!-- dbt-wiki:start --> ... <!-- dbt-wiki:end -->` vs `<!-- repo-wiki:start --> ... <!-- repo-wiki:end -->`）兩者互不覆蓋。

## 為什麼不用其他工具

| 工具 | 缺點 |
|---|---|
| dbt Cloud Discovery API | 要付費訂閱 |
| dbt docs generate + serve | HTML、LLM 不能直接查 |
| dbt-mcp + 只開 CLI | LLM 解析 `dbt list` stdout，沒結構化 query |
| dbt-mcp + Discovery | 要 dbt Cloud（付費） |
| dbt-osmosis / dbt-coves | 是 codegen，不是 query |
| 直接讀 manifest.json | 1-50MB；沒 query 介面；沒 column lineage |
| repo-wiki | WHY-first；不做 per-model WHAT 或 column lineage |
| 通用 code 搜尋 | 懂 code 不懂 dbt |

`dbt-wiki` 的獨特組合：**local-only + LLM 蒸餾語意知識 + manifest.json 結構化血緣 + sqlglot column lineage + LLM 可查詢語意／結構問句 + 零 warehouse 呼叫 + 在 Claude Code 用（不只 Desktop）**。

## 雙層架構

```
知識層（主體，LLM 蒸餾）
  entities/     業務物件——Customer、Order、Subscription 等
  metrics/      業務指標——MRR、churn、LTV 等；MetricFlow 定義為優先輸入
  concepts/     橫切業務規則——「活躍客戶」定義、財年、狀態列舉等

  各頁以帶類型的 ## Relationships 邊連結（depends_on / measures / applies_to 等）
  → 形成輕量 ontology / 知識圖譜

證據層（支撐，機械萃取）
  _evidence/    manifest + sqlglot 萃取的 model / source / macro 結構血緣頁
                是知識層的原料與引用對象；rescan 後若有變動則標知識頁 stale
```

知識層是 v2.0 的主體：讓分析師用業務語言理解資料，不必先逆向讀 SQL。
證據層保留完整機械血緣（v1.x 核心價值），降級至 `_evidence/` 作為支撐。

## 設計原則

1. **知識為主體，結構為證據**——分析師用業務語言（entities / metrics / concepts）查知識層；結構血緣是知識層的腳註
2. **manifest.json + compiled SQL 是真實源**——不重做 dbt 已 parse 的事
3. **永遠 parse `compiled/*.sql` 不 parse `raw_code`**——jinja 必須先被 dbt 展開
4. **Local-only**——無 Cloud、無 warehouse 呼叫
5. **Rescan idempotent**——對 `manifest_sha` diff，只更新改動的證據頁；受影響的知識頁標 stale
6. **Archive 不刪**——orphaned 頁面進 `.dbt-wiki/_archive/<date>/`
7. **Drift-aware query**——query 對 `manifest_sha` 對照當下；過期會警告
8. **與 repo-wiki 共存**——WHAT the data means 在這、WHY 在那；自由交叉連結

## 前置條件

- **dbt 專案**：你 dbt installation 支援的版本（建議 manifest.json schema v9+）
- 跑 `init` / `rescan` 前必須先 `dbt parse && dbt compile`
- **Python 3.10+** 加上以下任一：
  - [uv](https://github.com/astral-sh/uv)（推薦——script 用 PEP 723 inline metadata 自帶宣告 sqlglot，uv 自動在 ephemeral env 安裝），或
  - 在現用 Python env pip 裝 sqlglot（`pip install 'sqlglot>=25.0'`）
- **Dialect 支援**：sqlglot 支援 redshift / postgres / snowflake / bigquery / databricks / clickhouse / duckdb / mysql / oracle / spark / sqlite / tsql——從 `dbt_project.yml` profile 自動偵測

## Schema（v2.0）

`.dbt-wiki/SCHEMA.md` 定義雙層架構的頁型、frontmatter shape、命名規則，**frozen for v2.x**。v2.0 是對 v1.x 的破壞性變更（clean break，不寫 migration）——v1.x `.dbt-wiki/` 需重建，若含 User Notes 系統會印一次警告建議先備份。

## Fast-follow backlog（v2.x+）

- `sync` 的 materiality triage（Phase 2）——純註解 / description 的 cosmetic 變更自動跳過 redistill 把關，只有實質證據變更才提示重蒸
- `ingest` 寫入知識層頁面
- `domains/` 維度（主題領域 landscape）
- `catalog.json` 整合（真實 warehouse column type、row count）——opt-in
- `run_results.json` 整合（test pass/fail、last-run 時間）
- Dialect 邊角案例（Redshift late-binding view、Snowflake 特殊 function）
- 跨專案 lineage（`packages.yml` 拉的 dbt-utils 等，追進它們的 macro）
- `/dbt-wiki:diff <ref>`——比較 DAG 在不同 git ref（refactor review）
- 替代 parser（sqlfluff、dbt-column-lineage adapter）當 sqlglot fail

## 靈感與致謝

- [dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core)——manifest.json schema 是 canonical 結構化真實
- [tobymao/sqlglot](https://github.com/tobymao/sqlglot)——沒它 column-lineage 抽取做不到
- [`repo-wiki`](../repo-wiki/)——姊妹 plugin；SKILL.md / SCHEMA.md / log.md 慣例沿用
