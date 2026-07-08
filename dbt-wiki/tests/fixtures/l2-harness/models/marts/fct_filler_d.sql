-- Filler mart (L2 harness Task 7): plain per-region revenue rollup. Sparsely
-- commented — a single header note, no column-level comments — a deliberate
-- mid-point on the fixture's comment-density spectrum.
select
    region,
    sum(amount) as total_amount
from {{ ref('stg_filler_b') }}
group by region
