-- dim_users.sql
-- User dimension table with cohort information for retention analysis.

with users as (
    select * from {{ ref('stg_users') }}
)

select
    user_id,
    created_at,
    segment,
    country,
    spend_tier,
    -- Extract the cohort month (e.g., '2025-01-01') for retention analysis
    date_trunc('month', created_at)::date as cohort_month
from users