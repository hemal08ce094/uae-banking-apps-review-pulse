"""Interaction checks with Playwright against web/. Usage: verify.py"""
import sys, subprocess, time, pathlib, json
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent / "web"; port = 8767
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.2)
B = f"http://127.0.0.1:{port}"; fails = []
def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name, info); 
    if not ok: fails.append(name)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={"width":1440,"height":900}); page = ctx.new_page(); errs = []
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None); page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(B + "/index.html", wait_until="networkidle"); page.wait_for_timeout(2500)
        n = page.locator("#cards a.appcard").count(); check("six overview cards", n == 6, n)
        # sort control
        page.select_option("#sortSel", "low"); page.wait_for_timeout(200)
        first = page.locator("#cards a.appcard h3").first.inner_text(); check("sort by lowest 1-2 star share puts ADIB first", first.startswith("ADIB"), first)
        # chip toggle must not recolour survivors
        def strokes(): return page.evaluate("[...document.querySelectorAll('#lineBody svg path[stroke]')].map(p=>p.getAttribute('stroke'))")
        before = strokes(); page.click("[data-app=fab]"); page.wait_for_timeout(300); after = strokes()
        check("chip toggle removes one series", len(after) == len(before) - 1, f"{len(before)}->{len(after)}")
        check("survivors keep their colour", all(c in before for c in after) and "var(--c-fab)" not in after and after == [c for c in before if c != "var(--c-fab)"], after)
        page.click("[data-app=fab]"); page.wait_for_timeout(300); check("re-adding restores same colours", strokes() == before)
        for s in ("enbdx","fab","adcb","wio","mashreq","adib"): page.click(f"[data-app={s}]")
        page.wait_for_timeout(200); check("empty selection message", page.locator("#emptySel").is_visible() and not page.locator("#cmp").is_visible())
        for s in ("enbdx","fab","adcb","wio","mashreq","adib"): page.click(f"[data-app={s}]")
        page.click("[data-period='12']"); page.wait_for_timeout(300)
        check("period 12 shows 12 month labels range", "Nov 2025" in page.locator("#lineSub").inner_text(), page.locator("#lineSub").inner_text()[:90])
        page.click("[data-lview=table]"); page.wait_for_timeout(200); check("table view", page.locator("#lineBody table tr").count() > 10)
        page.click("[data-lview=chart]")
        cells = page.locator("#heat a.cell").count(); check("heatmap 20 themes x 6 apps", cells == 120, cells)
        page.click("[data-period='36']")
        # hover tooltip
        box = page.locator("#lineBody svg").bounding_box(); page.mouse.move(box["x"] + box["width"]*0.5, box["y"] + 150); page.wait_for_timeout(200)
        tip = page.locator("#tip"); check("hover tooltip lists every app", tip.is_visible() and tip.locator(".row").count() >= 7, tip.inner_text()[:80].replace("\n"," "))
        page.mouse.move(5, 5)
        # KPI sort
        page.click("#kpi th button:has-text('Written reviews')"); page.wait_for_timeout(100)
        firstrow = page.locator("#kpi tbody tr td.name").first.inner_text(); check("KPI sort by reviews", firstrow.startswith("ENBD") , firstrow)
        # mode persistence
        page.click("[data-mode=dark]"); page.reload(wait_until="networkidle"); page.wait_for_timeout(500)
        check("dark mode persists on reload", page.evaluate("document.documentElement.getAttribute('data-theme')") == "dark")
        page.click("[data-mode=light]")
        check("index console clean", not errs, errs[:3]); errs.clear()
        # card click -> app page
        page.goto(B + "/index.html", wait_until="networkidle"); page.wait_for_timeout(1500)
        page.locator("#cards a.appcard", has_text="FAB Mobile").click(); page.wait_for_load_state("networkidle"); page.wait_for_timeout(2500)
        check("navigated to app.html#fab", page.url.endswith("/app.html#fab"), page.url)
        check("app page hero names FAB", "FAB Mobile" in page.locator("#heroTitle").inner_text(), page.locator("#heroTitle").inner_text())
        S = json.load(open(root / "data/fab/summary.json")); hist = S["totals"]["hist"]
        check("app page total matches summary", page.locator("#stats .stat").first.locator(".val").inner_text().replace(",","") == str(S["totals"]["all"]), page.locator("#stats .stat").first.locator(".val").inner_text())
        page.click("[data-stars='1']"); page.wait_for_timeout(2500)
        v = page.locator("#stats .stat").first.locator(".val").inner_text().replace(",","")
        check("1-star tile equals summary.totals.hist[0]", v == str(hist[0]), f"{v} vs {hist[0]}")
        page.click("[data-stars='all']"); page.wait_for_timeout(1500)
        page.select_option("#themeSelect", "login"); page.wait_for_timeout(2500)
        th = [t for t in S["themes"] if t["key"] == "login"][0]; v = page.locator("#stats .stat").first.locator(".val").inner_text().replace(",","")
        check("theme filter equals summary theme count", v == str(th["count"]), f"{v} vs {th['count']}")
        page.select_option("#themeSelect", ""); page.wait_for_timeout(2000)
        v = page.locator("#stats .stat").first.locator(".val").inner_text().replace(",","")
        check("reset to all themes restores total", v == str(S["totals"]["all"]), v)
        page.fill("#q", "login"); page.wait_for_timeout(9000)
        txt = page.locator("#reviewList .small.muted").first.inner_text(); check("search lazy-loads and filters", "match" in txt, txt[:80])
        # switcher
        page.fill("#q", ""); page.select_option("#appSwitch", "wio"); page.wait_for_load_state("networkidle"); page.wait_for_timeout(2500)
        check("switcher loads wio", "Wio Personal" in page.locator("#heroTitle").inner_text(), page.locator("#heroTitle").inner_text())
        page.goto(B + "/app.html", wait_until="networkidle"); page.wait_for_timeout(1500)
        check("default app is enbdx", "ENBD X" in page.locator("#heroTitle").inner_text())
        check("app console clean", not errs, errs[:3])
        b.close()
finally:
    srv.terminate()
print("FAILED:", fails if fails else "none"); sys.exit(1 if fails else 0)
