"""Refresh store-level ratings (all star ratings, including star-only) for every app and append a dated snapshot to data/store_history.json.
Usage: fetch_store.py"""
import json, datetime, requests, sys
from google_play_scraper import app as gp_app
from common import REG, ROOT, rawf
KEEP = ["trackName","sellerName","averageUserRating","userRatingCount","version","currentVersionReleaseDate","releaseDate","minimumOsVersion","contentAdvisoryRating","fileSizeBytes","genres","releaseNotes"]
hist_f = ROOT/"data/store_history.json"; hist = json.loads(hist_f.read_text()) if hist_f.exists() else []
today = datetime.date.today().isoformat(); hist = [h for h in hist if h["date"] != today]
for app in REG["apps"]:
    for g in app["gens"]:
        row = {"date": today, "app": app["slug"], "gen": g["gen"]}
        try:
            res = requests.get(f"https://itunes.apple.com/lookup?id={g['ios']}&country=ae", timeout=20).json()["results"][0]
            rawf(app, "ios_app", g["gen"]).write_text(json.dumps({k: res.get(k) for k in KEEP}, indent=1))
            row["ios"] = {"avg": res.get("averageUserRating"), "count": res.get("userRatingCount")}
        except Exception as e: print("ios fail", app["slug"], e, file=sys.stderr)
        try:
            m = gp_app(g["play"], lang="en", country="ae")
            rawf(app, "play_app", g["gen"]).write_text(json.dumps({k: m.get(k) for k in ["title","score","ratings","reviews","histogram","version","installs","released","updated","developer","genre"]}, default=str, indent=1))
            row["play"] = {"avg": m.get("score"), "count": m.get("ratings"), "histogram": m.get("histogram")}
        except Exception as e: print("play fail", app["slug"], e, file=sys.stderr)
        hist.append(row); print(row)
hist_f.write_text(json.dumps(hist, indent=1))
