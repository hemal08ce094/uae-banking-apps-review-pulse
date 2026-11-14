#!/bin/zsh
# Wait for every collector, then rebuild all analysis and the static site.
cd ~/Documents/Github/ENBDXFeedback
while pgrep -f "fetch_ios_deep.py|fetch_ios_all.py|fetch_play_more.py|fetch_play.py|fetch_ios.py" >/dev/null; do sleep 60; done
./scripts/refresh_all.sh
echo FINALIZE_DONE
