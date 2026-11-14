"""Deep iOS pass through the apps.apple.com catalogue proxy (no 500 cap). Paced to stay under the rate limit; resumable.
Usage: fetch_ios_deep.py --app <slug> [--phase 1|2|all]
Phase 1 = ae in gb us sa ph pk eg; phase 2 = every other storefront; state is kept per app+id so phases resume."""
import json, time, sys, requests
from common import parse, rawf
PHASE1 = "ae in gb us sa ph pk eg".split()
ORDER = "ae sa in gb us eg pk ph ca au sg de fr lb jo bh kw om qa tr ru cn hk my id bd lk np ng ke za it es nl ie nz br mx jp kr".split()
ALL = """af al dz ao ai ag ar am au at az bs bh bb by be bz bj bm bt bo ba bw br vg bn bg bf kh cm ca cv ky td cl cn co cg cd cr ci hr cy cz dk dm do ec eg sv gq ee sz et fj fi fr ga gm ge de gh gr gd gt gw gy hn hk hu is in id iq ie il it jm jp jo kz ke kr xk kw kg la lv lb lr ly lt lu mo mg mw my mv ml mt mr mu mx fm md mn me ms ma mz mm na nr np nl nz ni ne ng mk no om pk pw pa pg py pe ph pl pt qa ro ru rw kn lc vc ws sa sn rs sc sl sg sk si sb za es lk sr se ch tw tj tz th to tt tn tr tm tc ug ua ae gb us uy uz vu ve vn ye zm zw""".split()
def add_args(ap): ap.add_argument("--phase", default="all", choices=["1","2","all"])
args, app = parse(__doc__, add_args)
if args.phase == "1": COUNTRIES = PHASE1
else:
    full = ORDER + [c for c in ALL if c not in ORDER]
    COUNTRIES = full if args.phase == "all" else [c for c in full if c not in PHASE1]
for g in app["gens"]:
    APP_ID, gen = g["ios"], g["gen"]
    out = rawf(app, "ios_deep_reviews", gen); state_f = rawf(app, "ios_deep_state", gen)
    seen = {r["id"]: r for r in json.loads(out.read_text())} if out.exists() else {}
    state = json.loads(state_f.read_text()) if state_f.exists() else {}
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15", "Accept": "application/json"})
    PACE = 4.0; ok_streak = 0
    def save():
        out.write_text(json.dumps(list(seen.values()), ensure_ascii=False, indent=1)); state_f.write_text(json.dumps(state))
    for cc in COUNTRIES:
        if state.get(cc) == "done": continue
        s.headers["Referer"] = f"https://apps.apple.com/{cc}/app/id{APP_ID}"
        off = int(state.get(cc) or 0); empty_streak = 0; got_cc = 0
        while True:
            url = f"https://apps.apple.com/api/apps/v1/catalog/{cc}/apps/{APP_ID}/reviews?l=en-GB&offset={off}&limit=10&platform=web&additionalPlatforms=appletv,ipad,iphone,mac"
            try:
                r = s.get(url, timeout=25)
            except Exception as e:
                print(cc, off, "net err", e, file=sys.stderr); time.sleep(10); continue
            if r.status_code == 429:
                PACE = min(PACE + 1.5, 15.0); ok_streak = 0
                print(cc, off, f"429 backoff, pace now {PACE:.1f}s", flush=True); time.sleep(45); continue
            ok_streak += 1
            if ok_streak >= 40 and PACE > 3.0: PACE -= 0.5; ok_streak = 0
            if r.status_code == 404:
                break
            if r.status_code != 200:
                print(cc, off, "status", r.status_code, r.text[:100], file=sys.stderr); time.sleep(5); empty_streak += 1
                if empty_streak > 3: break
                continue
            d = r.json(); data = d.get("data", [])
            for e in data:
                a = e["attributes"]; rid = f"ios-{e['id']}"
                if rid in seen: continue
                dr = a.get("developerResponse")
                seen[rid] = {"id": rid, "platform": "ios", "storefront": cc, "rating": a.get("rating"), "title": a.get("title", ""), "body": a.get("review", ""),
                    "author": a.get("userName", ""), "version": "", "date": a.get("date", "")[:10], "votes_helpful": 0, "votes_total": 0,
                    "reply": ({"body": dr.get("body"), "date": (dr.get("modified") or "")[:10]} if dr else None)}
                if gen: seen[rid]["generation"] = gen
                got_cc += 1
            off += 10; state[cc] = off
            if off % 200 == 0: save(); print(app["slug"], gen, cc, "offset", off, "new", got_cc, "total", len(seen), flush=True)
            if not data or not d.get("next"): break
            time.sleep(PACE)
        state[cc] = "done"; save(); print(app["slug"], gen, cc, "DONE new", got_cc, "total", len(seen), flush=True)
    save()
    print("deep ios saved:", app["slug"], gen, len(seen))
