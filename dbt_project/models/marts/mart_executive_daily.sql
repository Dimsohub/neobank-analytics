-- mart_executive_daily.sql
-- Daily aggregated KPIs for the Executive / Business Overview dashboard.

with transactions as (
    select * from {{ ref('fct_transactions') }}
),

daily_metrics as (
    select
        transaction_at::date as transaction_date,
        
        -- 1. Total Volume (Only successful transactions count towards volume)
        sum(case when status = 'Success' then amount_usd else 0 end) as total_volume_usd,
        
        -- 2. Total Revenue (Calculated in fct_transactions)
        sum(revenue_usd) as total_revenue_usd,
        
        -- 3. Active Users (DAU)
        count(distinct user_id) as daily_active_users,
        
        -- 4. Average Transaction Value (Successful only)
        avg(case when status = 'Success' then amount_usd else null end) as avg_transaction_value_usd,
        
        -- 5. Transaction Count
        count(transaction_id) as total_transactions,
        
        -- 6. Fraud metrics for the day
        sum(case when is_fraud_flag = 1 then 1 else 0 end) as fraud_transactions,
        sum(case when status = 'Blocked_Fraud' then amount_usd else 0 end) as blocked_fraud_volume_usd

    from transactions
    group by 1
)

select * from daily_metrics
order by transaction_date