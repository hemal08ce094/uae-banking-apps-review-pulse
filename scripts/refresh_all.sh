#!/usr/bin/env bash
# refresh every app, then rebuild data/compare.json
cd "$(dirname "$0")/.."
for slug in $(${PY:-.venv/bin/python} -c "import json;print(' '.join(a['slug'] for a in json.load(open('data/apps.json'))['apps']))"); do
  echo "== $slug"; ./scripts/refresh.sh $slug
done
${PY:-.venv/bin/python} scripts/build_compare.py
cp data/compare.json data/apps.json web/data/
echo REFRESH_ALL_DONE
