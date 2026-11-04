{#
  Скільки значень steam_count() прочитав як "невідомо".

  Steam іноді повертає від'ємний лічильник відгуку як беззнакове 32-бітне
  число (wrap-around): 4294967295 це -1, 4294967292 це -4. steam_count()
  замінює такі значення на NULL, бо справжнім підрахунком вони бути не
  можуть. Цей тест показує масштаб заміни, щоб дані не зникали мовчки.

  How many values steam_count() reads as unknown.

  Steam sometimes returns a negative review counter as an unsigned 32-bit
  integer (wrap-around): 4294967295 is -1, 4294967292 is -4. steam_count()
  maps such values to NULL, because they cannot be real counts. This test
  reports the scale of that substitution, so the data is never lost
  silently.

  severity: warn - the raw files are what Steam sent and cannot be
  corrected here, so this is something to watch, not a reason to stop the
  build. It turns into an error only if a counter overflows beyond what the
  macro covers, which would fail the model itself.

  Every row returned is one counter column where Steam sent at least one
  wrapped value.
#}

{{ config(severity = 'warn') }}

{% set counters = [
    'votes_up',
    'votes_funny',
    'comment_count',
    'playtime_at_review_min',
    'playtime_forever_min',
    'author_num_reviews',
] %}

with wrapped as (

{% for counter in counters %}
    select
        '{{ counter }}'                   as counter,
        count(*)                          as values_read_as_unknown,
        count(distinct recommendation_id) as reviews_affected,
        min(cast({{ counter }} as bigint)) as lowest_wrapped_value,
        max(cast({{ counter }} as bigint)) as highest_wrapped_value
    from {{ source('raw', 'reviews') }}
    where cast({{ counter }} as bigint) > 2147483647
    {%- if not loop.last %}
    union all
    {%- endif %}
{% endfor %}

)

select *
from wrapped
where values_read_as_unknown > 0
