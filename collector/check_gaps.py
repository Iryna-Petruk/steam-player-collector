"""
Check the collected data for gaps.

Prints, for each day and game, how many hourly snapshots were saved and
which hours are missing or failed. Expected: 24 successful snapshots per
game per day (fewer for the first and the current day).

Usage:
    python collector/check_gaps.py            # all days
    python collector/check_gaps.py 7          # last 7 days only
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = REPO_ROOT / "data" / "raw" / "players"


def main() -> int:
    files = sorted(DATA_ROOT.rglob("players_*.csv"))
    if not files:
        print("No data files yet.")
        return 0
    if len(sys.argv) > 1:
        files = files[-int(sys.argv[1]):]

    for path in files:
        day = path.stem.replace("players_", "")
        ok_hours = defaultdict(set)      # game -> hours with a successful value
        failed = defaultdict(list)       # game -> (hour, error)
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["collected_at_utc"] == "collected_at_utc":   # header repeated by a union merge
                    continue
                hour = int(row["collected_at_utc"][11:13])
                if row["status"] == "ok":
                    ok_hours[row["game"]].add(hour)
                else:
                    failed[row["game"]].append((hour, row["status"]))

        print(f"\n{day}")
        for game in sorted(set(ok_hours) | set(failed)):
            hours = ok_hours[game]
            missing = [h for h in range(24) if h not in hours]
            line = f"  {game:<28} {len(hours):>2}/24 ok"
            if missing and len(missing) < 24:
                line += f"   missing hours (UTC): {', '.join(str(h) for h in missing)}"
            print(line)
            for hour, error in failed[game]:
                print(f"      {hour:02d}:xx failed: {error}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
