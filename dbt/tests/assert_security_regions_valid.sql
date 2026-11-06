-- Every region granted in security_region_access must be either the 'ALL'
-- wildcard or a real region in dim_languages. A typo here would silently
-- give a user an empty report instead of the data they should see.

select
    a.user_email,
    a.region
from {{ ref('security_region_access') }} a
left join {{ ref('dim_languages') }} l on l.region = a.region
where a.region <> 'ALL'
  and l.region is null
