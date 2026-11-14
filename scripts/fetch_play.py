"""Pull every Google Play review (main languages) via google-play-scraper. Usage: fetch_play.py --app <slug>"""
import json, sys, time
from google_play_scraper import reviews, Sort, app as gp_app
from common import parse, rawf
args, app = parse(__doc__)
def mk(r, country, lang, gen):
    d = {"id": f"play-{r['reviewId']}", "platform": "android", "storefront": country, "lang": lang,
        "rating": r["score"], "title": "", "body": r["content"] or "", "author": r["userName"], "version": r.get("reviewCreatedVersion") or "",
        "date": r["at"].strftime("%Y-%m-%d"), "votes_helpful": r.get("thumbsUpCount", 0), "votes_total": None,
        "reply": ({"body": r["replyContent"], "date": r["repliedAt"].strftime("%Y-%m-%d")} if r.get("replyContent") else None)}
    if gen: d["generation"] = gen
    return d
for g in app["gens"]:
    PKG, gen = g["play"], g["gen"]
    out = rawf(app, "play_reviews", gen)
    try:
        meta = gp_app(PKG, lang="en", country="ae")
        rawf(app, "play_app", gen).write_text(json.dumps({k: meta.get(k) for k in ["title","score","ratings","reviews","histogram","version","installs","released","updated","developer","genre"]}, default=str, indent=1))
    except Exception as e:
        print("meta failed", PKG, e, file=sys.stderr)
    seen = {}
    def pull(lang, country, sort, cap=40000):
        token = None; got = 0; fails = 0
        while True:
            try:
                batch, token = reviews(PKG, lang=lang, country=country, sort=sort, count=200, continuation_token=token)
            except Exception as e:
                fails += 1
                print("err", lang, country, e, file=sys.stderr)
                if fails > 4: break
                time.sleep(3); continue
            for r in batch:
                if r["reviewId"] in seen: continue
                seen[r["reviewId"]] = mk(r, country, lang, gen); got += 1
            print(app["slug"], gen, lang, country, sort.name if hasattr(sort,'name') else sort, "batch", len(batch), "unique", len(seen), flush=True)
            if not token or not batch or got >= cap: break
            time.sleep(0.5)
    for lang, country in [("en","ae"),("ar","ae"),("en","us"),("en","in"),("en","gb"),("hi","in"),("ur","pk"),("fr","fr"),("ru","ru"),("tl","ph"),("en","sa"),("en","eg")]:
        pull(lang, country, Sort.NEWEST)
        out.write_text(json.dumps(list(seen.values()), ensure_ascii=False, indent=1))
    pull("en","ae", Sort.MOST_RELEVANT, cap=5000)
    out.write_text(json.dumps(list(seen.values()), ensure_ascii=False, indent=1))
    print("play reviews saved:", app["slug"], gen, len(seen))
