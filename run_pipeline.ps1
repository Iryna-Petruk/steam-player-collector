# Full local refresh on Windows (PowerShell):
#   1. get the latest data collected by GitHub Actions
#   2. load new and changed CSV files into PostgreSQL (raw schema)
#   3. rebuild and test all dbt models
# Run from the repository folder:  .\run_pipeline.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "== 1/3 git pull"
git pull --ff-only
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== 2/3 load raw data"
& .\.venv\Scripts\Activate.ps1
python warehouse\load_raw.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== 3/3 dbt build"
Set-Location dbt
dbt build
exit $LASTEXITCODE
