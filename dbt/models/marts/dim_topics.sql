-- Review topics with display names and order for Power BI.
select topic, topic_label, description, sort_order
from {{ ref('review_topic_labels') }}
