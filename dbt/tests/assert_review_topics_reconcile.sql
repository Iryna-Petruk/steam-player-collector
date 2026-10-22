-- Reconciliation: every topic mention in int_reviews_latest appears exactly
-- once in fct_review_topics_daily, per game and topic.

with expected as (
    select appid, 'bugs' as topic, count(*) filter (where has_topic_bugs) as n
    from {{ ref('int_reviews_latest') }} where is_topic_scanned group by appid
    union all
    select appid, 'performance', count(*) filter (where has_topic_performance)
    from {{ ref('int_reviews_latest') }} where is_topic_scanned group by appid
    union all
    select appid, 'price', count(*) filter (where has_topic_price)
    from {{ ref('int_reviews_latest') }} where is_topic_scanned group by appid
    union all
    select appid, 'story', count(*) filter (where has_topic_story)
    from {{ ref('int_reviews_latest') }} where is_topic_scanned group by appid
    union all
    select appid, 'content', count(*) filter (where has_topic_content)
    from {{ ref('int_reviews_latest') }} where is_topic_scanned group by appid
    union all
    select appid, 'none', count(*) filter (where not (has_topic_bugs or has_topic_performance
        or has_topic_price or has_topic_story or has_topic_content))
    from {{ ref('int_reviews_latest') }} where is_topic_scanned group by appid
),

actual as (
    select appid, topic, sum(reviews) as n
    from {{ ref('fct_review_topics_daily') }}
    group by appid, topic
)

select e.appid, e.topic, e.n as expected, a.n as actual
from expected e
left join actual a using (appid, topic)
where coalesce(a.n, 0) <> e.n
