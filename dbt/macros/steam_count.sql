{#
  Steam повертає 2^32-1 (4294967295) у лічильнику відгуку як "невідомо":
  від'ємне значення, записане як беззнакове 32-бітне число. Це не справжній
  підрахунок, і в integer воно не влізає, тому читаємо його як NULL.

  Steam returns 2^32-1 (4294967295) in a review counter to mean "unknown":
  a negative value encoded as an unsigned 32-bit integer. Such a number is
  not a real count and does not fit in integer, so read it as NULL.
#}
{% macro steam_count(column) -%}
    nullif(cast({{ column }} as bigint), 4294967295)
{%- endmacro %}
