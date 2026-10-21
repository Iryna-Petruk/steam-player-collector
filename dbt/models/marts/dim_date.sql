-- Calendar table for Power BI (mark it as the date table there).
-- Covers the whole period of our data plus the coming year.

select
    d::date                                                as date,
    extract(year from d)::int                              as year,
    extract(quarter from d)::int                           as quarter,
    'Q' || extract(quarter from d)::int                    as quarter_name,
    extract(month from d)::int                             as month,
    to_char(d, 'Mon')                                      as month_name,
    to_char(d, 'YYYY-MM')                                  as year_month,
    extract(isoyear from d)::int                           as iso_year,
    extract(week from d)::int                              as iso_week,
    extract(isodow from d)::int                            as weekday_number,   -- 1 = Monday
    to_char(d, 'Dy')                                       as weekday_name,
    extract(isodow from d) in (6, 7)                       as is_weekend
from generate_series(date '2015-01-01', date '2027-12-31', interval '1 day') as d
