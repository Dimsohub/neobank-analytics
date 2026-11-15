-- mart_customer_segmentation.sql
-- Segments users into High, Medium, and Low value tiers based on total spend volume.

with user_spend as (
    select
        user_id,
        sum(amount_usd) as total_spend_usd,
        count(transaction_id) as total_transactions
    from {{ ref('fct_transactions') }}
    where status = 'Success'
    group by 1
),

segmented as (
    select
        *,
        -- Divide users into 3 equal groups based on their total spend (1 = top spenders)
        ntile(3) over (order by total_spend_usd desc) as spend_group
    from user_spend
)

select
    s.user_id,
    u.segment, -- Standard, Premium, VIP
    s.total_spend_usd,
    s.total_transactions,
    -- Assign readable labels based on the NTILE group
    case
        when s.spend_group = 1 then 'High-Value'
        when s.spend_group = 2 then 'Medium-Value'
        else 'Low-Value'
    end as value_tier
from segmented s
left join {{ ref('dim_users') }} u on s.user_id = u.user_id
order by s.total_spend_usd desc