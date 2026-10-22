-- One row per review: its most recent version.
-- A review can appear several times in raw data (overlap windows, edits).
-- We keep the version with the latest updated_at; if two copies have the
-- same updated_at, the one fetched last wins.

with ranked as (

    select
        *,
        row_number() over (
            partition by recommendation_id
            order by updated_at desc, fetched_at desc
        ) as version_rank
    from {{ ref('stg_reviews') }}

)

select
    recommendation_id,
    appid,
    language,
    created_at,
    cast(created_at at time zone 'UTC' as date)            as created_date_utc,
    updated_at,
    updated_at > created_at                                as was_edited,
    is_positive,
    votes_up,
    votes_funny,
    weighted_vote_score,
    comment_count,
    is_steam_purchase,
    is_received_for_free,
    is_early_access_review,
    is_refunded,
    is_primarily_steam_deck,
    playtime_at_review_min,
    playtime_forever_min,
    author_num_reviews,
    has_developer_response,
    review_length,
    fetched_at,
    has_topic_bugs,
    has_topic_performance,
    has_topic_price,
    has_topic_story,
    has_topic_content,
    is_topic_scanned,
    topics_version
from ranked
where version_rank = 1
