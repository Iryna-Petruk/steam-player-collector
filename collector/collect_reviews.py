"""
Collect Steam user reviews (metadata only) for the games marked reviews=yes
in config/games.csv.

Uses the Steam Web API method IUserReviewsService/GetAppReviews (no key needed).
Docs: https://partner.steamgames.com/doc/webapi/IUserReviewsService

Two phases per game, chosen automatically:

1. BACKFILL - downloads the full review history once, one calendar month
   (by review creation date) at a time. Progress is saved after every
   completed month in state/reviews_state.json, so the backfill can be
   spread over several runs (GitHub stops a job after 6 hours).

2. INCREMENTAL - once the backfill is done, each run downloads only reviews
   that were created or updated since the previous run (the "watermark").

Privacy and size: the review text and the author's Steam ID are NOT stored.
Only metadata (date, language, positive/negative, playtime, votes...), the
length of the text and topic flags are saved. Topics (bugs, performance,
price, story, content) are found by keywords from config/review_topics.csv
while the text is in memory; the text is then discarded.

When the topic dictionary changes, its version changes too, and the backfill
starts again from the beginning, so every review is tagged by the same rules.

Output (append-only raw data; duplicates are removed later, in dbt):
    data/raw/reviews/<appid>/backfill/reviews_<appid>_<YYYY-MM>.csv
    data/raw/reviews/<appid>/updates/reviews_<appid>_updates_<YYYY-MM-DD>.csv

Usage:
    python collector/collect_reviews.py                 # normal run
    python collector/collect_reviews.py --probe 1091500 # test the API, saves nothing
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # find review_topics.py next to this file
import review_topics  # noqa: E402

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

API_URL = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/"

REPO_ROOT = Path(__file__).resolve().parent.parent
GAMES_FILE = REPO_ROOT / "config" / "games.csv"
STATE_FILE = REPO_ROOT / "state" / "reviews_state.json"
OUTPUT_ROOT = REPO_ROOT / "data" / "raw" / "reviews"

BACKFILL_FROM = datetime(2015, 1, 1, tzinfo=timezone.utc)  # before The Witcher 3 (May 2015)

FILTER_RECENT = 1          # sort by creation date, newest first (used for backfill)
FILTER_UPDATED = 2         # sort by last update, newest first (used for incremental)
PURCHASE_ALL = 1           # Steam purchases and keys from other stores
PER_PAGE = 100             # maximum allowed by the API

PAUSE_BETWEEN_REQUESTS = 1.5   # seconds; keeps us well under the anonymous rate limit
MAX_ATTEMPTS = 5               # per request
TIMEOUT_SECONDS = 30
OVERLAP_SECONDS = 2 * 86400    # incremental runs re-read 2 days to be safe
MAX_PAGES_PER_WINDOW = 5000    # safety stop: 500,000 reviews in one month

# Stop starting new work after this many minutes (GitHub kills jobs at 6 h).
TIME_BUDGET_MINUTES = float(os.environ.get("REVIEWS_TIME_BUDGET_MIN", "300"))

OUTPUT_COLUMNS = [
    "recommendation_id", "appid", "language",
    "created_utc", "updated_utc", "voted_up",
    "votes_up", "votes_funny", "weighted_vote_score", "comment_count",
    "steam_purchase", "received_for_free", "written_during_early_access",
    "refunded", "primarily_steam_deck",
    "playtime_at_review_min", "playtime_forever_min", "author_num_reviews",
    "has_developer_response", "review_length", "fetched_at_utc",
    "topic_bugs", "topic_performance", "topic_price", "topic_story", "topic_content",
    "topics_scanned", "topics_version",
]

TOPIC_DICTIONARY, TOPICS_VERSION = review_topics.load_dictionary()


class RateLimited(Exception):
    """Steam kept answering 429 Too Many Requests; stop for today."""


# ---------------------------------------------------------------------------
# Talking to Steam
# ---------------------------------------------------------------------------

def call_api(params: dict) -> dict:
    """
    One request to GetAppReviews. Parameters go into input_json, as Steam
    expects for Service interfaces; this also URL-encodes the cursor safely.
    Retries on network errors and 5xx; backs off hard on 429.
    """
    query = urllib.parse.urlencode({"input_json": json.dumps(params)})
    request = urllib.request.Request(
        f"{API_URL}?{query}",
        headers={"User-Agent": "steam-review-collector/1.0 (portfolio project)"},
    )
    rate_limit_hits = 0
    last_error = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as resp:
                return json.loads(resp.read().decode("utf-8")).get("response", {})
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}"
            if e.code == 429:
                rate_limit_hits += 1
                if rate_limit_hits >= 3:
                    raise RateLimited("Steam returned 429 three times in a row")
                time.sleep(60 * rate_limit_hits)      # 1 min, then 2 min
                continue
            if e.code < 500:
                raise                                   # 4xx other than 429: our mistake, stop
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            last_error = f"{type(e).__name__}: {e}"
        time.sleep(5 * attempt)
    raise RuntimeError(f"Request failed after {MAX_ATTEMPTS} attempts: {last_error}")


def base_params(appid: str) -> dict:
    return {
        "appid": int(appid),
        "languages": ["all"],
        "purchase_type": PURCHASE_ALL,
        "num_per_page": PER_PAGE,
    }


def to_row(r: dict, appid: str, fetched_at: str) -> dict:
    """Keep metadata and topic flags only. No review text, no author Steam ID."""
    author = r.get("author", {}) or {}
    b = lambda v: 1 if v else 0
    language = r.get("language", "")
    flags, scanned = review_topics.tag(r.get("review", ""), language, TOPIC_DICTIONARY)
    return {
        "recommendation_id": str(r.get("recommendationid", "")),
        "appid": appid,
        "language": language,
        "created_utc": iso(r.get("timestamp_created")),
        "updated_utc": iso(r.get("timestamp_updated")),
        "voted_up": b(r.get("voted_up")),
        "votes_up": r.get("votes_up", 0),
        "votes_funny": r.get("votes_funny", 0),
        "weighted_vote_score": r.get("weighted_vote_score", ""),
        "comment_count": r.get("comment_count", 0),
        "steam_purchase": b(r.get("steam_purchase")),
        "received_for_free": b(r.get("received_for_free")),
        "written_during_early_access": b(r.get("written_during_early_access")),
        "refunded": b(r.get("refunded")),
        "primarily_steam_deck": b(r.get("primarily_steam_deck")),
        "playtime_at_review_min": author.get("playtime_at_review", ""),
        "playtime_forever_min": author.get("playtime_forever", ""),
        "author_num_reviews": author.get("num_reviews", ""),
        "has_developer_response": b(r.get("developer_response")),
        "review_length": len(r.get("review", "") or ""),
        "fetched_at_utc": fetched_at,
        **{f"topic_{t}": flags[t] for t in review_topics.TOPICS},
        "topics_scanned": scanned,
        "topics_version": TOPICS_VERSION,
    }


# ---------------------------------------------------------------------------
# Helpers: time, files, state
# ---------------------------------------------------------------------------

def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(ts) -> str:
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat() if ts else ""


def month_start(d: datetime) -> datetime:
    return d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def next_month(d: datetime) -> datetime:
    return d.replace(year=d.year + 1, month=1) if d.month == 12 else d.replace(month=d.month + 1)


def write_csv(path: Path, rows: list[dict], append: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists() or not append
    with path.open("a" if append else "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        if is_new:
            w.writeheader()
        w.writerows(rows)


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(STATE_FILE)   # atomic: the state file is never half-written


def load_games() -> list[dict]:
    with GAMES_FILE.open(newline="", encoding="utf-8") as f:
        return [g for g in csv.DictReader(f)
                if g.get("appid", "").strip() and g.get("reviews", "").strip().lower() == "yes"]


# ---------------------------------------------------------------------------
# Backfill: one calendar month at a time
# ---------------------------------------------------------------------------

def fetch_window(appid: str, start: datetime, end: datetime, deadline: float) -> list[dict] | None:
    """
    All reviews created in [start, end). Returns None if the time budget ran
    out mid-window (nothing is saved for that month; it is redone next run).
    """
    fetched_at = now_utc().isoformat()
    params = base_params(appid) | {
        "filter": FILTER_RECENT,
        "date_range_start": int(start.timestamp()),
        "date_range_end": int(end.timestamp()) - 1,
        "cursor": "*",
    }
    rows, seen_cursors = [], set()
    for page in range(MAX_PAGES_PER_WINDOW):
        if time.monotonic() > deadline:
            return None
        resp = call_api(params)
        reviews = resp.get("reviews", []) or []
        if not reviews:
            return rows
        for r in reviews:
            created = int(r.get("timestamp_created", 0))
            # Guard: if Steam ever ignores the date filter, stop loudly
            # instead of silently downloading everything for every month.
            if not (start.timestamp() <= created < end.timestamp()):
                raise RuntimeError(
                    f"Date filter not respected for app {appid}: review created {iso(created)} "
                    f"outside {start:%Y-%m}. Run --probe and check the API.")
            rows.append(to_row(r, appid, fetched_at))
        cursor = resp.get("cursor")
        if not cursor or cursor in seen_cursors:   # no next page / cursor repeats
            return rows
        seen_cursors.add(cursor)
        params["cursor"] = cursor
        time.sleep(PAUSE_BETWEEN_REQUESTS)
    raise RuntimeError(f"More than {MAX_PAGES_PER_WINDOW} pages for {appid} {start:%Y-%m}")


def run_backfill(appid: str, game_state: dict, deadline: float) -> bool:
    """Continue the backfill. Returns True when the whole history is downloaded."""
    if "backfill_started_at" not in game_state:
        game_state["backfill_started_at"] = int(now_utc().timestamp())
        game_state["next_month"] = BACKFILL_FROM.strftime("%Y-%m")
    started = datetime.fromtimestamp(game_state["backfill_started_at"], timezone.utc)
    cur = datetime.strptime(game_state["next_month"], "%Y-%m").replace(tzinfo=timezone.utc)

    while cur <= started:
        end = min(next_month(cur), started)
        if end <= cur:
            break
        rows = fetch_window(appid, cur, end, deadline)
        if rows is None:
            print(f"  time budget reached; will continue from {cur:%Y-%m} next run")
            return False
        path = OUTPUT_ROOT / appid / "backfill" / f"reviews_{appid}_{cur:%Y-%m}.csv"
        if rows:                                    # no empty files for months before release
            write_csv(path, rows, append=False)    # overwrite: a month is written whole
            print(f"  {path.name}: {len(rows)} reviews")
        elif path.exists():
            path.unlink()                           # a re-run found nothing left (reviews deleted)
            print(f"  {path.name}: no reviews any more, file removed")
        cur = next_month(cur)
        game_state["next_month"] = cur.strftime("%Y-%m")
        save_state_now()                            # progress survives a crash

    game_state["backfill_done"] = True
    # Incremental runs will pick up everything created or updated after the backfill began.
    game_state["watermark"] = game_state["backfill_started_at"]
    return True


def restart_backfill(game_state: dict) -> None:
    """
    The topic dictionary changed (or this game was collected before topics
    existed): download the whole history again so every review is tagged by
    the same rules. Month files are overwritten one by one, so the old data
    stays usable until it is replaced.
    """
    old = game_state.get("topics_version", "none")
    for key in ("backfill_started_at", "next_month", "backfill_done", "watermark"):
        game_state.pop(key, None)
    game_state["topics_version"] = TOPICS_VERSION
    print(f"  topic dictionary {old} -> {TOPICS_VERSION}: backfill restarts from {BACKFILL_FROM:%Y-%m}")


# ---------------------------------------------------------------------------
# Incremental: reviews created or updated since the watermark
# ---------------------------------------------------------------------------

def run_incremental(appid: str, game_state: dict, deadline: float) -> None:
    watermark = int(game_state["watermark"])
    stop_before = watermark - OVERLAP_SECONDS
    fetched_at = now_utc()
    params = base_params(appid) | {"filter": FILTER_UPDATED, "cursor": "*"}
    rows, newest, seen_cursors = [], watermark, set()
    completed = False

    while time.monotonic() < deadline:
        resp = call_api(params)
        reviews = resp.get("reviews", []) or []
        if not reviews:
            completed = True
            break
        page_oldest = min(int(r.get("timestamp_updated", 0)) for r in reviews)
        for r in reviews:
            updated = int(r.get("timestamp_updated", 0))
            if updated >= stop_before:
                rows.append(to_row(r, appid, fetched_at.isoformat()))
                newest = max(newest, updated)
        cursor = resp.get("cursor")
        if page_oldest < stop_before or not cursor or cursor in seen_cursors:
            completed = True
            break
        seen_cursors.add(cursor)
        params["cursor"] = cursor
        time.sleep(PAUSE_BETWEEN_REQUESTS)

    if rows:
        path = OUTPUT_ROOT / appid / "updates" / f"reviews_{appid}_updates_{fetched_at:%Y-%m-%d}.csv"
        write_csv(path, rows, append=True)
        print(f"  {path.name}: +{len(rows)} reviews (incl. {OVERLAP_SECONDS // 86400}-day overlap)")
    else:
        print("  no new or updated reviews")
    if completed:
        game_state["watermark"] = newest
    else:
        # Pages come newest-first, so moving the watermark now would skip the
        # older updates we did not reach. Keep it; the next run re-reads them.
        print("  time budget reached; watermark kept, the next run will catch up")


# ---------------------------------------------------------------------------
# Probe: check the API behaves as expected, without saving anything
# ---------------------------------------------------------------------------

def probe(appid: str) -> int:
    print(f"Probing app {appid} ...")
    first = call_api(base_params(appid) | {"filter": FILTER_RECENT, "cursor": "*"})
    s = first.get("query_summary", {})
    print(f"  total reviews (all languages, all purchases): {s.get('total_reviews')}")
    print(f"  score: {s.get('review_score_desc')}  positive {s.get('total_positive')} / negative {s.get('total_negative')}")
    reviews = first.get("reviews", [])
    print(f"  first page: {len(reviews)} reviews, cursor present: {bool(first.get('cursor'))}")
    if reviews:
        print(f"  newest review created: {iso(reviews[0].get('timestamp_created'))}")
    # Check the date filter on a known past month.
    start, end = datetime(2023, 9, 1, tzinfo=timezone.utc), datetime(2023, 10, 1, tzinfo=timezone.utc)
    win = call_api(base_params(appid) | {"filter": FILTER_RECENT, "cursor": "*",
                                         "date_range_start": int(start.timestamp()),
                                         "date_range_end": int(end.timestamp()) - 1})
    dates = [int(r["timestamp_created"]) for r in win.get("reviews", [])]
    inside = all(start.timestamp() <= d < end.timestamp() for d in dates)
    print(f"  date filter test (Sep 2023): {len(dates)} reviews on first page, all inside window: {inside}")
    if dates and not inside:
        print("  PROBLEM: the date filter is not respected; do not run the backfill.")
        return 1
    print("Probe OK.")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

_STATE: dict = {}


def save_state_now() -> None:
    save_state(_STATE)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", metavar="APPID", help="test the API for one game and exit")
    args = parser.parse_args()
    if args.probe:
        return probe(args.probe)

    global _STATE
    _STATE = load_state()
    deadline = time.monotonic() + TIME_BUDGET_MINUTES * 60
    games = load_games()
    if not games:
        print("No games with reviews=yes in config/games.csv")
        return 0

    try:
        for g in games:
            appid = g["appid"].strip()
            game_state = _STATE.setdefault(appid, {"game": g["game"].strip()})
            print(f"{g['game']} ({appid})")
            if game_state.get("topics_version") != TOPICS_VERSION:
                restart_backfill(game_state)
                save_state_now()
            if not game_state.get("backfill_done"):
                print("  phase: backfill")
                run_backfill(appid, game_state, deadline)
            else:
                print("  phase: incremental")
                run_incremental(appid, game_state, deadline)
            save_state_now()
    except RateLimited as e:
        print(f"Stopped: {e}. Progress is saved; the next run continues.", file=sys.stderr)
        save_state_now()
    return 0


if __name__ == "__main__":
    sys.exit(main())
