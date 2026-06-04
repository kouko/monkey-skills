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

**Configuration / settings objects**: a 1:1 per-parent settings record
that has its own primary key (e.g. a per-account settings row, one row
per parent) IS an entity by the PK test — but title it to signal it is
configuration (`Account Settings`, not a bare event/object noun; reserve
the plain noun for the event/transaction entity if one exists) and say
so in the `## Summary`. If the record is purely 1:1
settings with no independent lifecycle and few fields, folding it into
the parent entity's page as a settings section is also acceptable —
create a separate page only when it has enough fields to stand alone.

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
they are two evidence models for one Customer entity. Note the boundary:
"the whole model family" means models for THIS entity only; a model from
a *different* entity's family that you read only to derive a relationship
edge does not belong in this page's `derived_from` (see §5.1
cross-entity exclusion rule).

---

## 2. Grain determination

The `## Grain` body section states what one row represents on the
**canonical mart / fact / dimension model** for the entity (not the
staging layer).

**Staging-only fallback**: if the entity's evidence contains no
mart/fact/dimension model (e.g. a staging-only slice), state the grain
from the most-downstream model available and add one line noting no
canonical mart exists yet — `Grain stated from staging; no mart/dim
model in this evidence slice.` A single-model (e.g. staging-only) entity
is valid: `derived_from` then carries one entry, and `status` stays
`seed`/`developing` to signal the entity will deepen once mart-layer
evidence is distilled.

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
| `acquired_at` | Date the customer first made a paying purchase (not trial start). Determines cohort membership. | `dim_customers.acquired_at` |
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

### 3.3 Where to source the Meaning AND which Evidence column to cite

**Meaning** — source priority order:
1. schema.yml `columns[].description` in the evidence model page
2. Inline SQL comments attached to that column (from `## Inline Comments` in evidence page)
3. LLM inference from column name + context of surrounding model description

Always prefer declared descriptions. LLM inference is a fallback only;
mark inferred entries with `(inferred)` if confidence is low.

**Evidence column** — canonical-model rule (resolves which model.column
to cite when the same datum appears in several models): cite the column
on the **canonical model** for the entity — the mart / fact / dimension
model that carries the entity's grain (the same model named in §2 Grain),
NOT the raw staging source it was renamed from. A staging column such as
`stg_customers.first_paid_at` that surfaces as `dim_customers.acquired_at`
on the dimension is cited at its canonical mart form `dim_customers.acquired_at`.
The mart column is the authoritative definition an analyst queries; the
staging lineage back to it is already recorded in the evidence page's
`## Column Lineage Chains`. Only when a field exists solely on a staging
model (never promoted to the mart) do you cite the staging column.

### 3.4 Value-domain capture for small-cardinality categorical columns

For any column with **≤ 20 distinct values** (a small-cardinality categorical
/ enum column), record the actual stored values as a `value_domain: [...]`
body annotation inline under that column's `## Fields` entry. This lets
SQL-generating consumers (e.g. a `pack` analytics bundle) map user-facing
terms to exact warehouse values without guessing.

**When to add it:**
- The column is categorical (region code, order status, tier, channel,
  currency code, etc.) AND has ≤ 20 distinct values.
- **Preferred:** you have production evidence — a `DISTINCT` query result, a dbt
  `accepted_values` test in schema.yml, or a documented enum from the source
  system. Tag these `(via: distinct)` or `(via: accepted_values)`.
- **Also permitted:** no production evidence exists but you can infer plausible
  values from SQL structure or column semantics. Tag these `(via: inferred)`.
  Inferred value_domains are a hypothesis, not ground truth; do not omit them
  solely because production evidence is unavailable.
- Omit entirely for free-text, numeric, or high-cardinality columns (IDs,
  timestamps, amounts). Those do not belong here; note them in `## Caveats`
  if the cardinality is surprising.

**Format** — body annotation only, NOT frontmatter:

```markdown
## Fields

| Field | Meaning | Evidence column |
|---|---|---|
| `region_code` | 2-letter region code stored in the warehouse. Lookup joins use this stored value, not the display name. `value_domain: [NL, EU, APAC] (via: accepted_values)` (user terms "Northland"/"Northland" map to stored value `NL`) | `dim_orders.region_code` |
| `order_status` | Lifecycle stage of the order. `value_domain: [pending, confirmed, shipped, cancelled] (via: distinct)` | `fct_orders.order_status` |
```

**Rules (aligned to SCHEMA §Value-domain / enum capture):**
1. Always append the `(via:)` provenance suffix so readers know the confidence
   level. Every `value_domain` entry must carry one of:
   - `(via: accepted_values)` — backed by a `schema.yml` `accepted_values`
     test; the list is authoritative and CI-enforced.
   - `(via: distinct)` — populated from a `DISTINCT` query over production
     data; accurate at distillation time but not CI-enforced.
   - `(via: inferred)` — derived from SQL structure or column semantics with
     NO `accepted_values` test and NO `DISTINCT` backing. This is a
     **hypothesis, not ground truth**: downstream SQL generators MUST treat
     this enum as provisional and avoid hard-failing on unlisted values.
   Inferred values ARE permitted — mark them `(via: inferred)` rather than
   omitting them.
2. Note any format surprise (suffix, locale, casing) that would cause an
   equality filter to miss rows — e.g. `value_domain: [NL, EU, APAC] (via: accepted_values)` not
   `["Northland", "Eurozone", "Asia-Pacific"]`.
3. If stored values differ from display labels, document both inline:
   `stored: NL`, `display: Northland`.
4. **≤ 20 values only.** Larger sets belong in a `knowledge-concept` page
   (e.g. "Status Codes") or a `## Caveats` note pointing to the source table.
5. The annotation goes in the **Meaning** cell of the Fields table (body
   annotation), not in the page's YAML frontmatter block.

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
| `depends_on` | entity → entity (directional) | The FROM entity holds a FK to the TO entity (child → parent, e.g. `opportunity.account_id` → Opportunity `depends_on` Account). Emit on the **FK-holder** side. |
| `joins` | entity ↔ entity (navigational) | A query-time join with no clear ownership direction, OR the **parent-side reverse edge** of a one-to-many you add for graph navigability (e.g. Account `joins` Opportunity so the graph is walkable from the parent). NOT a synonym of `depends_on`. |
| `converts_to` | entity → entity (lifecycle) | A **conversion / lifecycle-transition FK** — the FROM entity *becomes* the TO entity (e.g. a Lead's `converted_opportunity_id` / `converted_account_id`; once `is_converted`, the lead turns into an Opportunity + Account). Use this, NOT `depends_on`, for `converted_*`/`promoted_*`-style pointers — they are not ongoing structural dependencies. |

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

4. **Conversion / lifecycle FKs** → `converts_to`. A column like
   `converted_opportunity_id` / `converted_account_id` (often paired with
   an `is_converted` flag + `converted_date`) means the FROM entity
   *becomes* the TO entity. Emit `converts_to` from Lead → Opportunity /
   Account, NOT `depends_on` — a lead does not structurally depend on the
   account; the account is the artifact the lead turned into.

**Direction & reverse edges.** Encode the canonical edge on the
**FK-holder** (child) side as `depends_on → parent`. You MAY add the
reverse edge on the parent page as `joins → child` purely for graph
navigability ("show me all opportunities for this account") — but
`depends_on` and `joins` are NOT synonyms: the child→parent ownership is
`depends_on`; the parent→child convenience edge is `joins`.

**Dangling target (FK points to an un-distilled entity).** When a FK
target entity has no model in the current evidence slice (e.g. a
`converted_contact_id` whose Contact entity isn't in scope), still emit
the edge, and create a `status: seed` stub page for the target with
`derived_from: []` and a one-line body noting it is an auto-stub — so the
markdown link resolves. A later init/refresh that distills the target
promotes it `seed → developing`. Never drop the edge.

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
  - model.ecom_project.stg_customers
  - model.ecom_project.int_customers
  - model.ecom_project.dim_customers
  - model.ecom_project.fct_customer_activity
```

Include all evidence models **belonging to THIS entity's model family**
— not just the canonical mart, but also its staging / intermediate
ancestors (e.g. `stg_customers`, `int_customers`, `dim_customers`).
This is the freshness anchor: refresh uses this list to detect when a
knowledge page needs re-distilling.

**Cross-entity exclusion rule.** An evidence model that belongs to
ANOTHER entity's family — consulted only to derive a `## Relationships`
edge, never to describe this entity's own fields/grain — must NOT be
added to this entity's `derived_from`. It lives in that other entity's
`derived_from`. Example: when distilling Customer, you read `fct_orders`
to confirm the `fct_orders.customer_id` FK that yields the Customer↔Order
edge, but `fct_orders` is an Order-family model — it goes in
`order.md`'s `derived_from`, NOT `customer.md`'s. Adding it here would
make Customer falsely flag stale every time an Order model changes,
producing spurious re-distill triggers. Rule of thumb: a model earns a
slot in `derived_from` only if it sourced a row of this entity's
`## Fields` table or its `## Grain` — not if it only sourced a
relationship edge.

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

### 5.7 Alias capture for project-language retrieval (fully automatic)

During distillation, automatically populate the `aliases:` frontmatter
list — no human step required. Collect body terms that a query author
might search for but that:

- **(a)** do NOT appear in the page's `summary`, AND
- **(b)** an LLM could NOT bridge from the summary alone.

For entities these are typically: GL / account codes (e.g. `5010`),
project abbreviations (e.g. `MRR`, `NRR`, `lvl1`–`lvl3`), and non-obvious
project synonyms for the entity (e.g. `recurring-rev` for a recurring-revenue
entity).

**EXCLUDE**: terms already in the title or summary, generic words
(`customer`, `order`, `id`), and anything an LLM would naturally infer
from the summary alone.

**Tie-breaker**: when uncertain, prefer inclusion — a false-positive
alias costs a prune; a missed alias is permanent.

Also set `title_local`: the entity's title in the project's working
language. Use the exact term as it appears in the project's schema.yml
descriptions or internal documentation — NOT a translation of the
English title.

Both fields are emitted automatically on every `init` and `refresh`
run; a human may prune `aliases` later (pruning is never required, but
never re-add a term that was intentionally pruned).

**Frontmatter shape (extend the §5 provenance template)**:

```yaml
aliases:
  - "5010"            # GL account code used in internal docs, not in summary
  - MRR               # project abbreviation not inferable from English title
  - recurring-rev     # non-obvious project synonym for the entity
title_local: 經常性收入  # entity title in project's working language (from schema.yml)
```

---

## Caveats — severity/type tag convention

Each caveat bullet in `## Caveats` **may** be prefixed with one of the
following tags. Tagging is optional but recommended: it lets query
consumers and future distillers triage caveats at a glance without
reading every bullet.

| Tag | Meaning | When to use |
|---|---|---|
| `[bug]` | Produces wrong results if not handled | A source defect, unfiltered row, or aggregation trap that causes silent over/under-counting unless the query explicitly guards against it |
| `[limitation]` | Known coverage or scope gap, by design or upstream | A column that is NULL for a known segment, a model that covers only one region, or a metric that excludes a class of records by design |
| `[temporal]` | Date/period semantics gotcha | Future-dating artefacts, snapshot-vs-event-vs-accrual ambiguity, or a date column that does not mean what its name implies |
| `[no-test]` | No dbt test guards this datum | A column or invariant with no `not_null`, `unique`, `accepted_values`, or relationship test — data-quality risk is undetected by CI |

**Rules:**
- Use at most **one tag per bullet**.
- Omit the tag entirely if none of the four categories fits; plain bullets are valid.
- Do **not** invent new tags — use plain text to describe anything outside the four categories.

**Generic example:**

```markdown
## Caveats

- **[bug]** Unfiltered total row: source CSV appends a grand-total row;
  `SUM(qty)` over-counts unless `WHERE key IS NOT NULL`.
- **[limitation]** Coverage is domestic orders only; cross-border records
  are excluded upstream and will never appear in this model.
- **[temporal]** `close_date` reflects the accounting-close date, not
  the event date; for event-time analysis use `event_at` instead.
- **[no-test]** `tier` has no `accepted_values` test; new tiers added
  upstream will silently appear as unmapped values.
```

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
aliases:
  - cust        # project abbreviation used in internal SQL (e.g. cust_id)
  - buyer       # synonym used in Shopify event schema
title_local: null  # project uses English throughout; no alternate-language title
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
