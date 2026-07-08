-- Trap model (Task 6): each logical entity's rows are split across regions
-- (seed_regional_twins.region), so the full-scope amount must union ALL
-- regions before aggregating. Grouping by entity_id over every region's rows
-- captures the complete scope. Naively scanning a single region (e.g.
-- WHERE region = 'us') silently drops the other regions' twin rows and
-- undercounts — the scope-undercount trap this fixture guards against; it
-- must NOT be done here.
select
    entity_id,
    sum(amount) as full_scope_amount
from {{ ref('seed_regional_twins') }}
group by entity_id
