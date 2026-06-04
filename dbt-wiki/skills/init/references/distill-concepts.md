# Distillation Spec — `concepts/` (knowledge-concept pages)

This file tells Phase B of `dbt-wiki:init` how to produce pages under
`.dbt-wiki/concepts/`. Read it alongside `assets/SCHEMA.md`
(`## knowledge-concept` and `## Relationships spec`), which is the
normative contract for frontmatter shape, edge types, and naming.

---

## 1. Concept identification

A concept is a **cross-cutting business rule** that is encoded in SQL
but is NOT owned by a single entity. The core test:

> If the rule is applied in ≥2 distinct models or ≥2 distinct entities,
> it is a concept. If it only ever appears inside one entity's models,
> add it as a caveat or field note on that entity page instead.

### SQL signals to scan for

Scan every `_evidence/models/` page and its compiled SQL for the
following patterns:

| Pattern | Examples of what to surface |
|---|---|
| `CASE WHEN <col> = '<value>' THEN …` status/state mapping | Order status codes, subscription tier labels |
| `WHERE <date_col> >= DATEADD(…)` or `DATEDIFF(…) <= N` | "active in last 90 days", "retained this month" |
| `CASE WHEN DATEDIFF(…) <= N THEN 1 ELSE 0` activity flag | Active customer flag, churned flag |
| Named fiscal period logic (`CASE WHEN MONTH(…) >= 4 THEN YEAR(…) ELSE …`) | Fiscal year start, fiscal quarter |
| Enumeration tables / seed lookups mapped inline | Country→region, product category hierarchy |
| Threshold constants embedded in SQL literals (`90`, `30`, `0.05`) that appear in ≥2 models | Grace period days, churn rate threshold |

For each candidate, answer the three qualifying questions:

1. Is the rule **encoded in the transformation logic** — a SQL
   `CASE`/`WHERE`/literal constant, OR an enumeration / `accepted_values` /
   constraint declared in schema.yml? (Required. A rule that exists only
   as free-prose narration with no SQL and no schema.yml encoding is not
   yet a concept — note it as a caveat on the relevant entity instead.)
2. Does the rule appear in ≥2 evidence models or apply to ≥2 entities?
   (Required.)
3. Is the rule about a **business interpretation**, not just a SQL
   implementation detail like a type cast? (Required.)

All three must be Yes before creating a concept page. Q1 may be satisfied
via schema.yml `accepted_values`/enums — not only literal SQL — so
status-code and category concepts still qualify when the compiled `CASE`
lives in an upstream model outside the current evidence slice. (A pure
data-format observation — e.g. "opening hours stored as a weekday→slots
JSON blob" — fails Q3: it is an implementation detail, not a business
interpretation, so it is NOT a concept.)

**Q2 refinement — independent models, not parallel copies**: the
"≥2 models" test in Q2 means ≥2 *independent* evidence models. When
two (or more) models are structurally parallel copies that exist
*because of* the very rule you are evaluating — for example, a
per-segment model family where the segment split is the rule itself
(a total-population model and a single-channel/region variant that are
near-identical by construction) — they count as **one** source of
evidence, not two.
The rule passing Q2 "by construction" this way is not signal.

For such structural-segmentation rules, judge cross-cutting status by
whether the rule applies across the domain's downstream consumers:
does every metric or entity in the domain inherit the same split? If
yes, the rule is cross-cutting and Q2 is satisfied. Say so explicitly
in the concept's `## Applies To` section (e.g. "This segmentation
applies to every metric in the domain"). If you cannot verify
cross-domain applicability from the current evidence slice, still
create the concept when the segmentation visibly governs multiple
metrics in-slice, but add a one-sentence caveat: "Evidence limited to
models in the current slice — cross-domain applicability unverified."

---

## 2. Boundary judgment — concept vs. entity-page caveat

Adapt the 80% rule from `obsidian/skills/wiki-ingest/references/category-routing.md`:

| Question | If YES → concept page | If NO → entity-page caveat/field |
|---|---|---|
| Does the rule appear in ≥2 distinct entity models? | concept | entity caveat |
| Is the rule applied when computing ≥1 metric? | concept | entity field note |
| Could the rule change independently of any single entity (e.g. "what counts as active" could shift from 90→60 days without changing the Customer entity definition)? | concept | entity field note |
| Is the rule referred to by name in schema.yml descriptions, comments, or documentation? | concept | entity caveat |

**Boundary rule**: when exactly 2 of the 4 questions are Yes, prefer
a concept page — cross-cutting knowledge is easier to find when
centralized, and entity pages can still link to it via `applies_to`
edges. Only put knowledge on an entity page when it genuinely only
matters for that one entity and zero metrics.

**Examples**:

| Knowledge | Verdict | Why |
|---|---|---|
| `active_customer_flag = order in last 90 days` | concept page | Applied in both `fct_orders` and `fct_churn`; used by ≥2 metrics |
| `fiscal year starts April 1` | concept page | Applied across all date-dimension and mart models |
| `order status = 'cancelled'` | concept page | Status enumeration used by orders AND revenue metrics |
| `customer.email IS NOT NULL` used only in `stg_customers` | entity caveat on Customer | Single-entity data-quality check; not a cross-cutting rule |
| `orders.created_at` timezone normalization in a single model | entity caveat on Order | Single-model implementation detail |

---

## 3. `## Rule` section — plain-language definition

Write the rule as a **single declarative sentence** in business
language, followed by the SQL encoding as a supporting block:

```markdown
## Rule

An **active customer** is any customer who placed at least one order
within the last 90 calendar days, counted from the run date.

SQL encoding:

```sql
CASE
  WHEN DATEDIFF('day', MAX(orders.created_at), CURRENT_DATE) <= 90
    THEN TRUE
  ELSE FALSE
END AS is_active_customer
```
```

Guidelines for the Rule prose:
- Lead with the business meaning, not the SQL formula.
- Name the threshold explicitly ("90 calendar days", "April 1",
  "status code 'C'").
- If the rule has known exceptions or edge cases, note them in one
  sentence ("Excludes test orders where `order_type = 'internal'`").
- Cap the prose at ~100 words; move elaboration to `## Caveats` if
  the entity page type existed — for concept pages, keep it in the
  Rule section itself.

**Severity/type tags for caveats (optional but recommended)**: when
writing caveats — whether inline in the Rule section or in a
`## Caveats` block — prefix each caveat with a tag to signal impact:

| Tag | Meaning |
|---|---|
| `[bug]` | Wrong results if this caveat is not handled (e.g. a NULL propagation that silently zeroes a metric) |
| `[limitation]` | Known coverage or scope gap that does not produce wrong results, but constrains valid use (e.g. "only covers completed orders") |
| `[temporal]` | Date or period semantics gotcha (e.g. "window is calendar days, not business days") |
| `[no-test]` | No dbt test guards this datum; value is asserted by convention, not enforced |

Example:

```markdown
`[temporal]` The 90-day window uses `CURRENT_DATE` at query time, not
at event time — reruns on historical dates will produce different
cohort membership.
```

Tags are optional; omit them when the caveat is self-evidently low-risk.
Do NOT invent tags beyond the four above.

---

## 4. `## Applies To` section

List every entity and metric where the rule is encoded, with a brief
phrase explaining how:

```markdown
## Applies To

- **Customer** ([customer.md](../entities/customer.md)) —
  `is_active_customer` flag computed in `dim_customers`; used to segment
  active vs. inactive cohorts.
- **Churn Rate** ([churn-rate.md](../metrics/churn-rate.md)) —
  denominator of churn calculation is "active customers at start of period".
- **Monthly Active Users** ([monthly-active-users.md](../metrics/monthly-active-users.md)) —
  definition reuses the same 90-day window.
```

Use standard markdown hyperlinks here (relative paths, NO `[[wikilinks]]`),
exactly as in the §7 worked example. The example above is illustrative;
the §7 worked example is the definitive template. The machine-readable
version of these edges goes in the `relationships:` frontmatter — see
Section 5.

---

## 5. `## Relationships` typed edges

Concepts use **`applies_to`** edges pointing at entities and metrics.
Do NOT add `evidence` edges to `relationships:` — evidence belongs only
in `derived_from:` frontmatter and `## Evidence` body section (per
SCHEMA "Do NOT double-encode evidence edges").

### Frontmatter shape

```yaml
relationships:
  - type: applies_to
    target: ../entities/customer.md
    note: "is_active_customer flag in dim_customers"
  - type: applies_to
    target: ../metrics/churn-rate.md
    note: "denominator requires active-customer count"
```

### Path convention

- Concept page lives at `concepts/<slug>.md`.
- Entity target: `../entities/<slug>.md`
- Metric target: `../metrics/<slug>.md`
- Never use `[[wikilinks]]`. Never omit the `../` prefix for cross-folder
  targets.

### Edge type summary for concepts

| Edge type | From | To | When to use |
|---|---|---|---|
| `applies_to` | concept | entity | The rule is encoded in models that define/feed this entity |
| `applies_to` | concept | metric | The metric's algorithm depends on this rule |

Concepts do NOT emit `depends_on`, `joins`, or `measures` edges —
those belong to entity and metric pages respectively.

---

## 6. Frontmatter — full template

```yaml
---
type: knowledge-concept
title: Active Customer Definition      # human-readable business name
slug: active-customer                  # kebab-case; filename without .md
status: developing                     # seed | developing | mature | archived
summary: "A customer is active if they placed an order within the last 90 calendar days."
updated: 2026-06-01
derived_from:
  - model.example_dbt_project.dim_customers
  - model.example_dbt_project.fct_orders
relationships:
  - type: applies_to
    target: ../entities/customer.md
    note: "is_active_customer flag computed in dim_customers"
  - type: applies_to
    target: ../metrics/churn-rate.md
    note: "active-customer count is denominator of churn"
last_changed_by: "init run 2026-06-01"
tags: ["customer", "activity"]
stale: false
stale_at: null
stale_reason: null
aliases:
  - active_flag          # project SQL name, not in summary
  - "is_active_90d"      # field name variant used in fct_churn
title_local: アクティブ顧客定義   # concept title in project's working language; null if project is English-only
---
```

**Field guidance**:

- `slug` must be kebab-case and match the filename (e.g., `active-customer`
  → `concepts/active-customer.md`). Derive from the business title, not
  from any dbt model name (model names use underscores; concept slugs use
  hyphens — this contrast makes link casing signal which layer is
  referenced).
- `summary` must be ≤200 chars (tiered query reads it without loading
  the full page).
- `derived_from` lists evidence model `unique_id` values (format:
  `model.<package>.<model_name>`). Include every evidence model whose
  compiled SQL contains the CASE/WHERE logic that defines this concept.
  This list drives stale detection on refresh.
- `last_changed_by` is set to the commit SHA or PR number that last
  re-distilled this page. On first distillation by `init`, use
  `"init run <YYYY-MM-DD>"`.
- `stale` / `stale_at` / `stale_reason` are written by `/dbt-wiki:refresh`
  when a `derived_from` evidence model changes; do not set them manually
  during distillation.

---

## 6a. Alias capture for project-language retrieval (fully automatic)

During distillation, automatically populate the `aliases:` frontmatter
list — no human step required. Collect terms you wrote into this page's
body that a query author might search for but that:

- **(a)** do NOT appear in the page's `summary`, AND
- **(b)** an LLM could NOT bridge from the summary alone.

For concepts these are typically: project-specific rule names or codes
(e.g. `"active_flag"`, `"is_active_90d"`), status enumerations (e.g.
`"status 'C'"`, `"order_status = 'cancelled'"`), and non-obvious
project synonyms for the business rule (e.g. `"retention window"` for
a churn threshold concept).

**EXCLUDE**: terms already in the title or summary, generic words
(`customer`, `order`, `flag`), and anything an LLM would naturally
infer from the summary alone.

Also set `title_local`: this concept's title in the project's working
language (e.g. Japanese, Traditional Chinese). Use the exact term as
it appears in the project's schema.yml descriptions or internal
documentation — not a translation of the English title.

Both fields are emitted automatically on every `init` and `refresh`
run; a human may prune `aliases` later (pruning is never required, but
never add back a term that was intentionally removed).

**Frontmatter addition (extend Section 6 template)**:

```yaml
aliases:
  - active_flag          # project SQL name, not in summary
  - "is_active_90d"      # field name variant used in fct_churn
title_local: アクティブ顧客定義   # concept title in project's working language
```

---

## 7. Worked example — "Active Customer" concept page

### Source SQL (synthetic — from `compiled/dim_customers.sql`)

```sql
SELECT
  customer_id,
  customer_name,
  CASE
    WHEN DATEDIFF('day', MAX(o.created_at), CURRENT_DATE) <= 90
      THEN TRUE
    ELSE FALSE
  END AS is_active_customer
FROM stg_customers c
LEFT JOIN stg_orders o USING (customer_id)
WHERE o.order_type != 'internal'   -- exclude test orders
GROUP BY 1, 2
```

Same 90-day window also appears in `fct_churn.sql`:

```sql
-- churned = was active last period, not active this period
active_last_period AS (
  SELECT customer_id
  FROM stg_orders
  WHERE created_at BETWEEN DATEADD('day', -180, CURRENT_DATE)
                       AND DATEADD('day', -90,  CURRENT_DATE)
),
active_this_period AS (
  SELECT customer_id
  FROM stg_orders
  WHERE created_at >= DATEADD('day', -90, CURRENT_DATE)
)
```

This rule appears in two models (`dim_customers`, `fct_churn`), applies to
the Customer entity and the Churn Rate metric → qualifies as a concept.

### Distilled page: `concepts/active-customer.md`

```markdown
---
type: knowledge-concept
title: Active Customer Definition
slug: active-customer
status: developing
summary: "A customer is active if they placed at least one non-test order within the last 90 calendar days."
updated: 2026-06-01
derived_from:
  - model.example_dbt_project.dim_customers
  - model.example_dbt_project.fct_churn
relationships:
  - type: applies_to
    target: ../entities/customer.md
    note: "is_active_customer boolean flag on dim_customers"
  - type: applies_to
    target: ../metrics/churn-rate.md
    note: "active-customer count is both denominator and cohort boundary"
last_changed_by: "init run 2026-06-01"
tags: ["customer", "activity", "churn"]
stale: false
stale_at: null
stale_reason: null
aliases:
  - is_active_customer   # SQL field name in dim_customers
  - "active_flag"        # shorthand used in fct_churn comments
title_local: アクティブ顧客定義   # project uses Japanese in schema.yml descriptions
---

## Rule

An **active customer** is any customer who placed at least one
non-test order within the last **90 calendar days**, counted from the
run date. Test orders (`order_type = 'internal'`) are excluded from
this count.

SQL encoding (from `dim_customers`):

```sql
CASE
  WHEN DATEDIFF('day', MAX(o.created_at), CURRENT_DATE) <= 90
    THEN TRUE
  ELSE FALSE
END AS is_active_customer
-- WHERE o.order_type != 'internal'
```

## Applies To

- **Customer** ([customer.md](../entities/customer.md)) — the
  `is_active_customer` boolean is computed in `dim_customers` and
  segments active vs. lapsed customer cohorts.
- **Churn Rate** ([churn-rate.md](../metrics/churn-rate.md)) — the
  churn rate denominator is "customers active in the prior 90-day
  window"; `fct_churn` reuses the same threshold.

## Relationships

- applies_to → [Customer](../entities/customer.md) — `is_active_customer` flag in dim_customers
- applies_to → [Churn Rate](../metrics/churn-rate.md) — active-customer cohort boundary for churn denominator

## Evidence

- [dim_customers](../_evidence/models/dim_customers.md) — primary source of the 90-day CASE/WHEN logic
- [fct_churn](../_evidence/models/fct_churn.md) — reuses the same 90-day window for cohort splitting
```

---

## 8. Distillation checklist (Phase B — per concept)

Use this checklist once per identified concept before writing the page:

- [ ] Rule appears in ≥2 evidence models or applies to ≥2 entities (boundary test passed)
- [ ] SQL signal extracted verbatim and placed in `## Rule` code block
- [ ] Threshold / constant named explicitly in prose (not just in SQL)
- [ ] All entities and metrics in `## Applies To` have corresponding `relationships:` frontmatter entries
- [ ] `derived_from:` lists every evidence model whose SQL encodes the rule
- [ ] No `evidence` edges in `relationships:` (only `applies_to` edges)
- [ ] `slug` is kebab-case and matches the filename
- [ ] `summary` is ≤200 chars
- [ ] No `[[wikilinks]]` — only standard markdown links with relative paths
- [ ] `aliases:` populated with project-specific SQL names / synonyms not inferable from summary; `title_local:` set to project-language title (or `null` if English-only project)
