{#
  Steam повертає від'ємне значення лічильника відгуку як беззнакове
  32-бітне число: 4294967295 (2^32-1) це -1, 4294967292 (2^32-4) це -4.
  Справжній підрахунок ніколи не буває таким великим, тому будь-яке
  значення понад межу integer (2147483647) читаємо як "невідомо" -> NULL.

  Steam returns a negative review counter as an unsigned 32-bit integer:
  4294967295 (2^32-1) is -1, 4294967292 (2^32-4) is -4. A real count is
  never that large, so read anything above the integer range (2147483647)
  as unknown -> NULL. One condition covers every such encoding, instead of
  listing the individual values as they turn up.
#}
{% macro steam_count(column) -%}
    case when cast({{ column }} as bigint) > 2147483647
         then null else cast({{ column }} as bigint) end
{%- endmacro %}
