"""Resolve a per-app narrative (scripts/insights/<slug>.py) against its review corpus and write data/<slug>/insights.json.
Every quote is looked up by snippet in data/<slug>/reviews.json; a quote that no longer resolves prints MISSING QUOTE.
Usage: build_insights.py --app <slug>"""
import json, re, runpy, sys, datetime, statistics, collections
from common import parse, data_dir, ROOT
args, APP = parse(__doc__)
R = data_dir(APP)
rs = json.load(open(R/"reviews.json")); S = json.load(open(R/"summary.json"))
def find(snippet, prefer=None):
    hits = [r for r in rs if snippet.lower() in (r["title"] + " " + r["body"]).lower()]
    if prefer: hits = [h for h in hits if prefer(h)] or hits
    if not hits: print("MISSING QUOTE:", APP["slug"], snippet, file=sys.stderr); return None
    hits.sort(key=lambda r: (-r["helpful"], -r["len"])); r = hits[0]
    return {"id": r["id"], "platform": r["platform"], "rating": r["rating"], "date": r["date"], "version": r["version"], "helpful": r["helpful"], "title": r["title"], "body": r["body"]}
def dLabel(d): return datetime.date.fromisoformat(d).strftime("%-d %B %Y")
def mentions(rx, since=None, until=None, where=None):
    pat = re.compile(rx, re.I)
    return sum(1 for r in rs if pat.search(r["title"] + " " + r["body"]) and (not since or r["date"] >= since) and (not until or r["date"] <= until) and (not where or where(r)))
def avg(fn):
    v = [r["rating"] for r in rs if fn(r)]; return round(statistics.mean(v), 2) if v else None
def month(m):
    return next((x for x in S["monthly"]["all"] if x["month"] == m), {"month": m, "count": 0, "neg": 0, "pos": 0, "avg": None})
def top_themes(since, until=None, n=3, neg=True):
    c = collections.Counter(t for r in rs if r["date"] >= since and (not until or r["date"] <= until) and (r["sentiment"] == "negative" or not neg) for t in r["themes"])
    lab = {t["key"]: t["label"] for t in S["themes"]}
    return ", ".join(f"{lab[k]} ({v})" for k, v in c.most_common(n))
def pct(a, b): return round(100 * a / b) if b else 0
T = S["totals"]
G = dict(rs=rs, S=S, T=T, by_id={r["id"]: r for r in rs}, find=find, lo=lambda r: r["rating"] <= 3, hi=lambda r: r["rating"] >= 4,
    dLabel=dLabel, mentions=mentions, avg=avg, month=month, pct=pct, json=json, re=re, statistics=statistics, collections=collections, datetime=datetime,
    five_share=pct(T["hist"][4], T["all"]), low_share=pct(T["hist"][0] + T["hist"][1], T["all"]),
    neg_all=sum(1 for r in rs if r["sentiment"] == "negative"),
    top_themes=top_themes, reply_all=pct(S['replies']['count'], T['all']), lag=S['replies']['median_lag_days'],
    reply_rate=round(100 * S["replies"]["rate_android"]), ios_reply_rate=round(100 * S["replies"]["rate_ios"]))
path = ROOT/"scripts/insights"/f"{APP['slug']}.py"
if not path.exists():
    print("no narrative yet for", APP["slug"]); sys.exit(0)
ns = runpy.run_path(str(path), init_globals=G)
ins = ns["ins"]
ins["generated"] = S["generated"]
for sec in ("pains", "wins"):
    for item in ins[sec]: item["quotes"] = [q for q in item["quotes"] if q]
(R/"insights.json").write_text(json.dumps(ins, ensure_ascii=False, indent=1))
print("insights written:", APP["slug"], "quotes:", sum(len(i["quotes"]) for s in ("pains","wins") for i in ins[s]))
print(ins["headline"]); print(ins["lede"])
for e in ins["events"]: print(e["month"], e["label"], "|", e["detail"])
