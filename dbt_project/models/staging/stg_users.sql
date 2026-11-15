-- stg_users.sql
-- Standardizing user data for downstream analytics

with raw_users as (
    -- Referencing the source table we declared in sources.yml
    select * from {{ source('neobank_raw', 'raw_users') }}
)

select
    user_id::int as user_id,
    account_created_at::timestamp as created_at,
    user_segment::varchar as segment,
    primary_country::varchar as country,
    avg_spend_tier::float as spend_tier
from raw_users