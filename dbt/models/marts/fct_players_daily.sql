-- Daily Steam player metrics per game (UTC days).
-- coverage_pct shows how many of the 24 hourly snapshots we have, so a day
-- with gaps can be flagged or excluded in analysis instead of silently
-- pulling the average down or up.

with hourly as (
    select * from {{ ref('int_players_hourly') }}
),

failed as (
    select
        appid,
        cast(collected_hour_utc as date)                   as collected_date_utc,
        count(*)                                           as failed_requests
    from {{ ref('stg_players') }}
    where not is_ok
    group by 1, 2
)

select
    h.appid,
    h.collected_date_utc                                   as date,
    count(*)                                               as snapshots_ok,
    coalesce(max(f.failed_requests), 0)                    as failed_requests,
    round(count(*) / 24.0, 3)                              as coverage_pct,
    count(*) >= 20                                         as is_complete_day,
    round(avg(h.player_count))::int                        as avg_players,
    max(h.player_count)                                    as peak_players,
    min(h.player_count)                                    as min_players
from hourly h
left join failed f
    on f.appid = h.appid
   and f.collected_date_utc = h.collected_date_utc
group by h.appid, h.collected_date_utc
