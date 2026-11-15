-- mart_fraud_rate_trend.sql
-- Calculates the TRUE overall fraud rate per month (weighted average).
-- This prevents averaging daily percentages, which causes misleading spikes.

with transactions as (
    select * from {{ ref('fct_transactions') }}
    where transaction_at <= '2026-03-31'
)

select
    date_trunc('month', transaction_at)::date as transaction_date,
    count(transaction_id) as total_transactions,
    sum(case when is_fraud_flag = 1 then 1 else 0 end) as fraud_transactions,
    -- Correct math: Total Fraud / Total Transactions * 100
    round(
        (sum(case when is_fraud_flag = 1 then 1 else 0 end)::float / count(transaction_id)) * 100, 2
    ) as true_fraud_rate_pct
from transactions
group by 1
order by 1