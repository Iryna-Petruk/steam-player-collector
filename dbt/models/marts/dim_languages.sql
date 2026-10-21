-- Steam review languages mapped to markets and regions (seed language_markets.csv).
-- A language that appears in the data but is missing from the seed is still
-- included, as region 'Other', so no review is lost in Power BI.
-- Region is the column row-level security will filter on later.

with seen as (
    select distinct language from {{ ref('int_reviews_latest') }}
),

mapped as (
    select language, language_name, market, region
    from {{ ref('language_markets') }}
)

select
    coalesce(m.language, s.language)                       as language,
    coalesce(m.language_name, s.language)                  as language_name,
    coalesce(m.market, 'Other')                            as market,
    coalesce(m.region, 'Other')                            as region
from mapped m
full outer join seen s on s.language = m.language
