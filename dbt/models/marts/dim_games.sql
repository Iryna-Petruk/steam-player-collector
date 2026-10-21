select
    appid,
    game,
    role,
    is_cdpr,
    is_control,
    collects_reviews
from {{ ref('stg_games') }}
