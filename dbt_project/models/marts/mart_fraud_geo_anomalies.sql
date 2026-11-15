-- mart_fraud_geo_anomalies.sql
-- Identifies suspicious transactions where a user changes country within a short time frame.

with transactions as (
    select 
        transaction_id,
        user_id,
        transaction_at,
        amount_usd,
        transaction_country,
        user_primary_country,
        is_fraud_flag,
        status,
        -- Get the country and timestamp of the user's PREVIOUS transaction
        lag(transaction_country) over (partition by user_id order by transaction_at) as prev_country,
        lag(transaction_at) over (partition by user_id order by transaction_at) as prev_transaction_at
    from {{ ref('fct_transactions') }}
),

anomalies as (
    select
        transaction_id,
        user_id,
        transaction_at,
        amount_usd,
        transaction_country,
        user_primary_country,
        prev_country,
        prev_transaction_at,
        is_fraud_flag,
        status,
        -- Calculate the time difference in minutes
        datediff('minute', prev_transaction_at, transaction_at) as minutes_since_last_tx
    from transactions
    where 
        -- Condition 1: Country changed from the previous transaction
        transaction_country != prev_country 
        -- Condition 2: Time between transactions is less than 60 minutes (impossible to travel physically)
        and datediff('minute', prev_transaction_at, transaction_at) < 60
)

select * from anomalies
order by minutes_since_last_tx asc