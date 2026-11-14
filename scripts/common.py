"""Shared helpers: app registry, per-app paths, argparse."""
import argparse, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
REG = json.loads((ROOT/"data/apps.json").read_text())

def parse(desc="", extra=None):
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("--app", default="enbdx", help="slug from data/apps.json")
    if extra: extra(ap)
    a = ap.parse_args()
    return a, get(a.app)

def get(slug):
    for x in REG["apps"]:
        if x["slug"] == slug: return x
    raise SystemExit(f"unknown app {slug}; known: {[x['slug'] for x in REG['apps']]}")

def data_dir(app): return ROOT/"data"/app["slug"]
def raw_dir(app):
    d = data_dir(app)/"raw"; d.mkdir(parents=True, exist_ok=True); return d
def rawf(app, kind, gen=None):
    """kind e.g. ios_reviews. Multi-generation apps get a .<gen> suffix before .json."""
    suffix = f".{gen}" if gen else ""
    return raw_dir(app)/f"{kind}{suffix}.json"

PHASE1 = "ae in gb us sa ph pk eg".split()
ALL_STOREFRONTS = """af al dz ao ai ag ar am au at az bs bh bb by be bz bj bm bt bo ba bw br vg bn bg bf kh cm ca cv ky td cl cn co cg cd cr ci hr cy cz dk dm do ec eg sv gq ee sz et fj fi fr ga gm ge de gh gr gd gt gw gy hn hk hu is in id iq ie il it jm jp jo kz ke kr xk kw kg la lv lb lr ly lt lu mo mg mw my mv ml mt mr mu mx fm md mn me ms ma mz mm na nr np nl nz ni ne ng mk no om pk pw pa pg py pe ph pl pt qa ro ru rw kn lc vc ws sa sn rs sc sl sg sk si sb za es lk sr se ch tw tj tz th to tt tn tr tm tc ug ua ae gb us uy uz vu ve vn ye zm zw""".split()
