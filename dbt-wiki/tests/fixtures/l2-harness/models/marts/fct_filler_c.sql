select
    category,
    sum(amount) as total_amount,
    count(*) as record_count
from {{ ref('stg_filler_a') }}
group by category
