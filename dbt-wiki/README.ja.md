# dbt-wiki

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> dbt プロジェクトが扱うデータを**業務言語で理解・分析**するための、Local-only な LLM クエリ可能ナレッジベース。**二層構造**：①**知識層**（LLM 蒸餾）— `entities/`（業務オブジェクト）、`metrics/`（業務指標）、`concepts/`（横断的なビジネスルール）；②**証拠層**（機械的、`_evidence/` 配下）— manifest.json + [sqlglot](https://github.com/tobymao/sqlglot) による構造・カラムリネージのページ。Query は「churn とは何か」「売上に関連するエンティティは」といった**意味的な問い**と従来の構造リネージ問い合わせの両方に回答——**dbt Cloud 不要、マシンを離れない**。

**Version**: 1.0.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## 背景

dbt はファーストパーティで `dbt docs generate`（静的 HTML サイト）を持ち、エコシステムには有料ツール（dbt Cloud Discovery API、サードパーティ lineage プラットフォーム）も多数。しかし**会話型 LLM で dbt プロジェクト構造を聞く**という niche は空いている：

- **dbt Cloud Discovery API** — メタデータはあるが有料サブスクリプション必要
- **dbt docs serve** — 人が見る HTML、LLM 直接クエリ不可
- **`target/manifest.json`** — 構造化された真実だが 1-50MB、クエリインターフェイスなし
- **dbt-mcp Discovery 無効化** — CLI ツールのみ露出、LLM が `dbt list` の stdout を自前パース
- **汎用コード検索（Greptile、Cursor @Codebase）** — コードに詳しいが dbt に無頓着、lineage と column 関係を取りこぼす

`dbt-wiki` がこのギャップを埋める：**local-only**、**LLM クエリ可能**、**知識主体**の dbt ナレッジベース。知識層（entities / metrics / concepts）でデータを業務言語で理解し、証拠層（manifest + sqlglot column lineage）がそれを支える——dbt が既に生成する artifact から派生（warehouse 呼ばない、有料 Cloud 不要）。

## Skills

| Skill | いつ | 主入力 |
|---|---|---|
| [`/dbt-wiki:init`](skills/init/) | プロジェクトごとに 1 回（再実行安全） | `target/manifest.json` + `target/compiled/**/*.sql`（sqlglot column lineage）+ `dbt/models/**/*.sql`（raw — SQL/jinja インラインコメント） |
| [`/dbt-wiki:refresh`](skills/refresh/) | `dbt parse` / `compile` / `run` 後 model に変更 | `manifest_sha` で diff、変更ページのみ更新；user-owned `## User Notes` セクションは保持 |
| [`/dbt-wiki:ingest`](skills/ingest/) | manifest や schema.yml にない context（gotcha、設計理由、ticket 参照）を入れたいとき | 自由形式 text 引数；本文中の model / source / macro 名に自動添付 |
| [`/dbt-wiki:query`](skills/query/) | 業務概念（「churn とは」「売上に関連するエンティティは」）や model 構造 / lineage / カラムについて聞きたいとき | `.dbt-wiki/index.md` + 関連知識ページ・証拠ページ；drift 自動検知 |

## クイックスタート

1. [monkey-skills marketplace](https://github.com/kouko/monkey-skills) からインストール
2. 以下のいずれか — init が自動検出：
   - **[uv](https://github.com/astral-sh/uv)**（**推奨** — ephemeral env に sqlglot を自動インストール、dbt env を汚さない）：`brew install uv`（macOS）または `curl -LsSf https://astral.sh/uv/install.sh | sh`（Linux/macOS）
   - **または** dbt env に pip で sqlglot：`pip install 'sqlglot>=25.0'`
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
   # 意味的な問い（知識層）
   /dbt-wiki:query "churn とは何か？"
   /dbt-wiki:query "売上に関連するエンティティは？"
   /dbt-wiki:query "MRR はどう計算されている？"

   # 構造・リネージの問い（証拠層）
   /dbt-wiki:query "fct_orders は何に依存している？"
   /dbt-wiki:query "stg_customers.email を rename したらどの model に影響？"
   /dbt-wiki:query "marts_msd 配下で incremental なのは？"
   /dbt-wiki:query "fct_orders の sort key の理由は？"      # ingest した context から答える
   ```

## `init` の出力

```
.dbt-wiki/
  SCHEMA.md              # frozen schema (手動編集禁止)
  index.md               # 知識優先カタログ：entities / metrics / concepts 先頭、構造分類は証拠セクションへ
  log.md                 # append-only オペレーションログ
  lineage.md             # 完全 DAG (ASCII tree + adjacency list、証拠層から生成)
  entities/<name>.md     # 知識層：業務オブジェクト（Customer, Order など）LLM 蒸餾
  metrics/<name>.md      # 知識層：業務指標（MRR, churn など）— MetricFlow あれば取り込む
  concepts/<name>.md     # 知識層：横断的なビジネスルール（「活躍顧客＝90日以内購買」など）
  _evidence/
    models/<name>.md     # 証拠層：model 1 件 1 ファイル（manifest + sqlglot column lineage）
    sources/<src>__<table>.md  # 証拠層：宣言された source
    macros/<name>.md     # 証拠層：≥1 model に使われた macro
    seeds/, snapshots/, tests/, exposures/
  syntheses/             # query が保存した回答（lineage クラス）
  _internal/             # sqlglot ヘルパースクリプト (init が plugin からコピー)
  _archive/<date>/       # refresh で orphan になったページ（ハード削除しない）
```

## Column-level lineage（証拠層の核心）

dbt の `manifest.json` は **model-level** lineage（`fct_orders` depends on `stg_orders`）は提供するが、**column-level**（`fct_orders.customer_id` は `stg_orders.customer_id` から来る）は提供しない。この column-level lineage が証拠層の核心であり、LLM が knowledge entities / metrics / concepts を蒸餾する際の最も重要な原材料になる。

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

- **`.dbt-wiki/`** = **データが何を意味するか**（entities / metrics / concepts の知識層 + manifest・sqlglot の証拠層）
- **`.repo-wiki/`** = **WHY**（決定、リファクタ履歴、tribal knowledge — 手動 ingest）

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

`dbt-wiki` の独自組み合わせ：**local-only + 知識層（entities/metrics/concepts、LLM 蒸餾）+ 証拠層（manifest.json + sqlglot column lineage）+ 意味的・構造的クエリ両対応 + warehouse コール 0 + Claude Code で動く（Desktop のみではない）**。

## 設計原則

1. **知識層が主役、証拠層が脚注** — entities / metrics / concepts で業務意味を表現し、manifest + sqlglot の構造血緣がそれを裏付ける
2. **manifest.json + compiled SQL が真実の源** — dbt が既に parse したものを再派生しない
3. **常に `compiled/*.sql` をパース、`raw_code` ではない** — jinja は dbt が先に展開する
4. **Local-only** — Cloud なし、warehouse コールなし
5. **Refresh は idempotent** — `manifest_sha` を diff、証拠層の変更ページのみ更新；影響する知識ページを stale フラグ
6. **Archive、削除しない** — orphan ページは `.dbt-wiki/_archive/<date>/` へ
7. **Drift-aware query** — query は `manifest_sha` を現在と照合、古ければ警告
8. **repo-wiki と共存** — データの意味（知識・証拠）はこちら、WHY（決定・歴史）はあちら、自由クロスリンク

## 前提条件

- **dbt プロジェクト**：あなたの dbt インストールでサポートされるバージョン（manifest.json schema v9+ 推奨）
- `init` / `refresh` 実行前に `dbt parse && dbt compile` 必須
- **Python 3.10+** および以下のいずれか：
  - [uv](https://github.com/astral-sh/uv)（推奨 — script が PEP 723 インラインメタデータで sqlglot を宣言、uv が ephemeral env に自動インストール）、または
  - 現在の Python env に pip で sqlglot（`pip install 'sqlglot>=25.0'`）
- **Dialect サポート**：sqlglot は redshift / postgres / snowflake / bigquery / databricks / clickhouse / duckdb / mysql / oracle / spark / sqlite / tsql をサポート — `dbt_project.yml` profile から自動検出

## v2.0 は破壊的変更（クリーンビルド）

dbt-wiki **v2.0** は v1.x からの破壊的再設計であり、migration script はない。v1.x の `.dbt-wiki/` は移行されない——`/dbt-wiki:init` で再構築する（User Notes があれば事前バックアップ推奨）。`.dbt-wiki/SCHEMA.md` のページタイプ・frontmatter 構造・命名規則は v2.x の間は変更しない。重大 schema 変更は v3.0 で出す。

## fast-follow（v2.x）

- **refresh 自動再蒸餾** — manifest diff で変更された証拠ページから、関連する知識ページを自動 re-distill（MVP は stale フラグのみ）
- **`domains/` 次元** — entities / metrics / concepts を束ねる主題領域ランドスケープ（finance / marketing / product）
- **ingest → 知識ページ** — `/dbt-wiki:ingest` でコンテキストを知識ページにも記録
- `catalog.json` 統合（実 warehouse column type、row count） — opt-in
- `run_results.json` 統合（test pass/fail、last-run 時間）
- Dialect エッジケース（Redshift late-binding view、Snowflake 特殊関数）
- クロスプロジェクト lineage（`packages.yml` の dbt-utils 等）
- `/dbt-wiki:diff <ref>` — git ref 間の DAG 比較
- 代替パーサー（sqlfluff、dbt-column-lineage adapter）— sqlglot 失敗時

## インスピレーション & クレジット

- [dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core) — manifest.json schema が canonical 構造化真実
- [tobymao/sqlglot](https://github.com/tobymao/sqlglot) — これなしでは column-lineage 抽出が成り立たない
- [`repo-wiki`](../repo-wiki/) — 姉妹プラグイン；SKILL.md / SCHEMA.md / log.md の慣例を流用
