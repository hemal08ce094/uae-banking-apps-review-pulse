"""Print reading samples for writing a narrative: monthly dips, most-helpful negatives per theme, most-helpful positives, recent months. Usage: sample.py --app <slug> [--themes a,b] [--n 5]"""
import json, collections
from common import parse, data_dir
def add(ap): ap.add_argument("--themes", default=""); ap.add_argument("--n", type=int, default=4); ap.add_argument("--w", type=int, default=260); ap.add_argument("--months", default=""); ap.add_argument("--grep", default="")
a, APP = parse(__doc__, add)
R = data_dir(APP); rs = json.load(open(R/"reviews.json")); S = json.load(open(R/"summary.json"))
def show(r, w=a.w):
    t = (r["title"] + " | " if r["title"] else "") + r["body"].replace("\n", " ")
    print(f"  [{r['platform'][:2]} {r['rating']}* {r['date']} v{r['version'] or '-'} +{r['helpful']}] {t[:w]}")
print("TOTALS", S["totals"]["all"], "avg", S["totals"]["avg"], "replies", S["replies"]["count"], "lag", S["replies"]["median_lag_days"])
print("MONTHS (count>=40) lowest avg:")
ms = [m for m in S["monthly"]["all"] if m["count"] >= 40]
for m in sorted(ms, key=lambda m: m["avg"])[:6]: print("  ", m["month"], m["avg"], m["count"], "neg", m["neg"])
print("MONTHS highest:", [(m["month"], m["avg"], m["count"]) for m in sorted(ms, key=lambda m: -m["avg"])[:3]])
print("LAST 14 months:", [(m["month"], m["avg"], m["count"]) for m in S["monthly"]["all"][-14:]])
print("THEMES by negatives:", [(t["key"], t["negative"]) for t in sorted(S["themes"], key=lambda t: -t["negative"])[:10]])
for k in [t for t in a.themes.split(",") if t] or [t["key"] for t in sorted(S["themes"], key=lambda t: -t["negative"])[:5]]:
    print("== NEG theme", k)
    for r in sorted([r for r in rs if k in r["themes"] and r["rating"] <= 2 and r["len"] > 60], key=lambda r: -r["helpful"])[:a.n]: show(r)
print("== POS most helpful")
for r in sorted([r for r in rs if r["rating"] >= 4 and r["len"] > 80], key=lambda r: -r["helpful"])[:a.n+2]: show(r)
print("== RECENT negatives (latest 3 months)")
last = sorted({r["date"][:7] for r in rs})[-3:]
for r in sorted([r for r in rs if r["date"][:7] in last and r["rating"] <= 2 and r["len"] > 80], key=lambda r: -r["helpful"])[:a.n+2]: show(r)
print("== REPLY samples")
for r in [r for r in rs if r["reply"]][:2]: print("  ", r["reply"]["body"][:200].replace("\n"," "))

import re
for m in [x for x in a.months.split(",") if x]:
    rows = [r for r in rs if r["date"].startswith(m)]
    c = collections.Counter(w for r in rows if r["rating"] <= 2 for w in set(re.findall(r"[a-z]{5,}", (r["title"]+" "+r["body"]).lower())))
    print("== MONTH", m, len(rows), "reviews; common words in 1-2*:", c.most_common(14))
    for r in sorted([r for r in rows if r["rating"] <= 2 and r["len"] > 50], key=lambda r: -r["helpful"])[:a.n+1]: show(r)
if a.grep:
    rx = re.compile(a.grep, re.I); hits = [r for r in rs if rx.search(r["title"]+" "+r["body"])]
    print("== GREP", a.grep, len(hits), "by year", sorted(collections.Counter(r["date"][:4] for r in hits).items()))
    for r in sorted(hits, key=lambda r: -r["helpful"])[:a.n+2]: show(r)
