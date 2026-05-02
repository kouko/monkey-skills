# dbt-wiki

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Local-only な LLM クエリ可能 dbt プロジェクトナレッジベース。Init は `target/manifest.json`（model metadata、ref/source lineage、schema.yml カラム、tests）+ `target/compiled/**/*.sql`（[sqlglot](https://github.com/tobymao/sqlglot) で column-level lineage 抽出）を読む。各 model / source / macro が `.dbt-wiki/` 配下の markdown 1 ファイルに。Query は自然言語で model 構造、カラムデータフロー、materialization 設定、test カバレッジ、リファクタ影響を聞ける——**dbt Cloud 不要、マシンを離れない**。

**Version**: 1.0.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## 背景

dbt はファーストパーティで `dbt docs generate`（静的 HTML サイト）を持ち、エコシステムには有料ツール（dbt Cloud Discovery API、サードパーティ lineage プラットフォーム）も多数。しかし**会話型 LLM で dbt プロジェクト構造を聞く**という niche は空いている：

- **dbt Cloud Discovery API** — メタデータはあるが有料サブスクリプション必要
- **dbt docs serve** — 人が見る HTML、LLM 直接クエリ不可
- **`target/manifest.json`** — 構造化された真実だが 1-50MB、クエリインターフェイスなし
- **dbt-mcp Discovery 無効化** — CLI ツールのみ露出、LLM が `dbt list` の stdout を自前パース
- **汎用コード検索（Greptile、Cursor @Codebase）** — コードに詳しいが dbt に無頓着、lineage と column 関係を取りこぼす

`dbt-wiki` がこのギャップを埋める：**local-only**、**LLM クエリ可能**、**column lineage 内蔵**の dbt プロジェクトスナップショット、dbt が既に生成する artifact から派生（warehouse 呼ばない、有料 Cloud 不要）。

## Skills

| Skill | いつ | 主入力 |
|---|---|---|
| [`/dbt-wiki:init`](skills/init/) | プロジェクトごとに 1 回（再実行安全） | `target/manifest.json` + `target/compiled/**/*.sql`（sqlglot column lineage）+ `dbt/models/**/*.sql`（raw — SQL/jinja インラインコメント） |
| [`/dbt-wiki:refresh`](skills/refresh/) | `dbt parse` / `compile` / `run` 後 model に変更 | `manifest_sha` で diff、変更ページのみ更新；user-owned `## User Notes` セクションは保持 |
| [`/dbt-wiki:ingest`](skills/ingest/) | manifest や schema.yml にない context（gotcha、設計理由、ticket 参照）を入れたいとき | 自由形式 text 引数；本文中の model / source / macro 名に自動添付 |
| [`/dbt-wiki:query`](skills/query/) | dbt model 構造 / lineage / カラム / 暗黙知について聞きたいとき | `.dbt-wiki/index.md` + 関連 model ページ；drift 自動検知 |

## クイックスタート

1. [monkey-skills marketplace](https://github.com/kouko/monkey-skills) からインストール
2. dbt env で sqlglot をインストール：`pip install sqlglot`
3. dbt プロジェクトルートで：
   ```bash
   dbt parse        # target/manifest.json を生成
   dbt compile      # target/compiled/**/*.sql を生成（jinja 展開済；sqlglot がこれを必要とする）
   ```
4. Claude Code で：
   ```
   /dbt-wiki:init
   ```
5. dbt を変更したら：
   ```bash
   dbt parse && dbt compile
   ```
   それから：
   ```
   /dbt-wiki:refresh
   ```
6. （任意）manifest.json / schema.yml にない暗黙知を投入：
   ```
   /dbt-wiki:ingest "fct_orders の sort_key (order_date, customer_id) は Tableau extract がこの 2 列で join するため — incident #4521 参照"
   /dbt-wiki:ingest "marts_msd は incremental 実行前に prod_marts_readonly_group 権限付与が必要"
   ```
7. 何でも聞く：
   ```
   /dbt-wiki:query "fct_orders は何に依存している？"
   /dbt-wiki:query "stg_customers.email を rename したらどの model に影響？"
   /dbt-wiki:query "marts_msd 配下で incremental なのは？"
   /dbt-wiki:query "fct_orders の sort key の理由は？"      # ingest した context から答える
   ```

## `init` の出力

```
.dbt-wiki/
  SCHEMA.md              # frozen schema (手動編集禁止)
  index.md               # カタログ：tier / materialization / tag / group ごと
  log.md                 # append-only オペレーションログ
  lineage.md             # 完全 DAG (ASCII tree + adjacency list)
  models/<name>.md       # model 1 件 1 ファイル：frontmatter (materialization、sqlglot 抽出 sources 付き
                         #   columns、depends_on、feeds_into、tests) + body (description、SQL preview、
                         #   インライン SQL/jinja コメント (行番号付き)、column chain、user notes)
  sources/<src>__<table>.md  # 宣言された source 1 件 1 ファイル
  macros/<name>.md       # ≥1 model に使われた macro
  seeds/, snapshots/, tests/, exposures/   # その他 dbt resource
  _internal/extract_column_lineage.py      # sqlglot ヘルパー (init が plugin からコピー)
  _internal/extract_sql_comments.py        # SQL/jinja コメント抽出 (regex)
  _archive/<date>/       # refresh で orphan になった model（ハード削除しない）
```

## Column-level lineage（最大の差別化）

dbt の `manifest.json` は **model-level** lineage（`fct_orders` depends on `stg_orders`）は提供するが、**column-level**（`fct_orders.customer_id` は `stg_orders.customer_id` から来る）は提供しない。

dbt-wiki は sqlglot で `target/compiled/<project>/**/*.sql`（jinja は `dbt compile` が展開済）をパースして column-level lineage を抽出：

```yaml
columns:
  - name: customer_id
    description: "FK to dim_customers"
    tests: [not_null]
    sources:
      - "stg_orders.customer_id"
      - "stg_customers.id"  # via COALESCE
```

これにより dbt manifest だけでは答えられないクエリが可能に：
- `"fct_orders.customer_id はどこから？"` → compiled SQL を遡る
- `"stg_customers.email を rename したらどの model のどの column に影響？"` → `columns[].sources` 逆向き走査
- `"ROW_NUMBER() OVER (...) を使っている model は？"` → sqlglot AST スキャン
- `"schema.yml が抜けている column"` → sqlglot SELECT 列 vs schema.yml `columns:` の差分

## [`repo-wiki`](../repo-wiki/) との共存

両プラグインが同じ repo にインストールされていても綺麗に共存：

- **`.dbt-wiki/`** = STRUCTURE + COLUMN LINEAGE（manifest + sqlglot から自動派生）
- **`.repo-wiki/`** = WHY（決定、リファクタ履歴、tribal knowledge — 手動 ingest）

自由にクロスリンク：
```markdown
<!-- in .dbt-wiki/models/fct_orders.md -->
WHY: see [.repo-wiki/sources/2026-04-29-fsd-management-report-...](../.repo-wiki/sources/...)

<!-- in .repo-wiki/entities/DbtModels.md -->
For current dependencies of fct_orders, see [fct_orders](.dbt-wiki/models/fct_orders.md)
```

CLAUDE.md ドロップインは別マーカー（`<!-- dbt-wiki:start --> ... <!-- dbt-wiki:end -->` vs `<!-- repo-wiki:start --> ... <!-- repo-wiki:end -->`）でお互いを上書きしない。

## なぜ他のツールではダメか

| ツール | ギャップ |
|---|---|
| dbt Cloud Discovery API | 有料サブスクリプション必須 |
| dbt docs generate + serve | HTML、LLM クエリ不可 |
| dbt-mcp + CLI のみ | LLM が `dbt list` stdout をパース、構造化クエリなし |
| dbt-mcp + Discovery | dbt Cloud（有料）必須 |
| dbt-osmosis / dbt-coves | コード生成、クエリではない |
| manifest.json 直読み | 1-50MB、クエリインターフェイスなし、column lineage なし |
| repo-wiki | WHY-first；per-model WHAT や column lineage しない |
| 汎用コード検索 | コード理解、dbt 理解なし |

`dbt-wiki` の独自組み合わせ：**local-only + manifest.json 構造化真実 + sqlglot column lineage + LLM クエリ可能 + warehouse コール 0 + Claude Code で動く（Desktop のみではない）**。

## 設計原則

1. **manifest.json + compiled SQL が真実の源** — dbt が既に parse したものを再派生しない
2. **常に `compiled/*.sql` をパース、`raw_code` ではない** — jinja は dbt が先に展開する
3. **Local-only** — Cloud なし、warehouse コールなし（catalog.json は v2 backlog）
4. **Refresh は idempotent** — `manifest_sha` を diff、変更ページのみ更新
5. **Archive、削除しない** — orphan model は `.dbt-wiki/_archive/<date>/` へ
6. **Drift-aware query** — query は `manifest_sha` を現在と照合、古ければ警告
7. **repo-wiki と共存** — STRUCTURE はこちら、WHY はあちら、自由クロスリンク

## 前提条件

- **dbt プロジェクト**：あなたの dbt インストールでサポートされるバージョン（manifest.json schema v9+ 推奨）
- `init` / `refresh` 実行前に `dbt parse && dbt compile` 必須
- **Python 3.x** + **sqlglot**（`pip install sqlglot`）— column lineage 抽出用
- **Dialect サポート**：sqlglot は redshift / postgres / snowflake / bigquery / databricks / clickhouse / duckdb / mysql / oracle / spark / sqlite / tsql をサポート — `dbt_project.yml` profile から自動検出

## Schema は v2.0 まで凍結

`.dbt-wiki/SCHEMA.md` のページタイプ、frontmatter 構造、命名規則は v1.x の間は変更しない。重大 schema 変更は migration script 付きで v2.0 で出す。

## v2 backlog

- `catalog.json` 統合（実 warehouse column type、row count） — opt-in Phase 2
- `run_results.json` 統合（test pass/fail、last-run 時間）
- Dialect エッジケース（Redshift late-binding view、Snowflake 特殊関数）
- クロスプロジェクト lineage（`packages.yml` の dbt-utils 等、その macro まで追跡）
- `/dbt-wiki:diff <ref>` — git ref 間の DAG 比較（リファクタレビュー）
- 代替パーサー（sqlfluff、dbt-column-lineage adapter）— sqlglot 失敗時

## インスピレーション & クレジット

- [dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core) — manifest.json schema が canonical 構造化真実
- [tobymao/sqlglot](https://github.com/tobymao/sqlglot) — これなしでは column-lineage 抽出が成り立たない
- [`repo-wiki`](../repo-wiki/) — 姉妹プラグイン；SKILL.md / SCHEMA.md / log.md の慣例を流用
