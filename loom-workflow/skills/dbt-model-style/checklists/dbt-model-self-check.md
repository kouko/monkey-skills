# dbt Model Style Self-Check

After writing or editing a dbt model, tick each item. **Any MUST ✗ = non-conforming, must fix.** SHOULD/MAY are situational.

> Scope: only check **newly created or this-change models**. When editing an existing model, check just the **part you touched** (boy-scout, bounded); don't backfill the whole old model to satisfy the list.

## MUST — structure

- [ ] `final` CTE has **zero business logic**: no `CASE` / `WHERE` filter / rename computation / arithmetic — only column selection + aliases + comments
- [ ] the CTE first referencing an external model is **UPPERCASE** + `stg_/int_/mart_` prefix dropped + body is `SELECT *`
- [ ] CTE names are **not renamed** (kept so they trace back to the referenced model)
- [ ] intermediate transform CTEs use **lowercase descriptive** names
- [ ] one concern per CTE (no two derivations crammed together)
- [ ] the model ends with `SELECT * FROM final`

## MUST — naming

- [ ] no cosmetic rename of an already-pushed / documented model or column (change the display label, keep the technical id)
- [ ] column names **match content** (e.g. `__paid` excludes trial rows); to extend coverage, add a parallel column
- [ ] **variant-naming principle**: prefix stays the same, variants distinguished by a `__`-separated suffix (not by changing the prefix/base name)
- [ ] prefix follows the dbt official style guide (layer prefix + `__` separating source/entity)
- [ ] column references all carry the **full source-CTE qualifier** — no bare column names, no `t`/`o`/`ci` short aliases
- [ ] (adapt) prefix tokens (`mart_`/`dash_`/domain/region) + variant-suffix vocabulary (`__daily`/`__yoy`/`__denom`…) used correctly

## MUST — header (two blocks)

- [ ] first `/* */` = `---`-fenced **YAML frontmatter** + a 1–3 sentence unstructured narrative (both reach the table comment)
- [ ] required frontmatter fields present (layered) — all layers: `title`/`summary`/`grain`/`sources`; consumer layers (int/mart/dash) also `purpose`/`keys`(primary+join)
- [ ] **`grain` precise** — states what one row represents
- [ ] frontmatter is **strictly parseable YAML** (special chars quoted, lists `[]`, objects `{}`)
- [ ] fields ordered by importance (title→summary→grain→purpose→keys→related→sources→refresh), surviving ~1000-char truncation
- [ ] detailed business rules / mapping in the **second** `/* */` (human-facing, not in the comment), placed after the first block and before config
- [ ] **every `/* */` is closed** (no unclosed `/* ==`)

## MUST — column comments

- [ ] every `final` column has a purpose comment
- [ ] 4-space indent, SELECT columns vertically aligned, inline comments aligned

## MUST — SQL syntax / config

- [ ] uses `LISTAGG` (not `STRING_AGG`)
- [ ] mapping uses `UNION ALL` (not `FROM (VALUES)`)
- [ ] JOIN type explicit (`INNER` / `LEFT`); same-named join columns use `USING`
- [ ] config key is `materialized` (not `materialization`), wrapped in `{% if target.type=='redshift' %}`

## SHOULD / MAY — preferences

- [ ] intermediate chain passes through with `SOURCE_CTE.*` where possible, explicit list only in `final`
- [ ] to keep `.*` usable, prefer `USING` on JOINs; pre-rename upstream so keys share a name when needed
- [ ] when renaming a few columns, use "explicit + `.*`" instead of full explicit (accept the duplicate column for conciseness)
- [ ] when changing a column description, sync the header / inline / final comments **in all three places**
- [ ] column tags `[OUTPUT]` / `[METADATA]` / `[AUDIT]` (or source/lens tags)
- [ ] CJK comments aligned by visual width (CJK = 2, ASCII = 1)
- [ ] long column descriptions use **aligned `--` continuation lines** for multi-line (the generator merges them into one column description)
- [ ] (adapt) variant-suffix vocabulary consistent; version suffix only on new models
- [ ] after a config change, the docstring description is kept in sync
