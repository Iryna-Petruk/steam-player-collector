-- Event window checks:
--  1. date is always event_date + day_offset;
--  2. every series has all 84 days (-28 ... +55);
--  3. one row per event x target game x game x day (grain).

select 'date does not match offset' as problem, event_id, target_appid, appid
from {{ ref('fct_event_window') }}
where date <> event_date + day_offset

union all

select 'series is not 84 days long', event_id, target_appid, appid
from {{ ref('fct_event_window') }}
group by event_id, target_appid, appid
having count(*) <> 84 or count(distinct day_offset) <> 84

union all

select 'duplicate key in impact table', event_id, appid, null
from {{ ref('fct_event_impact') }}
group by event_id, appid
having count(*) > 1
