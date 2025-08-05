with
    t (total_cost) as (
        select
            sum(cost)
        from
            aws_cost_report
        where
            start_date >= '2025-07-01'
            and start_date < '2025-08-01'
    )
with
    c (cost, category) as (
        select
            sum(cost) as cost,
            r.cost_category
        from
            aws_cost_report r,
            t
        where
            r.start_date >= '2025-07-01'
            and r.start_date < '2025-08-01'
        group by
            r.cost_category,
            t.total_cost
        order by
            cost desc
    )
select
    c.cost,
    c.category,
    round((cost / t.total_cost) * 100, 0) as percentage
from
    c,
    t