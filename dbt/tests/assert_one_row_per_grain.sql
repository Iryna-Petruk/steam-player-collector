-- Grain checks for the fact tables: no duplicated keys.

select 'fct_players_daily' as model, appid::text, date::text, null as language, count(*) as n
from {{ ref('fct_players_daily') }}
group by appid, date
having count(*) > 1

union all

select 'fct_reviews_daily', appid::text, date::text, language, count(*)
from {{ ref('fct_reviews_daily') }}
group by appid, date, language
having count(*) > 1
