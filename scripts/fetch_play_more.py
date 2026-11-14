"""Second Play pass: more languages/countries, merged into the same file. Usage: fetch_play_more.py --app <slug>"""
import json, sys, time
from google_play_scraper import reviews, Sort
from common import parse, rawf
args, app = parse(__doc__)
PAIRS = [("ar","sa"),("ar","eg"),("hi","in"),("ur","pk"),("bn","bd"),("ml","in"),("ta","in"),("te","in"),("ne","np"),("si","lk"),("fr","fr"),("de","de"),("es","es"),("it","it"),("pt","br"),("ru","ru"),("tr","tr"),("fa","ir"),("id","id"),("ms","my"),("zh","cn"),("ja","jp"),("ko","kr"),("sw","ke"),("en","ca"),("en","au"),("en","za"),("en","ng"),("en","ph"),("en","pk"),("en","bd"),("en","lk"),("en","jo"),("en","lb"),("en","kw"),("en","qa"),("en","om"),("en","bh")]
for g in app["gens"]:
    PKG, gen = g["play"], g["gen"]
    out = rawf(app, "play_reviews", gen)
    seen = {r["id"].replace("play-","",1): r for r in json.loads(out.read_text())} if out.exists() else {}
    print("starting with", len(seen))
    def pull(lang, country, sort):
        token = None; fails = 0
        while True:
            try: batch, token = reviews(PKG, lang=lang, country=country, sort=sort, count=200, continuation_token=token)
            except Exception as e:
                fails += 1; print("err", lang, country, e, file=sys.stderr)
                if fails > 4: break
                time.sleep(3); continue
            for r in batch:
                rid = r["reviewId"]
                if rid in seen: continue
                seen[rid] = {"id": f"play-{rid}", "platform": "android", "storefront": country, "lang": lang, "rating": r["score"], "title": "", "body": r["content"] or "",
                    "author": r["userName"], "version": r.get("reviewCreatedVersion") or "", "date": r["at"].strftime("%Y-%m-%d"),
                    "votes_helpful": r.get("thumbsUpCount", 0), "votes_total": None,
                    "reply": ({"body": r["replyContent"], "date": r["repliedAt"].strftime("%Y-%m-%d")} if r.get("replyContent") else None)}
                if gen: seen[rid]["generation"] = gen
            print(app["slug"], gen, lang, country, "batch", len(batch), "unique", len(seen), flush=True)
            if not token or not batch: break
            time.sleep(0.5)
    for lang, country in PAIRS:
        pull(lang, country, Sort.NEWEST)
        out.write_text(json.dumps(list(seen.values()), ensure_ascii=False, indent=1))
    print("play reviews saved:", app["slug"], gen, len(seen))
