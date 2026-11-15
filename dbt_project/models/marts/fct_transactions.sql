-- fct_transactions.sql
-- Main fact table for transactions, enriched with user data and realistic bank revenue.

with transactions as (
    select * from {{ ref('stg_transactions') }}
),

users as (
    select * from {{ ref('stg_users') }}
),

joined as (
    select
        t.transaction_id,
        t.user_id,
        t.transaction_at,
        t.amount_usd,
        t.currency,
        t.transaction_type,
        t.category,
        t.merchant,
        t.device_type,
        t.country as transaction_country,
        t.status,
        t.is_fraud_flag,
        
        -- User attributes
        u.segment as user_segment,
        u.country as user_primary_country,
        
        -- Realistic Bank Revenue Logic (Revolut-style):
        -- 1. Interchange fee: 0.2% on card payments and subscriptions
        -- 2. ATM fee: 2% on withdrawals
        -- 3. FX fee: 1% if currency is not USD (since our base is USD)
        case 
            when t.status = 'Success' then
                (case when t.transaction_type in ('card_payment', 'subscription') then t.amount_usd * 0.002 else 0 end) +
                (case when t.transaction_type = 'atm_withdrawal' then t.amount_usd * 0.02 else 0 end) +
                (case when t.currency != 'USD' and t.transaction_type != 'atm_withdrawal' then t.amount_usd * 0.01 else 0 end)
            else 0 
        end as revenue_usd
        
    from transactions t
    left join users u on t.user_id = u.user_id
)

select * from joined