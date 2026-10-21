select
    event_id,
    event_date,
    end_date,
    (end_date - event_date) + 1                            as duration_days,
    appid,
    is_platform_wide,
    game,
    event_type,
    event_name,
    magnitude,
    source_url,
    notes
from {{ ref('stg_events') }}
