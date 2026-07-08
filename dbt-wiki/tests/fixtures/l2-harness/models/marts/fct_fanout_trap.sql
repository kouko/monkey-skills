-- Trap model (Task 3): pre-aggregates seed_fanout_line_items (one-to-many on
-- order_id) by order BEFORE joining to seed_fanout_orders, so each order's
-- shipping_fee (an order-grain attribute) is added exactly once per order.
-- Naively joining orders to raw line_items then summing quantity * unit_price
-- + shipping_fee re-adds shipping_fee once per line item — the fan-out trap
-- this fixture guards against; it must NOT be done here.
with line_items_by_order as (
    select
        order_id,
        sum(quantity * unit_price) as line_item_total
    from {{ ref('seed_fanout_line_items') }}
    group by order_id
)
select
    o.order_id,
    li.line_item_total + o.shipping_fee as order_total
from {{ ref('seed_fanout_orders') }} as o
join line_items_by_order as li on o.order_id = li.order_id
