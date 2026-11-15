-- mart_subscriptions.sql
-- Analyzes recurring payments (subscriptions) by merchant and user segment.

with transactions as (
    select * from {{ ref('fct_transactions') }}
    -- Only successful subscription payments
    where transaction_type = 'subscription' 
      and status = 'Success'
),

subscription_metrics as (
    select
        merchant,
        user_segment,
        count(transaction_id) as total_subscriptions,
        count(distinct user_id) as unique_subscribers,
        sum(amount_usd) as total_subscription_volume_usd,
        round(avg(amount_usd), 2) as avg_monthly_fee_usd
    from transactions
    group by 1, 2
)

select * from subscription_metrics
order by total_subscription_volume_usd desc