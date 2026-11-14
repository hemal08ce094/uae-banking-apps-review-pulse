"""Pull App Store reviews from the public RSS feed, main storefronts, both sort orders. Usage: fetch_ios.py --app <slug>"""
import json, time, sys, requests
from common import parse, rawf
COUNTRIES = ["ae","sa","in","gb","us","eg","pk","ph","ca","au","sg","de","fr","lb","jo","bh","kw","om","qa","tr","ru","cn","hk","my","id","bd","lk","np","ng","ke","za","it","es","nl","ie","nz","br","mx","jp","kr"]
args, app = parse(__doc__)
sess = requests.Session()
sess.headers["User-Agent"] = "Mozilla/5.0 (Macintosh) ReviewPulse/1.0"
KEEP = ["trackName","sellerName","averageUserRating","userRatingCount","version","currentVersionReleaseDate","releaseDate","minimumOsVersion","contentAdvisoryRating","fileSizeBytes","genres","releaseNotes"]
for g in app["gens"]:
    APP_ID, gen = g["ios"], g["gen"]
    try:
        res = sess.get(f"https://itunes.apple.com/lookup?id={APP_ID}&country=ae", timeout=20).json()["results"][0]
        rawf(app, "ios_app", gen).write_text(json.dumps({k: res.get(k) for k in KEEP}, indent=1))
    except Exception as e:
        print("lookup failed", APP_ID, e, file=sys.stderr)
    out = rawf(app, "ios_reviews", gen)
    seen = {}
    for cc in COUNTRIES:
        for sort in ("mostrecent","mosthelpful"):
            for page in range(1, 11):
                url = f"https://itunes.apple.com/{cc}/rss/customerreviews/page={page}/id={APP_ID}/sortby={sort}/json"
                try:
                    r = sess.get(url, timeout=20)
                    if r.status_code != 200: break
                    feed = r.json().get("feed", {})
                except Exception as e:
                    print(cc, sort, page, "err", e, file=sys.stderr); break
                entries = feed.get("entry", [])
                if isinstance(entries, dict): entries = [entries]
                for e in entries:
                    if "im:rating" not in e: continue
                    rid = e["id"]["label"]
                    if rid in seen: continue
                    seen[rid] = {
                        "id": f"ios-{rid}", "platform": "ios", "storefront": cc,
                        "rating": int(e["im:rating"]["label"]),
                        "title": e.get("title", {}).get("label", ""),
                        "body": e.get("content", {}).get("label", ""),
                        "author": e.get("author", {}).get("name", {}).get("label", ""),
                        "version": e.get("im:version", {}).get("label", ""),
                        "date": e.get("updated", {}).get("label", "")[:10],
                        "votes_helpful": int(e.get("im:voteSum", {}).get("label", 0) or 0),
                        "votes_total": int(e.get("im:voteCount", {}).get("label", 0) or 0),
                        "reply": None,
                    }
                    if gen: seen[rid]["generation"] = gen
                if not entries: break
                time.sleep(0.3)
            print(app["slug"], gen, cc, sort, "total so far", len(seen), flush=True)
        out.write_text(json.dumps(list(seen.values()), ensure_ascii=False, indent=1))
    out.write_text(json.dumps(list(seen.values()), ensure_ascii=False, indent=1))
    print("ios reviews saved:", app["slug"], gen, len(seen))
