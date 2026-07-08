select
    id,
    upper(region) as region,
    category,
    amount
from {{ ref('seed_filler') }}
