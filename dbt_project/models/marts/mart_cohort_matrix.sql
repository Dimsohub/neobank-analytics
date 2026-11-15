with first_tx as (
    select
        user_id,
        date_trunc('month', min(transaction_at))::date as cohort_month
    from {{ ref('fct_transactions') }}
    where status = 'Success'
      and transaction_at <= '2026-03-31' -- <-- ОБРЕЗАЕМ БУДУЩЕЕ
    group by 1
),
cohort_sizes as (
    select cohort_month, count(distinct user_id) as total_users
    from first_tx
    group by 1
    having count(distinct user_id) >= 10 -- <-- ИГНОРИРУЕМ КРОШЕЧНЫЕ КОГОРТЫ (меньше 10 чел)
),
activity as (
    select
        f.cohort_month,
        date_trunc('month', t.transaction_at)::date as activity_month,
        count(distinct t.user_id) as active_users
    from first_tx f
    join {{ ref('fct_transactions') }} t on f.user_id = t.user_id
    where t.status = 'Success'
      and t.transaction_at <= '2026-03-31' -- <-- ОБРЕЗАЕМ БУДУЩЕЕ
    group by 1, 2
)
select
    c.cohort_month,
    c.total_users,
    100.0 as month_0,
    max(case when a.activity_month = c.cohort_month + interval 1 month then round((a.active_users::float / c.total_users) * 100, 2) else 0 end) as month_1,
    max(case when a.activity_month = c.cohort_month + interval 2 month then round((a.active_users::float / c.total_users) * 100, 2) else 0 end) as month_2,
    max(case when a.activity_month = c.cohort_month + interval 3 month then round((a.active_users::float / c.total_users) * 100, 2) else 0 end) as month_3,
    max(case when a.activity_month = c.cohort_month + interval 4 month then round((a.active_users::float / c.total_users) * 100, 2) else 0 end) as month_4,
    max(case when a.activity_month = c.cohort_month + interval 5 month then round((a.active_users::float / c.total_users) * 100, 2) else 0 end) as month_5,
    max(case when a.activity_month = c.cohort_month + interval 6 month then round((a.active_users::float / c.total_users) * 100, 2) else 0 end) as month_6
from cohort_sizes c
left join activity a on c.cohort_month = a.cohort_month
group by 1, 2
order by 1