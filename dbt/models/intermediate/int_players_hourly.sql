-- One row per game per UTC hour.
-- Normally there is exactly one successful snapshot per hour, but a manual
-- run can add a second one; a delayed scheduled run can also land late in
-- the hour. We keep the latest successful snapshot of each hour.

with ranked as (

    select
        *,
        row_number() over (
            partition by appid, collected_hour_utc
            order by collected_at desc
        ) as snapshot_rank
    from {{ ref('stg_players') }}
    where is_ok

)

select
    appid,
    collected_hour_utc,
    cast(collected_hour_utc as date)                       as collected_date_utc,
    collected_at,
    player_count
from ranked
where snapshot_rank = 1
