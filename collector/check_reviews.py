"""
Summarise the collected review data: backfill progress, row counts,
date coverage and duplicates per game.

Usage:
    python collector/check_reviews.py
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = REPO_ROOT / "data" / "raw" / "reviews"
STATE_FILE = REPO_ROOT / "state" / "reviews_state.json"


def main() -> int:
    state = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}
    if not DATA_ROOT.exists():
        print("No review data yet.")
        return 0

    for app_dir in sorted(p for p in DATA_ROOT.iterdir() if p.is_dir()):
        appid = app_dir.name
        s = state.get(appid, {})
        ids = Counter()
        positive = total = 0
        first = last = ""
        months_with_data = 0
        for path in sorted(app_dir.rglob("*.csv")):
            file_rows = 0
            with path.open(newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    file_rows += 1
                    ids[row["recommendation_id"]] += 1
                    total += 1
                    positive += row["voted_up"] == "1"
                    created = row["created_utc"]
                    first = min(first, created) if first else created
                    last = max(last, created) if last else created
            if "backfill" in path.parts and file_rows:
                months_with_data += 1

        unique = len(ids)
        status = "done" if s.get("backfill_done") else f"in progress, next month {s.get('next_month', '?')}"
        print(f"\n{s.get('game', appid)} ({appid})")
        print(f"  backfill:          {status}")
        print(f"  rows / unique:     {total:,} / {unique:,}  (duplicates {total - unique:,}, removed later in dbt)")
        print(f"  created between:   {first[:10]} and {last[:10]}")
        print(f"  months with data:  {months_with_data}")
        if total:
            print(f"  positive share:    {positive / total:.1%} (raw, before deduplication)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
