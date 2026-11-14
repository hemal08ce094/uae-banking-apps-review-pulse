#!/bin/zsh
# Copy the analysed data next to the pages so web/ is a self-contained static site: scripts/build_web.sh <slug>
cd ~/Documents/Github/ENBDXFeedback
slug=${1:?usage: build_web.sh <slug>}
[ -f data/$slug/summary.json ] || { echo "no data for $slug"; exit 0; }
rm -rf web/data/$slug && mkdir -p web/data/$slug/reviews
cp data/$slug/summary.json data/$slug/index.json web/data/$slug/
[ -f data/$slug/insights.json ] && cp data/$slug/insights.json web/data/$slug/
cp data/$slug/reviews/*.json web/data/$slug/reviews/
cp data/apps.json web/data/
du -sh web/data/$slug
