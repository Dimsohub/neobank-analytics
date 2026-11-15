-- mart_fraud_velocity.sql
-- Identifies users with high transaction velocity (potential Card Testing).

with transactions as (
    select 
        transaction_id,
        user_id,
        transaction_at,
        amount_usd,
        is_fraud_flag,
        count(transaction_id) over (
            partition by user_id 
            order by transaction_at 
            range between interval '10 minutes' preceding and current row
        ) as tx_count_10min
    from {{ ref('fct_transactions') }}
),

high_velocity as (
    select *
    from transactions
    -- Lowered to 3 to catch anomalies in our synthetic dataset
    where tx_count_10min >= 3 
)

select * from high_velocity
order by tx_count_10min desc