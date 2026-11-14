"""Incremental refresh: only reviews newer than --since, merged by id into the existing raw files (nothing is overwritten).
Usage: fetch_recent.py --app <slug> [--since 2026-10-18] [--only ios|play]"""
import json, time, sys, requests
from common import parse, rawf, PHASE1
def add_args(ap):
    ap.add_argument("--since", default="2026-10-18"); ap.add_argument("--only", choices=["ios", "play"])
args, app = parse(__doc__, add_args)
SINCE = args.since

def merge(path, new):
    cur = {r["id"]: r for r in json.loads(path.read_text())} if path.exists() else {}
    added = sum(1 for r in new if r["id"] not in cur)
    for r in new: cur[r["id"]] = {**cur.get(r["id"], {}), **r}
    path.write_text(json.dumps(list(cur.values()), ensure_ascii=False, indent=1))
    return added, len(cur)

def play(g):
    from google_play_scraper import reviews, Sort
    PKG, gen = g["play"], g["gen"]; got = {}
    for lang, country in [("en","ae"),("ar","ae"),("en","us"),("en","in"),("en","gb"),("hi","in"),("ur","pk"),("fr","fr"),("ru","ru"),("tl","ph"),("en","sa"),("en","eg")]:
        token = None; fails = 0
        while True:
            try: batch, token = reviews(PKG, lang=lang, country=country, sort=Sort.NEWEST, count=200, continuation_token=token)
            except Exception as e:
                fails += 1; print("err", e, file=sys.stderr)
                if fails > 3: break
                time.sleep(3); continue
            for r in batch:
                if r["at"].strftime("%Y-%m-%d") < SINCE: continue
                got[r["reviewId"]] = {"id": f"play-{r['reviewId']}", "platform": "android", "storefront": country, "lang": lang, "rating": r["score"], "title": "", "body": r["content"] or "",
                    "author": r["userName"], "version": r.get("reviewCreatedVersion") or "", "date": r["at"].strftime("%Y-%m-%d"), "votes_helpful": r.get("thumbsUpCount", 0), "votes_total": None,
                    "reply": ({"body": r["replyContent"], "date": r["repliedAt"].strftime("%Y-%m-%d")} if r.get("replyContent") else None), **({"generation": gen} if gen else {})}
            if not batch or not token or min(r["at"].strftime("%Y-%m-%d") for r in batch) < SINCE: break
            time.sleep(0.5)
        print(app["slug"], gen, "play", lang, country, "recent so far", len(got), flush=True)
    print(app["slug"], gen, "play merged (added, total):", merge(rawf(app, "play_reviews", gen), list(got.values())))

def ios(g):
    """RSS feed, newest first, main storefronts; stops each storefront at --since."""
    APP_ID, gen = g["ios"], g["gen"]; got = {}
    s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (Macintosh) ReviewPulse/1.0"
    for cc in "ae sa in gb us eg pk ph ca au sg de fr lb jo bh kw om qa tr".split():
        for page in range(1, 11):
            try: r = s.get(f"https://itunes.apple.com/{cc}/rss/customerreviews/page={page}/id={APP_ID}/sortby=mostrecent/json", timeout=20)
            except Exception as e: print(cc, "err", e, file=sys.stderr); break
            if r.status_code != 200: break
            entries = r.json().get("feed", {}).get("entry", [])
            if isinstance(entries, dict): entries = [entries]
            entries = [e for e in entries if "im:rating" in e]
            if not entries: break
            for e in entries:
                d = e.get("updated", {}).get("label", "")[:10]
                if d < SINCE: continue
                rid = e["id"]["label"]
                got[rid] = {"id": f"ios-{rid}", "platform": "ios", "storefront": cc, "rating": int(e["im:rating"]["label"]), "title": e.get("title", {}).get("label", ""), "body": e.get("content", {}).get("label", ""),
                    "author": e.get("author", {}).get("name", {}).get("label", ""), "version": e.get("im:version", {}).get("label", ""), "date": d,
                    "votes_helpful": int(e.get("im:voteSum", {}).get("label", 0) or 0), "votes_total": int(e.get("im:voteCount", {}).get("label", 0) or 0), "reply": None, **({"generation": gen} if gen else {})}
            if min(e.get("updated", {}).get("label", "9")[:10] for e in entries) < SINCE: break
            time.sleep(0.3)
        print(app["slug"], gen, "ios rss", cc, "recent so far", len(got), flush=True)
    print(app["slug"], gen, "ios merged (added, total):", merge(rawf(app, "ios_reviews", gen), list(got.values())))

for g in app["gens"]:
    if args.only != "ios": play(g)
    if args.only != "play": ios(g)
