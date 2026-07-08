-- Filler mart (L2 harness Task 7): per-category average ticket, commented
-- column-by-column — the densely-commented end of the fixture's spectrum.
select
    category,                   -- product category label (widget / gadget)
    avg(amount) as avg_amount,  -- mean transaction amount within the category
    count(*) as record_count    -- number of filler records in the category
from {{ ref('stg_filler_a') }}
group by category
