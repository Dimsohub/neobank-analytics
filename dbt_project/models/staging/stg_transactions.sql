-- stg_transactions.sql
-- Standardizing transaction data

with raw_transactions as (
    -- Referencing the source table we declared in sources.yml
    select * from {{ source('neobank_raw', 'raw_transactions') }}
)

select
    transaction_id::int as transaction_id,
    user_id::int as user_id,
    timestamp::timestamp as transaction_at,
    amount_usd::float as amount_usd,
    currency::varchar as currency,
    converted_amount_usd::float as converted_amount_usd,
    transaction_type::varchar as transaction_type,
    category::varchar as category,
    merchant::varchar as merchant,
    device_type::varchar as device_type,
    country::varchar as country,
    status::varchar as status,
    is_fraud::int as is_fraud_flag
from raw_transactions