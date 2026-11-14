"""Second iOS pass: every App Store storefront not covered by fetch_ios.py, merged into the same file. Usage: fetch_ios_all.py --app <slug>"""
import json, time, sys, requests
from common import parse, rawf
ALL = """af al dz ao ai ag ar am au at az bs bh bb by be bz bj bm bt bo ba bw br vg bn bg bf kh cm ca cv ky td cl cn co cg cd cr ci hr cy cz dk dm do ec eg sv gq ee sz et fj fi fr ga gm ge de gh gr gd gt gw gy hn hk hu is in id iq ie il it jm jp jo kz ke kr xk kw kg la lv lb lr ly lt lu mo mg mw my mv ml mt mr mu mx fm md mn me ms ma mz mm na nr np nl nz ni ne ng mk no om pk pw pa pg py pe ph pl pt qa ro ru rw kn lc vc ws sa sn rs sc sl sg sk si sb za es lk sr se ch tw tj tz th to tt tn tr tm tc ug ua ae gb us uy uz vu ve vn ye zm zw""".split()
done = set("ae sa in gb us eg pk ph ca au sg de fr lb jo bh kw om qa tr ru cn hk my id bd lk np ng ke za it es nl ie nz br mx jp kr".split())
args, app = parse(__doc__)
sess = requests.Session(); sess.headers["User-Agent"] = "Mozilla/5.0 (Macintosh) ReviewPulse/1.0"
for g in app["gens"]:
    APP_ID, gen = g["ios"], g["gen"]
    out = rawf(app, "ios_reviews", gen)
    seen = {r["id"].replace("ios-","",1): r for r in json.loads(out.read_text())} if out.exists() else {}
    print("starting with", len(seen))
    for cc in [c for c in ALL if c not in done]:
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
                if not entries: break
                for e in entries:
                    if "im:rating" not in e: continue
                    rid = e["id"]["label"]
                    if rid in seen: continue
                    seen[rid] = {"id": f"ios-{rid}", "platform": "ios", "storefront": cc, "rating": int(e["im:rating"]["label"]),
                        "title": e.get("title", {}).get("label", ""), "body": e.get("content", {}).get("label", ""),
                        "author": e.get("author", {}).get("name", {}).get("label", ""), "version": e.get("im:version", {}).get("label", ""),
                        "date": e.get("updated", {}).get("label", "")[:10],
                        "votes_helpful": int(e.get("im:voteSum", {}).get("label", 0) or 0), "votes_total": int(e.get("im:voteCount", {}).get("label", 0) or 0), "reply": None}
                    if gen: seen[rid]["generation"] = gen
                time.sleep(0.3)
        print(app["slug"], gen, cc, "total", len(seen), flush=True)
    out.write_text(json.dumps(list(seen.values()), ensure_ascii=False, indent=1))
    print("ios reviews saved:", app["slug"], gen, len(seen))
