-- What reviews talk about: game x day (UTC) x language x topic.
-- Only reviews in languages covered by the topic dictionary (is_topic_scanned).
-- A review can mention several topics, so this table must NOT be summed
-- across topics; divide by fct_reviews_daily.topic_scanned_reviews instead.
-- topic = 'none': a scanned review that matched no topic.

with scanned as (

    select *
    from {{ ref('int_reviews_latest') }}
    where is_topic_scanned

),

one_row_per_topic as (

    select
        r.appid,
        r.created_date_utc as date,
        r.language,
        r.is_positive,
        t.topic
    from scanned r
    cross join lateral (
        values
            ('bugs',        r.has_topic_bugs),
            ('performance', r.has_topic_performance),
            ('price',       r.has_topic_price),
            ('story',       r.has_topic_story),
            ('content',     r.has_topic_content),
            ('none',        not (r.has_topic_bugs or r.has_topic_performance or r.has_topic_price
                                 or r.has_topic_story or r.has_topic_content))
    ) as t (topic, mentioned)
    where t.mentioned

)

select
    appid,
    date,
    language,
    topic,
    count(*)                                   as reviews,
    count(*) filter (where is_positive)        as positive_reviews,
    count(*) filter (where not is_positive)    as negative_reviews
from one_row_per_topic
group by appid, date, language, topic
