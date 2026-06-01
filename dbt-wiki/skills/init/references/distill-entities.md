# Distillation Spec — `entities/` (knowledge-entity pages)

This file is the authoritative procedure for Phase B entity distillation.
Read it before writing any `entities/` page. Do NOT invent a procedure
that contradicts this spec or the SCHEMA contract in `assets/SCHEMA.md`.

---

## 1. Entity identification

An **entity** is a business object — a thing the organisation tracks,
measures, or acts upon. Examples: Customer, Order, Subscription, Product,
Invoice, Campaign.

### 1.1 Signals to look for in the evidence layer

Work through the evidence in this order. A confident entity identification
typically fires on 2+ signals.

| Signal | What to look at | How to read it |
|---|---|---|
| **Model naming family** | `_evidence/models/` filenames | A set of models sharing a root noun (`stg_customers`, `int_customers`, `dim_customers`, `fct_customer_activity`) clusters around one entity. The root noun becomes the entity title. |
| **Grain statement** | Evidence model `## Description` / schema.yml `description` | "One row per unique customer" → entity = Customer. Distinct grains within a family are allowed (e.g., fct_orders is grain=order-line, fct_orders_daily is grain=order-day) — they still belong to the same Order entity. |
| **Lineage clustering** | Evidence model frontmatter `depends_on.refs` / `feeds_into` | Models that form a vertical chain (`stg_X → int_X → fct_X`) typically distil into one entity X. Cross-chains (`fct_orders depends on stg_customers`) signal a relationship between two entities, not one entity. |
| **Join-key columns** | Evidence model `columns[].name` and `columns[].description` | A `customer_id` column in multiple models is evidence for a Customer entity. FK descriptions ("FK to dim_customers") identify relationships between entities. |
| **schema.yml descriptions** | Evidence model `columns[].description`, model-level `description` | Plain-language descriptions written by the dbt author are the richest signal. Read them holistically across the model family. |

### 1.2 Entity vs concept boundary

Before creating an entity page, confirm the business object is an
entity (not a concept):

| Question | YES → entity | NO → concept |
|---|---|---|
| Does it have a primary key in at least one model? | ✓ | — |
| Is it something the business "has" or "tracks" (a noun)? | ✓ | — |
| Could it appear as a row in a database table? | ✓ | — |
| Is it a rule applied to something else (e.g., "active = last 90 days")? | — | ✓ |
| Is it a cross-cutting calculation without its own grain? | — | ✓ |

When genuinely ambiguous, prefer entity. Cross-cutting rules that exist
entirely inside a `CASE/WHERE` expression without their own primary key
belong in `concepts/`.

### 1.3 Naming

Entity title: the **business name** (capitalised noun), not the dbt
model name. `stg_orders`, `fct_orders`, `dim_order_items` → entity title
`Order`.

Entity slug (filename): kebab-case derived from the title.

| Title | Slug |
|---|---|
| Customer | `customer.md` |
| Order | `order.md` |
| Monthly Subscription | `monthly-subscription.md` |

### 1.4 One entity, many evidence models

An entity page is intentionally a **many-to-one distillation**: it
synthesises knowledge from the whole model family. List every evidence
model in `derived_from` (frontmatter) and `## Evidence` (body). Do not
create separate entity pages for `stg_customers` and `dim_customers` —
they are two evidence models for one Customer entity.

---

## 2. Grain determination

The `## Grain` body section states what one row represents on the
**canonical mart / fact / dimension model** for the entity (not the
staging layer).

Format: `One row = one <thing> [as of <qualifier>].`

Examples:
- `One row = one customer account (unique customer_id).`
- `One row = one order (unique order_id).`
- `One row = one subscription renewal event (subscription_id + renewal_date).`

If multiple models in the family have different grains, state the
primary grain (the one with the business PK) and note variants:
`Primary grain: one order (order_id). fct_orders_daily is
grain = order × calendar day.`

How to determine grain:
1. Find the model whose PK is declared with `tests: [unique, not_null]`
   in schema.yml — that is the authoritative grain model.
2. If no such test exists, use the `## Description` of the mart/fct
   model in the evidence layer.
3. Last resort: infer from the PK column name (e.g., `order_id` with
   `not_null` test implies grain = one order).

---

## 3. Fields section — plain-language column dictionary

The `## Fields` body section is the **glossary for this entity**. The
glossary does not live in a separate folder — it lives here.

### 3.1 What to include

Include only **meaningful business fields** — fields that an analyst
would need to understand the entity. Exclude:
- Internal plumbing columns (`_fivetran_synced`, `_etl_loaded_at`,
  surrogate-key hash columns, `dbt_updated_at`)
- Columns already self-explanatory from their name and type (e.g.,
  `created_at TIMESTAMP` needs no entry if the description is just
  "created at timestamp")
- Columns with `declared_in_schema_yml: false` AND no meaningful
  inference available

### 3.2 Format

Use a markdown table with three columns:

```markdown
## Fields

| Field | Meaning | Evidence column |
|---|---|---|
| `customer_id` | Unique identifier for the customer account. Primary key. | `dim_customers.customer_id` |
| `status` | Current lifecycle state: `active`, `churned`, `paused`. Populated from the CRM status field via the ETL normalisation step. | `dim_customers.status` |
| `acquired_at` | Date the customer first made a paying purchase (not trial start). Determines cohort membership. | `stg_customers.first_paid_at` |
| `ltv_usd` | Lifetime revenue (USD) from all completed orders. Recomputed nightly. | `fct_customer_activity.lifetime_revenue` |
```

Rules:
- **Field**: backtick-wrapped column name from the canonical model.
- **Meaning**: 1–3 sentences in plain business language. State the
  business definition, not just a restatement of the column name.
  If the column is an enum, list the valid values and their meaning.
- **Evidence column**: `<model_name>.<column_name>` pointing to the
  evidence model page that contains the authoritative definition.
  If the field is computed across multiple models, list the primary source.

### 3.3 Where to source the Meaning

Priority order:
1. schema.yml `columns[].description` in the evidence model page
2. Inline SQL comments attached to that column (from `## Inline Comments` in evidence page)
3. LLM inference from column name + context of surrounding model description

Always prefer declared descriptions. LLM inference is a fallback only;
mark inferred entries with `(inferred)` if confidence is low.

---

## 4. `## Relationships` — typed edges

### 4.1 What belongs in `relationships:` frontmatter

`relationships:` carries **knowledge→knowledge edges only**. It does NOT
carry evidence edges. Evidence is handled exclusively by `derived_from:`
(frontmatter) and `## Evidence` (body).

**Do NOT double-encode evidence edges.** If you have written a model uid
in `derived_from:`, do not also add it as a `relationships:` entry. These
are two different concerns: `derived_from` = freshness anchor for
evidence; `relationships:` = semantic graph between knowledge pages.

Permitted edge types for entity pages:

| Edge type | From → To | When to emit |
|---|---|---|
| `depends_on` | entity → entity | Two entities share a join key (FK relationship). |
| `joins` | entity ↔ entity | Alternative label when the join is bidirectional in queries (e.g., Order ↔ Customer is a standard JOIN not an ownership hierarchy). Use `depends_on` when directionality is clear. |

### 4.2 How to derive edges from evidence

1. **Shared join key**: if `dim_orders.customer_id` has a description
   "FK to dim_customers", emit `depends_on` from Order → Customer with
   note `"shares customer_id join key"`.
2. **`depends_on.refs`**: if a mart model for entity A refs models for
   entity B (e.g., `fct_orders` refs `stg_customers`), that indicates
   Order depends on Customer data — emit `depends_on` edge.
3. **Column lineage**: if `## Column Lineage Chains` in an order model
   shows `customer_id ← stg_customers.customer_id ← raw_data.customers_raw.id`,
   that confirms the FK relationship.

Emit an edge only when at least one of these signals is present. Do not
invent edges from name similarity alone.

### 4.3 Frontmatter shape

```yaml
relationships:
  - type: depends_on
    target: order.md           # bare slug — sibling entity in same folder
    note: "shares order_id join key; one customer has many orders"
  - type: depends_on
    target: ../concepts/active-customer.md   # cross-folder: prefix ../<folder>/
    note: "status field encodes the active-customer rule"
```

Target resolution rule (mirrors SCHEMA.md):
- Sibling knowledge page in same folder (`entities/`) → bare slug: `order.md`
- Cross-folder knowledge page → relative path: `../metrics/mrr.md`,
  `../concepts/active-customer.md`
- Never use absolute paths or `[[wikilinks]]`.

### 4.4 Body `## Relationships` section

Render the same edges in human-readable list form:

```markdown
## Relationships

- depends_on → [Order](order.md) — one customer has many orders; shares `customer_id` join key
- depends_on → [Active Customer](../concepts/active-customer.md) — `status` field encodes the active-customer rule
```

Format: `- <edge_type> → [<Title>](<target>) — <note>`

---

## 5. Frontmatter — provenance and lifecycle

Every entity page MUST carry the full shared provenance block from
SCHEMA.md. Required fields for Phase B distillation:

### 5.1 `derived_from`

List every evidence model `unique_id` the page was distilled from.
The unique_id format is `model.<package>.<model_name>`.

```yaml
derived_from:
  - model.example_dbt_project.stg_customers
  - model.example_dbt_project.int_customers
  - model.example_dbt_project.dim_customers
  - model.example_dbt_project.fct_customer_activity
```

Include ALL evidence models consulted — not just the canonical mart.
This is the freshness anchor: refresh uses this list to detect when
a knowledge page needs re-distilling.

### 5.2 `last_changed_by`

Set to the commit SHA or PR identifier of the init/refresh run that
produced this page. During init, use the session identifier or a
placeholder `"init-YYYY-MM-DD"` if no commit SHA is available yet.

```yaml
last_changed_by: "init-2026-06-01"
```

### 5.3 `status` lifecycle

| Status | When to use |
|---|---|
| `seed` | Auto-stub created by refresh; body not yet filled |
| `developing` | Phase B has distilled content; human review not yet done |
| `mature` | Reviewed and trusted by a domain expert |
| `archived` | Entity no longer appears in evidence layer |

Phase B init distillation produces pages at `developing` status.

### 5.4 `summary`

One sentence, maximum 200 characters. This is used by tiered query
without loading the full page body — keep it dense and business-facing.

```yaml
summary: "A person or organisation that has placed at least one paid order; the primary grain of revenue attribution."
```

### 5.5 `stale` fields

Set at distillation time:

```yaml
stale: false
stale_at: null
stale_reason: null
```

Refresh will overwrite these fields if any `derived_from` evidence model changes.

### 5.6 `tags`

Optional. Use tags from the dbt models' `config.tags` where they carry
business meaning (e.g., `["finance"]`, `["product"]`). Do not carry
over technical tags (`["daily", "incremental"]`).

---

## 6. Worked example

### Input: synthetic 3-tier evidence set

Three evidence models extracted from a manifest for a small e-commerce project:

**`_evidence/models/stg_customers.md`** (frontmatter excerpt):
```yaml
unique_id: model.ecom_project.stg_customers
type: model
depends_on:
  refs: []
  sources:
    - "raw_data.customers_raw"
feeds_into:
  - int_customers
  - fct_orders
columns:
  - name: customer_id
    description: "Source customer identifier from Shopify (raw integer id)"
    declared_in_schema_yml: true
    tests: [not_null]
    sources: []
  - name: email
    description: "Customer email address, normalised to lowercase"
    declared_in_schema_yml: true
    tests: [not_null, unique]
    sources: []
  - name: first_paid_at
    description: "Timestamp of first completed (non-trial) order"
    declared_in_schema_yml: true
    tests: []
    sources: []
```

**`_evidence/models/dim_customers.md`** (frontmatter excerpt):
```yaml
unique_id: model.ecom_project.dim_customers
type: model
depends_on:
  refs:
    - stg_customers
    - int_customers
feeds_into:
  - fct_orders
  - mart_finance_daily
columns:
  - name: customer_id
    description: "Primary key — unique customer account"
    declared_in_schema_yml: true
    tests: [not_null, unique]
    sources:
      - "stg_customers.customer_id"
  - name: status
    description: "Lifecycle state: active | churned | paused. Set by int_customers status-resolution logic."
    declared_in_schema_yml: true
    tests: [not_null]
    sources:
      - "int_customers.customer_status"
  - name: acquired_at
    description: "Date of first paid order. Determines cohort."
    declared_in_schema_yml: true
    tests: []
    sources:
      - "stg_customers.first_paid_at"
```

**`_evidence/models/fct_orders.md`** (frontmatter excerpt):
```yaml
unique_id: model.ecom_project.fct_orders
type: model
depends_on:
  refs:
    - dim_customers
    - stg_orders
columns:
  - name: order_id
    description: "Primary key — unique order"
    tests: [not_null, unique]
  - name: customer_id
    description: "FK to dim_customers — the customer who placed this order"
    tests: [not_null]
    sources:
      - "dim_customers.customer_id"
```

### Output: `entities/customer.md`

```markdown
---
type: knowledge-entity
title: Customer
status: developing
summary: "A person or organisation with at least one Shopify account; the primary grain for revenue attribution and lifecycle analysis."
updated: 2026-06-01
derived_from:
  - model.ecom_project.stg_customers
  - model.ecom_project.dim_customers
relationships:
  - type: depends_on
    target: order.md
    note: "one customer has many orders; fct_orders.customer_id FK to dim_customers.customer_id"
last_changed_by: "init-2026-06-01"
tags: []
stale: false
stale_at: null
stale_reason: null
---

## Summary

A Customer is a person or organisation that holds a Shopify account in
the e-commerce platform. Customers are the primary subject of retention
and revenue analysis: each metric that measures "how many customers" or
"how much revenue per customer" aggregates over this entity.

## Grain

One row = one customer account (unique `customer_id`).

The canonical model is `dim_customers`. `stg_customers` is a staging
layer that normalises raw Shopify IDs before dimension table population.

## Fields

| Field | Meaning | Evidence column |
|---|---|---|
| `customer_id` | Unique identifier for the customer account. Primary key; sourced from the Shopify raw integer id. | `dim_customers.customer_id` |
| `email` | Customer email address, normalised to lowercase. Used as the human-readable customer lookup key. | `stg_customers.email` |
| `status` | Current lifecycle state: `active` (placed an order recently), `churned` (no activity past threshold), `paused` (subscription on hold). Set by the int_customers status-resolution logic. | `dim_customers.status` |
| `acquired_at` | Date of the customer's first completed (non-trial) paid order. Defines cohort membership for retention analysis. | `dim_customers.acquired_at` |

## Relationships

- depends_on → [Order](order.md) — one customer has many orders; `fct_orders.customer_id` is a FK to `dim_customers.customer_id`

## Caveats

- `status` values are resolved by `int_customers` business logic; no
  dbt test enforces that all three enum values are valid — data-quality
  risk if the upstream CRM adds new status codes.
- `acquired_at` is `null` for trial accounts that never converted.
  Any cohort query on `acquired_at` must filter `WHERE acquired_at IS NOT NULL`.
- Column-level lineage is extracted one hop at a time; for the full
  chain from `customer_id` back to `raw_data.customers_raw.id` see
  `## Column Lineage Chains` in the `stg_customers` evidence page.

## Evidence

- [stg_customers](../_evidence/models/stg_customers.md)
- [dim_customers](../_evidence/models/dim_customers.md)
```

### Distillation trace (for the worked example)

| Step | What was done |
|---|---|
| Entity identification | Three models share root noun `customer` → Customer entity. `fct_orders` refs `dim_customers` → separate Order entity signalled by shared FK. |
| Grain | `dim_customers.customer_id` has `tests: [not_null, unique]` → canonical grain model; grain = one customer. |
| Fields | Included: `customer_id` (PK), `email` (lookup), `status` (business enum), `acquired_at` (cohort anchor). Excluded: `_fivetran_synced` (plumbing). |
| Relationships | `fct_orders.customer_id` FK description → `depends_on` edge Order→Customer (recorded on the Order entity page) and Customer→Order. |
| `derived_from` | Both staging and dimension models included; `fct_orders` excluded (it belongs to the Order entity's `derived_from`). |
| Caveats | Sourced from missing not_null tests on `status` enum + null behaviour of `acquired_at` as noted in schema.yml descriptions. |

---

## 7. Anti-patterns to avoid

| Anti-pattern | Correct approach |
|---|---|
| Creating one entity page per model (`stg_customers`, `dim_customers` each get a page) | One entity page per business object; list all evidence models in `derived_from`. |
| Putting evidence model links in `relationships:` frontmatter | Evidence belongs in `derived_from:` + `## Evidence` only. `relationships:` = knowledge→knowledge edges only. |
| Using `[[wikilinks]]` for any link | Always use standard markdown links: `[Title](slug.md)`. |
| Inventing entity edges from name similarity alone | Emit a `depends_on` / `joins` edge only when backed by a join key, FK description, or `depends_on.refs` signal. |
| Writing a 400-char `summary` | Summary is capped at 200 chars — tiered query reads it without loading the body. |
| Setting `status: mature` at distillation time | Phase B distillation produces `developing`; a human reviewer upgrades to `mature`. |
| Omitting plumbing-column exclusions | Do not include `_fivetran_synced`, `dbt_updated_at`, surrogate hash columns in `## Fields`. |
