#!/bin/zsh
# Per-app collected counts and running crawlers.
cd ~/Documents/Github/ENBDXFeedback
.venv/bin/python - <<'PY'
import json, pathlib, datetime
reg = json.load(open("data/apps.json"))["apps"]
def n(f):
    try: return len(json.load(open(f)))
    except Exception: return 0
print(f"{'app':9}{'gen':5}{'ios rss':>9}{'ios deep':>10}{'play':>8}  deep storefronts done")
for a in reg:
    for g in a["gens"]:
        sfx = f".{g['gen']}" if g["gen"] else ""
        d = pathlib.Path("data")/a["slug"]/"raw"
        st = d/f"ios_deep_state{sfx}.json"
        done = sum(1 for v in json.load(open(st)).values() if v == "done") if st.exists() else 0
        print(f"{a['slug']:9}{(g['gen'] or '-'):5}{n(d/f'ios_reviews{sfx}.json'):>9}{n(d/f'ios_deep_reviews{sfx}.json'):>10}{n(d/f'play_reviews{sfx}.json'):>8}  {done}")
    s = pathlib.Path("data")/a["slug"]/"summary.json"
    if s.exists():
        j = json.load(open(s)); print(f"{'':9}analysed: {j['totals']['all']} written reviews, collected {j.get('collected')}, coverage: {j.get('coverage',{}).get('text')}")
PY
echo "--- running collectors"
pgrep -fl "fetch_|collect_all" | sed 's/.*scripts\//  /' || echo "  none"
