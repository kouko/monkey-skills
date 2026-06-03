---
name: dbt-model-style
description: >-
  Enforces a dbt + Redshift model **writing-style & structure** contract — CTE
  roles, the zero-logic `final` CTE, naming, the two-block YAML header, column
  comments/tags, and Redshift syntax. Use when authoring, editing, or reviewing
  a dbt model (`.sql`), or when asked whether one 「符合規範嗎」. Adoptable
  template: project-specific items are tagged `(adapt)`; model comments &
  frontmatter values stay in the user's working language. Do NOT use for
  calculation logic, business rules, metric formulas, or layer-dependency design
  — style & structure ONLY. dbt 撰寫風格・CTE 結構・命名・註解・排版。dbt
  スタイル・命名規則。
---

# dbt Model Style

## Purpose & scope

An adoptable dbt + Redshift **model writing-style template**: once a team adopts it, every model anyone (or an agent) writes looks consistent, reads well, maintains easily, and parses cleanly for tooling. **This is an opinionated default, not the only right answer** — items tagged `(adapt)` (naming vocabulary, header schema, warehouse-persistence mechanism) are tuned per project; the remaining MUST/SHOULD rules are cross-project dbt good habits.

**When it applies**: whenever you author / edit / review **any** dbt model. **Write comment text and frontmatter *values* in the user's working language** (the examples in this doc stay in Chinese as a demonstration).

**Style & structure only — not computation.** This skill covers how CTEs are arranged, how columns are named, how comments are written, how JOINs are declared. It does **not** cover calculation logic, business rules, metric formulas, NULL/denominator semantics, or layer-dependency design — those are a separate matter, out of scope here.

**When a request mixes style and logic** (common — e.g. "fix the source-A→B fallback *and* tidy the `final` CTE"): do the **style/structure** part under this skill; for the **calculation/business-rule** part, name it explicitly and hand it back as out of scope — don't silently change computation, and don't refuse the whole request. Split the edit; don't let "I'm already in here" pull you across the boundary.

**One boundary that genuinely blurs — name-vs-content.** A few style rules can only be *checked* by glancing at the computation: the variant-suffix naming MUST (§3) says a `__paid` column must not smuggle in trial rows, so confirming the **name matches what the column computes** requires reading the logic. That read-to-verify-the-name is in scope; **changing** the computation to fix a mismatch is not — flag the mismatch and hand the logic fix back.

Rules come in four levels:

| Level | Meaning |
|---|---|
| **MUST** | Hard rule; violating it is non-conforming |
| **SHOULD** | Strongly recommended; do it when you can |
| **MAY** | Situational preference; fall back when you can't |
| **(adapt)** | Opinionated default; tune per project (naming vocabulary, header schema, warehouse-persistence mechanism, etc.) |

> The one MUST to remember: **the `final` CTE has zero logic — column selection + comments only.** Every other MUST is structural discipline that keeps a model traceable and machine-parseable.

---

## Scope of enforcement (read first — don't run wild)

This template applies to **newly created models and the model you're currently editing** — whichever you touch, bring it up to standard.

- **Do not proactively mass-backfill / rewrite existing models just to satisfy this guide.** That's pure churn and risk; don't do it unless the user explicitly asks.
- When editing an existing model, use the **boy-scout rule (bounded)**: bring the **part you touch** (that CTE, those few columns, the header) up to standard — don't rewrite the whole file on the way.
- An existing model that doesn't match this guide but you aren't touching this time → **leave it; it's not a bug.**
- A large-scale rollout is a **separate, explicitly-authorized task**, not a side effect of writing a model.

---

## The whole picture: what a model looks like + writing order

First the overall skeleton (condensed; details in the sections below):

```sql
/* ---                                          ← header ①: YAML frontmatter (reaches the table comment)  §5.1
title:   ... / summary: ... / grain: ...              all layers
purpose: ... / keys: {...}                            consumer layers
sources: [...] / related: [...] / refresh: ...
---
<1–3 sentence unstructured narrative — context the frontmatter can't express>
*/

/* business rules / mapping (header ②: human-facing, not in the comment) */                       §5.2

{% if target.type=='redshift' %}                 ← config (only when a table)                       §7
{{ config(materialized='table', sort=[...], tags=[...]) }}
{% endif %}

WITH SOURCE_MODEL AS (                            ← reference CTE: UPPERCASE, prefix dropped, SELECT *  §1.1
    SELECT * FROM {{ ref('int_...') }}
),
transformed AS (                                  ← intermediate CTE: lowercase, one concern, all logic here  §1.1
    SELECT SOURCE_MODEL.*, ...                          pass through with .* when you can             §2
    FROM SOURCE_MODEL
),
final AS (                                        ← final: zero logic, explicit columns + aligned comments + tags  §1.2 §4
    SELECT col_a,        -- [OUTPUT] ...
           col_b         -- [AUDIT]  ...
    FROM transformed
)

SELECT * FROM final                               ← fixed ending
```

**Recommended writing order** (inside-out; backfill the header last):

1. **Decide `grain` and `keys` first** — what one row represents, the primary / join keys. This shapes the whole model.
2. Write the **reference CTE** (UPPERCASE, `SELECT *` off the upstream).
3. Write the **intermediate transform CTEs** — one CTE per step, **all calculation/logic lives here**.
4. Write **`final`** — explicit column list + aligned comments + tags, **no logic**.
5. Close with `SELECT * FROM final`, add `config`.
6. **Backfill the header**: `grain`/`keys` were decided in step 1; fill in `summary`/`purpose`/`sources`/`related` + the second business-rules block.

> Full runnable example: `references/example-model.sql`. Section details: §1 CTE structure · §2 `.*` conciseness · §3 naming · §4 comments & layout · §5 header · §6 Redshift syntax · §7 config.

---

## 1. CTE structure

### 1.1 The three CTE roles

```sql
/* == 取得每日維度資料 ================================================== */
WITH DAILY_DIMENSION AS (            -- ① 初次引用 model 的 CTE：全大寫
    SELECT *
    FROM {{ ref('int_metric__daily_dimension') }}
),

/* == 計算週起始日 ================================================== */
daily_with_week AS (                 -- ② 中間轉換 CTE：小寫描述性
    SELECT DAILY_DIMENSION.*,
           DATE_TRUNC('week', data_date)::DATE AS week_start_date
    FROM DAILY_DIMENSION
),

/* == 最終輸出 ================================================== */
final AS (                           -- ③ final CTE：純選欄 + 註解，零邏輯
    SELECT week_start_date,          -- 週起始日（星期一）
           data_date                 -- 資料日期
    FROM daily_with_week
)

SELECT * FROM final
```

- **MUST** — the CTE that first references an external model is **UPPERCASE**, drops the `stg_/int_/mart_` prefix, and contains `SELECT *` (no column-by-column list). The name reflects the referenced model's business content; for over-long names, extract the key dimensions (`int_dim__metric_by_segment_region` → `SEGMENT_REGION`).
- **MUST** — **don't rename CTEs.** Once a CTE name is set, keep it — the name must trace back to the model it references; renaming breaks that thread. (This is about the CTE's *own name*, distinct from §3's *column aliases*.)
- **MUST** — intermediate transform CTEs use **lowercase descriptive** names (`daily_with_week` / `weekly_aggregation`) reflecting what the step does.
- **MUST** — **one concern per CTE.** Better to add a CTE than to cram two derivations together to "save a CTE" — split, and a future change touches only one, with no cross-contamination.
- **MUST** — the model always ends with `SELECT * FROM final`.

### 1.2 The `final` CTE iron law (highest priority)

**MUST — the `final` CTE must contain no business logic.** Only column selection + aliases + comments. Every `CASE`, `WHERE` filter, rename computation, or arithmetic moves up into a dedicated preceding CTE.

```sql
-- ❌ 錯：邏輯混在 final
final AS (
    SELECT id,
           CASE WHEN score >= 0.7 THEN 'high' ELSE 'low' END AS tier,  -- 業務邏輯不該在這
           amount
    FROM src
)

-- ✅ 對：邏輯上移，final 只選欄
classified AS (
    SELECT src.*,
           CASE WHEN score >= 0.7 THEN 'high' ELSE 'low' END AS tier
    FROM src
),
final AS (
    SELECT id,        -- 識別碼
           tier,      -- 分級
           amount     -- 金額
    FROM classified
)
```

Why: separating logic from output shape → easier to test, review, debug; `final` becomes a stable column-schema contract, so a drop-in replacement is a direct column diff.

---

## 2. Minimize explicit declaration / maximize `.*` passthrough

**SHOULD / MAY — an optional conciseness idiom.** Pass columns through with `.*` so adding an upstream column changes only one line in `final`. **Be concise when you can; fall back to explicit declaration the moment it doesn't fit.** It never overrides `final` zero-logic (§1.2).

Four scenarios, in brief:

- **Single-source (no JOIN)** — `SOURCE_CTE.*` + your derived columns. Always works.
- **JOIN** — `JOIN ... USING (key)` + an **unqualified `SELECT *`** keeps the join key single; ⚠️ `a.*, b.*` does **not** dedupe even with USING (key appears twice → collision). Pre-rename so keys share a name if needed.
- **Few renames** — pull the renamed columns out explicitly (`source_cte.col AS new`) + `source_cte.*` for the rest; don't enumerate the whole CTE just to rename a few.
- **Fall back** — enumerate explicitly when value columns collide / need renaming (e.g. both sources expose a `value` column), or keys are differently named so USING can't fold them. (USING still folds identically-named keys even under `FULL OUTER JOIN`.)

> **When a CTE JOINs ≥2 sources and you intend `.*` passthrough, read `references/dotstar-passthrough.md` in full before writing it** — that file holds the exact `USING` + unqualified-`*` rule, the duplicate-column trap, and the fallback chain. (Single-source passthrough — the common case — doesn't need it.)

---

## 3. Naming

- **MUST** — **model / column names are a user-facing contract.** Once pushed and documented, don't rename them for cosmetics — downstream models, Tableau filter keys, and BI reports depend on them. When you need to change what's shown, change the **display label**; keep the technical column id unchanged.
- **MUST** — **name matches content.** A column name's qualifier is its promise: a `__paid` metric must not smuggle in trial rows. To add coverage, open a **parallel column** (`__trial` / `__total`) — don't loosen the existing column's semantics.
- **MUST — variant-naming principle (stable prefix, suffix distinguishes the variant)**: for models / CTEs / columns sharing one base, the **prefix stays the same** to mark shared identity; different variants (time scale, classification, source, scope…) are always distinguished by a **`__`-separated suffix** — not by changing the prefix or the base name.
- **MUST — prefix per the dbt official style guide**: layer prefix + `__` separating source/entity (`stg_<source>__<entity>`, `int_`, marts use `fct_` / `dim_`). This is a general dbt convention, not a claim unique to this template.
- **MUST** — **always qualify column references with the source CTE** (`source_cte.col`); no bare column names, no short table aliases (`t` / `o` / `ci`); write the full CTE name inside JOINs too.
- **(adapt)** — **prefix tokens** (example; each project defines its own set): marts use `mart_` / `dash_` / `expt_`, paired with a domain code (e.g. `rev_` / `cust_` / `ads_` / `prod_`) and region (e.g. `region_a_` / `region_b_`).
- **(adapt)** — **variant-suffix vocabulary** (example; each project defines its own): time scale `__daily` `__weekly` `__mtd` `__qtd` `__ytd` `__yoy` `__mom`; role `__denom` `__predict_value`; scope/grain `__region_b` `__by_customer`; multi-source symmetric `__from_<source>` (leave no implicit default); a version suffix (e.g. `__v2`) goes **only on new models** (keep existing names; never `replace_all` the token in bulk).

---

## 4. Column layout & comments

- **MUST** — 4-space indent; `SELECT` columns vertically aligned; inline `--` comments aligned.

```sql
SELECT month,                               -- 統計月份
       city,                                -- 縣市
       SUM(amount) AS total_amount          -- 總金額
```

- **MUST** — every `final` column has a purpose comment. Group with section headers:

```sql
final AS (
    SELECT -- === 識別欄位 ===
           entity_id,                       -- 實體唯一識別碼

           -- === 主要輸出 ===
           output_value,                    -- [OUTPUT] 處理後輸出值

           -- === 品質監控 ===
           quality_score                    -- [METADATA] 品質評分
    FROM cleaned
)
```

- **MAY — column comments can span multiple lines**: when one column's description is too long, continue on **aligned `--` continuation lines** — the continuation `--` aligns under the first comment's `--`, so it reads as belonging to that column.

```sql
final AS (
    SELECT entity_id,          -- 實體編號：整合多來源後的唯一識別，
                               -- 來源優先序 A > B > C，C 僅補缺漏、不覆蓋既有值
           amount              -- 金額
    FROM cleaned
)
```

  **(adapt)** if your project generates schema YAML from inline comments, aligned continuation lines are merged into **the same column's description**; note the generator may normalize the continuation indentation (don't rely on indentation inside the comment for layout).

- **SHOULD** — a column-tag system marking provenance / role: `[OUTPUT]` primary business output, `[METADATA]` monitoring/debug, `[AUDIT]` lineage/audit. **Tags are extensible** to source/lens tags (`[BU_B]` `[地理視角]` `[ERP+product]`).
- **SHOULD** — **3-site comment sync**: when you change a column's description, update the header frontmatter/narrative, the internal inline comment, and the `final` column comment **all three at once**. Drift leaves readers with contradictory descriptions of the same column.
- **MAY** — align CJK comments/tables by **visual width** (CJK char = 2, ASCII = 1), not character count, or mixed CJK/ASCII goes ragged.
- **(adapt)** — if your project generates schema YAML from inline comments (instead of hand-written `.yml`), then **inline comments = the single source of truth for the schema**; comment quality is load-bearing, not decoration.

---

## 5. The header: two blocks (frontmatter payload + human-facing prose)

The header splits into **two separate `/* */` blocks** — this split is functional, not cosmetic:

> **Mechanism (adapt)**: this two-block design assumes your project **(a)** uses dbt `persist_docs` to write the model description into the warehouse table comment (column comments into column comments), and **(b)** has tooling that takes the **first `/* ... */` block** as the description (e.g. some sql→yml scripts use a non-greedy regex that grabs only the first block). Under that assumption, **only the first block reaches the table comment** — seen by humans reading the comment and by SQL-aware LLMs/MCPs (MCP = a Model Context Protocol server an agent queries, e.g. a Redshift comment server); the second block stays in the `.sql` for humans. If your project doesn't enable `persist_docs`, the two-block split is still a good readability convention — it just loses the "reaches the comment" incentive.

> **Is it wired up? (check once, per project)** — the "first block reaches the comment" payoff is **invisible from the `.sql` alone**, so confirm the machinery before maintaining the header on faith:
> 1. `dbt_project.yml` has `persist_docs: {relation: true, columns: true}` (or the model/folder-level equivalent).
> 2. After a `dbt run`, the comment actually landed — check with `\d+ <schema>.<table>` in `psql`, or `get_table_comment` via the redshift-comment MCP.
>
> **If both hold** → the comment-reaching incentives apply (field-order-for-truncation at the ~1000-char list/search cut, keyword-rich `summary`/`purpose` for `search_tables`, first block as the agent-facing description).
> **If neither holds** → treat §5 as **readability-only**: keep the two-block split + YAML shape (they still help humans and the validator), but the truncation / keyword / discoverability rules are moot — don't optimize for a comment nothing reads.
>
> `scripts/validate_header.py` checks the header's **shape** (fields present, parseable YAML, balanced `/* */`) — it does **not** verify the comment persisted. The two steps above are the only persistence check.

### 5.1 First `/* */`: frontmatter + short narrative (→ table comment, for MCP/agent)

```sql
/* ---
title:   區域 B 每日指標值（雙來源合併）
summary: 來源 A（本地）+ 來源 B（forecast）合併後的每日指標值，來源 B 優先 / 來源 A fallback
grain:   一列 = 一個 (metric_date, entity_id)
purpose: 區域 B 每日指標值的日/月趨勢、entity 別分析；每日營運報表的指標來源
keys:
  primary: [metric_date, entity_id]
  join:    [metric_date, entity_id]
related:
  - { table: int_dim__entity_dimension, join_on: entity_id, adds: entity 基本資料 / 地區 / 分類 }
  - { table: int_metric__daily_dimension, join_on: [metric_date, entity_id], adds: 其他每日指標 }
sources: [int_metric__daily_value__region_b__source_a, int_metric__daily_value__region_b__source_b__by_sub]
refresh: 日更 T+1（依上游 FDW 延遲）
---

來源 B-only 的 row 沒對到來源 A 是正常現象（來源 A 只攤本地）。分析總值時用 daily_value（已 merge），勿用 from_source_a / from_source_b 的透明欄位相加。
*/
```

- **MUST** — the first `/* */` contains: ① a `---`-fenced **YAML frontmatter**, ② followed by a **1–3 sentence unstructured narrative** (context the frontmatter can't express — also written for the MCP/agent).

Field requirements are **layered** (staging isn't queried directly by analysts/MCP and is usually 1:1 with its source, so it's relaxed):

- **All layers MUST**: `title` (the Chinese name, replacing the old `# heading`), `summary`, `grain`, `sources`.
- **Consumer layers (intermediate / marts / dash) additionally MUST**: `purpose`, `keys` (`primary` + `join`).
- **Consumer layers SHOULD**: `related` (joinable dimension tables + `join_on` key + `adds` = what it expands — key to agent analysis efficiency; accept the manual-upkeep / possible-staleness cost), `refresh`.
- **Staging layer**: the four all-layer MUST fields suffice; `purpose` / `keys` / `related` are usually trivial and may be omitted.
- **MAY field**: `layer` (omit if inferable from name/path; if set, it overrides the validator's layer inference).
- **Order fields by importance** (`title` → `summary` → `grain` → `purpose` → `keys` → `related` → `sources` → `refresh`): if the description persists into a warehouse comment, tooling often **truncates to ~1000 chars** in list/search, so the most important must come first to survive.

#### Frontmatter content requirements

- **MUST — `grain` required and precise**: what one row represents ("one entity per day" / "one record per month per category"). This is the single most important field for understanding content + joining correctly.
- **MUST — strictly parseable YAML**: quote values containing `:` / `#` / leading whitespace and other special chars; lists use `[...]`; objects use `{ key: val }`.
- **MUST — `summary` / `purpose` carry analytical keywords**: an MCP's `search_tables` matches on comment keywords, so good ones improve the table's discoverability.
- **`keys.join` semantics**: the keys **downstream can JOIN this table on to expand analysis**. If there's no join key beyond the primary key (common for a single-upstream terminal mart), setting `join` = `primary` or **omitting `join`** is fine — don't fill it just for the sake of it.
- **Omit `related` when there's none**: list only tables that **really exist and can be joined to expand analysis**; if none, **omit the whole `related`** — don't fabricate.
- **Use `join_on`, not `on`**: the related join-key field is `join_on`. **A bare `on` is a reserved boolean in YAML 1.1** — PyYAML parses `on:` as `True` and the frontmatter breaks — which is exactly why we avoid it.

### 5.2 Second `/* */`: detailed business rules / mapping (human-facing, not in the comment)

```sql
/* 重要業務規則 / 過濾邏輯
   * 來源 B 優先、來源 A fallback，單一單位為 canonical
   * source flag: 'source_b' | 'source_a'

   業務邏輯 Mapping (如適用):
        - 分類名稱       來源代碼       來源名稱
*/
```

- **SHOULD** — put verbose business rules, filter logic, and mapping tables here, to avoid bloating the table comment.
- **Position: immediately after the first block and before `config`** (the two comment blocks are adjacent, then `config`, then the first CTE).

### 5.3 Common

- **MUST — every `/* */` must be closed.** An unclosed `/* ==` makes the rest of the file get eaten as comment text, breaking Redshift parsing and `dbt run`.
- **SHOULD** — when `config` (`sort` / `tags`) or the schema changes, keep the frontmatter (especially `grain` / `keys` / `sources`) and the narrative in sync — no drift.

---

## 6. SQL syntax style (Redshift)

Style-level syntax choices (not calculation logic):

- **MUST** — use `LISTAGG(col, ' | ')`, **not `STRING_AGG`** (Redshift has none).
- **MUST** — small mapping/lookup uses `UNION ALL`, **not `FROM (VALUES ...)`** (Redshift has none). **(adapt)** inline UNION ALL table vs a dbt seed — per project convention.

```sql
FROM (
              SELECT 'code1' AS code, 'name1' AS category
    UNION ALL SELECT 'code2' AS code, 'name2' AS category
) AS mapping_table
```

- **MUST** — always **specify the JOIN type explicitly** (`INNER` / `LEFT`); no implicit `FROM a, b WHERE` joins.
- **MUST** — same-named join columns use `USING (col, ...)`, terser than a verbose `ON a.x = b.x AND ...`; for the precise preconditions when combined with `.*` passthrough see §2 / `references/dotstar-passthrough.md`.
- **note** — Redshift doesn't support `SELECT * EXCEPT` or `FILTER (WHERE ...)`; rewrite the latter with an inline `CASE` or a JOIN.

---

## 7. Config block

- **MUST** — wrap table materialization in an environment guard:

```sql
{% if target.type=='redshift' %}
{{ config(
    materialized = 'table',
    sort = ['primary_key_column', 'date_column'],
    tags = ['some_tag']
) }}
{% endif %}
```

- **MUST** — the key is **`materialized`**, not `materialization` (the latter is invalid; there are mis-spelled cases in the wild — don't copy them).
- **SHOULD** — choose `sort` keys that match the columns actually filtered / joined.

---

## Anti-pattern quick reference

| Anti-pattern | Fix |
|---|---|
| `CASE` / `WHERE` / rename computation inside `final` | Move into a dedicated preceding CTE; `final` selects only (§1.2) |
| Declaring every column just to rename a few | Renamed columns explicit + `.*` for the rest (§2) |
| Renaming a CTE / using short aliases `t` `o` | Keep the CTE name; qualify columns with the full CTE name (§1.1 §3) |
| Cosmetically renaming an already-pushed column | Change the display label; keep the technical id (§3) |
| Forgetting to close `/* ==` | Every `/*` needs a `*/` (§5) |
| `STRING_AGG` / `FROM (VALUES)` / `materialization=` | `LISTAGG` / `UNION ALL` / `materialized=` (§6 §7) |
| Cramming multiple derivations into one CTE | One concern per CTE (§1.1) |

---

## After writing / editing

1. Run `checklists/dbt-model-self-check.md` item by item.
2. Run mechanical validation:
   ```bash
   # Always checked: layered required header fields + parseable, keys/related shape, /* */ balance, materialized spelling
   python scripts/validate_header.py models/
   # Opt-in: related/sources tables actually exist in the manifest (cures `related` staleness)
   python scripts/validate_header.py --manifest target/manifest.json models/
   ```
   A non-zero exit code = violations. Without `--manifest` it stays **zero-config and runs on a lone file** (only PyYAML, usually already in a dbt env). **(adapt)** the layered required-key lists are at the top of the script (`BASE_REQUIRED` / `CONSUMER_EXTRA`) — tune to your frontmatter schema; adopters wire it into pre-commit / CI / a dbt step.
3. Ship / open the PR only after it passes.
