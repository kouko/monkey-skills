-- Trap model (Task 4): passes seed_categorical's `status` column through
-- unchanged, preserving its fixed value_domain (the accepted set
-- {active, churned, trial}). The .yml declares an `accepted_values` generic
-- dbt test on this column, so `dbt build` fails if any out-of-domain value
-- ever leaks in — the categorical trap this fixture guards against, where a
-- silent transformation (an unmapped CASE branch, a typo) emits a value
-- outside the declared domain without anyone noticing.
select
    customer_id,
    status
from {{ ref('seed_categorical') }}
