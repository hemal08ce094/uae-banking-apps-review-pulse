"""Merge both stores, tag themes, and emit the aggregate + chunked files the dashboard lazy-loads. Usage: analyze.py --app <slug>"""
import json, re, pathlib, collections, datetime, statistics, sys
from common import parse, rawf, data_dir, PHASE1, ALL_STOREFRONTS
_args, APP = parse(__doc__)
R = data_dir(APP)
def load(kind, gen):
    f = rawf(APP, kind, gen)
    return json.loads(f.read_text()) if f.exists() else []
def load1(kind, gen):
    f = rawf(APP, kind, gen)
    return json.loads(f.read_text()) if f.exists() else {}
ios, play = [], []
store_ios, store_play = {}, {}
for g in APP["gens"]:
    gen = g["gen"]
    rss, deep = load("ios_reviews", gen), load("ios_deep_reviews", gen)
    _by = {r["id"]: r for r in deep}
    for r in rss:
        if r["id"] in _by and _by[r["id"]].get("reply"): r["reply"] = _by[r["id"]]["reply"]
        _by[r["id"]] = r
    ios += list(_by.values()); play += load("play_reviews", gen)
    store_ios[gen or "all"] = load1("ios_app", gen); store_play[gen or "all"] = load1("play_app", gen)
for r in ios + play: r.setdefault("generation", None)
_mt = [f.stat().st_mtime for g in APP["gens"] for k in ("ios_reviews","ios_deep_reviews","play_reviews") for f in [rawf(APP, k, g["gen"])] if f.exists()]
collected = datetime.date.fromtimestamp(max(_mt)).isoformat() if _mt else None

def combine_ios(d):
    vals = [v for v in d.values() if v.get("userRatingCount")]
    n = sum(v["userRatingCount"] for v in vals)
    return {"avg": (sum(v["averageUserRating"]*v["userRatingCount"] for v in vals)/n) if n else None, "count": n or None, "version": next((v.get("version") for v in vals), None)}
def combine_play(d):
    vals = [v for v in d.values() if v.get("ratings")]
    n = sum(v["ratings"] for v in vals)
    hist = [sum((v.get("histogram") or [0]*5)[i] for v in vals) for i in range(5)] if vals else None
    return {"avg": (sum(v["score"]*v["ratings"] for v in vals)/n) if n else None, "count": n or None, "reviews": sum(v.get("reviews") or 0 for v in vals) or None,
            "version": next((v.get("version") for v in vals), None), "histogram": hist, "installs": next((v.get("installs") for v in vals), None)}
ios_app = combine_ios(store_ios); play_app = combine_play(store_play)
def deep_coverage():
    done = set(); started = False
    for g in APP["gens"]:
        f = rawf(APP, "ios_deep_state", g["gen"])
        if f.exists():
            started = True; st = json.loads(f.read_text())
            d = {c for c, v in st.items() if v == "done"}
            done = d if not done else done & d
    if not started: return {"phase": 0, "text": "deep App Store crawl not started", "done_storefronts": 0}
    p1 = all(c in done for c in PHASE1)
    p2 = all(c in done for c in ALL_STOREFRONTS)
    if p2: return {"phase": 2, "text": "complete", "done_storefronts": len(done)}
    if p1: return {"phase": 1, "text": "deep crawl phase 1 of 2 complete, phase 2 running", "done_storefronts": len(done)}
    return {"phase": 0, "text": "deep crawl phase 1 of 2 running", "done_storefronts": len(done)}
COVERAGE = deep_coverage()

THEMES = {
 "login":        ("Login & access",      r"log ?in|sign ?in|password|passcode|otp|one.time|verif|locked|lock(ed)? out|face ?id|touch ?id|biometric|fingerprint|finger print|\bpin\b|uae ?pass|emirates ?id|registration|register|activat|كلمة المرور|دخول|تسجيل"),
 "stability":    ("Crashes & errors",    r"crash|freez|hang|stuck|not work|doesn.?t work|dont work|won.?t (open|load)|error|bug|glitch|white screen|blank|black screen|technical (issue|error)|try again later|something went wrong|يعلق|خطأ|لا يعمل|مشكلة"),
 "speed":        ("Speed & loading",     r"\bslow|loading|takes (forever|too long|ages|time)|lag|spinner|wait(ing)? (for|too)|يطلع|بطيء"),
 "update":       ("App updates",         r"updat|new version|latest version|old version|after the upgrade|upgrad|تحديث|النسخة"),
 "transfers":    ("Transfers & payments",r"transfer|payment|\bpay\b|paying|send money|beneficiar|iban|remit|international|exchange rate|swift|salary|bill|utility|dewa|etisalat|\bdu\b|تحويل|حوال|دفع|فاتورة"),
 "cards":        ("Cards",               r"\bcard|credit card|debit|apple pay|samsung pay|google pay|contactless|card limit|block(ed)? (my )?card|cvv|بطاقة|بطاقتي"),
 "support":      ("Call centre & chat",  r"customer (service|care|support)|call ?cent|support team|\bsupport\b|\bchat\b|\beva\b|\bagent|no response|on hold|hotline|helpline|whatsapp|call ?back|waiting time|wait(ed|ing)? (for )?\d+ (min|hour)|خدمة العملاء|الاتصال|واتساب"),
 "branch":       ("Branch & staff",      r"branch|\bstaff\b|employee|teller|\bmanager\b|relationship manager|\brm\b|rude|unprofessional|attitude|misbehav|sales (rep|person|team)|فرع|موظف|الموظفين|تعامل"),
 "products":     ("Bank products",       r"\bloan|mortgage|credit limit|limit (increase|reduction|decrease)|interest rate|profit rate|deposit|savings|investment|\bfund|insurance|takaful|overdraft|\bemi\b|insta?l+ment|salary account|current account|fixed deposit|\bfinance\b|cheque|check ?book|\batm\b|\bcash\b|قرض|تمويل|وديعة|حساب جاري|حساب توفير|صراف|شيك"),
 "disputes":     ("Disputes & complaints",r"dispute|complain|refund|charge ?back|case (was |is )?closed|no resolution|unresolved|escalat|ombudsman|central bank|consumer protection|fraud (team|department|investigation)|شكوى|استرداد|نزاع|مصرف الإمارات المركزي"),
 "fees":         ("Fees & charges",      r"\bfee|charge|interest|hidden|deduct|penalt|\brate\b|expensive|رسوم|فائدة|خصم"),
 "usability":    ("Design & usability",  r"\bui\b|\bux\b|design|interface|user.?friendly|easy to use|easy|simple|intuitive|navigat|confus|layout|font|dark mode|clutter|complicated|look and feel|smooth|سهل|سلس|تصميم|واجهة"),
 "features":     ("Missing features",    r"feature|option|missing|wish|please add|should (have|add|include)|need(s)? (to|a|an)|would be (nice|great|good)|widget|statement|download|export|pdf|search|filter|history|lack|ميزة|خاصية|أتمنى|ياريت"),
 "security":     ("Security & fraud",    r"fraud|scam|hack|unauthori[sz]ed|secur|phish|stole|theft|suspicious|أمان|نصب|احتيال"),
 "notifications":("Notifications",       r"notif|alert|\bsms\b|reminder|إشعار|تنبيه"),
 "device":       ("Device compatibility",r"android|iphone|ipad|ios ?\d|samsung|huawei|pixel|xiaomi|oneplus|root|jailbr|tablet|screen size|not (supported|compatible)|compatib|version of (android|ios)|الجهاز|هاتف"),
 "rewards":      ("Rewards & offers",    r"plus points|reward|cashback|cash back|offer|skywards|miles|loyalty|promo|مكافآت|عروض|نقاط"),
 "account":      ("Account & onboarding",r"open(ing)? (an )?account|onboard|new account|kyc|document|salary account|account open|savings|minimum balance|closure|close (my )?account|فتح حساب|حساب"),
 "liv":          ("Old app & migration", r"old (app|version)|previous (app|version)|earlier app|blue app|bring back|go back to the old|switch(ed)? to (the )?new|forced to (update|upgrade|move|migrate)|migrat|التطبيق القديم|النسخة القديمة"),
 "smartpass":    ("Smart Pass & approvals",r"smart ?pass|smart token|authoris|authoriz|approve|approval|in.app (confirmation|payment)|سمارت باس"),
}
THEME_RX = {k: re.compile(v[1], re.I) for k, v in THEMES.items()}
POS_RX = re.compile(r"excellent|great|love|amazing|awesome|best|perfect|fantastic|brilliant|wonderful|superb|smooth|easy|convenient|helpful|good|nice|fast|quick|reliable|thank|well done|ممتاز|رائع|جميل|شكرا|سهل|افضل|أفضل", re.I)
NEG_RX = re.compile(r"worst|terrible|horrible|useless|pathetic|disappoint|frustrat|annoy|bad|poor|waste|ridiculous|never|cannot|can.?t|unable|fail|not working|hate|rubbish|garbage|شيء|سيء|سئ|أسوأ|اسوأ|زفت|ما يفتح|لا يعمل", re.I)

def lang_of(t):
    if re.search(r"[؀-ۿ]", t): return "ar"
    if re.search(r"[ऀ-ॿ]", t): return "hi"
    if re.search(r"[Ѐ-ӿ]", t): return "ru"
    if re.search(r"[ঀ-৿]", t): return "bn"
    if re.search(r"[一-鿿]", t): return "zh"
    return "en"

def norm(r):
    gen = r.get("generation")
    text = (r.get("title") or "") + ". " + (r.get("body") or "")
    text = text.strip(". ").strip()
    body = (r.get("body") or "").replace("\ufffd", "")
    r["title"] = (r.get("title") or "").replace("\ufffd", "")
    themes = [k for k, rx in THEME_RX.items() if rx.search(text)]
    rating = int(r["rating"])
    sent = "positive" if rating >= 4 else "negative" if rating <= 2 else "neutral"
    # a 3-star with clearly negative words reads as a complaint; a 3-star with praise reads as a mild win
    if rating == 3:
        p, n = len(POS_RX.findall(body)), len(NEG_RX.findall(body))
        if n > p: sent = "negative"
        elif p > n: sent = "positive"
    out_r = {
        "id": r["id"], "platform": r["platform"], "store": r.get("storefront",""), "lang": r.get("lang") or lang_of(text),
        "rating": rating, "sentiment": sent, "title": r.get("title") or "", "body": body, "author": r.get("author") or "",
        "version": r.get("version") or "", "date": r["date"], "helpful": r.get("votes_helpful") or 0,
        "reply": r.get("reply"), "themes": themes, "len": len(body),
    }
    if gen: out_r["generation"] = gen
    return out_r

reviews = [norm(r) for r in ios + play if r.get("date") and r.get("rating")]
if not reviews:
    print("no reviews yet for", APP["slug"]); sys.exit(2)
reviews.sort(key=lambda r: r["date"], reverse=True)
print("merged", len(reviews), "ios", sum(r["platform"]=="ios" for r in reviews), "android", sum(r["platform"]=="android" for r in reviews))

def ym(d): return d[:7]
months = sorted({ym(r["date"]) for r in reviews})
_bm = collections.defaultdict(list)
for r in reviews: _bm[ym(r["date"])].append(r)
def series(filter_fn):
    out = []
    for m in months:
        rs = [r for r in _bm[m] if filter_fn(r)]
        out.append({"month": m, "count": len(rs), "avg": round(statistics.mean([r["rating"] for r in rs]), 2) if rs else None,
                    "neg": sum(r["sentiment"]=="negative" for r in rs), "pos": sum(r["sentiment"]=="positive" for r in rs),
                    "hist": [sum(r["rating"]==s for r in rs) for s in (1,2,3,4,5)]})
    return out

by_month = collections.defaultdict(list)
for r in reviews: by_month[ym(r["date"])].append(r)
theme_stats = []
for k, (label, _) in THEMES.items():
    rs = [r for r in reviews if k in r["themes"]]
    if not rs: continue
    neg = [r for r in rs if r["sentiment"]=="negative"]
    theme_stats.append({"key": k, "label": label, "count": len(rs), "negative": len(neg), "positive": sum(r["sentiment"]=="positive" for r in rs),
        "neutral": sum(r["sentiment"]=="neutral" for r in rs), "avg": round(statistics.mean([r["rating"] for r in rs]), 2),
        "ios": sum(r["platform"]=="ios" for r in rs), "android": sum(r["platform"]=="android" for r in rs),
        "share_of_negative": round(len(neg) / max(1, sum(r["sentiment"]=="negative" for r in reviews)), 3),
        "monthly": {p: [[sum(1 for r in by_month[m] if k in r["themes"] and r["platform"]==p), sum(1 for r in by_month[m] if k in r["themes"] and r["platform"]==p and r["sentiment"]=="negative"), sum(1 for r in by_month[m] if k in r["themes"] and r["platform"]==p and r["sentiment"]=="positive")] for m in months] for p in ("ios","android")}})
theme_stats.sort(key=lambda t: -t["count"])

# version table: sample size >= 15 so a single angry reviewer does not define a release
ver = collections.defaultdict(list)
for r in reviews:
    if r["version"]: ver[(r["platform"], r["version"])].append(r)
def vkey(v):
    return tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[.\-]", v)[:4])
versions = sorted([{"platform": p, "version": v, "count": len(rs), "avg": round(statistics.mean([r["rating"] for r in rs]), 2),
                    "neg_share": round(sum(r["sentiment"]=="negative" for r in rs)/len(rs), 3),
                    "first": min(r["date"] for r in rs), "last": max(r["date"] for r in rs),
                    "top_themes": [k for k, _ in collections.Counter(t for r in rs if r["sentiment"]=="negative" for t in r["themes"]).most_common(3)]}
                   for (p, v), rs in ver.items() if len(rs) >= 15], key=lambda x: (x["platform"], vkey(x["version"])))

replies = [r for r in reviews if r["reply"]]
def reply_lag(r):
    try: return (datetime.date.fromisoformat(r["reply"]["date"]) - datetime.date.fromisoformat(r["date"])).days
    except Exception: return None
lags = [l for l in map(reply_lag, replies) if l is not None and l >= 0]

summary = {
  "generated": datetime.date.today().isoformat(),
  "months": months,
  "collected": collected,
  "coverage": COVERAGE,
  "app": {"slug": APP["slug"], "name": APP["name"], "bank": APP["bank"], "developer": APP["developer"], "note": APP.get("note"),
          "gens": [{"gen": g["gen"], "ios_id": g["ios"], "play_id": g["play"]} for g in APP["gens"]],
          "ios_id": APP["gens"][0]["ios"], "play_id": APP["gens"][0]["play"],
          "ios_url": f"https://apps.apple.com/ae/app/id{APP['gens'][0]['ios']}", "play_url": f"https://play.google.com/store/apps/details?id={APP['gens'][0]['play']}",
          "store_rating": {"ios": ios_app, "android": play_app}, "store_rating_by_gen": {"ios": store_ios, "android": store_play}},
  "totals": {"all": len(reviews), "ios": sum(r["platform"]=="ios" for r in reviews), "android": sum(r["platform"]=="android" for r in reviews),
             "first": min(r["date"] for r in reviews), "last": max(r["date"] for r in reviews),
             "avg": round(statistics.mean([r["rating"] for r in reviews]), 2),
             "avg_ios": round(statistics.mean([r["rating"] for r in reviews if r["platform"]=="ios"]), 2) if any(r["platform"]=="ios" for r in reviews) else None,
             "avg_android": round(statistics.mean([r["rating"] for r in reviews if r["platform"]=="android"]), 2) if any(r["platform"]=="android" for r in reviews) else None,
             "hist": [sum(r["rating"]==s for r in reviews) for s in (1,2,3,4,5)],
             "hist_ios": [sum(r["rating"]==s for r in reviews if r["platform"]=="ios") for s in (1,2,3,4,5)],
             "hist_android": [sum(r["rating"]==s for r in reviews if r["platform"]=="android") for s in (1,2,3,4,5)],
             "sentiment": dict(collections.Counter(r["sentiment"] for r in reviews)),
             "langs": collections.Counter(r["lang"] for r in reviews).most_common(8),
             "storefronts_ios": collections.Counter(r["store"] for r in reviews if r["platform"]=="ios").most_common(12),
             "with_text": sum(r["len"] > 0 for r in reviews), "untagged": sum(not r["themes"] and r["len"] > 20 for r in reviews)},
  "monthly": {"all": series(lambda r: True), "ios": series(lambda r: r["platform"]=="ios"), "android": series(lambda r: r["platform"]=="android")},
  "themes": theme_stats,
  "versions": versions,
  "replies": {"count": len(replies), "android": sum(r["platform"]=="android" for r in replies), "ios": sum(r["platform"]=="ios" for r in replies),
              "rate_android": round(sum(r["platform"]=="android" for r in replies)/max(1,sum(r["platform"]=="android" for r in reviews)), 3),
              "rate_ios": round(sum(r["platform"]=="ios" for r in replies)/max(1,sum(r["platform"]=="ios" for r in reviews)), 3),
              "median_lag_days": statistics.median(lags) if lags else None, "by_year": collections.Counter(r["date"][:4] for r in replies)},
  "chunks": [],
}
# Lazy-load chunks: one file per calendar year, newest first in each.
chunks_dir = R/"reviews"; chunks_dir.mkdir(exist_ok=True)
for f in chunks_dir.glob("*.json"): f.unlink()
by_year = collections.defaultdict(list)
for r in reviews: by_year[r["date"][:4]].append(r)
for y, rs in sorted(by_year.items(), reverse=True):
    (chunks_dir/f"{y}.json").write_text(json.dumps(rs, ensure_ascii=False, separators=(",",":")))
    summary["chunks"].append({"year": y, "file": f"reviews/{y}.json", "count": len(rs), "bytes": (chunks_dir/f"{y}.json").stat().st_size})
theme_keys = list(THEMES.keys())
_month_i = {m:i for i,m in enumerate(months)}
index = {"themes": theme_keys, "months": months, "platforms": ["ios","android"], "sentiments": ["negative","neutral","positive"],
         "rows": [[0 if r["platform"]=="ios" else 1, _month_i[ym(r["date"])], r["rating"], {"negative":0,"neutral":1,"positive":2}[r["sentiment"]], sum(1<<theme_keys.index(t) for t in r["themes"])] for r in reviews]}
(R/"index.json").write_text(json.dumps(index, separators=(",",":")))
summary["index"] = {"file": "index.json", "bytes": (R/"index.json").stat().st_size}
(R/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=str))
(R/"reviews.json").write_text(json.dumps(reviews, ensure_ascii=False, separators=(",",":")))
if APP["gens"][0]["gen"]: print("generation split:", collections.Counter(r.get("generation") for r in reviews))
print(json.dumps(summary["totals"], ensure_ascii=False, default=str)[:900])
print("themes:", [(t["label"], t["count"], t["avg"]) for t in theme_stats])
print("versions with >=15 reviews:", len(versions), "replies:", len(replies), "median lag", summary["replies"]["median_lag_days"])
