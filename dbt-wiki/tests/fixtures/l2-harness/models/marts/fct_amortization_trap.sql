-- Trap model (Task 5): "today" is the fixed reference date 2026-07-01 for
-- this fixture (DuckDB has no wall-clock notion of the fixture's present, so
-- the fixture's "today" is hardcoded here and in seed_amortization's real
-- rows). Real amortization snapshots land on/before it; a forward-dated
-- placeholder row (2099-12-31) sits after it. Taking MAX(as_of_date) naively
-- selects that placeholder — the trap this fixture guards against. The
-- correct as-of-today snapshot filters to as_of_date <= today FIRST, then
-- takes the latest remaining snapshot; it must NOT be MAX over all rows.
with as_of_today as (
    select
        cast(as_of_date as date) as as_of_date,
        book_value
    from {{ ref('seed_amortization') }}
    where cast(as_of_date as date) <= date '2026-07-01'
)
select
    as_of_date,
    book_value
from as_of_today
where as_of_date = (select max(as_of_date) from as_of_today)
