-- models/gold/gold_customer_360.sql
-- THE single customer view — joins all 4 sources

{{ config(materialized='table') }}

with txn as (
    select
        customer_id,
        count(distinct order_id)                    as total_orders,
        round(sum(amount_inr - discount_inr), 2)    as total_spend_inr,
        round(avg(amount_inr - discount_inr), 2)    as avg_order_value,
        0                                           as total_returns,
        0                                           as return_rate,
        max(timestamp_utc) 		            as last_order_date,
        case
            when sum(amount_inr - discount_inr) > 500000 then 'Platinum'
            when sum(amount_inr - discount_inr) > 100000 then 'Gold'
            when sum(amount_inr - discount_inr) > 25000  then 'Silver'
            else 'Bronze'
        end                                         as clv_tier
    from {{ ref('silver_transactions') }}
    group by customer_id
),

web as (
    select
        customer_id,
        count(*)                                    as total_web_events,
        count(case when event_type='add_to_cart' then 1 end) as cart_adds,
        mode() within group (order by device)       as preferred_device,
        mode() within group (order by category)     as favourite_category
    from {{ ref('silver_web_logs') }}
    group by customer_id
),

rev as (
    select
        customer_id,
        count(*)                                    as total_reviews,
        round(avg(rating), 2)                       as avg_rating,
        count(case when sentiment='positive' then 1 end) as positive_reviews,
        count(case when sentiment='negative' then 1 end) as negative_reviews
    from {{ ref('silver_reviews') }}
    group by customer_id
)

select
    t.customer_id,
    coalesce(t.total_orders,     0)                as total_orders,
    coalesce(t.total_spend_inr,  0)                as total_spend_inr,
    coalesce(t.avg_order_value,  0)                as avg_order_value,
    coalesce(t.total_returns,    0)                as total_returns,
    coalesce(t.return_rate,      0)                as return_rate,
    t.clv_tier,
    t.last_order_date,
    coalesce(w.total_web_events, 0)                as total_web_events,
    coalesce(w.cart_adds,        0)                as cart_adds,
    w.preferred_device,
    w.favourite_category,
    coalesce(r.total_reviews,    0)                as total_reviews,
    coalesce(r.avg_rating,       0)                as avg_rating,
    coalesce(r.positive_reviews, 0)                as positive_reviews,
    coalesce(r.negative_reviews, 0)                as negative_reviews,
    current_timestamp                              as refreshed_at
from txn t
left join web w using (customer_id)
left join rev r using (customer_id)