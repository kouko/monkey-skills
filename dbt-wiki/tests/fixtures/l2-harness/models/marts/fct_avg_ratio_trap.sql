-- Trap model (Task 2): computes the mathematically correct weighted ratio
-- from seed_avg_ratio's numerator/denominator components. The seed also
-- carries a pre-aggregated `ratio` column per row; naively averaging that
-- column (AVG(ratio)) is the well-known trap this fixture exists to guard
-- against — it must NOT be used here.
select
    sum(numerator) / sum(denominator) as weighted_ratio
from {{ ref('seed_avg_ratio') }}
