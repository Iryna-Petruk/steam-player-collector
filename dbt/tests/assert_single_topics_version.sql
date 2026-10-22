-- Warning, not error: while the collector re-tags the history after a
-- dictionary change, old and new topic versions are mixed for a few days.
-- Topic shares are only comparable over time once this test passes.
{{ config(severity = 'warn') }}

select appid, count(distinct topics_version) as versions
from {{ ref('int_reviews_latest') }}
where is_topic_scanned
group by appid
having count(distinct topics_version) > 1
