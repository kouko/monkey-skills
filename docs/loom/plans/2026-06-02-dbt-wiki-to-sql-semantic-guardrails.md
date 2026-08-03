# Plan: dbt-wiki to-sql semantic guardrails

**Source brief**: docs/code-toolkit/specs/2026-06-02-dbt-wiki-to-sql-semantic-guardrails.md
**Total tasks**: 5
**Critical-path depth**: 2 (≤5 ✓) — T1→T2 (prompt-assembly) and T3→T5 (SCHEMA→entities); T1/T3/T4 are level-1 parallel leaves
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-02)

> **Scope**: pure spec/markdown — close the dogfood-found *semantic* (valid-SQL-wrong-answer) gaps via prompt guardrails (to-sql/prompt-assembly.md) + distill knowledge-capture (init distill specs + SCHEMA). On branch `feat/dbt-wiki-nl2sql-to-sql` (distill changes precedented here by f0a7d861).
> **Acceptance**: all RED **grep diagnostics** (no code/tests; dbt-wiki specs aren't pytest-tested). Verification = grep + reviewer + dogfood-case cross-check.
> **HARD constraint**: do NOT renumber existing prompt-assembly §5-§8 (add as §4e/§4f sub-sections or append) — a prior renumber broke 5 cross-file refs in SKILL.md ([[feedback_cross_file_section_refs_shotgun_surgery]]). Worked examples fully synthetic (no real customer data).
> **Finish-time**: bump 2.2.0 → 2.3.0 + CHANGELOG; the date-forward caveat (brief item 8) was already done (f0a7d861) — not a task here.

---

## Task 1 — prompt-assembly: aggregate-semantics + fan-out/grain rules

- **Description**: In `prompt-assembly.md`, add two guardrail sub-sections (e.g. §4e Aggregate Semantics, §4f Join Grain / Fan-out), placed without renumbering §5-§8. (a) **Aggregate semantics**: for ratio/average measures, default to **aggregate-level** `SUM(numerator)/SUM(denominator)` — NOT `AVG(row-level ratio)` — and prefer the metric page's `## Calculation` form if defined; state the aggregation form used as an assumption. Give the AOV contrast as a (synthetic) example. (b) **Join grain / fan-out**: every JOIN must use the **full grain key** named in the relationship edge's `note` (compound keys like `customer_no + rr_month`, not a single column); when two joined tables are at different grains, warn and never `SUM` over the fanned-out rows.
- **Module**: `dbt-wiki/skills/to-sql/references/prompt-assembly.md`
- **Files touched**: `dbt-wiki/skills/to-sql/references/prompt-assembly.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/to-sql/references/prompt-assembly.md` (§3 join-path, §4/§4d existing rules — match register; do not renumber §5-§8)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-02-dbt-wiki-to-sql-semantic-guardrails.md`
- **Acceptance**:
  - **RED**: `grep -ni "aggregate-level\|fan-out\|grain key\|SUM(.*)/.*SUM\|AVG(" dbt-wiki/skills/to-sql/references/prompt-assembly.md` shows no aggregate-semantics/fan-out rule.
  - **GREEN**: both rules present (aggregate-level default + compound-grain-key/fan-out warning), with the no-AVG-of-ratios guidance and the prefer-metric-Calculation note; §5-§8 headers unchanged.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "1. 聚合語意：ratio/average 預設 aggregate-level (SUM/SUM)…" + "2. fan-out / grain：join 必須用完整 grain key（複合）…" (Smallest End State A).

## Task 2 — prompt-assembly: value-grounding + source-disambiguation rules + wire into template/output

- **Description**: In `prompt-assembly.md`, add two more guardrail sub-sections (e.g. §4g Value Grounding, §4h Source Disambiguation), no renumber. (a) **Value grounding**: for a categorical equality filter, use the knowledge-layer recorded value-domain/enum if present; else do NOT assume the user's term equals the stored value — note the stored-format assumption or use `ILIKE`/normalization (synthetic example: user "台灣"/"台北" vs stored `TW`/`台北市`). (b) **Source disambiguation**: when ≥2 candidate sources answer the same business term (e.g. operational vs financial-close), surface both with their basis instead of silently picking one. Then **wire all four new rules (T1+T2) into the §6 prompt template** (one line directing the generator to apply them) and add an **assumptions surface to the §8 output contract** (state aggregation form / grain key / value-mapping / source chosen).
- **Module**: `dbt-wiki/skills/to-sql/references/prompt-assembly.md`
- **Files touched**: `dbt-wiki/skills/to-sql/references/prompt-assembly.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/to-sql/references/prompt-assembly.md` (§6 template, §8 output contract incl. existing §8e/§8f assumption sections — match their pattern)
- **Acceptance**:
  - **RED**: `grep -ni "value.grounding\|value-domain\|ILIKE\|stored value\|disambiguat\|multiple sources\|候選來源" dbt-wiki/skills/to-sql/references/prompt-assembly.md` shows no value-grounding/source rule.
  - **GREEN**: both rules present; the §6 template references the 4 semantic guardrails; §8 output contract has an assumptions surface covering aggregation/grain/value/source; §5-§8 numbers still unchanged.
- **Dependencies**: Task 1 completes first
- **Independent**: false  # same file as Task 1 (prompt-assembly.md)
- **Brief item covered**: "3. value-grounding：分類值…絕不假設使用者詞=DB存值" + "4. source-disambiguation：≥2 候選來源…surface 兩者" (Smallest End State A).

## Task 3 — SCHEMA: compound join-key in Relationships spec + value-domain in knowledge-entity page type

- **Description**: In `SCHEMA.md`, (a) the **Relationships spec**: require an edge's `note` to record the **full/compound join key** (all key columns, e.g. `customer_no + rr_month`) when the join is on a composite key — so consumers don't join on a partial key and fan out. (b) the **knowledge-entity page type** (`## Fields` or a value-domain note): allow/require capturing a **value-domain/enum** for small-cardinality categorical columns (the actual stored values + format, e.g. region ∈ {`TW`,`HK`,`SG`}). State a cardinality threshold so large columns aren't enumerated (per brief OQ2). Additive only; honor the v2.x freeze (optional/additive, no breaking change to existing fields).
- **Module**: `dbt-wiki/skills/init/assets/SCHEMA.md`
- **Files touched**: `dbt-wiki/skills/init/assets/SCHEMA.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md` (Relationships spec / typed-edge `note`; knowledge-entity `## Fields`; the freeze header already permits additive optional content)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-02-dbt-wiki-to-sql-semantic-guardrails.md`
- **Acceptance**:
  - **RED**: `grep -ni "compound\|composite\|full join key\|value-domain\|enum\|allowed values" dbt-wiki/skills/init/assets/SCHEMA.md` shows no compound-key/value-domain capture spec.
  - **GREEN**: Relationships spec requires the compound/full join key in `note`; knowledge-entity page type documents value-domain/enum capture for small categorical columns with a cardinality threshold; additive (freeze-compatible).
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "5. relationship edge note 記複合 join key" + "7. 分類欄記 value-domain/enum + stored format" (Smallest End State B; the SCHEMA-spec half).

## Task 4 — distill-metrics: require derived-ratio aggregation-form definition in §5 Calculation

- **Description**: In `distill-metrics.md` §5 (Calculation Section), add a requirement: when a metric is a **derived ratio / average** (e.g. AOV = sales/invoices, conversion rate), the `## Calculation` MUST define the **aggregation form** — specifically whether it is aggregate-level (`SUM(num)/SUM(denom)`) vs an average of row-level ratios — because the two diverge materially (synthetic example). This gives to-sql an authoritative definition (consumed by Task 1's prompt rule). Additive to §5; do not disturb the existing §5/§5b materialized-column content.
- **Module**: `dbt-wiki/skills/init/references/distill-metrics.md`
- **Files touched**: `dbt-wiki/skills/init/references/distill-metrics.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/references/distill-metrics.md` (§5 Calculation, §5b materialized columns, §6 caveats — match register; additive)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-02-dbt-wiki-to-sql-semantic-guardrails.md`
- **Acceptance**:
  - **RED**: `grep -ni "ratio\|aggregate-level\|SUM(.*)/.*SUM\|average of\|derived ratio\|aggregation form" dbt-wiki/skills/init/references/distill-metrics.md` shows no derived-ratio aggregation-form requirement in §5.
  - **GREEN**: §5 requires defining the aggregation form for derived-ratio metrics (aggregate-level vs avg-of-ratios), with the rationale that the forms diverge; additive, §5b intact.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "6. metric 頁 ## Calculation 定義 derived-ratio 聚合形式：如 AOV = SUM(sales)/SUM(invoices)" (Smallest End State B).

## Task 5 — distill-entities: populate value-domain/enum capture for categorical fields

- **Description**: In `distill-entities.md`, add to the `## Fields` distillation procedure: for small-cardinality categorical columns, capture the **value-domain/enum** (the actual stored values + format) per the SCHEMA spec (defined in Task 3) — so to-sql can map user terms to stored values (region `TW` not "台灣"; city `台北市` not "台北"). Reference SCHEMA's cardinality threshold. Additive to the Fields procedure.
- **Module**: `dbt-wiki/skills/init/references/distill-entities.md`
- **Files touched**: `dbt-wiki/skills/init/references/distill-entities.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/references/distill-entities.md` (the `## Fields` distillation procedure — match register)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md` (Task 3 — the value-domain field shape + cardinality threshold this populates; must align)
- **Acceptance**:
  - **RED**: `grep -ni "value-domain\|enum\|allowed values\|stored value\|categorical" dbt-wiki/skills/init/references/distill-entities.md` shows no value-domain capture procedure.
  - **GREEN**: distill-entities `## Fields` procedure captures value-domain/enum for small categorical columns, aligned with SCHEMA's threshold (Task 3); additive.
- **Dependencies**: Task 3 completes first
- **Independent**: false  # doc-mirrors-spec: must align with the value-domain field shape SCHEMA defines in Task 3 (disjoint file, but semantic dependency)
- **Brief item covered**: "7. 分類欄記 value-domain/enum + stored format" (Smallest End State B; the distill-entities half that populates the SCHEMA field).

## Notes

- **Dependency shape**: Level-1 leaves **T1 ∥ T3 ∥ T4** (disjoint files: prompt-assembly.md / SCHEMA.md / distill-metrics.md; no semantic dep) → all `Independent: true`, dispatch in one wave. **T2** extends T1's file (prompt-assembly.md → same file, sequential, `Independent: false`). **T5** depends on T3 (doc-mirrors-spec: aligns with SCHEMA's value-domain field shape; disjoint file but semantic dep → `Independent: false`). Critical path = T1→T2 (depth 2) and T3→T5 (depth 2); max **depth 2**.
- **Two-skill span**: T1/T2 = to-sql skill; T3/T4/T5 = init skill. Both on this branch (dogfood-driven coherence; precedented by f0a7d861). Reviewer should treat as one coherent "semantic guardrails" change.
- **No renumber** (prompt-assembly): add §4e-§4h sub-sections; verify §5-§8 + SKILL.md cross-refs unchanged.
- **Governance**: all worked examples synthetic; zero real customer data/numbers/names in any file.
- **Out of plan**: gold examples (separate brief), B packager (part-2), execution validation, date-forward caveat (already done f0a7d861).
