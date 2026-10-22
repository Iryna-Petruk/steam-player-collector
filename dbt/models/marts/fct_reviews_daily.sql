-- Daily review metrics per game and language, by the day the review was
-- written (UTC). Uses the latest version of every review, so an edited
-- review counts with its current recommendation.
-- Steam's official score counts only reviews from Steam purchases, hence
-- the separate steam_purchase_* columns.

select
    r.appid,
    r.created_date_utc                                     as date,
    r.language,
    count(*)                                               as reviews,
    count(*) filter (where r.is_positive)                  as positive_reviews,
    count(*) filter (where not r.is_positive)              as negative_reviews,
    count(*) filter (where r.is_steam_purchase)            as steam_purchase_reviews,
    count(*) filter (where r.is_steam_purchase and r.is_positive)
                                                           as steam_purchase_positive_reviews,
    count(*) filter (where r.playtime_at_review_min < 120) as reviews_under_2h_played,
    count(*) filter (where r.playtime_at_review_min < 120 and not r.is_positive)
                                                           as negative_reviews_under_2h_played,
    count(*) filter (where r.was_edited)                   as edited_reviews,
    -- Denominators for topic shares: only reviews whose language the
    -- topic dictionary covers (see fct_review_topics_daily).
    count(*) filter (where r.is_topic_scanned)             as topic_scanned_reviews,
    count(*) filter (where r.is_topic_scanned and not r.is_positive)
                                                           as topic_scanned_negative_reviews,
    round((percentile_cont(0.5) within group (order by r.playtime_at_review_min) / 60.0)::numeric, 1)
                                                           as median_hours_at_review
from {{ ref('int_reviews_latest') }} r
group by r.appid, r.created_date_utc, r.language
