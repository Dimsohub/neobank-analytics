-- mart_user_retention.sql
-- Cohort analysis to track user retention over time.

with users as (
    select user_id, cohort_month from {{ ref('dim_users') }}
),

-- We only look at successful transactions to measure true activity
transactions as (
    select distinct 
        user_id, 
        date_trunc('month', transaction_at)::date as activity_month
    from {{ ref('fct_transactions') }}
    where status = 'Success'
),

-- Calculate how many months have passed since the user registered
cohort_activity as (
    select
        u.cohort_month,
        t.activity_month,
        u.user_id,
        -- Calculate the difference in months between activity and registration
        datediff('month', u.cohort_month, t.activity_month) as month_offset
    from users u
    join transactions t on u.user_id = t.user_id
),

-- Count how many users from each cohort were active in each month
cohort_sizes as (
    select 
        cohort_month, 
        count(distinct user_id) as total_cohort_users
    from users
    group by 1
),

retention_calc as (
    select
        ca.cohort_month,
        ca.month_offset,
        count(distinct ca.user_id) as active_users,
        cs.total_cohort_users,
        -- Retention rate in percentage
        round((count(distinct ca.user_id)::float / cs.total_cohort_users) * 100, 2) as retention_rate_pct
    from cohort_activity ca
    join cohort_sizes cs on ca.cohort_month = cs.cohort_month
    group by 1, 2, 4
)

select * from retention_calc
order by cohort_month, month_offset