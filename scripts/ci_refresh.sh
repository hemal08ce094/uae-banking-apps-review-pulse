#!/usr/bin/env bash
# Daily refresh for GitHub Actions (or any Linux box): store snapshot, recent reviews, analysis, weekly/daily files. No git, no publishing.
set -u
cd "$(dirname "$0")/.."
export PY=${PY:-python3}
SINCE=$(date -d '10 days ago' +%F 2>/dev/null || date -v-10d +%F)
$PY scripts/fetch_store.py
for a in enbdx fab adcb wio mashreq adib; do $PY scripts/fetch_recent.py --app "$a" --since "$SINCE" | grep merged; done
./scripts/refresh_all.sh | tail -1
$PY scripts/build_weekly.py web/data web/data/weekly.json
$PY scripts/build_daily.py web/data web/data/daily.json
