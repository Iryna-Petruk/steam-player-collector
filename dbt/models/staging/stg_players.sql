-- One row per game per collector run, with proper types.
-- Failed requests are kept (player_count is null) so gaps stay visible.

select
    cast(collected_at_utc as timestamptz)                  as collected_at,
    date_trunc('hour', cast(collected_at_utc as timestamptz) at time zone 'UTC')
                                                           as collected_hour_utc,
    cast(appid as integer)                                 as appid,
    game,
    role,
    cast(player_count as integer)                          as player_count,
    status,
    status = 'ok'                                          as is_ok,
    _source_file,
    _loaded_at
from {{ source('raw', 'players') }}
