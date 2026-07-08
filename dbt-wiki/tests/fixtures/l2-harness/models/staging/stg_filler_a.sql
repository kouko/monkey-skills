-- Filler staging model (L2 harness Task 7). Non-trap: a plain pass-through
-- over seed_filler, commented column-by-column. One of the densely-commented
-- fillers that exercise dbt-wiki's comments-as-source-of-truth assumption on
-- ordinary models (as opposed to the trap models' catch-the-mistake role).
select
    id,        -- surrogate key, one row per filler record
    category,  -- product category label (widget / gadget)
    region,    -- sales region label (north / south / east / west)
    amount     -- transaction amount in whole currency units
from {{ ref('seed_filler') }}
