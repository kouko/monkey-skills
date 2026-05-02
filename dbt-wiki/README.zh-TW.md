# dbt-wiki

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Local-only LLM 可查詢的 dbt 專案知識庫。Init 讀 `target/manifest.json`（model metadata、ref/source lineage、schema.yml 欄位、tests）+ `target/compiled/**/*.sql`（用 [sqlglot](https://github.com/tobymao/sqlglot) 抽 column-level lineage）。每個 model / source / macro 各成一份 markdown 在 `.dbt-wiki/`。Query 用自然語言問 model 結構、欄位資料流、materialization 設定、test 覆蓋、refactor 影響——**不需 dbt Cloud、不離開機器**。

**Version**: 1.0.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## 背景

dbt 第一方有 `dbt docs generate`（靜態 HTML 網站），生態裡也有付費工具（dbt Cloud Discovery API、第三方 lineage 平台）。但**對話式 LLM 查 dbt 專案結構**這個 niche 是空的：

- **dbt Cloud Discovery API**——有 metadata，但要付費訂閱
- **dbt docs serve**——HTML 給人看，LLM 沒法直接查
- **`target/manifest.json`**——結構化真實，但 1-50MB；沒 query 介面
- **dbt-mcp 不開 Discovery**——只露 CLI 工具；LLM 要自己解析 `dbt list` stdout
- **通用 code 搜尋（Greptile、Cursor @Codebase）**——懂 code 但不懂 dbt；漏 lineage 與 column 關係

`dbt-wiki` 補上這個缺口：**local-only**、**LLM 可查詢**、**含 column lineage** 的 dbt 專案 snapshot，從 dbt 已產出的 artifact 衍生（不打 warehouse、不需付費 Cloud）。

## Skills

| Skill | 何時用 | 主要輸入 |
|---|---|---|
| [`/dbt-wiki:init`](skills/init/) | 每專案一次（重跑安全） | `target/manifest.json` + `target/compiled/**/*.sql`（sqlglot column lineage）+ `dbt/models/**/*.sql`（raw — SQL/jinja inline 註解） |
| [`/dbt-wiki:refresh`](skills/refresh/) | `dbt parse` / `compile` / `run` 後 model 有變 | 對 `manifest_sha` 做 diff，只更新改動的 page；保留 user-owned `## User Notes` 段 |
| [`/dbt-wiki:ingest`](skills/ingest/) | 想塞 manifest 或 schema.yml 沒有的 context（gotcha、設計理由、ticket 連結） | 自由文字 arg；自動依文中提到的 model / source / macro 名附上 |
| [`/dbt-wiki:query`](skills/query/) | 想問 dbt model 結構 / lineage / 欄位 / tribal knowledge 時 | `.dbt-wiki/index.md` + 相關 model page；自動偵測 drift |

## 快速上手

1. 從 [monkey-skills marketplace](https://github.com/kouko/monkey-skills) 安裝
2. 在你的 dbt env 安裝 sqlglot：`pip install sqlglot`
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
   /dbt-wiki:refresh
   ```
6. （選擇性）塞入 manifest.json / schema.yml 沒有的 tribal knowledge：
   ```
   /dbt-wiki:ingest "fct_orders sort_key 設 (order_date, customer_id) 是因為 Tableau extract join 在這兩欄——見 incident #4521"
   /dbt-wiki:ingest "marts_msd 跑 incremental 前要先 grant prod_marts_readonly_group 權限"
   ```
7. 問任何問題：
   ```
   /dbt-wiki:query "fct_orders 依賴什麼？"
   /dbt-wiki:query "rename stg_customers.email 會影響哪些 model？"
   /dbt-wiki:query "marts_msd 下哪些是 incremental？"
   /dbt-wiki:query "fct_orders sort key 為什麼這樣設？"      # 從 ingest 進來的 context 答
   ```

## `init` 產出

```
.dbt-wiki/
  SCHEMA.md              # frozen schema (請勿手動編輯)
  index.md               # 目錄：依 tier / materialization / tag / group 分組
  log.md                 # append-only 操作記錄
  lineage.md             # 完整 DAG (ASCII tree + adjacency list)
  models/<name>.md       # 每個 model 一份：frontmatter (materialization、欄位含 sqlglot 抽出的 sources、
                         #   depends_on、feeds_into、tests) + body (description、SQL preview、
                         #   inline SQL/jinja 註解含行號、column chain、user notes)
  sources/<src>__<table>.md  # 每個宣告的 source 一份
  macros/<name>.md       # 每個被 ≥1 model 用的 macro
  seeds/, snapshots/, tests/, exposures/   # 其他 dbt resource
  _internal/extract_column_lineage.py      # sqlglot 助手 (init 從 plugin 複製過來)
  _internal/extract_sql_comments.py        # SQL/jinja 註解抽取 (regex)
  _archive/<date>/       # refresh 時 orphaned 的 model（永不硬刪）
```

## Column-level lineage（最大差異化）

dbt 的 `manifest.json` 給你 **model-level** lineage（`fct_orders` depends on `stg_orders`）但**不給 column-level**（`fct_orders.customer_id` 從 `stg_orders.customer_id` 來）。

dbt-wiki 用 sqlglot parse `target/compiled/<project>/**/*.sql`（jinja 已被 `dbt compile` 展開）抽出 column-level lineage：

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

- **`.dbt-wiki/`** = STRUCTURE + COLUMN LINEAGE（從 manifest + sqlglot 自動衍生）
- **`.repo-wiki/`** = WHY（決策、refactor 歷史、tribal knowledge——手動 ingest）

任意交叉連結：
```markdown
<!-- in .dbt-wiki/models/fct_orders.md -->
WHY: see [.repo-wiki/sources/2026-04-29-fsd-management-report-...](../.repo-wiki/sources/...)

<!-- in .repo-wiki/entities/DbtModels.md -->
For current dependencies of fct_orders, see [fct_orders](.dbt-wiki/models/fct_orders.md)
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

`dbt-wiki` 的獨特組合：**local-only + manifest.json 結構化真實 + sqlglot column lineage + LLM 可查詢 + 零 warehouse 呼叫 + 在 Claude Code 用（不只 Desktop）**。

## 設計原則

1. **manifest.json + compiled SQL 是真實源**——不重做 dbt 已 parse 的事
2. **永遠 parse `compiled/*.sql` 不 parse `raw_code`**——jinja 必須先被 dbt 展開
3. **Local-only**——無 Cloud、無 warehouse 呼叫（catalog.json 是 v2 backlog）
4. **Refresh idempotent**——對 `manifest_sha` diff，只更新改動的 page
5. **Archive 不刪**——orphaned model 進 `.dbt-wiki/_archive/<date>/`
6. **Drift-aware query**——query 對 `manifest_sha` 對照當下；過期會警告
7. **與 repo-wiki 共存**——STRUCTURE 在這、WHY 在那；自由交叉連結

## 前置條件

- **dbt 專案**：你 dbt installation 支援的版本（建議 manifest.json schema v9+）
- 跑 `init` / `refresh` 前必須先 `dbt parse && dbt compile`
- **Python 3.x** + **sqlglot**（`pip install sqlglot`）——column lineage 抽取
- **Dialect 支援**：sqlglot 支援 redshift / postgres / snowflake / bigquery / databricks / clickhouse / duckdb / mysql / oracle / spark / sqlite / tsql——從 `dbt_project.yml` profile 自動偵測

## Schema 在 v2.0 之前 freeze

`.dbt-wiki/SCHEMA.md` 的 page type、frontmatter shape、命名規則在 v1.x **不會改**。重大 schema 改動配 migration script 一起在 v2.0 出。

## v2 backlog

- `catalog.json` 整合（真實 warehouse column type、row count）——opt-in Phase 2
- `run_results.json` 整合（test pass/fail、last-run 時間）
- Dialect 邊角案例（Redshift late-binding view、Snowflake 特殊 function）
- 跨專案 lineage（`packages.yml` 拉的 dbt-utils 等，追進它們的 macro）
- `/dbt-wiki:diff <ref>`——比較 DAG 在不同 git ref（refactor review）
- 替代 parser（sqlfluff、dbt-column-lineage adapter）當 sqlglot fail

## 靈感與致謝

- [dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core)——manifest.json schema 是 canonical 結構化真實
- [tobymao/sqlglot](https://github.com/tobymao/sqlglot)——沒它 column-lineage 抽取做不到
- [`repo-wiki`](../repo-wiki/)——姊妹 plugin；SKILL.md / SCHEMA.md / log.md 慣例沿用
