#!/bin/zsh
# Daily: store snapshot, recent reviews, analysis, dated weekly/daily files, git push, republish the Artifact.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"
cd ~/Documents/Github/ENBDXFeedback || exit 1
PY=.venv/bin/python; LOG=data/_recent/daily.log; mkdir -p data/_recent
exec >> $LOG 2>&1
echo "=== daily refresh $(date)"
SINCE=$(date -v-10d +%F)
$PY scripts/fetch_store.py
for a in enbdx fab adcb wio mashreq adib; do $PY scripts/fetch_recent.py --app $a --since $SINCE | grep merged; done
./scripts/refresh_all.sh | tail -1
python3 scripts/build_weekly.py web/data web/data/weekly.json
python3 scripts/build_daily.py web/data web/data/daily.json
# files to republish: everything in web/data except past-year review chunks
python3 - <<'PY'
import json, pathlib, datetime
root = pathlib.Path("web"); yr = str(datetime.date.today().year); m = {}
for p in sorted((root/"data").rglob("*.json")):
    parts = p.relative_to(root/"data").parts
    if len(parts) == 3 and parts[1] == "reviews" and parts[2] != yr + ".json": continue
    m[str(p.relative_to(root))] = str(p.resolve())
m["app.html"] = str((root/"app.html").resolve())
pathlib.Path("data/_publish_files.json").write_text(json.dumps(m, indent=1))
print("publish files:", len(m))
PY
git add -A && git -c user.name="Hemal Modi" -c user.email="hemal08ce094@gmail.com" commit -q -m "Daily data refresh $(date +%F)" && git push -q && echo pushed
claude -p "$(cat scripts/publish_prompt.md)" --allowedTools "Artifact" "Read" --permission-mode acceptEdits --model sonnet | tail -3
echo "=== done $(date)"
