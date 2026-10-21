-- Events calendar with typed dates. Single-day events get end_date = event_date,
-- so every event can be treated as a date range.

select
    event_id,
    cast(event_date as date)                               as event_date,
    cast(coalesce(nullif(end_date, ''), event_date) as date) as end_date,
    case when appid = 'ALL' then null else cast(appid as integer) end as appid,
    appid = 'ALL'                                          as is_platform_wide,
    game,
    event_type,
    event_name,
    magnitude,
    source_url,
    notes
from {{ source('raw', 'events') }}
