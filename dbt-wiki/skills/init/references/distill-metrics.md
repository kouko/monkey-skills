# distill-metrics.md — Metric Distillation Spec (Phase B)

This file defines the procedure for Phase B metric distillation. Init
follows this procedure to produce `metrics/` knowledge pages from the
evidence layer. Do NOT invent procedure that contradicts this spec or
SCHEMA.md.

Referenced from: `SKILL.md § Phase B step 3`

---

## 1. What Is a Business Metric?

A **business metric** is a scalar or time-series business measure that
aggregates rows from one or more entities to answer a performance
question — "how much?", "how many?", "at what rate?". Metrics are
distinct from entities (which describe objects) and concepts (which
describe rules).

Signals that a column or model represents a metric rather than an
entity attribute:

- The column name contains measurement vocabulary: `revenue`, `mrr`,
  `arr`, `ltv`, `gmv`, `churn`, `rate`, `count`, `conversion`,
  `retention`, `nrr`, `acv`, `cac`, `arpu`, `margin`.
- The model is in a mart layer (`models/marts/`, `models/reporting/`,
  `models/finance/`) and its SELECT includes aggregate functions:
  `SUM(...)`, `COUNT(...)`, `AVG(...)`, `COUNT(DISTINCT ...)`.
- The model has a `GROUP BY` clause establishing a measurement grain
  (typically a time period + an entity key).
- The schema.yml description says "measures", "calculates", "tracks",
  "rate of", or "total".
- The model feeds an exposure (BI tool / dashboard) directly.

One evidence model can produce multiple metrics (e.g. `fct_mrr.sql`
computes `new_mrr`, `expansion_mrr`, `churned_mrr`, `net_mrr`). Each
distinct business measure gets its own `metrics/` page.

---

## 2. MetricFlow Branch (authoritative ingest)

**Check for MetricFlow / dbt Semantic Layer definitions first** before
deriving anything from SQL.

### 2a. Detection

In `manifest.json`, check for a top-level `"semantic_models"` key —
MetricFlow (dbt Semantic Layer) always populates it. Gate on this key
alone:

```python
has_metricflow = bool(manifest.get("semantic_models"))
```

**Do NOT gate on the `"metrics"` key.** Legacy dbt (≤1.5) projects can
declare `metrics:` YAML *without* MetricFlow — those manifests carry a
non-empty `metrics` key but NO `semantic_models`. Routing them into the
ingest branch would reference an absent `semantic_models` block. A bare
`metrics` key without `semantic_models` is the legacy path and belongs
in the SQL-derivation branch. Only the co-presence of `semantic_models`
+ `metrics` indicates MetricFlow.

If `has_metricflow` is true, take the **MetricFlow ingest branch (§2b)**.
Otherwise, take the **SQL-derivation branch (§3)**.

### 2b. MetricFlow Ingest Branch

When the project defines Semantic Layer resources, **ingest them as
authoritative** — do NOT re-derive definitions from raw SQL.

For each entry in `manifest["metrics"]`:

| Manifest field | Maps to page section |
|---|---|
| `name` | kebab-case slug + `title` frontmatter |
| `description` | `## Definition` body |
| `type` (`simple` / `ratio` / `cumulative` / `derived`) | mention in `## Calculation` |
| `type_params.measure` (for simple metrics) | `## Calculation` — the aggregate expression |
| `type_params.numerator` / `denominator` (ratio) | `## Calculation` |
| `filter` | `## Caveats` — note the filter condition in plain language |
| `dimensions` (from parent semantic_model) | `## Relationships` — `measures` edge to the entity |
| `label` | use as `title` if present, else humanize `name` |

For each metric, find its parent `semantic_model` (via
`manifest["semantic_models"]` — the semantic model that contains the
`measure` this metric references). The semantic model's `node_relation`
field names the underlying dbt model. Record that model's `unique_id`
in `derived_from:`.

**Do NOT generate or author MetricFlow specs.** Only read what the
project already declared. If a metric definition is ambiguous in the
manifest, represent what is written — do not speculate about intent.

---

## 3. SQL-Derivation Branch (when MetricFlow is absent)

Use this branch when `has_metricflow` is false.

### 3a. Identify metrics from evidence

Scan `_evidence/models/` pages (built by Phase A). For each model, look
for metric signals (§1). Candidate identification heuristics in order of
confidence:

1. **Aggregate SELECT + GROUP BY** in compiled SQL — highest confidence.
   Example: `SUM(revenue) ... GROUP BY date_trunc('month', created_at), customer_id`
2. **schema.yml description** mentioning measurement vocabulary — medium
   confidence. Example: `description: "Monthly recurring revenue per customer"`.
3. **Column name pattern** matching measurement vocabulary in a mart-layer
   model — lower confidence. Confirm by checking SQL before creating a page.

For each confirmed metric candidate, determine:

- **Name**: the business name (not the SQL column name). Derive from
  schema.yml description or column name. Examples: `monthly_recurring_revenue`,
  not `mrr_usd`; `customer_churn_rate`, not `pct_churned`. The business
  name maps to the file slug by replacing underscores with hyphens per
  §8 (`monthly_recurring_revenue` → `monthly-recurring-revenue.md`).
- **Grain**: what the `GROUP BY` aggregates over — time period, entity key,
  or both. State as "one row per `<grain>`".
- **Aggregation**: `SUM`, `COUNT`, `AVG`, `COUNT DISTINCT`, ratio, etc.
- **Source model**: which evidence model computes this metric
  (`unique_id` from manifest).

### 3b. Group metrics by source model

One `fct_` or `rpt_` model often computes several related metrics. Group
them by source model to avoid redundant `derived_from` lookups. Create
one page per distinct business measure, but all pages from the same model
share the same `derived_from` entry.

---

## 4. Definition Section

Write `## Definition` in plain language. Explain:

- **What the metric measures** — the business question it answers.
- **Why it matters** — why a business stakeholder cares about this number.
- **Unit** — is it a currency amount, a count, a percentage, a ratio?
- **Reporting grain** — over what time period and entity is it typically
  reported (e.g., per month per account, per week per cohort)?

Do NOT paste raw SQL. Do NOT use column names as the explanation.

Example (churn rate):

> Measures the fraction of active customers who cancelled during a period.
> A rising churn rate signals that the product is losing customers faster
> than it retains them. Reported as a percentage, typically monthly.

---

## 5. Calculation Section

Write `## Calculation` in plain language. Cover:

1. **The formula in words** — describe the numerator and denominator (for
   rates / ratios), or the aggregation and its filter conditions (for
   sums / counts). Reference the metric `type` if MetricFlow was ingested.
2. **The measurement grain** — what one output row represents.
3. **Key edge cases or gotchas** — NULLs, division-by-zero guards,
   currency conversions, trial-period exclusions, etc. These move to
   `## Caveats` if they are data-quality issues rather than algorithmic
   choices.

Example (churn rate):

> Churn rate = (customers who cancelled in period) / (customers active at
> period start). Computed monthly: the denominator is the customer count
> on the first day of the month; the numerator counts distinct customers
> whose `cancelled_at` falls within that calendar month. Customers who
> cancelled and reactivated in the same month are excluded (see the
> "active customer" concept for the reactivation rule).

Cite the SQL model where this logic lives, but do not dump raw SQL inline.
The evidence link in `## Evidence` carries the full SQL path.

---

## 6. Caveats Section

Write `## Caveats` for anything that can surprise a consumer of the metric:

- Known data-quality gaps (e.g., "trials before 2023-01 are excluded
  because the `trial_started_at` column was not backfilled").
- Test coverage from evidence: which schema.yml tests guard the
  underlying model (not_null, unique, accepted_values).
- Currency / timezone handling, if relevant.
- Lag: does this metric reflect near-real-time data or a daily snapshot?

Source caveats from evidence model pages (`columns[].tests`,
`generic_tests`, `## Description`, inline SQL comments).

---

## 7. Relationships Section (typed edges)

Write `## Relationships` in the page body and the `relationships:`
frontmatter block. The two MUST be in sync.

Two edge types for metrics:

### 7a. `measures` edge — metric → entity (the measurement grain)

Every metric measures something over an entity. The GROUP BY grain of the
aggregation determines the target entity.

- `type: measures`
- `target:` the entity page this metric aggregates over (relative path
  from the `metrics/` folder: `../entities/<entity-slug>.md`)
- `note:` the GROUP BY key(s) in plain language

Example: a monthly churn rate grouped by customer maps to a `measures`
edge targeting `../entities/customer.md`.

If the metric measures over multiple entities (e.g., revenue per customer
per product), emit one `measures` edge per entity.

### 7b. `depends_on` edge — metric → concept (algorithm dependency)

When the metric's calculation depends on a cross-cutting business rule
that is also modelled as a `knowledge-concept` page, record the dependency.

- `type: depends_on`
- `target:` the concept page (`../concepts/<concept-slug>.md`)
- `note:` why the metric depends on this rule (one line)

Example: churn rate depends on the "active customer" definition because
the denominator is the active-customer count. Record this as
`depends_on → [Active Customer](../concepts/active-customer.md)`.

**Do NOT add `evidence`-type edges to `relationships:`.** Evidence links
go only in `derived_from:` frontmatter and `## Evidence` body section
(SCHEMA.md: "Do NOT double-encode evidence edges").

---

## 8. Frontmatter

All metric pages use `type: knowledge-metric`. Required fields:

```yaml
---
type: knowledge-metric
title: <Human-Readable Metric Name>
status: developing          # seed | developing | mature | archived
summary: "<≤200 chars — one-line business meaning>"
updated: <YYYY-MM-DD>
derived_from:
  - model.<project>.<evidence_model>    # unique_id of the model(s) this metric is distilled from
relationships:
  - type: measures
    target: ../entities/<entity-slug>.md
    note: "<GROUP BY grain description>"
  - type: depends_on                    # only if a concept dependency exists
    target: ../concepts/<concept-slug>.md
    note: "<why the metric depends on this concept>"
last_changed_by: "<commit SHA or PR#>"
tags: []
stale: false
stale_at: null
stale_reason: null
---
```

`derived_from` must list the `unique_id` of every evidence model that
contains the metric computation. This is the freshness anchor: refresh
flags the page stale if any listed unique_id changes.

Slug: kebab-case from the business `title`, not the SQL column name.
Examples: `monthly-recurring-revenue.md`, `customer-churn-rate.md`,
`gross-merchandise-value.md`.

---

## 9. Evidence Section

Write `## Evidence` as a bullet list of links to the `_evidence/` model
pages the metric was distilled from:

```markdown
## Evidence
- [fct_mrr](../_evidence/models/fct_mrr.md)
- [stg_subscriptions](../_evidence/models/stg_subscriptions.md)
```

Paths are relative from the `metrics/` folder. Use `../_evidence/models/`
prefix. One bullet per `derived_from` model.

---

## 10. Worked Example — Customer Churn Rate

This example shows a complete metric page distilled from synthetic
evidence (no MetricFlow — SQL-derivation branch).

**Synthetic evidence context:**
- `fct_churn_monthly.sql` computes monthly churn. Its compiled SQL
  contains `COUNT(DISTINCT customer_id)` with a `WHERE cancelled_at
  BETWEEN ...` filter and a `GROUP BY date_trunc('month', period_start)`.
- `stg_subscriptions.sql` stages raw subscription events. The schema.yml
  description on `fct_churn_monthly` says: "Monthly churn rate per
  customer cohort. Denominator is active customers at month start;
  numerator is cancellations in the month."
- Evidence `unique_ids`:
  - `model.acme.fct_churn_monthly`
  - `model.acme.stg_subscriptions`
- The concept page `active-customer.md` exists under `concepts/`
  (defines "active = had a paid subscription on the first day of the
  period").

**Output file**: `.dbt-wiki/metrics/customer-churn-rate.md`

```markdown
---
type: knowledge-metric
title: Customer Churn Rate
status: developing
summary: "Fraction of active customers who cancelled in a given month; monthly cadence, per-customer grain."
updated: 2026-06-01
derived_from:
  - model.acme.fct_churn_monthly
  - model.acme.stg_subscriptions
relationships:
  - type: measures
    target: ../entities/customer.md
    note: "GROUP BY customer_id — one rate per customer cohort per month"
  - type: depends_on
    target: ../concepts/active-customer.md
    note: "denominator uses the active-customer definition (paid sub on period start)"
last_changed_by: "PR #000"
tags: ["finance", "retention"]
stale: false
stale_at: null
stale_reason: null
---

## Definition

Measures the fraction of customers who were active at the start of a
month and cancelled their subscription during that month. A rising churn
rate signals that the product is retaining customers less effectively.
Reported as a percentage on a monthly cadence.

## Calculation

Churn rate = (customers who cancelled in the month) / (customers active
at the first day of the month).

The denominator counts distinct `customer_id` values that held an active
paid subscription on the first day of the measurement month (per the
active-customer concept — see Relationships). The numerator counts
distinct `customer_id` values whose `cancelled_at` timestamp falls within
that calendar month.

Customers who cancelled and reactivated within the same calendar month
are excluded from the numerator (they do not represent net churn for the
period). The calculation is performed monthly; no intra-month cadence
is supported.

## Caveats

- Subscription records before 2022-01-01 are excluded: the
  `subscription_started_at` column was not backfilled for legacy imports.
- Trial accounts (where `plan_type = 'trial'`) are excluded from both
  numerator and denominator; only paid subscriptions are counted.
- The `stg_subscriptions` model has a `not_null` test on `customer_id`
  and a `unique` test on `subscription_id`; no known null gaps in
  production as of last schema.yml audit.
- Metric reflects a daily batch snapshot, not real-time data. Lag is
  typically one business day.

## Relationships

- measures → [Customer](../entities/customer.md) — GROUP BY customer_id grain
- depends_on → [Active Customer](../concepts/active-customer.md) — denominator definition

## Evidence

- [fct_churn_monthly](../_evidence/models/fct_churn_monthly.md)
- [stg_subscriptions](../_evidence/models/stg_subscriptions.md)
```

---

## 11. Summary of Decision Rules

| Situation | Action |
|---|---|
| `manifest["semantic_models"]` or `manifest["metrics"]` present | MetricFlow ingest branch (§2b) — do not re-derive |
| No MetricFlow, mart model with `SUM`/`COUNT` + `GROUP BY` | SQL-derivation branch (§3) |
| Multiple metrics in one model | One page per distinct business measure; share `derived_from` |
| Metric depends on a concept page | Add `depends_on` edge in both frontmatter and `## Relationships` |
| Evidence link placement | `derived_from:` + `## Evidence` only — never in `relationships:` |
| Slug | kebab-case from business title, not SQL column name |
| `summary` field | ≤200 chars, one line, plain language |
