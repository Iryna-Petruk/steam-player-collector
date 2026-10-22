-- Business-rule checks: values that would mean a bug upstream.

select 'negative player count' as problem, appid::text as key
from {{ ref('fct_players_daily') }}
where min_players < 0

union all
select 'coverage above 100%', appid::text
from {{ ref('fct_players_daily') }}
where coverage_pct > 1

union all
select 'more positive than total', appid::text || ' ' || date::text
from {{ ref('fct_reviews_daily') }}
where positive_reviews > reviews

union all
select 'review updated before created', recommendation_id::text
from {{ ref('int_reviews_latest') }}
where updated_at < created_at

union all
select 'topic flag on a review that was not scanned', recommendation_id::text
from {{ ref('int_reviews_latest') }}
where not is_topic_scanned
  and (has_topic_bugs or has_topic_performance or has_topic_price or has_topic_story or has_topic_content)

union all
select 'more topic-scanned reviews than reviews', appid::text || ' ' || date::text
from {{ ref('fct_reviews_daily') }}
where topic_scanned_reviews > reviews

union all
select 'event ends before it starts', event_id
from {{ ref('dim_events') }}
where end_date < event_date
