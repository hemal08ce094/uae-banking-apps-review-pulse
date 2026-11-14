# UAE Banking Apps Review Pulse

Every public written review from the Apple App Store and Google Play for six UAE banking apps, collected locally, analysed with one shared theme list, and shown in a static site: a comparison dashboard (`web/index.html`) and one detail page per app (`web/app.html#<slug>`).

Apps are listed in `data/apps.json` (slug, store ids, fixed colours). ADCB has two app generations (new "ADCB." and the previous "ADCB"); both are collected, tagged with `generation`, and merged under one slug.

## Layout

- `data/apps.json` the registry. Add an app here and every script picks it up.
- `data/<slug>/raw/` collector output: `ios_reviews*.json` (RSS), `ios_deep_reviews*.json` (catalogue API) and its `ios_deep_state*.json`, `play_reviews*.json`, store metadata. Multi-generation apps add a `.new` or `.old` suffix.
- `data/<slug>/summary.json`, `insights.json`, `index.json`, `reviews.json`, `reviews/<year>.json` analysis output.
- `data/compare.json` like-for-like record per app plus computed cross-app findings.
- `scripts/insights/<slug>.py` the written narrative for each app. Every quote is resolved by snippet against the real reviews and every number is computed.
- `web/` the site. `web/data` is a copy made by `scripts/build_web.sh` and `refresh_all.sh`; host `web/` as-is.

## Commands

Run with the venv at `.venv` (Python 3.9). Every script takes `--app <slug>`.

```
scripts/collect_all.sh [slug ...]   # the five new apps, in order, in the background (nohup)
scripts/status.sh                   # per-app counts and running crawlers
scripts/refresh.sh <slug>           # analyze + insights + copy to web/data/<slug>
scripts/refresh_all.sh              # every app, then compare.json
scripts/serve.sh                    # http://127.0.0.1:8080
```

Individual steps: `fetch_ios.py` (RSS, main storefronts), `fetch_ios_all.py` (RSS, the rest), `fetch_ios_deep.py [--phase 1|2|all]` (catalogue API, no cap, resumable), `fetch_play.py`, `fetch_play_more.py`, `analyze.py`, `build_insights.py`, `build_compare.py`.

`collect_all.sh` runs Play for all apps at once, iOS RSS one app at a time, then the deep App Store crawl in two phases (phase 1: ae in gb us sa ph pk eg; phase 2: every other storefront), two crawlers at a time. It refreshes the site after phase 1 and at the end. `scripts/finalize.sh` waits for collectors and refreshes everything.

## Checks

```
scripts/shoot.py <outdir>     # index + app pages, desktop and phone, light and dark; asserts no overflow, clean console
scripts/slices.py <outdir> [page] [screens]
scripts/verify.py             # card navigation, chip recolouring, heatmap, mode persistence, app-page filters vs summary
scripts/sample.py --app <slug> [--months 2026-03] [--grep regex]   # reading samples for writing a narrative
```

## Notes

- Star-only ratings are not public, so every count here is a written review.
- Apple's RSS feed stops at 500 reviews per storefront and sort order and returns little for some apps. The catalogue endpoint the apps.apple.com page uses pages past that with `offset`, ten at a time, and rate-limits hard; the deep collector adapts its pace and resumes from its state file.
- Themes are keyword tags (English and Arabic) in `scripts/analyze.py`, identical for every app; sentiment comes from the star rating, with 3-star reviews resolved by wording.
- `coverage` in each summary says how far the deep App Store crawl has got; pages and cards show a chip until it is complete.
