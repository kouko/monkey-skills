---
title: dbt-wiki Lineage
type: lineage
last_updated: <YYYY-MM-DD>
manifest_sha: <md5>
---

# dbt Project Lineage (DAG)

> Auto-generated from `target/manifest.json` (model-level) plus sqlglot
> column-level extraction. Regenerated on every `/dbt-wiki:init` and
> `/dbt-wiki:refresh`. Do not edit by hand.

## Statistics

- Models: <N>
- Sources (declared): <N>
- DAG depth: <max levels from any source to any leaf model>
- Leaf models (no downstream): <N>
- Root sources (no model upstream within project): <N>

## ASCII Tree (per source/seed)

For each declared source / seed, a downward traversal showing all
descendant models. Indentation = DAG depth. Same model may appear under
multiple sources; the symbol `→` marks first occurrence vs `↺` for repeat.

```
source: raw_data.orders_raw
  → stg_orders [view]
    → int_orders_with_customer [ephemeral]
      → fct_orders [table, incremental]
        → dim_orders_summary [table]
        → mart_finance_daily [table]
    → stg_orders_dedup [view]
      → ↺ fct_orders
```

(auto-populated by init)

## Adjacency List (per model, alphabetical)

For each model, its direct parents (depends_on) and direct children
(feeds_into). Use this when ASCII tree is too tall.

### fct_orders
- **depends_on (model refs)**: [stg_orders](models/stg_orders.md), [stg_customers](models/stg_customers.md), [int_orders_with_customer](models/int_orders_with_customer.md)
- **depends_on (sources)**: raw_data.orders_raw
- **depends_on (macros)**: dbt_utils.surrogate_key, dbt_utils.safe_cast
- **feeds_into (models)**: [dim_orders_summary](models/dim_orders_summary.md), [mart_finance_daily](models/mart_finance_daily.md)
- **column-level lineage extracted**: yes (sqlglot)

(auto-populated by init for every model)

## Tier-aggregated view (large projects only, >500 nodes)

If model count exceeds 500, this section appears with:

```
source: raw_data.*
  → Staging (N models)
    → Intermediate (M models)
      → Marts (K models)
        → Marts MSD (L models)
```

Detail per tier in subsections below.
