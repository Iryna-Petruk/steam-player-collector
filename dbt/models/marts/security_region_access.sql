-- Row-level security mapping for Power BI: which regions each user may see.
-- One row per user x region; a user with region 'ALL' sees every region.
-- Demo users only (fictional example.com addresses) -- this repo is public.
-- Power BI reads this table in a dynamic RLS role that matches USERPRINCIPALNAME()
-- against user_email and filters dim_languages[region].

select
    user_email,
    region
from {{ ref('region_access_users') }}
