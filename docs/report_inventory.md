# Report and model inventory — CDPR Health Hub

Read-only audit of `CDPR_Health_Hub.Report` (PBIR on disk) and
`CDPR_Health_Hub.SemanticModel` (live Power BI Desktop instance, port 53103).
Audited read-only and generated 2026-11-11; sections 1-7 describe the report
as it was *before* the fix pass of the same day. Section 8 carries the
status of every issue after it.

Sources: `definition/pages/*/page.json`, `definition/pages/*/visuals/*/visual.json`,
`definition/report.json`, the semantic model's TMDL, and DAX run against the open
Desktop model.

---

## 1. Report shell

| Item | Value |
|---|---|
| Page order (`pages.json`) | Overview → Player Voice → What drives interest → **About** → **Event log** |
| Landing / active page | Overview |
| Canvas | 1920 × 1080, `FitToPage`, every page |
| Base theme | `Fluent2-CY26SU10` (SharedResources) |
| Custom theme | `Back-Catalogue Health Hub v2 (independent)` (RegisteredResources) |
| Custom visual | Deneb (`deneb7E15AEF80B9E4D4F8E12924291ECE89A`), v2.0.1.0, used 4× |
| Report-level filters | none |
| Settings | `useStylableVisualContainerHeader` true · `exportDataMode` AllowSummarized · `defaultDrillFilterOtherVisuals` true · `allowChangeFilterTypes` true · `useEnhancedTooltips` true · `filterPaneHiddenInEditMode` true · `useDefaultAggregateDisplayName` true |
| Filter pane | `outspacePane.expanded = true` — the pane opens **expanded for viewers** |
| Visuals | 68 total (23 / 18 / 18 / 4 / 5) |

The page order in the file is **About before Event log**, not "Event log, About".

Theme palette actually in the file (first 8 data colours):
`#A87400 #2F5D8C #9AA0A6 #B3122E #D9752B #5F6368 #8A9097 #B4B9BF`,
foreground `#1F2328`, background `#FFFFFF`, page background `#F3F3F1`,
good/minimum `#5F6368`, neutral `#9AA0A6`, bad/maximum `#B3122E`, tableAccent `#2F5D8C`.
Note `#C4C8CD` (named in the house palette) is **not** in the theme file;
`#8A9097` and `#B4B9BF` are in the theme but not in the house palette.

Two theme files exist: `back_catalogue_theme_v2.json` at the repo root (8 data
colours) and the registered copy inside the report (the same 8 followed by
Power BI's 248 filler colours). The registered one is what applies.

---

## 2. Pages

### 2.1 Overview (`88e530bfd11be9320119`)

**Purpose:** how the two CDPR back-catalogue games are doing right now — score,
recent movement, review volume and what the negative reviews complain about.

* Background image: `Overview_background_clean_1920x1080-3.png` (registered as
  `Overview_background_clean_19203914623981568306.png`), scaling `Normal`.
  The card group headings ("Steam score, all time", "Recent score (30 days) vs all
  time", "Reviews, last 30 days", "Bugs in negative reviews, last 30 days"), the
  slicer labels and the two game legends are **painted into the PNG**, not set as
  visual titles.
* Page filter: `Game[role] IN {"cdpr"}` (`howCreated: User`, not hidden, not locked).
* 23 visuals, 50 `NoFilter` interaction overrides.

| id | type | title / subtitle | fields | visual-level filters |
|---|---|---|---|---|
| `b2c6403b` | advancedSlicer | title hidden | `Game[Game Label]` | saved selection: Cyberpunk 2077; The Witcher 3; Baldur's Gate 3 |
| `93aa83ce` | advancedSlicer | title "Time window", hidden | `Time Window[Time Window]` | saved selection: *Selected period* |
| `52ad895a` | slicer (date slider) | title "Period", hidden | `Date[date]` | RelativeDate: last 12 months to today |
| `243590c9` | slicer | **no title set** | `Language[region]` | — |
| `c891b290` | actionButton | — | — | type `ClearAllSlicers`, text "Clear all slicers" |
| `f9e120b6` | pageNavigator | — | — | `showHiddenPages = false`, 4 columns |
| `53a571e4` | shape (line) | — | — | fill + outline `#B3122E` |
| `9d71ee47` | card | — | `[Data Through]`, `[Last Refreshed]` | — |
| `4b7cced4` | card | — | `[Steam Score %]` | `Game[game] = Cyberpunk 2077` (hidden) |
| `675e0bef` | card | — | `[Steam Score %]` | `Game[game] = The Witcher 3: Wild Hunt` (hidden) |
| `c3b692b6` | card | — | `[Recent Score % (30d)]` | `Game[game] = Cyberpunk 2077` (hidden) |
| `dd33662f` | card | — | `[Recent Score % (30d)]` | `Game[game] = The Witcher 3: Wild Hunt` (hidden) |
| `3f91a4c7` | card | — | `[Recent vs All-time (pp)]` | `Game[game] = Cyberpunk 2077` (hidden) |
| `7c25e8b1` | card | — | `[Recent vs All-time (pp)]` | `Game[game] = The Witcher 3: Wild Hunt` (hidden) |
| `ba26a40e` | card | — | `[Reviews]` | `Game[game] = Cyberpunk 2077`; `Time Window = Last 30 days` (both hidden) |
| `59a60519` | card | — | `[Reviews]` | `Game[game] = The Witcher 3: Wild Hunt`; `Time Window = Last 30 days` |
| `b84d16ea` | card | — | `[Bugs Share CY (to date)]` | `Game[game] = Cyberpunk 2077`; `Topic[topic_label] = Bugs & crashes`; `Time Window = Last 30 days` |
| `e570c3fb` | card | — | `[Bugs Share CY (to date)]` | `Game[game] = The Witcher 3: Wild Hunt`; same two extra filters |
| `81b02860` | card | — | `[Topic Share of Negative %]` | `Game[game] = Cyberpunk 2077`; `Topic[topic_label] = Bugs & crashes`; `Time Window = Last 30 days` |
| `467f44b9` | card | — | `[Topic Share of Negative %]` | `Game[game] = The Witcher 3: Wild Hunt`; same two extra filters |
| `82dd9b58` | Deneb | "Steam score by month (Steam purchases only)" | `Date[year_month]`, `Game[game]`, `[Steam Score %]`, `[Reviews]`, `[Key Event In Month]` | — (spec drops months with < 300 reviews) |
| `f937c072` | clusteredBar | "What negative reviews are about (share of negative reviews mentioning each topic)" / "A review can mention several topics" | `Topic[topic_label]`, `Game[game]`, `[Topic Share of Negative %]` | `Topic[topic_label] NOT IN {"No topic found"}` (hidden) |
| `2d740824` | lineChart | "Reviews per month" / "Log scale · current month to date" | `Date[month_start]`, `Game[game]`, `[Reviews]` | — (value axis `logAxisScale = true`) |

**Interactions switched off** (50 `NoFilter` edges). Summarised by source:

| slicer / source | still filters |
|---|---|
| `b2c6403b` Game Label | the two charts + the Deneb chart only (all 12 cards excluded) |
| `52ad895a` Period | the two charts + the topic bar chart only |
| `93aa83ce` Time window | **only the topic bar chart** (14 of 16 data visuals excluded) |
| `243590c9` Region | **everything — no interaction is switched off for it** |
| `f937c072` topic bar chart (cross-filter source) | the two time-series charts only |

**Hard-coded colours.** Cards: `#E6E6E6` border (border `show=false`, inert) and
`#FFFFFF` background. Slicers: outline `#D5D7DA` (visible, off-palette). Shape:
`#B3122E`. Deneb spec: `#A87400` / `#2F5D8C` game scale, `#5F6368` labels,
`#F3F3F1` x-grid, **`#EEEEEC` y-grid (off-palette)**, `#FFFFFF` marker fill.
Card value font colours: `[Recent Delta Colour]` measure on the two delta cards,
`[Bugs Card Colour]` measure on the two Topic-Share cards, fixed `#5F6368` on the
two `Bugs Share CY` cards.

### 2.2 Player Voice (`ae23cbe900d06057a24c`)

**Purpose:** what players complain about in negative reviews, where those reviews
come from, and who writes them.

* Background image: `PlayerVoice_background_1920x1080.png`
  (`PlayerVoice_background_1920x106437791581025385.png`), `Normal`.
  Card headings "Negative reviews, selected period", "Negative reviews from
  newcomers (<2h played)", "Main complaint in negative reviews" are in the PNG.
* Page filter: `Game[role] IN {"cdpr"}`.
* 18 visuals, 6 `NoFilter` overrides.

| id | type | title / subtitle | fields | visual-level filters |
|---|---|---|---|---|
| `6c958506` | advancedSlicer | title hidden | `Game[Game Label]` | saved selection: CP2077; The Witcher 3; Baldur's Gate 3 |
| `87dbfb86` | advancedSlicer | "Time window", hidden | `Time Window[Time Window]` | saved selection: *Selected period* |
| `c7b45144` | slicer | "Period", hidden | `Date[date]` | RelativeDate: last 12 months |
| `c4298579` | slicer | **no title set** | `Language[region]` | — |
| `34d779fa` | actionButton | — | — | `ClearAllSlicers` |
| `49eca0b7` | pageNavigator | — | — | `showHiddenPages = false` |
| `912b1562` | shape (line) | — | — | `#B3122E` |
| `19e91157` | card | — | `[Data Through]`, `[Last Refreshed]` | — |
| `c663ebdb` / `07cbdce2` | card ×2 | — | `[Negative Reviews]` | `Game[game]` = CP2077 / TW3 (**not** hidden) |
| `163c4ccd` / `65b9ea46` | card ×2 | — | `[Negative from Newcomers %]` | `Game[game]` = CP2077 / TW3 |
| `80ee5db2` / `7a75cce7` | card ×2 | — | `[Main Complaint]` | `Game[game]` = CP2077 / TW3 |
| `d5bf475e` | lineChart (small multiples) | "How complaints changed over time" / "Share of negative reviews mentioning each topic, by year" | `Date[year]`, `Game[game]` (rows), `Topic[topic_label]` (series), `[Topic Share of Negative %]` | `Topic[topic_label] NOT IN {"No topic found"}` |
| `df812d50` | lineChart | "Negative reviews from newcomers" / "Written with less than 2 hours played" | `Date[year]`, `Game[game]`, `[Negative from Newcomers %]` | `Topic[topic_label] NOT IN {"No topic found"}` |
| `7d929df0` | pivotTable | "What each region complains about" / "share of negative reviews mentioning each topic" | rows `Language[region]`, cols `Topic[topic_label]`, `[Topic Share of Negative %]` | `Topic[topic_label] NOT IN {"No topic found"}` |
| `100248db` | pivotTable | "Steam score by market" / "Top 10 markets by reviews" | rows `Language[market]`, cols `Game[game]`, `[Steam Score %]`, `[Reviews]` | `[Reviews] > 1000` (Advanced) **and** TopN 10 markets by `[Reviews]` |

**Interactions switched off:** only the Game Label slicer, and only against the six
KPI cards. Time window, Period and Region all filter every visual.

**Hard-coded colours.** `#E6E6E6` inert card borders, `#D5D7DA` slicer outlines,
`#B3122E` shape. `d5bf475e` fixes topic colours: Bugs & crashes `#B3122E`,
Performance `#D9752B`, Story & characters `#5F6368`, Content & features `#8A9097`,
Price & value `#B4B9BF` (all in-theme). Both pivot tables use white→`#B3122E`
gradients (`100248db` runs `#B3122E` at the minimum of `[Steam Score %]`,
`7d929df0` runs `#B3122E` at the maximum of `[Topic Share of Negative %]`, with a
white font below the 35 % band).

### 2.3 What drives interest (`79f61fe7414e4d67b910`)

**Purpose:** which events move the Steam score and which bring review activity back.

* Background image: `WhatDrives_background_1920x1080-2.png`
  (`WhatDrives_background_1920x1089233740888889853.png`), `Normal`.
  Card headings "Events measured", "Median review activity, 2 weeks after vs 4
  weeks before", "Average score change, 2 weeks after (pp)" are in the PNG.
* Page filter: `Game[role] IN {"cdpr"}`.
* 18 visuals, **no `visualInteractions` block at all** — every interaction is at its
  default.

| id | type | title / subtitle | fields | visual-level filters |
|---|---|---|---|---|
| `2e467280` | advancedSlicer | title hidden | `Game[Game Label]` | saved selection: CP2077; The Witcher 3; Baldur's Gate 3 |
| `96eabca1` | slicer | **title show = true, no text** | `Event[event_type]` | — |
| `0b62f417` | slicer | **title show = true, no text** | `Event[event_name]` | — |
| `eeb10054` | actionButton | — | — | `ClearAllSlicers` |
| `c1cc8d50` | pageNavigator | — | — | `showHiddenPages = false`, width 650 |
| `f413bbd2` | shape (line) | — | — | `#B3122E` |
| `1e193649` | card | — | `[Data Through]`, `[Last Refreshed]` | — |
| `81f36eeb` / `0a30b840` | card ×2 | — | `[Events Measured]` | `Game[game]` = CP2077 / TW3 |
| `4513c306` / `f69224bd` | card ×2 | — | `[Median Reviews Uplift 2w]` | `Game[game]` = CP2077 / TW3 |
| `7efe3ef1` / `d004e750` | card ×2 | — | `[Avg Score Change 2w (pp)]` | `Game[game]` = CP2077 / TW3 |
| `0364d049` | Deneb | "Most events barely move the score · a few technical overhauls do" / "one dot per event · black tick = median · Steam score, first 2 weeks vs 4 weeks before (pp)" | `Event[event_type]`, `Event[event_name]`, `Event[event_date]`, `Game[game]`, `Event Impact[score_change_2w_pp]`, `[net_score_change_2w_pp]`, `[reviews_uplift_2w_pct]` | — |
| `1dd8b385` | clusteredBar | "Which events bring players back" / "average, 2 weeks vs 4 weeks before" | `Event[event_type]`, `[Median Reviews Uplift 2w]`, `[Median Net Reviews Uplift 2w]` | — |
| `927fe977` | clusteredBar — **HIDDEN** | "Typical activity uplift (2 weeks)" / "median, vs 4 weeks before" | same three fields as `1dd8b385` | — |
| `b8370712` | lineChart | "Review activity around events" / "**ndex**, 100 = 4 weeks before · average of selected events · log scale" | `Event Window[day_offset]`, `[Reviews Index (Event Game)]`, `[Reviews Index (Controls)]` | — |
| `b74da243` | Deneb | "When did players suddenly start talking?" / "Weekly reviews vs the year's median week · darker = up to 8× · select one game" | `Date[date]`, `[Reviews]`, `[Negative Reviews]` | — |

**Hard-coded colours.** `1dd8b385` series fills `#C4C8CD` (gross) and `#1F2328`
(net), **plus a leftover diverging fill rule `#B3122E → #FFFFFF → #0E8A9A` driven
by `[Avg Score Change 2w (pp)]`** that the per-series fills override.
`b8370712`: `#1F2328` event-game line, `#9AA0A6` dashed control line and both
reference lines ("Event" at x = 0, "Before-event level" at y = 100).
`0364d049`: `#A87400` / `#2F5D8C`, `#9AA0A6` zero rule, `#1F2328` median tick,
`#EEEEEC` grid (off-palette).
`b74da243`: colour ramp **`#EEF1F5 → #8FA6BF → #2E3F55`** — three off-palette blues.

### 2.4 About (`c9520b2f190774ea4831`)

**Purpose:** what the report is for, how the numbers are built, the KPI dictionary
and the limitations.

* **No page background object.** The whole page is one image visual
  `813c099064a6958e9cc8` at 0,0 1920×1080 showing `About_page_v2_1920x1080.png`
  (registered as `About_page_v2_1920x10802657111250281975.png`).
* No page filters.
* 4 visuals: the image, `3bfdac85` card (`[Data Through]`, `[Last Refreshed]`),
  `527439f0` shape (`#B3122E` line), `b9cd11bb` pageNavigator.
* The page navigator here is the only one with **`showHiddenPages = true`**, so it
  lists the hidden Event log page as a fifth tile while the other three navigators
  show four.
* The image states the colour rule in words: *"red only marks a problem (a drop in
  score, bugs)"*.

### 2.5 Event log (`e97c03195001d56ceca0`) — hidden

**Purpose:** the full event table with before/after score for each event, reached by
drill-through from an event.

* `visibility: HiddenInViewMode`.
* Background image: `EventLog_background_1920x1080.png`
  (`EventLog_background_1920x1080003008021012396944.png`), `Normal`.
* 5 visuals, no interaction overrides.

| id | type | title / subtitle | fields | visual-level filters |
|---|---|---|---|---|
| `42409cd5` | advancedSlicer | title hidden | `Game[Game Label]` | saved selection: CP2077; The Witcher 3; Baldur's Gate 3 |
| `651acbe1` | slicer | **title show = true, no text** | `Event[event_type]` | — |
| `5642585a` | actionButton | — | — | type `Back`, text "Back", fill `#5F6368` |
| `b0dd7a8d` | tableEx | **no title** / "net = vs control group (available as control data arrives)" | `Event[event_date]` (Date), `Event[event_name]` (Event), `Game[game]` (Game), `Event Impact[reviews_uplift_2w_pct]`, `[net_reviews_uplift_2w_pct]`, `[score_change_2w_pp]`, `[net_score_change_2w_pp]`, `[overlapping_event_ids]` | `Event Impact[reviews_uplift_2w_pct]` is not blank |
| `ed26e664` | Deneb | "Steam score before and after each event" / "grey = 4 weeks before · coloured = first 2 weeks after · Steam sales excluded (see table)" | `Event[event_name]`, `[event_date]`, `[event_type]`, `Game[game]`, `Event Impact[steam_score_pre]`, `[steam_score_2w]`, `[net_score_change_2w_pp]` | `Event Impact[reviews_uplift_2w_pct]` is not blank |

**Hard-coded colours.** `b0dd7a8d` conditional background on
`Event Impact[score_change_2w_pp]`: `#B3122E` at −5 → `#FFFFFF` at 0 →
**`#0E8A9A` at +5 (off-palette teal)**. `ed26e664`: `#B3122E` "fell" / `#5F6368`
"rose", `#C4C8CD` before-dot, `#EEEEEC` grid (off-palette), `#1F2328` labels.

---

## 3. Slicers, sync groups, navigation, drill-through

### Slicers and sync groups

| sync group | field | pages | visuals |
|---|---|---|---|
| `Game Label` | `Game[Game Label]` | Overview, Player Voice, What drives, Event log | `b2c6403b`, `6c958506`, `2e467280`, `42409cd5` |
| `Time Window` | `Time Window[Time Window]` | Overview, Player Voice | `93aa83ce`, `87dbfb86` |
| `date` | `Date[date]` | Overview, Player Voice | `52ad895a`, `c7b45144` |
| `region` | `Language[region]` | Overview, Player Voice | `243590c9`, `c4298579` |
| `event_type` | `Event[event_type]` | What drives, Event log | `96eabca1`, `651acbe1` |
| *(none)* | `Event[event_name]` | What drives | `0b62f417` — **not synced** |

All sync groups have `fieldChanges: true` and `filterChanges: true`.

The `Date[date]` slicers carry a RelativeDate filter: last 12 months, upper bound
today. All four Game Label slicers carry the saved selection
`{Cyberpunk 2077; The Witcher 3; Baldur's Gate 3}`; Baldur's Gate 3 is a control
game and cannot appear on the three pages that filter `Game[role] = "cdpr"`, nor in
`Event Impact`, so the third value is dead.

### Page navigator

Four navigators, one per visible page, all at x 659.86 y 20.35, height 35,
`rectangleRoundedByPixel` with 4 px radius, 4 columns, selected tile filled with
theme data colour 0 (`#A87400`), selected text `#1F2328` Segoe UI Semibold 11.

* Overview, Player Voice: width 600, `showHiddenPages = false`.
* What drives interest: **width 650**, `showHiddenPages = false`.
* About: width 600, **`showHiddenPages = true`** → shows 5 tiles including Event log.

Each visible page also carries a decorative `#B3122E` line shape just under the
navigator, marking the current tab:

| page | x | y | width | height |
|---|---|---|---|---|
| Overview | 659.864 | 49.417 | 143.891 | 13.081 |
| Player Voice | 811.404 | 49.762 | 143.758 | 12.441 |
| What drives interest | 989.751 | 50.794 | 155.283 | 11.610 |
| About | 1112.743 | 49.762 | 143.758 | 12.441 |

### Drill-through on Event log

| item | value |
|---|---|
| Binding | `pageBinding` name `8607f74d21d334bd395a`, type `Drillthrough` |
| Field | `Event[event_name]` (parameter `3c75275f4010192e617b`, bound to filter `fd073d80064b005e4347`) |
| Keep all filters | **not recorded in the file.** The PBIR page schema (page/2.1.0) has no `keepFilters` property; the nearest is `acceptsFilterContext`, which defaults to `Default` ("flows filter context"). It is absent here, so the page runs on the default — incoming filter context flows. |
| Cross-report | `referenceScope` absent → `Default` (same report only) |
| Back button | yes — `5642585a`, `actionButton` type `Back`, text "Back", icon `back`, fill `#5F6368`, at 749.67 / 100, 100 × 40 |
| Hidden | yes, `visibility: HiddenInViewMode` |

**Which source visuals offer it.** Drill-through is offered by a visual that carries
`Event[event_name]`. Outside the Event log page that is exactly two visuals, and only
one of them can offer a context menu:

* `0364d049` — the Deneb dot plot on *What drives interest* (`event` field in its
  dataset). The only real drill-through entry point.
* `0b62f417` — the `Event[event_name]` slicer on the same page. Slicers do not offer
  drill-through.

No other visual on any page carries `Event[event_name]`, so the event bar chart, the
heat map, the index line chart and every KPI card cannot reach the page.

### Saved filter state in the file

| page | filter | how created | state |
|---|---|---|---|
| Event log | `Event[event_name] IN {"Steam Summer Sale 2026"}` | `Drillthrough` | **left in the file** |
| Overview, Player Voice, What drives | `Game[role] IN {"cdpr"}` | `User` | intended |
| Overview, Player Voice | `Date[date]` relative last 12 months | slicer default | intended |
| 4 Game Label slicers | CP2077 / The Witcher 3 / Baldur's Gate 3 | slicer selection | stale (BG3) |
| 2 Time Window slicers | *Selected period* | slicer selection | intended |

### Hidden objects

* Hidden page: **Event log**.
* Hidden visual: **`927fe977` on What drives interest** — a second copy of the
  activity-uplift bar chart, same three fields as the visible `1dd8b385`, sitting
  under it at 1172.4 / 631.8, 359.9 × 420.1.

---

## 4. Semantic model

### Tables and row counts

| table | rows | kind | notes |
|---|---|---|---|
| `Date` | 4 748 | dimension, marked as date table | 2015–2027 |
| `Event` | 51 | dimension | event calendar with source URLs |
| `Game` | 5 | dimension | 2 CDPR + 3 control |
| `Language` | 31 | dimension | language → market → region; RLS key |
| `Topic` | 6 | dimension | topic dictionary |
| `Reviews Daily` | 216 098 | fact | game × date × language |
| `Review Topics Daily` | 372 412 | fact | game × date × language × topic |
| `Players Daily` | 110 | fact | game × date (22 days) |
| `Event Impact` | 62 | fact | one row per event × CDPR game |
| `Event Window` | 20 832 | fact | event study, day −28…+55 |
| `Security Region Access` | 5 | RLS mapping, hidden, no relationships |
| `Refresh Info` | 1 | technical, hidden |
| `Time Window` | 5 | calculation group |
| `_Measures` | 1 (BLANK) | measure container |

### Relationships — 13, all active, all many-to-one, all single-direction

| from | to |
|---|---|
| `Reviews Daily[appid]` → `Game[appid]` | |
| `Reviews Daily[date]` → `Date[date]` | |
| `Reviews Daily[language]` → `Language[language]` | |
| `Review Topics Daily[appid]` → `Game[appid]` | |
| `Review Topics Daily[date]` → `Date[date]` | |
| `Review Topics Daily[language]` → `Language[language]` | |
| `Review Topics Daily[topic]` → `Topic[topic]` | |
| `Players Daily[appid]` → `Game[appid]` | |
| `Players Daily[date]` → `Date[date]` | |
| `Event Impact[event_id]` → `Event[event_id]` | |
| `Event Impact[appid]` → `Game[appid]` | |
| `Event Window[event_id]` → `Event[event_id]` | |
| `Event Window[target_appid]` → `Game[appid]` | not `appid` — the control series keeps its own `appid` |

`Event` has an `appid` column but **no relationship to `Game`**: the Game slicer does
not filter the `Event` table directly, only through `Event Impact` / `Event Window`.
There is no relationship between `Event` and `Date` either.

### Measures by display folder (34, all in `_Measures`)

**Reviews (7)**
| measure | one line |
|---|---|
| `Reviews` | `SUM('Reviews Daily'[reviews])` |
| `Positive Reviews` | sum of positive reviews |
| `Negative Reviews` | sum of negative reviews |
| `Positive %` | positive share of all reviews |
| `Steam Score %` | positive share of Steam-purchase reviews only — the Steam number |
| `Recent Score % (30d)` | `Steam Score %` over the last 30 days up to the period end or last data date |
| `Negative from Newcomers %` | negatives written with < 2 h played, as a share of negatives |
| `Recent vs All-time (pp)` | `Recent Score % (30d)` minus all-time `Steam Score %`, in pp |

**Topics (7)**
| measure | one line |
|---|---|
| `Topic Mentions` | reviews mentioning the topic |
| `Topic Mentions (Negative)` | negative reviews mentioning the topic |
| `Topic Share of Negative %` | topic negatives ÷ topic-scanned negatives |
| `Topic Positive %` | positive share within a topic's mentions |
| `Topic Coverage %` | share of reviews that were scanned for topics |
| `Bugs Share CY (to date)` | bugs share of negatives, 1 Jan → last data date; own time window; dynamic format string prefixes the year |
| `Main Complaint` | the highest-share topic and its share, e.g. "Bugs & crashes · 34%" |

**Players (4)** — `Avg Daily Players`, `Peak Players`, `Data Coverage %`,
`Complete Days`: average players over complete days, highest hourly snapshot,
average snapshot completeness, count of complete days.

**Events (10)** — `Reviews Index (Event Game)`, `Reviews Index (Controls)`,
`Players Index (Event Game)`, `Players Index (Controls)` (100 = the 4 weeks before
the event); `Events Measured` (events with a usable 2-week impact);
`Median Reviews Uplift 2w` and `Median Net Reviews Uplift 2w` (median activity
uplift, gross and net of controls); `Avg Score Change 2w (pp)` and
`Avg Net Score Change 2w (pp)`; `Major Events In Month` (concatenated major event
names in the period).
Plus `Key Event In Month` — the sparser one-per-game-per-month version used for the
Overview chart annotations.

**Data quality (2)** — `Data Through` (last full day = last review date − 1),
`Last Refreshed` (model refresh timestamp).

**Formatting (2)** — `Recent Delta Colour` (`#B3122E` when the recent score is below
all-time, else `#5F6368`), `Bugs Card Colour` (`#B3122E` when the card's bugs share
is more than 5 pp above the year-to-date baseline, else `#1F2328`).

### Calculation group — `Time Window`, precedence 10

Column `Time Window[Time Window]`, 5 items:

| item | effect |
|---|---|
| `Selected period` | `SELECTEDMEASURE()` unchanged |
| `Last 30 days` | last 30 days from the period end or last data date |
| `Last 12 months` | last 12 months from the same anchor |
| `Prior year` | `SAMEPERIODLASTYEAR` |
| `YoY change` | current minus prior year, blank if either side is blank |

The four non-trivial items pass 13 measures through untouched via
`ISSELECTEDMEASURE`: `Recent Score % (30d)`, the four index measures,
`Events Measured`, the two median uplifts, the two average score changes,
`Major Events In Month`, `Data Through`, `Last Refreshed`.
`Bugs Share CY (to date)` is **not** on that list but protects itself with
`REMOVEFILTERS('Date')`.

### RLS / OLS

One role, **`Regional access`**, `modelPermission: read`:

* **RLS** on `Language`: dynamic — the user's regions come from
  `'Security Region Access'` by `USERPRINCIPALNAME()`; the literal region `ALL`
  grants every region.
* **RLS** on `Security Region Access`: a user sees only their own rows.
* **OLS** on `Players Daily`: `columnPermission failed_requests = none` and
  `snapshots_ok = none` — both columns are hidden from the role entirely.

No perspectives, no translations beyond the `en-US` culture, no other roles.

### BPA

Tabular Editor 2.29.0 run read-only against
`CDPR_Health_Hub.SemanticModel\definition\database.tmdl` with `bpa\BPARules.json`
(68 rules):

```
No objects in violation of Best Practices.
```
**Exit code 0, zero violations** — matches `bpa/README.md`. 26
`BestPracticeAnalyzer_IgnoreRules` annotations (13 in `_Measures`, 4 in
`Event Window`, 3 each in `Date` and the role, 1 each in `Refresh Info`,
`Security Region Access` and `Time Window`) and 3 removed rules are still in place.

---

## 5. Objects no visual uses

### Measures — 14 of 34

`Positive Reviews`, `Positive %`, `Topic Mentions`, `Topic Mentions (Negative)`,
`Topic Positive %`, `Topic Coverage %`, `Avg Daily Players`, `Peak Players`,
`Data Coverage %`, `Complete Days`, `Players Index (Event Game)`,
`Players Index (Controls)`, `Avg Net Score Change 2w (pp)`, `Major Events In Month`.

Four of these — `Positive %`, `Topic Coverage %`, the Players index pair — are
**documented in the About page's KPI dictionary** but appear in no visual.
`Major Events In Month` was superseded by `Key Event In Month`.
`Avg Net Score Change 2w (pp)` has no card even though its gross twin has two.

### Tables

**`Players Daily`** — 110 rows, four measures and an OLS rule, but not one visual on
any page reads it. The About page's "Data & Method" box advertises
"Hourly concurrent players since 21 Oct 2026".

`Security Region Access` and `Refresh Info` are hidden technical tables, as intended
(`Refresh Info` reaches the UI through `[Last Refreshed]`).

### Columns

Visible in the model, used by no visual **and** by no DAX expression, relationship,
sort-by or role:

| table | columns |
|---|---|
| `Date` | `is_weekend`, `iso_week`, `iso_year`, `month_name`, `quarter`, `quarter_name`, `weekday_name`, `weekday_number` |
| `Event` | `duration_days`, `end_date`, `game`, `notes`, `source_url` |
| `Event Impact` | `avg_players_2w`, `avg_players_pre`, `control_reviews_uplift_2w_pct`, `control_score_change_2w_pp`, `n_control_games`, `net_players_uplift_2w_pct`, `net_reviews_uplift_4_8w_pct`, `players_uplift_2w_pct`, `reviews_per_day_2w`, `reviews_per_day_4_8w`, `reviews_per_day_pre`, `reviews_uplift_4_8w_pct` |
| `Event Window` | `avg_players`, `date`, `negative_reviews`, `positive_reviews`, `reviews`, `steam_purchase_positive_reviews`, `steam_purchase_reviews`, `window_phase` |
| `Game` | `collects_reviews`, `is_cdpr`, `is_control`, **`Game Swatch`** (calculated ImageUrl column built for a legend that no visual shows) |
| `Language` | `language_name` |
| `Players Daily` | `failed_requests`, `min_players`, `snapshots_ok` |
| `Reviews Daily` | `edited_reviews`, `median_hours_at_review`, `reviews_under_2h_played` |
| `Topic` | `description` |

Used by DAX but by no visual (expected): `Date[month]`, `Date[year]`,
`Event[appid]`, `[is_platform_wide]`, `[magnitude]`, `Event Window[series_role]`,
`Players Daily[is_complete_day]`, `Topic[topic]`, `Topic[sort_order]` (sort-by), and
every hidden key and measure base column.

**Hidden columns bound directly into visuals:** `Event Impact[score_change_2w_pp]`
and `Event Impact[net_score_change_2w_pp]` are `isHidden` in the model yet appear as
fields in the Event log table and in both Deneb event charts. They keep working, but
a report author cannot re-add them from the field list.

---

## 6. Consistency checks

### 6.1 Titles vs fields

| where | title / subtitle says | field actually is |
|---|---|---|
| What drives, `1dd8b385` | "Which events bring players back" / **"average, 2 weeks vs 4 weeks before"** | `[Median Reviews Uplift 2w]` and `[Median Net Reviews Uplift 2w]` — **medians**. The hidden twin `927fe977` gets this right ("median, vs 4 weeks before"). |
| What drives, `b8370712` | subtitle starts **"ndex, 100 = …"** | should read "Index, 100 = …" — the leading `I` is missing in the literal |
| Overview, card group 4 | PNG heading "Bugs in negative reviews, **last 30 days**" | covers two measures: `[Topic Share of Negative %]` (really last 30 days) and `[Bugs Share CY (to date)]` (**year to date**, self-labelled only by its dynamic format string, e.g. "2026: 34.0%") |
| Player Voice, `100248db` | "Steam score by market" / "Top 10 markets by reviews" | correct — TopN 10 by `[Reviews]`, plus a second `[Reviews] > 1000` filter that is redundant once the Top 10 is applied |
| Event log, `b0dd7a8d` | **no title at all**, only a subtitle | its neighbour `ed26e664` has a title; the page reads lopsided |
| 5 slicers | no title text but `title.show` is true (explicit on `96eabca1`, `0b62f417`, `651acbe1`; inherited from the theme's `title: show = true` on `243590c9` and `c4298579`) | Power BI falls back to the field name, so these render **"event_type"**, **"event_name"**, **"region"** in snake case, on top of the labels already painted into the background PNGs |

### 6.2 "All time" / "last 30 days" cards vs their interactions

| card group | label | mechanism | verdict |
|---|---|---|---|
| Overview "Steam score, all time" | all time | Time window, Period and Game slicers all set to `NoFilter`; **Region is not** | all-time in *date* terms ✓, but a region selection silently narrows it |
| Overview "Recent score (30 days) vs all time" | 30 d vs all time | `[Recent Score % (30d)]` and `[Recent vs All-time (pp)]` have their own windows and are on the calc group's pass-through list; slicers excluded | ✓ |
| Overview "Reviews, last 30 days" | last 30 d | hidden `Time Window = Last 30 days` visual filter + Time window slicer excluded | ✓ |
| Overview "Bugs in negative reviews, last 30 days" | last 30 d | `[Topic Share of Negative %]` carries the `Last 30 days` filter ✓; `[Bugs Share CY (to date)]` carries the same filter but ignores it (`REMOVEFILTERS('Date')`) and stays year-to-date | ✗ label covers two different windows |
| Player Voice "Negative reviews, selected period" etc. | selected period | Time window slicer filters every visual on the page | ✓ |
| What drives interest cards | event measures | all three measures are on the calc group's pass-through list; the page has no Time window slicer | ✓ |

**The biggest finding here:** the Overview Time window slicer is 680 px wide, sits at
the top of the page, and after the 14 `NoFilter` overrides it changes **exactly one
visual** — the topic bar chart `f937c072`. The Period slicer changes three, the
Region slicer changes all sixteen. The same Time window slicer on Player Voice
changes everything.

### 6.3 Colours outside the palette

House palette: games `#A87400` / `#2F5D8C`, red `#B3122E` for problems only,
greys `#1F2328` `#5F6368` `#9AA0A6` `#C4C8CD`, orange `#D9752B`.

| hex | where | visible? |
|---|---|---|
| **`#0E8A9A`** teal | Event log `b0dd7a8d` conditional background (positive end of the −5/0/+5 scale); leftover fill rule on What drives `1dd8b385` | yes, in the Event log table |
| **`#2E3F55` `#8FA6BF` `#EEF1F5`** blues | `b74da243` "When did players suddenly start talking?" colour ramp | yes, the whole heat map |
| **`#D5D7DA`** | outlines of all four Game Label slicers, both Time window slicers, all three "Clear all slicers" buttons | yes |
| **`#EEEEEC`** | grid colour in 3 of the 4 Deneb specs (`82dd9b58`, `0364d049`, `ed26e664`); the fourth uses `#F3F3F1` | faint but yes, and inconsistent between specs |
| `#E6E6E6` | `border.color` on ~20 cards and slicers | no — `border.show` is false |
| `#8A9097`, `#B4B9BF` | topic series on Player Voice `d5bf475e` | yes — in the theme, not in the house list |
| `#C4C8CD` | `1dd8b385` gross-uplift bars, `ed26e664` before-dot | yes — in the house list, **not** in the theme file |

**Red used where nothing is wrong.** The About page states *"red only marks a problem
(a drop in score, bugs)"*. Against that:

* four `#B3122E` line shapes mark the active page-navigator tab on Overview,
  Player Voice, What drives interest and About — pure decoration;
* `100248db` paints the lowest Steam scores red — defensible as "a problem";
* `7d929df0` paints the highest topic shares red — also defensible.

### 6.4 Game names

Three names for one game coexist:

| name | where |
|---|---|
| **The Witcher 3** | `Game[Game Label]` — all four game slicers, and the legends painted into every background PNG |
| **The Witcher 3: Wild Hunt** | `Game[game]` — every chart legend and axis, the market pivot's column headers, the Event log table, the hard-coded `scale.domain` in the Overview and What-drives Deneb specs, and the `Game[game] = …` filter on all 12 pairs of KPI cards |
| **TW3** / **CP2077** | the Event log Deneb spec (`ed26e664`) builds its row labels as `(datum.game == 'Cyberpunk 2077' ? 'CP2077' : 'TW3') + ' · ' + …` |

So a viewer picks "The Witcher 3" in the slicer and reads "The Witcher 3: Wild Hunt"
in the chart beside it, and "TW3" on the Event log. `Game[Game Swatch]`, built to
carry the game colour into tables and cards, is used nowhere.

### 6.5 Misaligned visuals

**Visible (≥ 3 px), worth fixing first:**

* Overview, second KPI row (The Witcher 3): `675e0bef`, `dd33662f` and `467f44b9` sit
  at **y = 230**, while `59a60519`, `7c25e8b1` and `e570c3fb` sit at **y = 235** —
  a 5 px step across one row.
* Overview slicer row: y = 100.288 (Region), 101.721 (Time window), 101.741 (Period),
  104.648 (Clear button), 104.901 (Game) — a 4.6 px spread; heights 36.25 / 36 /
  43.60 / 28 / 35.
* What drives interest slicer row: heights 33.38 (`0b62f417`), 35 (`2e467280`),
  37.73 (`96eabca1`); y = 101 / 101.587 / 104.901.
* Page navigator on What drives interest is 650 px wide against 600 px on the other
  three pages, and its red tab marker is 155.28 px against 143.76–143.89 px.

**Near misses, differing by less than 3 px:**

| page | attribute | visuals | diff |
|---|---|---|---|
| Overview | `x` | `4b7cced4` 356.631 vs `675e0bef` 356.027 (the two Steam-score cards) | 0.604 px |
| Overview | `x` | `467f44b9` 1719.735 vs `81b02860` 1719.568 | 0.167 px |
| Overview | `x` | `ba26a40e` 1269.934 vs `59a60519` 1269.831 | 0.103 px |
| Overview | `y` | `b84d16ea` 170.022 vs the five other top-row cards at 170 | 0.022 px |
| Overview | `y` | `e570c3fb` 234.989 vs `59a60519` / `7c25e8b1` at 235 | 0.011 px |
| Overview | `height` | cards are 78.790 (`3f91a4c7`, `b84d16ea`), 80 (eight cards) and 80.173 (`7c25e8b1`, `e570c3fb`) | up to 1.38 px |
| Overview | right edge | `2d740824` / `f937c072` 1880.265, `467f44b9` 1879.735, `81b02860` 1879.568, `9d71ee47` 1882.210, `c891b290` 1882.506 | up to 2.94 px |
| Overview | `y` | Region slicer 100.288 vs Time window 101.722 | 1.434 px |
| Player Voice | `x` | `c663ebdb` 507.170 vs `07cbdce2` 507 | 0.170 px |
| Player Voice | `x` | `163c4ccd` 1123.019 vs `65b9ea46` 1123 | 0.019 px |
| Player Voice | `x` / `width` | `100248db` 1121.814 / 760.454 vs `7d929df0` 1122.119 / 759.735 | 0.305 / 0.718 px |
| Player Voice | `y` | `80ee5db2` 169.412 vs the 170 row; `7a75cce7` 229.305 vs the 230 row | 0.588 / 0.695 px |
| Player Voice | `height` | `80ee5db2` / `7a75cce7` 80.428 vs the other four cards at 80 | 0.428 px |
| Player Voice | `height` | `7d929df0` 274 vs `df812d50` 273.377 | 0.623 px |
| What drives | right edge | `1dd8b385` / `b8370712` 1884.694 vs `1e193649` 1882.210 vs `eeb10054` 1882.506 | up to 2.48 px |
| What drives | `y` | `927fe977` (hidden) 631.762 vs `b8370712` 632.154 | 0.392 px |
| Event log | `y` / `height` | `651acbe1` 101 / 37.73, `5642585a` 100 / 40, `42409cd5` 104.901 / 35 | 1–2.7 px |
| every page | bottom edge | the refresh card ends at 55.231, the navigator at 55.348 (About: equal) | 0.117 px |

---

## 7. Key numbers for the README

All DAX run against the live model on 2026-11-11. Review history 2015-05-18 →
2026-11-10 (the last day is partial); the model's own "data through" date is
**2026-11-09**.

### Steam score per game

| game | all time | last 30 days | reviews (all time) |
|---|---|---|---|
| **Cyberpunk 2077** | **87.7 %** | **94.0 %** | 1 005 191 |
| **The Witcher 3: Wild Hunt** | **96.4 %** | **91.3 %** | 909 406 |
| Baldur's Gate 3 *(control)* | 96.8 % | 94.7 % | 864 852 |
| ELDEN RING *(control)* | 93.2 % | 92.3 % | 1 161 614 |
| Red Dead Redemption 2 *(control)* | 92.6 % | 94.7 % | 935 491 |

Cyberpunk 2077 is **6.3 pp above** its all-time score over the last 30 days;
The Witcher 3 is **5.1 pp below** its own — the Remaster effect.

### Bugs share of negative reviews

Share of topic-scanned negative reviews mentioning *Bugs & crashes*:

| game | 2020 | 2025 | 2026 (YTD) | last 30 days | all time |
|---|---|---|---|---|---|
| Cyberpunk 2077 | **50.8 %** | 33.9 % | 34.0 % | **40.5 %** | 43.1 % |
| The Witcher 3: Wild Hunt | 12.1 % | 19.3 % | 27.7 % | **39.1 %** | 18.2 % |

Last-30-day bases: 1 078 scanned negative reviews for Cyberpunk 2077, 504 for
The Witcher 3. The Witcher 3's bugs share has risen every period shown — 12 % → 19 %
→ 28 % → 39 %.

### Five largest score drops (first 2 weeks vs 4 weeks before)

| # | event | type | date | game | score change | net of controls |
|---|---|---|---|---|---|---|
| 1 | The Witcher 3 Remastered (free upgrade) | major_update | 2026-09-29 | The Witcher 3 | **−17.6 pp** | −18.0 pp |
| 2 | Next-gen update 4.0 | major_update | 2022-12-14 | The Witcher 3 | −10.4 pp | −8.4 pp |
| 3 | Update 1.62 Ray Tracing: Overdrive | patch | 2023-04-11 | Cyberpunk 2077 | −8.7 pp | −9.0 pp |
| 4 | Patch 1.1 | patch | 2021-01-22 | Cyberpunk 2077 | −4.2 pp | −3.1 pp |
| 5 | Patch 1.3 with free DLC | major_update | 2021-08-18 | Cyberpunk 2077 | −3.7 pp | −3.8 pp |

All five are technical releases. No sale, expansion or transmedia event appears.

### Five largest net activity uplifts (first 2 weeks vs 4 weeks before, net of controls)

| # | event | type | date | game | net uplift | gross uplift | score change |
|---|---|---|---|---|---|---|---|
| 1 | Update 2.0 | major_update | 2023-09-21 | Cyberpunk 2077 | **+595 %** | +449 % | −2.8 pp |
| 2 | The Witcher 3 Remastered (free upgrade) | major_update | 2026-09-29 | The Witcher 3 | **+554 %** | +523 % | −17.6 pp |
| 3 | Cyberpunk: Edgerunners premiere on Netflix | transmedia | 2022-09-13 | Cyberpunk 2077 | +457 % | +430 % | +0.6 pp |
| 4 | Phantom Liberty expansion | expansion | 2023-09-26 | Cyberpunk 2077 | +300 % | +224 % | +0.4 pp |
| 5 | Cyberpunk: Edgerunners 2 premiere on Netflix | transmedia | 2026-10-20 | Cyberpunk 2077 | +245 % | +190 % | −1.6 pp |

The Witcher 3 Remaster is the only event in both lists: the second-largest audience
surge and by far the largest score drop.

### Markets with at least 10 000 reviews (all time, Steam score)

**Cyberpunk 2077** — 11 markets qualify:

| | market | reviews | Steam score |
|---|---|---|---|
| lowest | **South Korea** | 26 044 | **79.2 %** |
| | China | 251 712 | 80.9 % |
| | Taiwan & Hong Kong | 11 044 | 84.0 % |
| highest | **Poland** | 27 732 | **95.4 %** |

**The Witcher 3: Wild Hunt** — 11 markets qualify:

| | market | reviews | Steam score |
|---|---|---|---|
| lowest | **South Korea** | 17 270 | **94.0 %** |
| | China | 211 835 | 94.8 % |
| highest | **Brazil** | 55 477 | **98.6 %** |
| | Poland | 49 579 | 98.3 % |

South Korea is the weakest market for both games; the spread is 16.2 pp for
Cyberpunk 2077 and only 4.6 pp for The Witcher 3.

### Volumes

| | |
|---|---|
| Events in the calendar | **51** |
| Event × game impact rows | 62, of which **58** have a measured 2-week impact |
| Reviews, all five games | **4 876 554** |
| Reviews, the two CDPR games | **1 914 597** |
| Days with review data | 4 195 distinct dates, 2015-05-18 → 2026-11-10 |
| Days of player data | **22** (2026-10-21 → 2026-11-11), 110 rows, 95 complete days |
| Games tracked | 5 (2 CDPR, 3 control) |
| Markets | 31 languages → markets and regions |
| Topics | 6 |

---

## 8. Issue list

Ordered roughly by how much a reader would notice. **Status added 2026-11-11**
after the fix pass: 15 of the 24 are fixed, 3 partly, 6 deliberately kept.
Sections 1–7 above still describe the state *before* that pass.

The fix pass also replaced the Overview and About artwork with the v3 PNGs and
unified the slicer row on all four pages that have one; neither was on this list.

A **third pass** on the same day added none of its own entries either: the Event
log page filter, the navigator font fit, four Event log changes, the new
`Event[event_type_label]`, two Player Voice details and one Deneb axis. It is
written up under [Third pass](#third-pass-2026-11-11--event-type-labels-event-log-navigator-fit)
below, and the **Clean** list at the end of this section reflects it.

| # | issue | status |
|---|---|---|
| 1 | Overview Time window slicer changed one visual | **fixed** |
| 2 | "Bugs … last 30 days" covers a year-to-date number | kept |
| 3 | Overview Region slicer has no interaction overrides | kept |
| 4 | Red used as decoration (four tab markers) | kept |
| 5 | Drill-through filter left saved in the file | **fixed** |
| 6 | Three game names in one report | **partly** |
| 7 | Five slicers render a raw column name | **fixed** |
| 8 | "average" subtitle over median fields | **fixed** |
| 9 | Off-palette colours | **partly** |
| 10 | Hidden duplicate visual `927fe977` | **fixed** |
| 11 | "ndex" typo | **fixed** |
| 12 | Drill-through has one real entry point | kept |
| 13 | "Keep all filters" not recorded anywhere | kept |
| 14 | About navigator shows the hidden page; navigator widths disagree | **fixed** |
| 15 | `Players Daily` reaches no visual | kept |
| 16 | Four KPI dictionary entries describe unused measures | kept |
| 17 | Event log table has no title | **fixed** |
| 18 | Stale "Baldur's Gate 3" slicer selection | **fixed** |
| 19 | Two hidden model columns bound into visuals | kept |
| 20 | Page order puts hidden Event log after About | **fixed** |
| 21 | Filter pane opens expanded; page filters on show | **fixed** |
| 22 | `Avg Net Score Change 2w (pp)` has no card; `Game Swatch` unused | **partly** |
| 23 | Alignment | **fixed** |
| 24 | Market pivot carries a redundant filter | **fixed** |

### What was fixed

**1 · Overview Time window slicer.** Deleted (`93aa83ce`). Its 14 `NoFilter`
overrides went with it, so the page is down from 50 interaction overrides to 36
and from 23 visuals to 22. The KPI cards keep their own hidden
`Time Window = Last 30 days` filters, so "Reviews, last 30 days" and both bugs
card groups still read 30 days. Player Voice keeps its copy (`87dbfb86`), now
the only member of the `Time Window` sync group.

**5 · Saved drill-through value.** `Event[event_name] = "Steam Summer Sale 2026"`
removed from the Event log page. The filter container `fd073d80064b005e4347`
and its `pageBinding` parameter stay, now with no `filter` property — which the
`filterConfiguration/1.3.0` schema allows (only `name` is required).

**7 · Slicer titles.** `title.show = false` on all five: `243590c9` and
`c4298579` (region, which inherited `true` from the theme) and `96eabca1`,
`0b62f417`, `651acbe1` (event_type / event_name, explicit `true`).

**8 · "Which events bring players back".** Subtitle is now
"Median, first 2 weeks vs 4 weeks before", matching
`[Median Reviews Uplift 2w]` / `[Median Net Reviews Uplift 2w]`.

**10 · Hidden duplicate.** `927fe977` deleted from What drives interest
(18 visuals → 17).

**11 · Typo.** `b8370712` subtitle now reads "Index, 100 = 4 weeks before …".

**14 · Page navigators.** All four are now width 600 with
`showHiddenPages = false` (What drives interest was 650; the About navigator was
already `false` on disk before this pass, so §3's "only one with `true`" was
already out of date).

**17 · Event log table.** Title "All events, newest first" — which the visual's
own sort backs up: `Event[event_date]` descending.

**18 · Stale slicer selection.** "Baldur's Gate 3" dropped from all four Game
Label slicers; each now saves Cyberpunk 2077 and The Witcher 3.

**20 · Page order.** Overview → Player Voice → What drives interest →
**Event log** → About.

**21 · Filter pane.** `outspacePane.expanded = false`, and the three
`Game[role] IN {"cdpr"}` page filters carry `isHiddenInViewMode: true` and
`isLockedInViewMode: true`.

**24 · Market pivot.** The `Advanced` `[Reviews] > 1000` filter is gone;
the TopN 10 markets by `[Reviews]` remains and does the same job.

**Images.** The Overview and About artwork are the v3 PNGs. Both were already
registered with matching bytes
(`Overview_background_v3_1920x1023222584110160627.png`,
`About_page_v3_1920x10805021259861420947.png`), and the About page had already
gained a page background pointing at the v3 copy — but the full-page image
visual `813c099064a6958e9cc8` still showed v2, so the page still rendered the
old art. That visual was deleted and the page now shows its v3 background, like
the other four pages. The orphaned `About_page_v2_…png` registration and file
went too (7 registered resources → 6). About is down from 4 visuals to 3.

**Slicer rows.** Unified on every page that has one: Game, Time window, Period,
Region and the event dropdowns at `y = 104.9, height 35`; "Clear all slicers"
at `y = 108, height 28`; the Event log "Back" button at `y = 104.9, height 35`.
Player Voice was not named in §6.5 but had the same 4.6 px spread as Overview,
so it got the same treatment.

### Partly fixed

**6 · Game names.** Every chart and table now binds `Game[Game Label]`, so they
read "The Witcher 3": `2d740824`, `f937c072`, `82dd9b58` (Overview),
`d5bf475e`, `df812d50`, `100248db` (Player Voice), `0364d049` (What drives),
`b0dd7a8d`, `ed26e664` (Event log). The hard-coded `scale.domain` in the
Overview and What-drives Deneb specs is now `["Cyberpunk 2077", "The Witcher 3"]`.

Deliberately unchanged:

* the Event log Deneb (`ed26e664`) still builds its row labels as
  `CP2077` / `TW3` — there is no room for the full names in that column;
* the **12 hidden KPI card filters still bind `Game[game] = "The Witcher 3:
  Wild Hunt"`**. They are filters, not labels, so nothing shows the long name;
  swapping them would be 12 more edits for no visible gain.

So two names still coexist in the file, but only one — "The Witcher 3" — is now
visible anywhere outside the Event log abbreviations.

Mechanics worth recording: the three Deneb visuals keep
`nativeQueryRef`/`displayName` of `"game"` on the swapped field, because Deneb
names its dataset columns from `displayName` and all three specs reference
`datum.game`. The other six take `nativeQueryRef: "Game Label"`, except
`100248db` (header already renamed `" "`) and `b0dd7a8d` (renamed `"Game"`),
which keep theirs. `b0dd7a8d` also carried a saved column width keyed on
`"metadata": "Game.game"`, which was repointed to `Game.Game Label` so the
width survives.

**9 · Off-palette colours.** Gone:

* `#0E8A9A` in both places — the Event log conditional background now runs
  `#B3122E` → `#FFFFFF` → **`#E6E7E9`**, and the leftover diverging fill rule on
  `1dd8b385` was removed outright (its per-series `#C4C8CD` / `#1F2328` fills
  were already overriding it);
* the grid disagreement — `82dd9b58`'s x-axis `#F3F3F1` is now `#EEEEEC`, so all
  three Deneb specs that draw a grid use `#EEEEEC`. The heat map `b74da243` has
  no grid, so its `#F3F3F1` is untouched.

Still off-palette, by decision: the heat map's `#EEF1F5 / #8FA6BF / #2E3F55`
blue ramp, `#D5D7DA` on slicer and button outlines, `#EEEEEC` itself, and the
new `#E6E7E9`. `#E6E7E9` is a neutral light grey rather than a second hue, so
the Event log table no longer reads teal-for-good against the About page's
"red only marks a problem" rule, but it is not in the house list either.

**22 · `Game Swatch`.** Deleted from the model (`Game` is down from 8 columns to
7). The two auto-generated Q&A entries that bound to it — entity
`game.game_swatch` and relationship `game_has_game_swatch` in
`cultures/en-US.tmdl` — were removed with it, leaving 192 entities and 125
relationships in the linguistic metadata. `Avg Net Score Change 2w (pp)` still
has no card.

**23 · Alignment.** Snapped to the **background grid** rather than to
neighbouring visuals. The painted cards measure 40 → 1880 on every page, with
inner edges at 488/504/952/968/1416/1432 (Overview KPI row),
643/659/1262/1277 (Player Voice and What drives KPI rows) and 1107/1123 (the
chart rows on all five pages).

Applied:

* every chart, table and flush KPI card on a card that ends at 1880 now ends at
  exactly **1880**: `2d740824`, `f937c072`, `81b02860`, `467f44b9` (Overview),
  `7d929df0`, `100248db` (Player Voice), `1dd8b385`, `b8370712` (What drives),
  `ed26e664` (Event log) — the two What-drives charts had been overhanging the
  card by 4.7 px;
* every visual that starts at the left page margin now starts at exactly **40**:
  `82dd9b58`, `2d740824`, `d5bf475e`, `df812d50`, `0364d049`, `b74da243`,
  `b0dd7a8d` (which was 3.6 px in);
* the header strip is at a single right edge of 1880 on all five pages and stays
  byte-identical across them: the Data through / Last refreshed card at
  `x = 1645.995`, "Clear all slicers" at `x = 1730`;
* the **inner column edge**, in a second pass: every left-column visual now ends
  at exactly **1107** (`82dd9b58`, `d5bf475e`, `df812d50`, `0364d049`,
  `b74da243`, `b0dd7a8d` — all width 1067 from x 40) and every right-column
  visual starts at exactly **1123** (`f937c072`, `7d929df0`, `100248db`,
  `1dd8b385`, `b8370712`, `ed26e664` — all x 1123 width 757). They had been off
  by 0.8–2.6 px, bleeding over the gutter between the two painted cards.
  Overview's `2d740824` is excluded: it sits on the full-width card, 40 → 1880;
* the vertical snaps §6.5 listed: the Witcher KPI row to `y = 235`, all twelve
  Overview cards to `height 80`, `b84d16ea` to `y = 170`, Player Voice
  `80ee5db2` / `7a75cce7` to `y = 170 / 230` and `height 80`, `df812d50` to
  `height 274`, and the three page navigators to `height 34.882664…` so their
  bottom edge meets the refresh card at 55.231 (About already did).

**Still not on the grid.** Every edge that remains off the grid belongs to a KPI
value card sitting inside its painted card — 24 visuals, down from 36 after the
first pass:

| what | edge | note |
|---|---|---|
| KPI value cards | various | inset inside their painted cards by design, not flush: Overview columns at 356.0/356.6, 718.8, 820.1, 1269.8/1269.9, 1596.5 ending at 486.0/486.6, 819.7, 950.1, 1399.8/1399.9, 1719.6; Player Voice at 507/507.17 → 637 and 1123 → 1253; What drives at 507 → 637, 1100 → 1230, 1700 → 1830. The sub-pixel pairs (`4b7cced4` 356.631 vs `675e0bef` 356.026, `ba26a40e` 1269.934 vs `59a60519` 1269.831, `c663ebdb` 507.170 vs `07cbdce2` 507, `163c4ccd` 1123.019 vs `65b9ea46` 1123) are unchanged, because the agreed rule was to snap to the grid and not to each other |
| the wide "Main complaint" cards | 1861.818 | `80ee5db2` / `7a75cce7` sit 18 px inside the painted card, clearly not meant to be flush |
| the Player Voice / What drives KPI rows | 643 / 659 / 1262 / 1277 | those rows do have their own inner column edges, but every visual in them is one of the inset value cards above — the nearest approach is 637 against 643 — so nothing snapped to them |
| the Overview KPI row | 488 / 952 | worth a look rather than a fix: the column-1 cards end at 486.0 / 486.6 and the column-2 cards at 950.1, which is 1.4–2.0 px short of the painted card edge. Close enough that they may have been meant to sit flush right; the rest of that row's edges are nowhere near a card edge, so they were treated as inset like the others |
| header and slicer strip | — | 28 visuals — slicers, navigators, buttons, tab markers — sit above the painted cards on the page background, so the grid does not apply. The Overview Period and Region slicers were moved to `x = 490` and `x = 817` to line up with the PERIOD and REGION labels painted at 430 and 760 in the new background |
| the four tab markers | — | decorative shapes, left where they are, except the one noted below |

**The What drives interest tab marker, fixed in the second pass.** Its navigator
went 650 → 600, which moved tile 3 from 984.864–1147.364 to 959.864–1109.864
and left the marker `f413bbd2` straddling tiles 3 and 4 at 989.751–1145.034.
It is now `x = 961.404, y = 49.762, width = 143.758, height = 12.441` — Player
Voice's marker rounded to 3 dp, giving the same 1.54 px left and 4.70 px right
inset inside its tile. The §3 table above still lists its old geometry.

**Not verified.** The two Period slicers (`52ad895a`, `c7b45144`) are
`Between` date slicers that went from height 43.603 to 35 — the largest
reduction in the pass — and Power BI Desktop was closed throughout, so nothing
rendered them. The dropdowns are safe: `0b62f417` already rendered at 33.379
with the same theme font and gained room at 35.

### Deliberately kept

* **2** — `[Bugs Share CY (to date)]` still sits under a "last 30 days" heading
  painted into the PNG. Fixing it means a new measure, a new card, or new
  artwork, none of which was in scope.
* **3** — the Overview Region slicer still filters all sixteen data visuals,
  including the "all time" cards.
* **4** — the four `#B3122E` tab markers are still decoration. They were
  explicitly left in place.
* **12** — only `0364d049` carries `Event[event_name]`, so the Deneb dot plot is
  still the one way into the Event log page.
* **13** — "keep all filters" is still unrecorded; `acceptsFilterContext` is
  absent, so the page runs on the PBIR default.
* **15, 16, 19** — `Players Daily`, the four unused KPI dictionary measures and
  the two hidden columns bound into visuals are all unchanged; they are model and
  documentation questions, not report-layout ones.
* **22, in part** — `Avg Net Score Change 2w (pp)` still has no card.
* The inert leftovers: `legend.showGradientLegend = false` on `1dd8b385` (which
  only mattered while the fill rule existed) and `#E6E6E6` `border.color` on
  ~20 cards with `border.show = false`.

### Third pass, 2026-11-11 — event-type labels, Event log, navigator fit

Nothing in this pass came off the list above; all six items were new requests.
Power BI Desktop was closed throughout, so none of it has been rendered.

**A · Event log page filter.** `Event log` was the one page with data visuals and
no `Game[role] IN {"cdpr"}` page filter, which is why its Game slicer still
offered Baldur's Gate 3 — the control game that cannot appear in `Event Impact`.
It now carries the same filter as the other three, copied from What drives
interest: `howCreated: User`, `isHiddenInViewMode: true`,
`isLockedInViewMode: true`, name `fa9f3507fde1c72dcccf`. The page keeps its
`Drillthrough` container `fd073d80064b005e4347` (still with no saved value), so
the `filterConfig` now holds two filters. Four pages filter `role`; only About
does not, and it has no data visual.

**B · Page navigators.** All four navigators now set the **selected** tile to
Segoe UI Semibold **10** (`text` block with `selector.id = "selected"`), down
from 11, so "What drives interest" fits its 150 px tile. The `default` state is
untouched at 11, as is the Semibold family, the `#1F2328` font colour and the
theme-colour-0 selected fill. Width stays 600 across all four, so the four
`#B3122E` tab markers still line up — the memory note about recomputing a
marker's `x` only applies to a width change, and there was none.

**C · Event log, four changes.**

* **Back button `5642585a`** now matches the "Clear all slicers" buttons instead
  of being the only solid-filled button in the report: `fill.show = false` (the
  `#5F6368` `fillColor` entry dropped), `text.fontColor` and `icon.lineColor`
  `#5F6368`, `outline.show = true` with `lineColor` `#D5D7DA`, and
  `y = 108, height = 28` against the slicer row's 104.9 / 35 — the same offset
  the other three pages' Clear-all buttons use. The `back` icon and its left
  alignment are unchanged.
* **Data through / Last refreshed** is now on all five pages. `9d71ee47` was
  copied from Overview as `34b05499e9b0f036fc24` — byte-identical apart from
  `name`, so the same two-value `cardVisual` at the same
  `x = 1645.995, y = 11.628, 234 × 43.603`, which is the header strip's single
  right edge of 1880.
* **Table `b0dd7a8d`** lost its eighth column, `Event Impact[overlapping_event_ids]`
  ("Overlapping events"), so seven columns share the 1067 px width without a
  horizontal scrollbar. No saved `columnWidth` pointed at it (only `event_name`
  and `Game Label` have one), and nothing else in the report references
  `overlapping_event_ids` now. Subtitle replaced with
  "2 weeks after vs 4 weeks before · net = vs control games", which states the
  comparison window the old one left out.
* **Deneb `ed26e664`** subtitle is now "Grey = 4 weeks before · dot = first 2
  weeks after · red = score fell · Steam sales excluded" — it names the red
  encoding, which the spec has had all along (`#B3122E` "fell" / `#5F6368`
  "rose") but no label explained.

**D · `Event[event_type_label]` and `Event[event_type_sort]`.** Two calculated
columns, added through the modeling MCP on a folder connection and exported back
onto `definition`; the round trip touched `tables/Event.tmdl` and nothing else,
so the model diff is 49 added lines.

| raw `event_type` | label | sort |
|---|---|---|
| `release` | Release | 1 |
| `major_update` | Major update | 2 |
| `patch` | Patch | 3 |
| `expansion` | Expansion | 4 |
| `transmedia` | Transmedia | 5 |
| `platform_sale` | Platform sale | 6 |
| `announcement` | Announcement | 7 |
| `related_release` | Related release | 8 |
| `other`, and anything else | Other | 9 |

The list covers all **nine** values the pipeline accepts, not just the seven
that the CDPR pages can show: `stg_events.event_type` has a dbt
`accepted_values` test and `collector/validate_events.py` has a matching
`EVENT_TYPES` set, and both list `related_release` and `other` as well. One row
is `related_release` today (ER002, "Elden Ring Nightreign launch"), a control
game, so the label only ever surfaces off the `role = "cdpr"` pages. The
`SWITCH` ends in a bare `"Other"` / `9`, so a tenth type added upstream shows as
"Other" rather than blank. Both column descriptions say the list mirrors those
two files and has to change with them.

`event_type_sort` is `int64`, `formatString: 0`, `summarizeBy: none`, hidden,
and is `event_type_label`'s `sortByColumn` — which is also why it keeps
`isAvailableInMdx: true` (`SET_ISAVAILABLEINMDX_TO_TRUE_ON_NECESSARY_COLUMNS`)
and why `UNNECESSARY_COLUMNS` does not fire on it despite being hidden and bound
to no visual: both rules exempt a column `UsedInSortBy`. Being *calculated*
columns, though, they do fall in the scope of
`FIRST_LETTER_OF_OBJECTS_MUST_BE_CAPITALIZED`, which `event_type` and every
other name in the table would fail if the rule reached data columns. Rather than
break the table's snake_case for two columns, both carry
`annotation BestPracticeAnalyzer_IgnoreRules = {"RuleIDs":["FIRST_LETTER_OF_OBJECTS_MUST_BE_CAPITALIZED"]}`,
the same treatment `Date[month_start]` already has, and both are listed in
`bpa/README.md`.

Rebound from `Event[event_type]` to `Event[event_type_label]`, with
`queryRef` and `nativeQueryRef` following the field:

* `1dd8b385` "Which events bring players back" — the `Category` projection;
* `96eabca1` (What drives interest) and `651acbe1` (Event log) — both Event type
  slicers. They keep `syncGroup` `"event_type"` and so stay synced with each
  other; neither had a saved selection in `objects.general.filter`, so there are
  no stale literals of the kind the renamed `Game` column left behind.

Deliberately **not** rebound: the two Deneb datasets. `0364d049` and `ed26e664`
both project `Event[event_type]` as `type` and build their own labels in the
spec (`upper(substring(replace(datum.type, '_', ' '), 0, 1)) + …`), which lands
on the same text as the new column for every value — "Major update", "Platform
sale", "Related release" — so the dot plot and the bar chart beside it read the
same without touching a spec. `Event[event_type]` therefore still has three
consumers: the two specs and `[Events Measured]`-style DAX in `_Measures.tmdl`,
which filters `Event[event_type] IN { "release", "expansion", "major_update" }`
on the raw codes.

**E · Player Voice, two details.**

* **`100248db` "Steam score by market"** has `subTotals.rowSubtotals = false`
  added next to the `columnSubtotals = false` it already had, so the bottom
  Total row goes. That row aggregated only the TopN 10 markets, so it read as a
  Steam score that disagreed with the all-markets figure on Overview — two
  different numbers for the same label, with nothing on the page to say why.
* **`7d929df0` "What each region complains about"** subtitle is now
  "Share of negative reviews mentioning each topic" with a capital S, matching
  every other subtitle in the report.

**F · Deneb `0364d049` axes.** The x axis gained `labelFontSize: 11`. The other
two properties asked for were **already in that state** — x `labelColor` was
`#5F6368` and y `labelFontSize` was 12 — so this is a one-property change, and
all four specs now set an explicit axis label size except `b74da243`, the heat
map, whose x labels are month names written by a `labelExpr`.

**Not verified.** Desktop was closed for the whole pass, so nothing here has
been rendered, and three items in particular are worth a look on reopening:

* `icon.lineColor` on the back button. No button in this report had ever set an
  icon colour, so there was no known-good precedent to copy; the name comes from
  the theme-JSON shape for `actionButton` icons, written into the existing
  `selector.id = "default"` entry beside `shapeType`. If Desktop ignores it the
  glyph stays the theme default and only the label turns grey.
* `subTotals.rowSubtotals` on `100248db`. `columnSubtotals` was already in the
  file, so the object name is right; the row half of the pair is inferred, not
  copied from a precedent.
* whether seven columns really clear the scrollbar in `b0dd7a8d`. Five of the
  seven are auto-sized, and the header texts are long ("Net score change (pp)").
* the two calculated columns need a recalculation, which the first open does,
  and Desktop will add its own Q&A entries for them to
  `cultures/en-US.tmdl` on the next save — this pass wrote none.

### Clean

* **BPA: 0 violations**, Tabular Editor 2.29.0 exits 0, against all 68 rules —
  re-run after adding `Event[event_type_label]` and `Event[event_type_sort]`.
* All 76 report JSON files parse, and each is UTF-8 without BOM, CRLF,
  2-space indent, no trailing newline. Every one also re-serialises
  byte-identically, which is what keeps a structural edit to a one-hunk diff:
  the float literals have to be preserved as written (17 significant digits),
  because `json.dumps` shortens them.
* `pageOrder` covers exactly the five page folders, and each of the 66 visuals
  is named after its own folder; all 42 `visualInteractions` sources and targets
  resolve; the deleted visuals are referenced nowhere.
* Registered resources: 6 declared == 6 on disk, and every `ItemName` referenced
  from a page or visual is registered. The seventh — the theme — is reached
  through `report.json`'s `themeCollection.customTheme`, not an `ItemName`,
  so a checker that only scans `ItemName` reports it as unused.
* All 48 filter containers resolve against the model and agree with their own
  declared field, and all 101 projections carry a `queryRef` that matches the
  field beside it. So do the 25 `metadata` selectors — saved column widths,
  per-series fills, conditional formatting — each of which still names a field
  its visual projects.
* All four Deneb specs parse as JSON and every field reference in them resolves
  to a dataset projection or a transform output.
* Every sync group is internally consistent: all four `Game Label` slicers on
  `Game[Game Label]`, both Event type slicers on `Event[event_type_label]`,
  and the `date`, `region` and `Time Window` groups unchanged.
* All 13 relationships are active, many-to-one and single-direction; no
  ambiguity, no inactive leftovers.
* Every measure, column and table carries a description.
* RLS and OLS are both in place and documented, with the dynamic-RLS exceptions
  annotated on the objects.
* The calculation group's pass-through list is complete for the measures that have
  their own time window.
