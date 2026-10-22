-- Review metadata with proper types. Still contains duplicates:
-- the same review appears again in overlap windows and after updates.
-- Deduplication happens in int_reviews_latest.

select
    cast(recommendation_id as bigint)                      as recommendation_id,
    cast(appid as integer)                                 as appid,
    language,
    cast(created_utc as timestamptz)                       as created_at,
    cast(updated_utc as timestamptz)                       as updated_at,
    voted_up = '1'                                         as is_positive,
    cast(votes_up as integer)                              as votes_up,
    cast(votes_funny as integer)                           as votes_funny,
    cast(nullif(weighted_vote_score, '') as numeric)       as weighted_vote_score,
    cast(comment_count as integer)                         as comment_count,
    steam_purchase = '1'                                   as is_steam_purchase,
    received_for_free = '1'                                as is_received_for_free,
    written_during_early_access = '1'                      as is_early_access_review,
    refunded = '1'                                         as is_refunded,
    primarily_steam_deck = '1'                             as is_primarily_steam_deck,
    cast(playtime_at_review_min as integer)                as playtime_at_review_min,
    cast(playtime_forever_min as integer)                  as playtime_forever_min,
    cast(author_num_reviews as integer)                    as author_num_reviews,
    has_developer_response = '1'                           as has_developer_response,
    cast(review_length as integer)                         as review_length,
    cast(fetched_at_utc as timestamptz)                    as fetched_at,
    -- Topic flags (keyword dictionary, see config/review_topics.csv).
    -- Files collected before topics existed have NULL here -> false / not scanned.
    coalesce(topic_bugs = '1', false)                      as has_topic_bugs,
    coalesce(topic_performance = '1', false)               as has_topic_performance,
    coalesce(topic_price = '1', false)                     as has_topic_price,
    coalesce(topic_story = '1', false)                     as has_topic_story,
    coalesce(topic_content = '1', false)                   as has_topic_content,
    coalesce(topics_scanned = '1', false)                  as is_topic_scanned,
    topics_version,
    _source_file
from {{ source('raw', 'reviews') }}
