-- mart_spend_by_category.sql
-- Aggregates spending volume and transaction counts by category and user segment.
-- Used for the Donut Chart on the Customer Behavior dashboard.

with transactions as (
    select * from {{ ref('fct_transactions') }}
    where status = 'Success' -- We only analyze successful payments
),

category_metrics as (
    select
        category,
        user_segment,
        count(transaction_id) as total_transactions,
        sum(amount_usd) as total_spend_usd,
        round(avg(amount_usd), 2) as avg_transaction_value_usd
    from transactions
    group by 1, 2
)

select * from category_metrics
order by total_spend_usd desc