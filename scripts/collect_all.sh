#!/bin/zsh
# Collect the five new apps. Run with: nohup scripts/collect_all.sh > data/collect_all.log 2>&1 &
# Order: iOS RSS + Google Play first (Play for all apps runs concurrently), then the deep App Store crawl
# in two phases (phase 1 = ae in gb us sa ph pk eg; phase 2 = every other storefront), at most 2 deep crawlers at once.
# Safe to re-run: every collector resumes or merges into its raw files. Pass slugs to limit the set.
cd ~/Documents/Github/ENBDXFeedback
PY=.venv/bin/python
if [ $# -gt 0 ]; then APPS=($@); else APPS=(fab adcb wio mashreq adib); fi
for a in $APPS; do mkdir -p data/$a/raw; done

# Google Play: all apps concurrently, main languages then more languages.
for a in $APPS; do
  ( $PY scripts/fetch_play.py --app $a > data/$a/raw/play.log 2>&1
    $PY scripts/fetch_play_more.py --app $a > data/$a/raw/play_more.log 2>&1 ) &
done

# iOS RSS, one app after another (itunes.apple.com).
for a in $APPS; do $PY scripts/fetch_ios.py --app $a > data/$a/raw/ios.log 2>&1; done
# remaining RSS storefronts run alongside the deep crawl (different host).
( for a in $APPS; do $PY scripts/fetch_ios_all.py --app $a > data/$a/raw/ios_all.log 2>&1; done ) &

# deep crawl, phase 1 then phase 2, two crawlers at a time.
print -l $APPS | xargs -P 2 -I{} zsh -c "$PY scripts/fetch_ios_deep.py --app {} --phase 1 >> data/{}/raw/ios_deep.log 2>&1"
echo "phase 1 done $(date)"; ./scripts/refresh_all.sh > data/refresh_phase1.log 2>&1
print -l $APPS | xargs -P 2 -I{} zsh -c "$PY scripts/fetch_ios_deep.py --app {} --phase 2 >> data/{}/raw/ios_deep.log 2>&1"
echo "phase 2 done $(date)"
wait
./scripts/refresh_all.sh > data/refresh_final.log 2>&1
echo "COLLECT_ALL_DONE $(date)"
