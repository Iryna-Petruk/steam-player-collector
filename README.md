# CD PROJEKT Back-Catalogue Health Hub

**How alive are The Witcher 3 and Cyberpunk 2077 between major releases, and which events move player interest and sentiment?**

An end-to-end analytics project on public Steam data: automated collection, a tested PostgreSQL + dbt warehouse, and a Power BI semantic model with row-level security, versioned in Git.

> Independent portfolio project based on public data. Not affiliated with or endorsed by CD PROJEKT or Valve. No company logos or game assets are used.

## Key findings

1. **Cyberpunk 2077's recovery is visible in the data.** The Steam score of reviews written each year rose from about 80% in 2020–2021 to about 95% in 2024–2026; in early November 2026 the last 30 days (93.9%) were well above the all-time score (87.7%). Bugs were mentioned in about half of negative reviews in 2020 and about a third in 2026.
2. **The Witcher 3 Remastered (29 Sep 2026) drove the largest reaction in the calendar, and the sharpest drop in score.** Reviews per day were 6.2× the pre-event level in the first two weeks (23× on launch day), while the Steam score fell from 96.3% to 78.7% (−17.7 pp). Bugs went from 13% of negative reviews before the launch to 32% in launch week and 39% a month later; performance complaints rose from 5% to 24% and then eased to 13%. A month later the positive share was 89.5%, still below the 95% before the launch. ([analysis](analysis/witcher3_remaster_findings.md))
3. **Technical overhauls of an old game hurt the score at first; content and TV do not.** Both large technical updates of The Witcher 3 (next-gen 4.0 in 2022: −10.4 pp; Remastered: −17.7 pp) lowered the score in the first two weeks, while Netflix premieres and expansions raised activity with a stable or rising score (Edgerunners: +430% reviews, +0.6 pp).
4. **Markets differ in what they complain about.** Bugs dominate negative reviews in Western Europe (44%) and the Americas (43%), but only 29% in Central & Eastern Europe, where story is mentioned more often (25%). Poland, the studio's home market, rates Cyberpunk 2077 at 95.4%, among the highest of the large markets.

*Effects net of the control group (Baldur's Gate 3, ELDEN RING, Red Dead Redemption 2) are being added as the control group's review history finishes loading; the findings above compare each game with its own 4 weeks before the event.*

## Report

| Page | Question it answers |
| --- | --- |
| **Overview** | Score, recent score, review volume and main complaints per game over time |
| **Player Voice** | What players complain about, by region and market, and who writes negative reviews |
| **What drives interest** | Event study: activity and score around every release, patch, expansion, Netflix premiere and Steam sale, vs a fixed control group |
| **About** | KPI dictionary, data and method, limitations |

## Architecture

```
Steam Web API ──► GitHub Actions ──► CSV in Git ──► PostgreSQL ──► dbt ──► Power BI
  players (hourly)   cron-job.org       raw, append-only   raw          staging      semantic model
  reviews (daily)    trigger            no review text     (text)       intermediate RLS by region
                                                                        marts        PBIP / TMDL in Git
```

| Layer | What it does |
| --- | --- |
| Collection | Hourly concurrent players and full review history for 5 games (2 CDPR + 3 control). Review text and author IDs are never stored: topics (bugs, performance, price, story, content) are tagged by a versioned keyword dictionary in 10 languages while the text is in memory. |
| Warehouse | Idempotent loader (SHA-256 per file), dbt layers raw → staging → intermediate → marts; 80+ data tests including reconciliation of every review, grain checks and a counter wrap-around guard. |
| Event study | `fct_event_window` (every event on a −28…+55 day axis) and `fct_event_impact` (uplift vs 4 weeks before and difference-in-differences vs the control group); NULL when the data cannot support a number. |
| Semantic model | Star schema, ~25 measures in display folders with descriptions, dedicated date table, event tables related through the target game; measures reconciled against SQL to the last digit. |
| Security | Dynamic RLS: a tested, version-controlled access table maps users to regions; a read-only database role for Power BI. |

## What this project demonstrates

| Requirement | Where |
| --- | --- |
| Semantic models and DAX | Star schema, time intelligence (rolling 30-day score), event-study and difference-in-differences measures, KEEPFILTERS, non-additive measures with explicit denominators |
| Platform management, RLS, refresh | Dynamic RLS by region, read-only `powerbi_reader` role, grants re-applied by dbt, one-command refresh (`run_pipeline.ps1`) |
| SQL (PostgreSQL) and data modelling | dbt models, window functions, generated date spines, event windows |
| Git workflow | Power BI project as PBIP/TMDL, pull requests with squash merge, CI-style collection in GitHub Actions |
| Shared KPIs and standards | KPI dictionary, measure descriptions, report theme as a file, documented limitations |
| Data quality | 80+ dbt tests, reconciliation DAX vs SQL, data-coverage KPIs, manual precision checks of the topic dictionary |

## Run it

```powershell
git clone https://github.com/Iryna-Petruk/steam-player-collector
cd steam-player-collector
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# PostgreSQL connection from PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
.\run_pipeline.ps1          # git pull -> load raw -> dbt build
```

Then open `CDPR_Health_Hub.pbip` in Power BI Desktop and refresh. Technical details of the collectors, warehouse and tests: [docs/pipeline.md](docs/pipeline.md).

## Limitations

Steam only (no consoles, GOG or Epic) · players in offline mode are not counted · player history starts on 21 Oct 2026, reviews go back to 2015 · keyword topics do not understand sarcasm or negation · the event calendar is maintained by hand, with a source for every event.
