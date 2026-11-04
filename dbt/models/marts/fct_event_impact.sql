-- One row per event and CD PROJEKT RED game: how much the event moved
-- review activity, review score and players, compared with the 4 weeks
-- before AND with the control games on the same days.
--
--   uplift          event game: (after / before) - 1
--   control uplift  control games on the same days, combined as a geometric
--                   mean of their after/before ratios (excluded controls and
--                   controls without data are left out; n_control_games says
--                   how many were used)
--   net uplift      difference-in-differences on ratios:
--                   (1 + uplift) / (1 + control uplift) - 1
--                   "how much more than comparable games moved on the same days"
--
-- A number is NULL when the data cannot support it: fewer than 21 known
-- days before or 14 after, fewer than 30 Steam-purchase reviews for a score,
-- fewer than 20 / 10 complete player days. NULL means "not measurable",
-- never zero.

with w as (
    select * from {{ ref('fct_event_window') }}
),

per_game as (

    select
        event_id, target_appid, appid, series_role, is_excluded_control,

        avg(reviews) filter (where window_phase = 'pre')        as rpd_pre,
        avg(reviews) filter (where window_phase = 'post_2w')    as rpd_2w,
        avg(reviews) filter (where window_phase = 'post_4_8w')  as rpd_4_8w,
        count(reviews) filter (where window_phase = 'pre')      as days_pre,
        count(reviews) filter (where window_phase = 'post_2w')  as days_2w,
        count(reviews) filter (where window_phase = 'post_4_8w') as days_4_8w,

        sum(steam_purchase_reviews) filter (where window_phase = 'pre')          as spr_pre,
        sum(steam_purchase_positive_reviews) filter (where window_phase = 'pre') as spp_pre,
        sum(steam_purchase_reviews) filter (where window_phase = 'post_2w')          as spr_2w,
        sum(steam_purchase_positive_reviews) filter (where window_phase = 'post_2w') as spp_2w,

        avg(avg_players) filter (where window_phase = 'pre')       as players_pre,
        avg(avg_players) filter (where window_phase = 'post_2w')   as players_2w,
        count(avg_players) filter (where window_phase = 'pre')     as player_days_pre,
        count(avg_players) filter (where window_phase = 'post_2w') as player_days_2w

    from w
    group by event_id, target_appid, appid, series_role, is_excluded_control

),

ratios as (

    select
        *,
        case when days_pre >= 21 and days_2w >= 14 and rpd_pre > 0
             then rpd_2w / rpd_pre end                               as reviews_ratio_2w,
        case when days_pre >= 21 and days_4_8w >= 21 and rpd_pre > 0
             then rpd_4_8w / rpd_pre end                             as reviews_ratio_4_8w,
        case when days_pre >= 21 and spr_pre >= 30
             then spp_pre::numeric / spr_pre end                     as score_pre,
        case when days_2w >= 14 and spr_2w >= 30
             then spp_2w::numeric / spr_2w end                       as score_2w,
        case when player_days_pre >= 20 and player_days_2w >= 10 and players_pre > 0
             then players_2w / players_pre end                       as players_ratio_2w
    from per_game

),

controls as (

    select
        event_id, target_appid,
        count(*) filter (where reviews_ratio_2w > 0)                          as n_control_games,
        exp(avg(ln(reviews_ratio_2w)) filter (where reviews_ratio_2w > 0))     as control_reviews_ratio_2w,
        exp(avg(ln(reviews_ratio_4_8w)) filter (where reviews_ratio_4_8w > 0)) as control_reviews_ratio_4_8w,
        avg(score_2w - score_pre)                                             as control_score_change_2w,
        exp(avg(ln(players_ratio_2w)) filter (where players_ratio_2w > 0))     as control_players_ratio_2w
    from ratios
    where series_role = 'control' and not is_excluded_control
    group by event_id, target_appid

),

event_overlaps as (

    -- Other events for the same game (or platform-wide) from 4 weeks before
    -- to 2 weeks after: the measured effect may be shared with them.
    select
        e.event_id, g.appid as target_appid,
        string_agg(o.event_id, ', ' order by o.event_date)                    as overlapping_event_ids
    from {{ ref('stg_events') }} e
    join {{ ref('stg_games') }} g on g.is_cdpr and (e.is_platform_wide or e.appid = g.appid)
    join {{ ref('stg_events') }} o
      on o.event_id <> e.event_id
     and (o.is_platform_wide or o.appid = g.appid)
     and o.event_date between e.event_date - 28 and e.event_date + 13
    group by e.event_id, g.appid

)

select
    r.event_id,
    r.target_appid                                                  as appid,
    e.event_date,
    e.event_type,
    e.magnitude,
    e.event_name,
    e.is_platform_wide,

    round(r.rpd_pre, 1)                                             as reviews_per_day_pre,
    round(r.rpd_2w, 1)                                              as reviews_per_day_2w,
    round(r.rpd_4_8w, 1)                                            as reviews_per_day_4_8w,
    round(r.reviews_ratio_2w - 1, 4)                                as reviews_uplift_2w_pct,
    round(r.reviews_ratio_4_8w - 1, 4)                              as reviews_uplift_4_8w_pct,
    round(c.control_reviews_ratio_2w - 1, 4)                        as control_reviews_uplift_2w_pct,
    round(r.reviews_ratio_2w / c.control_reviews_ratio_2w - 1, 4)   as net_reviews_uplift_2w_pct,
    round(r.reviews_ratio_4_8w / c.control_reviews_ratio_4_8w - 1, 4) as net_reviews_uplift_4_8w_pct,
    coalesce(c.n_control_games, 0)                                  as n_control_games,

    round(r.score_pre, 4)                                           as steam_score_pre,
    round(r.score_2w, 4)                                            as steam_score_2w,
    round((r.score_2w - r.score_pre) * 100, 2)                      as score_change_2w_pp,
    round(c.control_score_change_2w * 100, 2)                       as control_score_change_2w_pp,
    round((r.score_2w - r.score_pre - c.control_score_change_2w) * 100, 2)
                                                                    as net_score_change_2w_pp,

    round(r.players_pre)                                            as avg_players_pre,
    round(r.players_2w)                                             as avg_players_2w,
    round(r.players_ratio_2w - 1, 4)                                as players_uplift_2w_pct,
    round(r.players_ratio_2w / c.control_players_ratio_2w - 1, 4)   as net_players_uplift_2w_pct,

    o.overlapping_event_ids
from ratios r
join {{ ref('stg_events') }} e on e.event_id = r.event_id
left join controls c on c.event_id = r.event_id and c.target_appid = r.target_appid
left join event_overlaps o on o.event_id = r.event_id and o.target_appid = r.target_appid
where r.series_role = 'event_game'
