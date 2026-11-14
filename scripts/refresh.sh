#!/bin/zsh
# analyze + insights + web copy for one app: scripts/refresh.sh <slug>
cd ~/Documents/Github/ENBDXFeedback
slug=${1:?usage: refresh.sh <slug>}
PY=.venv/bin/python
$PY scripts/analyze.py --app $slug 2>&1 | grep -v -i warn || true
[ -f data/$slug/summary.json ] || { echo "no data for $slug yet"; exit 0; }
$PY scripts/build_insights.py --app $slug 2>&1 | grep -v -i warn | head -3
./scripts/build_web.sh $slug
