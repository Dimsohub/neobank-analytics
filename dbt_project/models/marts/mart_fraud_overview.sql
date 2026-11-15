-- mart_fraud_overview.sql
-- Aggregates transaction statuses and fraud metrics for the Risk Control dashboard.

with transactions as (
    select * from {{ ref('fct_transactions') }}
    -- Filter out future dates
    where transaction_at <= '2026-03-31'
),

daily_risk_metrics as (
    select
        transaction_at::date as transaction_date,
        status,
        count(transaction_id) as transaction_count,
        sum(amount_usd) as total_volume_usd,
        
        -- Correct math: calculate fraud rate per date and status
        round(
            (sum(case when is_fraud_flag = 1 then 1 else 0 end)::float / count(transaction_id)) * 100, 2
        ) as fraud_rate_pct
        
    from transactions
    group by 1, 2
)

select * from daily_risk_metrics
order by transaction_date, status