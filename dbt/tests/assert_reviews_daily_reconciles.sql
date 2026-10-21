-- Reconciliation: the daily table must contain every deduplicated review
-- exactly once. Returns a row (= test fails) for any game where totals differ.

with daily as (
    select appid, sum(reviews) as reviews_in_daily
    from {{ ref('fct_reviews_daily') }}
    group by appid
),

latest as (
    select appid, count(*) as reviews_unique
    from {{ ref('int_reviews_latest') }}
    group by appid
)

select l.appid, l.reviews_unique, d.reviews_in_daily
from latest l
left join daily d using (appid)
where d.reviews_in_daily is distinct from l.reviews_unique
