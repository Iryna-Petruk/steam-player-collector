select
    cast(appid as integer)        as appid,
    game,
    role,
    role = 'cdpr'                 as is_cdpr,
    role = 'control'              as is_control,
    lower(reviews) = 'yes'        as collects_reviews
from {{ source('raw', 'games') }}
