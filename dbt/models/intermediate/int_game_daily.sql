-- One row per game per day: review totals (all languages) and player metrics.
-- Days without reviews inside a game's review history get 0, not a missing
-- row: "nobody wrote a review" is information. Days before a game's first
-- review (or for games whose reviews we do not collect) stay NULL = unknown.
-- The last day of data is usually incomplete (the collector runs once a
-- day), so the series stops at the last COMPLETE day.

with reviews as (

    -- sum() over a bigint returns numeric in PostgreSQL, and Power Query reads
    -- an unconstrained numeric as a floating point Double. These are counts, so
    -- cast them back to bigint and keep them integers all the way to the model.
    select
        appid,
        date,
        cast(sum(reviews) as bigint)                          as reviews,
        cast(sum(positive_reviews) as bigint)                 as positive_reviews,
        cast(sum(negative_reviews) as bigint)                 as negative_reviews,
        cast(sum(steam_purchase_reviews) as bigint)           as steam_purchase_reviews,
        cast(sum(steam_purchase_positive_reviews) as bigint)  as steam_purchase_positive_reviews
    from {{ ref('fct_reviews_daily') }}
    group by appid, date

),

players as (
    select appid, date, avg_players, is_complete_day
    from {{ ref('fct_players_daily') }}
),

last_complete_day as (
    select max(d) - 1 as d
    from (
        select max(date) as d from reviews
        union all
        select max(date) from players
    ) x
),

spans as (

    select
        g.appid,
        (select min(date) from reviews r where r.appid = g.appid) as first_review_date,
        (select min(date) from players p where p.appid = g.appid) as first_players_date
    from {{ ref('stg_games') }} g

),

spine as (

    select s.appid, d.date, s.first_review_date
    from spans s
    join {{ ref('dim_date') }} d
      on d.date >= least(coalesce(s.first_review_date, s.first_players_date),
                         coalesce(s.first_players_date, s.first_review_date))
     and d.date <= (select d from last_complete_day)

)

select
    s.appid,
    s.date,
    s.date >= s.first_review_date                                  as has_review_data,
    case when s.date >= s.first_review_date then coalesce(r.reviews, 0) end
                                                                   as reviews,
    case when s.date >= s.first_review_date then coalesce(r.positive_reviews, 0) end
                                                                   as positive_reviews,
    case when s.date >= s.first_review_date then coalesce(r.negative_reviews, 0) end
                                                                   as negative_reviews,
    case when s.date >= s.first_review_date then coalesce(r.steam_purchase_reviews, 0) end
                                                                   as steam_purchase_reviews,
    case when s.date >= s.first_review_date then coalesce(r.steam_purchase_positive_reviews, 0) end
                                                                   as steam_purchase_positive_reviews,
    p.avg_players,
    coalesce(p.is_complete_day, false)                             as is_complete_players_day
from spine s
left join reviews r on r.appid = s.appid and r.date = s.date
left join players p on p.appid = s.appid and p.date = s.date
