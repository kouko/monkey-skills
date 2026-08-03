# Plan: dbt-wiki NL2SQL — part-1 = A (runtime consumer `dbt-wiki:to-sql`, zero-shot)

**Source brief**: docs/code-toolkit/specs/2026-06-02-dbt-wiki-nl2sql-skill.md
**Total tasks**: 6
**Critical-path depth**: 4 (≤5 ✓) — T1→T2→T5→T6; T3/T4 are level-1 leaves parallel with T1
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-02) — see Notes for the post-PASS additive amendment (T6 + T5 RED fix)

> **Scope**: This plan is **part-1 (A) only** — the runtime consumer skill `dbt-wiki:to-sql`, zero-shot (OQ1 LOCKED: no gold examples in v1, prompt leaves a few-shot slot). Part-2 (B, the portable packager `pack-sql-skill`) is a separate future brief/plan.
> **Deliverable**: a new dbt-wiki skill folder `dbt-wiki/skills/to-sql/` (auto-discovered — plugin.json does not enumerate skills). Components: one static-validation helper script + two reference files + the SKILL.md procedure.
> **Boundary (hard)**: NEVER connect to warehouse / execute SQL — validation is **static** (sqlglot parse + manifest existence). Generates SQL, does not run it.
> **Test convention**: dbt-wiki scripts use a custom `if __name__ == "__main__"` mini-harness (`@case` / `tuple[bool,str]` / `main()`), NOT vanilla pytest — match `skills/init/assets/extract_column_lineage_test.py`. Reference-file (doc) tasks use a RED grep diagnostic.
> **Version/CHANGELOG**: bump dbt-wiki 2.1.0 → 2.2.0 + CHANGELOG entry at finish time (not a plan task).

---

## Task 1 — Static SQL validator: parse + extract referenced tables/columns

- **Description**: Create `validate_sql.py` with a function that takes a SQL string, parses it with sqlglot, and returns the set of referenced (table, column) pairs (and bare table refs). Handle parse failure → return a structured `{ok: false, error}`. Write its sibling test first (TDD) with inline synthetic SQL cases (a clean SELECT, a JOIN, a parse-error case).
- **Module**: `dbt-wiki/skills/to-sql/assets/validate_sql.py`
- **Files touched**: `dbt-wiki/skills/to-sql/assets/validate_sql.py`, `dbt-wiki/skills/to-sql/assets/validate_sql_test.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/extract_column_lineage.py` (existing sqlglot usage pattern)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/extract_column_lineage_test.py` (custom test-harness convention to match)
- **Acceptance**:
  - **RED**: `validate_sql_test.py` cases fail before impl — e.g. `extract_refs("SELECT a, b FROM t JOIN u ON …")` should return the referenced tables {t,u} + columns; a malformed SQL returns `{ok: false}`. Run via `python3 validate_sql_test.py` (custom harness), expect non-zero before impl.
  - **GREEN**: `python3 dbt-wiki/skills/to-sql/assets/validate_sql_test.py` prints `N/N passed`, exit 0; covers clean SELECT, JOIN multi-table, and parse-error path.
- **External surfaces**:
  - SDK package: `sqlglot` (parse / expression walk) — grounding: in-repo evidence, already a dbt-wiki dep used in `skills/init/assets/extract_column_lineage.py`.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "靜態驗證：sqlglot parse 通過 + 引用到的 table/column 存在於 manifest" (Smallest End State A step 4) — this task is the parse + ref-extraction half.

## Task 2 — Static SQL validator: check referenced refs exist in manifest

- **Description**: Extend `validate_sql.py` with a function that takes the extracted (table, column) refs + a `manifest.json` path, loads the manifest, builds the set of known models/relations + their columns, and reports any referenced table/column NOT present (returns `{ok, missing_tables, missing_columns}`). If `catalog.json` present, optionally enrich with real column sets. Test-first with a small inline synthetic manifest fixture + refs that do/don't exist.
- **Module**: `dbt-wiki/skills/to-sql/assets/validate_sql.py`
- **Files touched**: `dbt-wiki/skills/to-sql/assets/validate_sql.py`, `dbt-wiki/skills/to-sql/assets/validate_sql_test.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md` (manifest fields: model `unique_id`, `columns[]` — lines 350-407)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/to-sql/assets/validate_sql.py` (extended in Task 1)
- **Acceptance**:
  - **RED**: new test cases fail before impl — a ref to an existing model.column → `ok: true`; a ref to a nonexistent column → `missing_columns` non-empty; nonexistent table → `missing_tables` non-empty. Synthetic manifest built inline in the test.
  - **GREEN**: `python3 dbt-wiki/skills/to-sql/assets/validate_sql_test.py` prints all-passed incl. the existence cases; exit 0.
- **External surfaces**:
  - Internal data contract: dbt `manifest.json` structure (`nodes[].columns`, `unique_id`) — grounding: in-repo evidence, `skills/init/` already parses the same manifest; shape documented in `assets/SCHEMA.md:350-407`.
- **Dependencies**: Task 1 completes first
- **Independent**: false  # same file as Task 1 (validate_sql.py); extends its output
- **Brief item covered**: "引用到的 table/column 存在於 manifest（catalog.json 在的話加型別檢查）" (Smallest End State A step 4) — the manifest-existence half.

## Task 3 — Reference: retrieval procedure (NL question → relevant pages)

- **Description**: Write `references/retrieval.md` defining how `to-sql` gathers schema context for a business question: reuse `query`'s tiered retrieval (summary frontmatter → full page), which knowledge to pull (entities + fields, metrics incl. `## Materialized Columns` cards, concepts, `relationships` edges for join-paths) + backing evidence columns; and how to handle not-found / ambiguous / too-broad (narrow-by-tier, ask-to-disambiguate). Read-only consumption of `.dbt-wiki/`.
- **Module**: `dbt-wiki/skills/to-sql/references/retrieval.md`
- **Files touched**: `dbt-wiki/skills/to-sql/references/retrieval.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/query/SKILL.md` (K1–K3 retrieval + tiered loading + drift check — lines 116-171, 54-65)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/references/distill-metrics.md` (§5b column cards — a key retrieval target)
- **Acceptance**:
  - **RED**: `test -f dbt-wiki/skills/to-sql/references/retrieval.md` fails (file absent).
  - **GREEN**: file exists and specifies: tiered retrieval reuse, the knowledge/evidence page set to pull (incl. column cards + relationship join-paths), and not-found/ambiguous/too-broad handling.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "用 query 的分層檢索挑出相關 entities/metrics（含欄位卡映射）/concepts/關係邊（+ evidence schema）" (Smallest End State A step 1).

## Task 4 — Reference: prompt-assembly procedure (schema-linking → SQL generation contract)

- **Description**: Write `references/prompt-assembly.md` defining how to build the generation prompt from retrieved context: schema-linking (business term → entity field), use of column-card mappings (materialized variant → physical `model.column`, SELECT-don't-aggregate), relationship join-paths (from `relationships` edges), an explicit **few-shot slot** (empty in v1, documented for the later examples increment), and the **output contract** (the SQL + which knowledge pages were cited + the static-validation result + drift caveat). State the dialect rule (follow the manifest adapter's dialect).
- **Module**: `dbt-wiki/skills/to-sql/references/prompt-assembly.md`
- **Files touched**: `dbt-wiki/skills/to-sql/references/prompt-assembly.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-02-dbt-wiki-nl2sql-skill.md` (the brief — pipeline + output contract)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/references/distill-metrics.md` (§5b column-card shape used in schema-linking)
- **Acceptance**:
  - **RED**: `test -f dbt-wiki/skills/to-sql/references/prompt-assembly.md` fails (file absent).
  - **GREEN**: file exists and covers: schema-linking, column-card use, join-path assembly, the explicit empty few-shot slot, the output contract (SQL + citations + validation result + drift caveat), and the dialect rule.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "組 prompt：schema-linking + 欄位卡 + 關係圖 join-path … v1 zero-shot，prompt 內建 few-shot slot" + "回傳 SQL + 引用 + 驗證結果" (Smallest End State A steps 2-3, 5-6).

## Task 5 — SKILL.md: orchestrating procedure + frontmatter (query-vs-to-sql disambiguation)

- **Description**: Write `skills/to-sql/SKILL.md` tying the pipeline together: frontmatter (`name: to-sql`, description scoping it as "NL business question → runnable SQL", explicitly distinct from `query`'s "explain the data"); pre-condition + drift check (reuse query's WIKI_DIR + manifest_sha logic); Step 1 retrieve (→ `references/retrieval.md`); Step 2 assemble prompt (→ `references/prompt-assembly.md`); Step 3 generate SQL; Step 4 static-validate by running `assets/validate_sql.py` against the current manifest; Step 5 present SQL + cited pages + validation result + drift caveat. Reaffirm the NEVER-execute boundary.
- **Module**: `dbt-wiki/skills/to-sql/SKILL.md`
- **Files touched**: `dbt-wiki/skills/to-sql/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/query/SKILL.md` (pre-condition/drift Step 0, output structure — the sibling to mirror)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/to-sql/references/retrieval.md` (Task 3)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/to-sql/references/prompt-assembly.md` (Task 4)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/to-sql/assets/validate_sql.py` (Task 1+2)
- **Acceptance**:
  - **RED**: `test -f dbt-wiki/skills/to-sql/SKILL.md` fails; and `grep -l "name: to-sql" dbt-wiki/skills/to-sql/SKILL.md` empty.
  - **GREEN**: SKILL.md exists with valid frontmatter (name + description distinguishing from query); body has the 5 steps (pre-condition/drift → retrieve → assemble → generate → static-validate → present) referencing the two reference files + the validator script by relative path; the NEVER-execute boundary is restated. `grep` confirms references to `references/retrieval.md`, `references/prompt-assembly.md`, `assets/validate_sql.py`.
- **Dependencies**: Tasks 1, 2, 3, 4 complete first
- **Independent**: false  # orchestrator; references all prior tasks' outputs
- **Brief item covered**: "A = 新 sibling skill `dbt-wiki:to-sql` … pipeline = 檢索→組 prompt→生 SQL→靜態驗證→回傳" + "在 router/README 明確兩者分工（query=理解資料、to-sql=產查詢）" (Decision + Axis 5).

## Task 6 — Add `to-sql` to README Skills tables (query-vs-to-sql disambiguation)

- **Description**: Add a `/dbt-wiki:to-sql` row to the `## Skills` table in all three READMEs (`README.md`, `README.ja.md`, `README.zh-TW.md`), worded to disambiguate from `query` (query = understand the data / explain meaning + lineage; to-sql = turn a business question into a runnable SQL query). Match the existing row format (skill link | when-to-use | inputs). Do NOT bump the README `**Version**` line here — version bump is a finish-time step.
- **Module**: `dbt-wiki/` (README skill-table docs)
- **Files touched**: `dbt-wiki/README.md`, `dbt-wiki/README.ja.md`, `dbt-wiki/README.zh-TW.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/README.md` (the `## Skills` table — lines ~22-29)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/to-sql/SKILL.md` (Task 5 — the skill being documented; match its description)
- **Acceptance**:
  - **RED**: `grep -c "to-sql" dbt-wiki/README.md` returns 0 (no row yet).
  - **GREEN**: each of the 3 READMEs' `## Skills` table has a `to-sql` row that names its purpose and contrasts it with `query` (understand vs generate-query); row format matches the existing rows.
- **Dependencies**: Task 5 completes first
- **Independent**: false  # documents the skill from Task 5; must reflect its final name/description
- **Brief item covered**: "在 router/README 明確兩者分工（query=理解資料、to-sql=產查詢），避免使用者混淆/觸發錯 skill" (Decision + Axis 5 — the disambiguation lives in the README Skills table, dbt-wiki's de-facto router since there is no `using-dbt-wiki` router skill).

## Notes

- **Post-PASS additive amendment (2026-06-02)**: plan-document-reviewer returned PASS 14/14 on the 5-task version. Its advisory flagged that the brief's "router/README disambiguation" had no covering task. Recon confirmed `dbt-wiki/README*.md` carry a `## Skills` table (the de-facto router; no `using-dbt-wiki` skill exists). **T6 added** to cover it, and **T5's RED ellipsis** replaced with a concrete path. This amendment is **additive + schema-safe**: T6 is a new terminal task with all required fields, depends only on T5, leaves the DAG acyclic, and moves critical-path depth 3 → 4 (still ≤5). No existing task's contract changed → re-review skipped per writing-plans §"Amending a PASS plan".
- **Dependency shape**: Level-1 leaves **T1 ∥ T3 ∥ T4** (disjoint files: validate_sql.py / retrieval.md / prompt-assembly.md; no semantic dep) → all `Independent: true`, dispatch in one wave. **T2** extends T1's file (same file → sequential, `Independent: false`). **T5** is the orchestrator, depends on T1+T2+T3+T4. **T6** (README disambiguation) depends on T5. Critical path = T1 → T2 → T5 → T6 = **depth 4**.
- **Anthropic skill structure**: `skills/to-sql/` must stay flat — `assets/` and `references/` are single-level subfolders, no nesting (validate-skill-folder-structure hook enforces).
- **Boundary guard**: no task may add warehouse/execution code. Validation is static only.
- **Out of this plan (part-1)**: gold-example generation (separate brief), the portable packager B (part-2), execution-based validation (OQ4 future), vector-DB retrieval.
- **Finish-time (not plan tasks)**: bump plugin 2.1.0 → 2.2.0 + CHANGELOG; whole-branch review; verification (run the validator's custom-harness test + confirm folder-structure hook clean).
