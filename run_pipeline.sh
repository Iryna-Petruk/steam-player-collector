#!/usr/bin/env bash
# Full local refresh on Mac / Linux:
#   1. get the latest data collected by GitHub Actions
#   2. load new and changed CSV files into PostgreSQL (raw schema)
#   3. rebuild and test all dbt models
# Run from the repository folder:  ./run_pipeline.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/3 git pull"
git pull --ff-only

echo "== 2/3 load raw data"
source .venv/bin/activate
python warehouse/load_raw.py

echo "== 3/3 dbt build"
cd dbt
dbt build
