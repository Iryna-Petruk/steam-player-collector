# The Witcher 3 Remastered launch — reaction in the review data

**Game:** The Witcher 3: Wild Hunt (appid 292030)
**Event:** W3013 — "The Witcher 3 Remastered", free upgrade, released 2026-09-29 (`config/events.csv`)
**Data as of:** 2026-11-04 (2026-11-04 itself is excluded everywhere: the day is still incomplete)
**Queries:** `analysis/witcher3_remaster.dax`, Query 3 and Query 2, run against the `CDPR_Health_Hub` semantic model

Three fixed windows, tied to the event and not moving with new data:

| Window | Dates | Days |
| --- | --- | --- |
| Before | 2026-07-08 .. 2026-09-28 | 83 |
| Launch | 2026-09-29 .. 2026-10-05 | 7 |
| After | 2026-10-06 .. 2026-11-03 | 29 |

The windows have different lengths, so every count below is also given per day.

## Table 1 — Overall review health

| Metric | Before (83 d) | Launch (7 d) | After (29 d) |
| --- | --- | --- | --- |
| Reviews | 15,438 | 10,809 | 8,400 |
| Negative reviews | 764 | 2,660 | 881 |
| Negative reviews per day | 9.2 | 380.0 | 30.4 |
| Positive % | 95.1% | 75.4% | 89.5% |
| Negative from newcomers % (under 2 h played) | 11.3% | 8.0% | 6.1% |
| Negatives scanned for topics | 676 | 2,470 | 804 |
| Topic coverage of negatives | 88.5% | 92.9% | 91.3% |

Positive % fell by 19.7 pp from Before to Launch and recovered to 6.4 pp below the baseline in After. In absolute terms the negative flow was 41× the baseline during launch week and was still 3.3× the baseline a month later.

## Table 2 — Topics of negative reviews

Share = topic mentions ÷ negatives scanned for topics (the "Negatives scanned" row of Table 1). Δ pp columns are differences between shares, in percentage points.

| Topic | Before: mentions | Before: /day | Before: share | Launch: mentions | Launch: /day | Launch: share | After: mentions | After: /day | After: share | Δ pp Launch–Before | Δ pp After–Before |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bugs | 91 | 1.1 | 13.5% | 802 | 114.6 | 32.5% | 316 | 10.9 | 39.3% | +19.0 | +25.8 |
| Performance | 34 | 0.4 | 5.0% | 591 | 84.4 | 23.9% | 105 | 3.6 | 13.1% | +18.9 | +8.0 |
| Story | 164 | 2.0 | 24.3% | 218 | 31.1 | 8.8% | 159 | 5.5 | 19.8% | −15.4 | −4.5 |
| Content | 139 | 1.7 | 20.6% | 211 | 30.1 | 8.5% | 86 | 3.0 | 10.7% | −12.0 | −9.9 |
| Price | 39 | 0.5 | 5.8% | 81 | 11.6 | 3.3% | 23 | 0.8 | 2.9% | −2.5 | −2.9 |
| No topic found | 332 | 4.0 | 49.1% | 1,121 | 160.1 | 45.4% | 320 | 11.0 | 39.8% | −3.7 | −9.3 |

One review can carry several topics, so the shares do not sum to 100% and must not be added together. "No topic found" is the share of scanned negatives that the keyword dictionary matched to no topic.

## Findings

**1. Both technical topics grew by a multiple, and they drove the launch-week reaction.**
Bugs went from 1.1 mentions per day in the baseline to 114.6 per day during launch week (105×), performance from 0.4 to 84.4 per day (206×). Their shares of scanned negatives rose by +19.0 pp and +18.9 pp respectively. These are two separate measurements of two separate topics — they are not added up, because a review complaining about both is counted in both rows.

**2. Story, content and price did not grow as a proportion of the complaints.**
Their per-day mention counts rose in launch week, as everything did when the negative flow went up 41×, but their shares fell: story −15.4 pp, content −12.0 pp, price −2.5 pp. The negative reviews of launch week were not the usual complaints at a higher volume; their composition shifted to the technical state of the release.

**3. Bugs did not come back down with the volume.**
By the After window the overall negative flow had dropped from 380 to 30.4 per day, but bugs mentions were 10.9 per day — still 9.9× the baseline of 1.1 per day (91 over 83 days → 316 over 29 days), and their share was the highest of any window at 39.3% (+25.8 pp over the baseline). Performance recovered much further: 3.6 per day, 8.8× the baseline, share back to 13.1%. The remaining complaint a month after launch is bugs, not frame rate.

**4. "No topic found" fell, and this is a change in the reviews, not in the dictionary.**
The share fell from 49.1% to 45.4% to 39.8% (−9.3 pp from Before to After). The topic dictionary cannot explain it: the dictionary version is the same `r2-b9b7752b` for every window — verified across all 915,457 collected The Witcher 3 reviews, and enforced by the dbt test `assert_single_topics_version`. Language coverage of negatives also only moved between 88.5% and 92.9%. So the same rules matched more of the text, which means the negativity itself became more specific: players named concrete problems instead of writing generic dissatisfaction.

**5. The Steam Autumn Sale is not the main explanation.**
The decisive argument is timing. The spike began on 2026-09-29 and 2026-09-30, with 966 and 693 negative reviews per day (against a baseline of 9.2 per day), while the Steam Autumn Sale 2026 (ST015) only started on 2026-10-01 — by which day the negative flow was already falling: 375, then 209, then 184. The two largest days of the reaction are before the sale existed, so the sale cannot account for the spike.

The sale does overlap 2026-10-01 .. 2026-10-05 inside the Launch window and the first three days of After, and its contribution within those days has not been measured separately. That would need a comparison against the control group over the same sale window, which this analysis does not do.

As a supporting argument, the share of negative reviews written with under 2 hours of playtime moved the wrong way for a sale-driven explanation: 11.3% before, 8.0% in launch week, 6.1% after. A wave of new buyers bouncing off the game would push that share up; instead the complaints came disproportionately from accounts with more playtime — consistent with existing owners taking the free upgrade.

## Limitations

- Topic shares use negatives that were scanned for topics as the denominator (88.5–92.9% of negatives per window); reviews in languages outside the 10-language dictionary are excluded from the shares.
- Topics are keyword-based: sarcasm and negation are not understood ("no bugs at all" counts as bugs). This is why topics are reported for negative reviews only.
- A review can mention several topics. Shares are per topic and are never summed; differences between shares are reported in percentage points.
- The Before window is a quiet baseline, but it is 83 days against 7 and 29 — per-day rates, not raw counts, are the comparable figures.
- Steam only; off-topic review activity is excluded by Steam's default filter.
- The sale's own effect inside 2026-10-01 .. 2026-10-08 is not isolated (see finding 5).
