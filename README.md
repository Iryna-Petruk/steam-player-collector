# Steam Player Collector

Hourly collection of concurrent Steam player counts for CD PROJEKT RED games and a fixed control group of comparable single-player titles. This is the first data source of the **CD PROJEKT Back-Catalogue Health Hub**, a Power BI portfolio project.

> Independent analysis based on public data. Not affiliated with or endorsed by CD PROJEKT or Valve.

## What it does

- Every hour (minute 17, UTC) a GitHub Actions workflow calls the public Steam Web API method `ISteamUserStats/GetNumberOfCurrentPlayers` for each game in `config/games.csv`.
- Results are appended to a daily CSV file: `data/raw/players/YYYY/MM/players_YYYY-MM-DD.csv`.
- Failed requests are retried and, if still failing, recorded with an error status instead of being silently skipped.
- `collector/check_gaps.py` reports missing or failed hours per game and day.

## Games tracked

| Role | Games |
| --- | --- |
| CD PROJEKT RED | Cyberpunk 2077, The Witcher 3: Wild Hunt |
| Control group | Baldur's Gate 3, ELDEN RING, Red Dead Redemption 2 |

The control group was chosen before any analysis and is kept fixed, so event-impact comparisons are not cherry-picked.

## Data columns

| Column | Description |
| --- | --- |
| collected_at_utc | Time of the request, UTC, ISO 8601 |
| appid | Steam application ID |
| game | Game name |
| role | `cdpr` or `control` |
| player_count | Players currently in game on Steam; empty if the request failed |
| status | `ok` or an error description |

## Limitations

- Steam only: console, GOG and Epic players are not included.
- Players in offline mode are not counted by Steam.
- Scheduled GitHub Actions runs can be delayed or occasionally skipped; gaps are visible through `check_gaps.py`.
- History starts on the day collection began; the API does not provide past values.

## Run locally

```bash
python collector/collect_players.py
python collector/check_gaps.py 7
```

Python 3.10+; no packages to install.
