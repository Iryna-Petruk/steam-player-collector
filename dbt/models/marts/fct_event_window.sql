-- Event study table: every event that concerns a CD PROJEKT RED game, laid
-- out on a common axis "days from the event" (day_offset -28 ... +55),
-- for the event game and, on the same calendar days, for each control game.
--
-- Grain: event_id x target_appid x appid x day_offset
--   target_appid  the CD PROJEKT RED game the event is about
--                 (platform-wide events, e.g. Steam sales, get one target per CDPR game)
--   appid         the game whose numbers are on this row: the target itself
--                 (series_role = 'event_game') or a control game ('control')
--
-- Windows (whole weeks, so weekday effects cancel out):
--   pre        -28 ... -1   baseline, 4 weeks
--   post_2w      0 ... 13   immediate reaction, 2 weeks
--   post_2_4w   14 ... 27
--   post_4_8w   28 ... 55   does the effect last?
--
-- A control game that has its own (non platform-wide) event inside the
-- window is flagged is_excluded_control: its numbers move for its own
-- reasons and must not be used as a baseline for this event.

{% set pre_days = 28 %}
{% set post_days = 55 %}

with events as (
    select * from {{ ref('stg_events') }}
),

games as (
    select * from {{ ref('stg_games') }}
),

targets as (

    select e.event_id, e.event_date, g.appid as target_appid
    from events e
    join games g
      on g.is_cdpr
     and (e.is_platform_wide or e.appid = g.appid)

),

series as (

    select t.event_id, t.event_date, t.target_appid, t.target_appid as appid,
           'event_game' as series_role
    from targets t

    union all

    select t.event_id, t.event_date, t.target_appid, g.appid, 'control'
    from targets t
    cross join games g
    where g.is_control

),

excluded_controls as (

    select distinct t.event_id, t.target_appid, x.appid
    from targets t
    join events x
      on not x.is_platform_wide
     and x.appid in (select appid from games where is_control)
     and x.event_date between t.event_date - {{ pre_days }} and t.event_date + {{ post_days }}

),

grid as (

    select s.*, o.day_offset, s.event_date + o.day_offset as date
    from series s
    cross join generate_series(-{{ pre_days }}, {{ post_days }}) as o (day_offset)

),

joined as (

    select
        g.event_id,
        g.target_appid,
        g.appid,
        g.series_role,
        g.event_date,
        g.day_offset,
        g.date,
        case
            when g.day_offset < 0   then 'pre'
            when g.day_offset <= 13 then 'post_2w'
            when g.day_offset <= 27 then 'post_2_4w'
            else 'post_4_8w'
        end                                                    as window_phase,
        (x.appid is not null)                                  as is_excluded_control,
        d.reviews,
        d.positive_reviews,
        d.negative_reviews,
        d.steam_purchase_reviews,
        d.steam_purchase_positive_reviews,
        case when d.is_complete_players_day then d.avg_players end
                                                               as avg_players
    from grid g
    left join {{ ref('int_game_daily') }} d
      on d.appid = g.appid and d.date = g.date
    left join excluded_controls x
      on x.event_id = g.event_id and x.target_appid = g.target_appid and x.appid = g.appid

),

baseline as (

    select
        event_id, target_appid, appid,
        avg(reviews)      as pre_reviews_per_day,
        avg(avg_players)  as pre_avg_players
    from joined
    where window_phase = 'pre'
    group by event_id, target_appid, appid

)

select
    j.*,
    -- Index: 100 = this game's own average in the 4 weeks before the event.
    -- Makes games of different size comparable on one chart.
    round(100.0 * j.reviews / nullif(b.pre_reviews_per_day, 0), 1)  as reviews_index,
    round(100.0 * j.avg_players / nullif(b.pre_avg_players, 0), 1)  as players_index
from joined j
left join baseline b
  on b.event_id = j.event_id and b.target_appid = j.target_appid and b.appid = j.appid
