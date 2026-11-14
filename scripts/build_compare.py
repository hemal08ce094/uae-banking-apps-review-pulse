"""Build data/compare.json from every app's summary.json and reviews.json: one like-for-like record per app plus computed cross-app findings."""
import json, datetime, statistics
from common import REG, ROOT
D = ROOT/"data"
apps = []
for a in REG["apps"]:
    sf = D/a["slug"]/"summary.json"
    if sf.exists(): apps.append((a, json.loads(sf.read_text())))
def add_months(m, k):
    y, mo = int(m[:4]), int(m[5:])
    t = y*12 + mo - 1 + k; return f"{t//12:04d}-{t%12+1:02d}"
last_month = max(S["months"][-1] for _, S in apps)
months = [add_months(last_month, -i) for i in range(35, -1, -1)]
last_date = max(S["totals"]["last"] for _, S in apps)
ref = datetime.date.fromisoformat(last_date)
def window(rs, lo_days, hi_days):
    a, b = (ref - datetime.timedelta(days=hi_days)).isoformat(), (ref - datetime.timedelta(days=lo_days)).isoformat()
    v = [r["rating"] for r in rs if a < r["date"] <= b]
    return (round(statistics.mean(v), 2), len(v)) if v else (None, 0)
out = {"generated": datetime.date.today().isoformat(), "months": months, "reference_date": last_date, "apps": [], "findings": []}
for a, S in apps:
    T, rep = S["totals"], S["replies"]
    rs = json.loads((D/a["slug"]/"reviews.json").read_text())
    mall = {m["month"]: m for m in S["monthly"]["all"]}
    neg_total = T["sentiment"].get("negative", 0)
    themes = [{"key": t["key"], "label": t["label"], "count": t["count"], "negative": t["negative"],
               "negative_share": round(t["negative"]/t["count"], 3) if t["count"] else 0,
               "share_of_negatives": round(t["negative"]/neg_total, 3) if neg_total else 0, "avg": t["avg"]} for t in S["themes"]]
    top3 = sorted(themes, key=lambda t: -t["negative"])[:3]
    a90, n90 = window(rs, 0, 90); p90, pn90 = window(rs, 90, 180)
    sr = S["app"]["store_rating"]
    low = T["hist"][0] + T["hist"][1]; high = T["hist"][3] + T["hist"][4]
    out["apps"].append({
        "slug": a["slug"], "name": a["name"], "bank": a["bank"], "developer": a["developer"], "note": a.get("note"),
        "store": {"ios": {"avg": sr["ios"].get("avg"), "count": sr["ios"].get("count")},
                  "android": {"avg": sr["android"].get("avg"), "count": sr["android"].get("count"), "histogram": sr["android"].get("histogram")}},
        "totals": {"all": T["all"], "ios": T["ios"], "android": T["android"], "avg": T["avg"], "avg_ios": T.get("avg_ios"), "avg_android": T.get("avg_android"),
                   "hist": T["hist"], "low_share": round(low/T["all"], 4), "high_share": round(high/T["all"], 4), "negatives": neg_total},
        "replies": {"count": rep["count"], "rate": round(rep["count"]/T["all"], 3), "rate_ios": rep["rate_ios"], "rate_android": rep["rate_android"], "median_lag_days": rep["median_lag_days"]},
        "monthly_avg": [mall[m]["avg"] if m in mall else None for m in months],
        "monthly_count": [mall[m]["count"] if m in mall else 0 for m in months],
        "themes": themes, "top_complaints": [{"key": t["key"], "label": t["label"], "negative": t["negative"], "share_of_negatives": t["share_of_negatives"]} for t in top3],
        "recent": {"avg_90": a90, "n_90": n90, "avg_prior_90": p90, "n_prior_90": pn90, "delta": round(a90 - p90, 2) if a90 is not None and p90 is not None else None},
        "first": T["first"], "last": T["last"], "collected": S.get("collected"), "coverage": S.get("coverage", {}),
    })
A = out["apps"]
F = out["findings"]
NW = {2:"two",3:"three",4:"four",5:"five",6:"six"}.get(len(A), str(len(A)))
def pc(x): return f"{round(100*x)}%"
if len(A) >= 2:
    hi_r = max(A, key=lambda x: x["replies"]["rate"]); lo_r = min(A, key=lambda x: x["replies"]["rate"])
    lag = hi_r['replies']['median_lag_days']; lag_s = "under a day" if lag is not None and lag < 1 else f"{lag:g} day" + ("" if lag == 1 else "s")
    F.append(f"{hi_r['name']} answers {pc(hi_r['replies']['rate'])} of its written reviews, the highest of the {NW} apps, with a median reply time of {lag_s}. {lo_r['name']} answers {pc(lo_r['replies']['rate'])}.")
    lo_s = min(A, key=lambda x: x["totals"]["low_share"]); hi_s = max(A, key=lambda x: x["totals"]["low_share"])
    F.append(f"{lo_s['name']} has the smallest share of one and two star reviews ({pc(lo_s['totals']['low_share'])} of {lo_s['totals']['all']:,}); {hi_s['name']} has the largest ({pc(hi_s['totals']['low_share'])} of {hi_s['totals']['all']:,}).")
    gaps = [(x, (x["store"]["android"]["avg"] or x["store"]["ios"]["avg"] or 0) - x["totals"]["avg"]) for x in A if (x["store"]["android"]["avg"] or x["store"]["ios"]["avg"])]
    if gaps:
        g, d = max(gaps, key=lambda p: p[1])
        F.append(f"The widest gap between store rating and written reviews is {g['name']}: {(g['store']['android']['avg'] or g['store']['ios']['avg']):.2f} stars in the store against {g['totals']['avg']:.2f} among the {g['totals']['all']:,} people who wrote a review.")
    # theme where one app stands out most against the median of the others
    best = None
    for t in A[0]["themes"]:
        k = t["key"]; vals = {}
        for x in A:
            tt = next((q for q in x["themes"] if q["key"] == k), None)
            vals[x["slug"]] = tt["share_of_negatives"] if tt else 0
        for x in A:
            others = [v for s, v in vals.items() if s != x["slug"]]
            margin = vals[x["slug"]] - statistics.median(others)
            if best is None or margin > best[0]: best = (margin, x, t["label"], vals[x["slug"]], statistics.median(others))
    for k in (best,):
        if k: F.append(f"{k[2]} is where {k[1]['name']} stands apart: it appears in {pc(k[3])} of its negative reviews, against a median of {pc(k[4])} for the other apps.")
    movers = [x for x in A if x["recent"]["delta"] is not None and x["recent"]["n_90"] >= 30 and x["recent"]["n_prior_90"] >= 30]
    if movers:
        up = max(movers, key=lambda x: x["recent"]["delta"]); dn = min(movers, key=lambda x: x["recent"]["delta"])
        F.append(f"Over the latest 90 days to {ref.day} {ref.strftime('%B %Y')}, {up['name']} moved most upward ({up['recent']['avg_prior_90']:.2f} to {up['recent']['avg_90']:.2f}) and {dn['name']} moved most downward ({dn['recent']['avg_prior_90']:.2f} to {dn['recent']['avg_90']:.2f}).")
    most = max(A, key=lambda x: x["totals"]["all"]); least = min(A, key=lambda x: x["totals"]["all"])
    F.append(f"Written reviews range from {least['totals']['all']:,} for {least['name']} to {most['totals']['all']:,} for {most['name']}, so a month of {least['name']} reviews moves on far fewer voices than a month of {most['name']}.")
(D/"compare.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
print("compare.json:", [(x["slug"], x["totals"]["all"]) for x in A]); [print(" -", f) for f in F]
