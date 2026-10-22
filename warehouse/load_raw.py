"""
Load the CSV files of this repository into the raw schema of PostgreSQL.

    data/raw/players/**/*.csv   ->  raw.players
    data/raw/reviews/**/*.csv   ->  raw.reviews
    config/games.csv            ->  raw.games
    config/events.csv           ->  raw.events

Safe to run as often as you like (idempotent):
  - a file that has not changed since the last load is skipped;
  - a file that changed (e.g. today's players file got new hourly rows) is
    reloaded: its old rows are deleted and the new content inserted, in one
    transaction, so the table never contains half a file;
  - a file that was deleted from the repository loses its rows too.
Older review files, written before topic flags existed, have fewer columns;
the missing columns are loaded as NULL.

Connection settings come from the standard PostgreSQL environment variables
(PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE). Defaults: localhost:5432,
user postgres, database cdpr_hub.

Usage:
    python warehouse/load_raw.py                 # load new and changed files
    python warehouse/load_raw.py --full-refresh  # empty raw tables, reload everything
"""

import argparse
import csv
import hashlib
import os
import sys
import time
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parent.parent
CREATE_SQL = Path(__file__).resolve().parent / "sql" / "create_raw.sql"

# (glob pattern inside the repo, target table, expected CSV header, minimum columns)
# A file may have fewer columns than expected only if it is an older format:
# its header must then equal the first N expected columns (N >= minimum).
SOURCES = [
    ("data/raw/players/**/*.csv", "raw.players",
     ["collected_at_utc", "appid", "game", "role", "player_count", "status"], 6),
    ("data/raw/reviews/**/*.csv", "raw.reviews",
     ["recommendation_id", "appid", "language", "created_utc", "updated_utc", "voted_up",
      "votes_up", "votes_funny", "weighted_vote_score", "comment_count", "steam_purchase",
      "received_for_free", "written_during_early_access", "refunded", "primarily_steam_deck",
      "playtime_at_review_min", "playtime_forever_min", "author_num_reviews",
      "has_developer_response", "review_length", "fetched_at_utc",
      "topic_bugs", "topic_performance", "topic_price", "topic_story", "topic_content",
      "topics_scanned", "topics_version"], 21),
    ("config/games.csv", "raw.games", ["appid", "game", "role", "reviews"], 4),
    ("config/events.csv", "raw.events",
     ["event_id", "event_date", "end_date", "appid", "game", "event_type", "event_name",
      "magnitude", "source_url", "notes"], 10),
]


def connect() -> psycopg.Connection:
    os.environ.setdefault("PGHOST", "localhost")
    os.environ.setdefault("PGPORT", "5432")
    os.environ.setdefault("PGUSER", "postgres")
    os.environ.setdefault("PGDATABASE", "cdpr_hub")
    # autocommit: every `with conn.transaction()` block is then a real, separate
    # transaction, so files loaded before an error stay loaded.
    return psycopg.connect(autocommit=True)   # psycopg reads the PG* variables itself


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_file(conn, path: Path, table: str, columns: list[str], min_columns: int) -> int:
    """Replace all rows of this file in the table. Returns the number of rows loaded."""
    rel = path.relative_to(REPO_ROOT).as_posix()
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None) or []
        if len(header) < min_columns or header != columns[:len(header)]:
            raise ValueError(f"{rel}: unexpected header {header}, expected {columns}")
        with conn.transaction():
            conn.execute(f"delete from {table} where _source_file = %s", (rel,))
            col_list = ", ".join(header + ["_source_file"])
            n = 0
            with conn.cursor().copy(f"copy {table} ({col_list}) from stdin") as copy:
                for row in reader:
                    if not row:
                        continue
                    # Empty CSV cells become NULL, everything else stays text.
                    copy.write_row([v if v != "" else None for v in row] + [rel])
                    n += 1
            conn.execute(
                """insert into raw.load_log (source_file, target_table, sha256, row_count, loaded_at)
                   values (%s, %s, %s, %s, now())
                   on conflict (source_file) do update
                   set sha256 = excluded.sha256, row_count = excluded.row_count, loaded_at = now()""",
                (rel, table, sha256_of(path), n),
            )
    return n


def remove_deleted_files(conn, table: str, present: set[str]) -> int:
    """Delete rows of files that were loaded before but no longer exist in the repository."""
    loaded = {r[0] for r in conn.execute(
        "select source_file from raw.load_log where target_table = %s", (table,)).fetchall()}
    gone = sorted(loaded - present)
    for rel in gone:
        with conn.transaction():
            conn.execute(f"delete from {table} where _source_file = %s", (rel,))
            conn.execute("delete from raw.load_log where source_file = %s", (rel,))
    return len(gone)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-refresh", action="store_true", help="empty raw tables and reload all files")
    args = parser.parse_args()

    started = time.monotonic()
    with connect() as conn:
        conn.execute(CREATE_SQL.read_text(encoding="utf-8"))
        if args.full_refresh:
            with conn.transaction():
                for _, table, _, _ in SOURCES:
                    conn.execute(f"truncate {table}")
                conn.execute("truncate raw.load_log")
            print("Full refresh: raw tables emptied.")

        known = dict(conn.execute("select source_file, sha256 from raw.load_log").fetchall())

        for pattern, table, columns, min_columns in SOURCES:
            files = sorted(REPO_ROOT.glob(pattern))
            loaded = skipped = rows = 0
            for path in files:
                rel = path.relative_to(REPO_ROOT).as_posix()
                if known.get(rel) == sha256_of(path):
                    skipped += 1
                    continue
                rows += load_file(conn, path, table, columns, min_columns)
                loaded += 1
            removed = remove_deleted_files(conn, table, {p.relative_to(REPO_ROOT).as_posix() for p in files})
            total = conn.execute(f"select count(*) from {table}").fetchone()[0]
            print(f"{table:<12} files: {len(files):>4}  loaded: {loaded:>4}  unchanged: {skipped:>4}  "
                  f"removed: {removed:>3}  rows loaded now: {rows:>9,}  rows in table: {total:>10,}")

    print(f"Done in {time.monotonic() - started:.1f} s")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except psycopg.OperationalError as e:
        print(f"Cannot connect to PostgreSQL: {e}\nCheck that the server runs and PG* variables are set.",
              file=sys.stderr)
        sys.exit(1)
