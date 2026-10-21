"""
Collect the current number of Steam players for a list of games.

Run once per hour by GitHub Actions (see .github/workflows/collect-players.yml).
Each run appends one row per game to a daily CSV file:

    data/raw/players/YYYY/MM/players_YYYY-MM-DD.csv

Columns:
    collected_at_utc  when the request was made (UTC, ISO 8601)
    appid             Steam application ID
    game              human-readable name from config/games.csv
    role              "cdpr" or "control" (from config/games.csv)
    player_count      players online in Steam right now (empty if the request failed)
    status            "ok" or a short error description

Only the Python standard library is used, so nothing needs to be installed.
"""

import csv
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

# Public Steam Web API endpoint. No API key is needed for this method.
API_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"

# The repository root is one level above this file's folder (collector/).
REPO_ROOT = Path(__file__).resolve().parent.parent
GAMES_FILE = REPO_ROOT / "config" / "games.csv"
OUTPUT_ROOT = REPO_ROOT / "data" / "raw" / "players"

OUTPUT_COLUMNS = ["collected_at_utc", "appid", "game", "role", "player_count", "status"]

MAX_ATTEMPTS = 3          # how many times to try one game before giving up
RETRY_WAIT_SECONDS = 5    # wait before the 2nd attempt; doubles each time (5, 10)
PAUSE_BETWEEN_GAMES = 1   # be polite to the API: 1 second between requests
TIMEOUT_SECONDS = 20      # give up on a single request after this long


def load_games(path: Path) -> list[dict]:
    """Read the list of games to track from config/games.csv."""
    with path.open(newline="", encoding="utf-8") as f:
        games = [row for row in csv.DictReader(f) if row.get("appid", "").strip()]
    if not games:
        raise SystemExit(f"No games found in {path}")
    return games


def fetch_player_count(appid: str) -> tuple[int | None, str]:
    """
    Ask Steam how many people are playing this game right now.

    Returns (player_count, status). On failure player_count is None and
    status explains what went wrong, so the problem is visible in the data.
    """
    url = API_URL.format(appid=appid)
    request = urllib.request.Request(url, headers={"User-Agent": "steam-player-collector/1.0 (portfolio project)"})
    last_error = "unknown error"

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read().decode("utf-8"))
            # Expected shape: {"response": {"player_count": 12345, "result": 1}}
            body = payload.get("response", {})
            if body.get("result") == 1 and "player_count" in body:
                return int(body["player_count"]), "ok"
            last_error = f"unexpected response: {json.dumps(payload)[:120]}"
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}"
        except urllib.error.URLError as e:
            last_error = f"network error: {e.reason}"
        except (TimeoutError, ValueError) as e:
            last_error = f"{type(e).__name__}: {e}"

        if attempt < MAX_ATTEMPTS:
            time.sleep(RETRY_WAIT_SECONDS * 2 ** (attempt - 1))

    return None, last_error


def output_file_for(moment: datetime) -> Path:
    """Daily file, grouped into year/month folders so no folder gets huge."""
    return OUTPUT_ROOT / f"{moment:%Y}" / f"{moment:%m}" / f"players_{moment:%Y-%m-%d}.csv"


def append_rows(path: Path, rows: list[dict]) -> None:
    """Append rows to the CSV, writing the header first if the file is new."""
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    games = load_games(GAMES_FILE)
    # One timestamp for the whole run, so all games in a run share the same hour.
    collected_at = datetime.now(timezone.utc).replace(microsecond=0)

    rows = []
    for i, game in enumerate(games):
        if i > 0:
            time.sleep(PAUSE_BETWEEN_GAMES)
        appid = game["appid"].strip()
        count, status = fetch_player_count(appid)
        rows.append({
            "collected_at_utc": collected_at.isoformat(),
            "appid": appid,
            "game": game["game"].strip(),
            "role": game.get("role", "").strip(),
            "player_count": "" if count is None else count,
            "status": status,
        })
        print(f"{game['game']:<28} {status:<12} {'' if count is None else count}")

    target = output_file_for(collected_at)
    append_rows(target, rows)
    print(f"Saved {len(rows)} rows to {target.relative_to(REPO_ROOT)}")

    # If every single request failed, exit with an error so GitHub marks the run
    # as failed and sends you an email. Partial failures are only recorded.
    if all(r["status"] != "ok" for r in rows):
        print("All requests failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
