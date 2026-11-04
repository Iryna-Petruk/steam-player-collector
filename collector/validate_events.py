"""
Validate config/events.csv, the hand-maintained calendar of events
(patches, expansions, Netflix premieres, announcements, Steam sales).

Run after every manual edit:
    python collector/validate_events.py

Checks: required columns, unique IDs, valid dates, end_date not before
event_date, allowed event types and magnitudes, known AppIDs, and a
source URL for every event. Exits with code 1 if anything is wrong.
"""

import csv
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVENTS_FILE = REPO_ROOT / "config" / "events.csv"
GAMES_FILE = REPO_ROOT / "config" / "games.csv"

COLUMNS = ["event_id", "event_date", "end_date", "appid", "game", "event_type",
           "event_name", "magnitude", "source_url", "notes"]
EVENT_TYPES = {"release", "expansion", "major_update", "patch", "transmedia",
               "announcement", "platform_sale", "related_release", "other"}
MAGNITUDES = {"major", "minor"}


def parse_date(value: str):
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def main() -> int:
    with GAMES_FILE.open(newline="", encoding="utf-8") as f:
        known_appids = {g["appid"].strip() for g in csv.DictReader(f)} | {"ALL"}

    with EVENTS_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            print(f"Columns must be exactly: {','.join(COLUMNS)}")
            return 1
        rows = list(reader)

    errors, seen = [], set()
    for line, r in enumerate(rows, start=2):           # line 1 is the header
        where = f"line {line} ({r['event_id'] or 'no id'})"
        if not r["event_id"]:
            errors.append(f"{where}: missing event_id")
        elif r["event_id"] in seen:
            errors.append(f"{where}: duplicate event_id")
        seen.add(r["event_id"])

        start = parse_date(r["event_date"])
        if not start:
            errors.append(f"{where}: event_date must be YYYY-MM-DD, got '{r['event_date']}'")
        if r["end_date"]:
            end = parse_date(r["end_date"])
            if not end:
                errors.append(f"{where}: end_date must be YYYY-MM-DD or empty")
            elif start and end < start:
                errors.append(f"{where}: end_date is before event_date")

        if r["appid"] not in known_appids:
            errors.append(f"{where}: appid '{r['appid']}' is not in games.csv (use ALL for platform-wide events)")
        if r["event_type"] not in EVENT_TYPES:
            errors.append(f"{where}: event_type '{r['event_type']}' not in {sorted(EVENT_TYPES)}")
        if r["magnitude"] not in MAGNITUDES:
            errors.append(f"{where}: magnitude must be major or minor")
        if not r["event_name"]:
            errors.append(f"{where}: missing event_name")
        if not r["source_url"].startswith(("http://", "https://")):
            errors.append(f"{where}: every event needs a source_url")

    if errors:
        print(f"{len(errors)} problem(s) in {EVENTS_FILE.name}:")
        for e in errors:
            print("  - " + e)
        return 1

    by_type = {}
    for r in rows:
        by_type[r["event_type"]] = by_type.get(r["event_type"], 0) + 1
    print(f"{EVENTS_FILE.name}: {len(rows)} events, all valid.")
    for t, n in sorted(by_type.items()):
        print(f"  {t:<16} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
