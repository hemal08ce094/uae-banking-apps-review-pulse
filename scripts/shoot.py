"""Render the comparison dashboard and app pages with headless Chromium at desktop and phone sizes, light and dark.
Asserts no horizontal overflow and a clean console, writes full-page shots and viewport-sized slices of the first 3 screens.
Usage: shoot.py [outdir]"""
import sys, subprocess, time, pathlib
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent / "web"
port = 8765
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp"); out.mkdir(parents=True, exist_ok=True)
PAGES = [("index", "index.html"), ("fab", "app.html#fab"), ("enbdx", "app.html#enbdx")]
VIEWS = [("desktop", 1440, 900), ("phone", 390, 844)]
bad = 0
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        for scheme in ("light", "dark"):
            for vname, w, h in VIEWS:
                for pname, path in PAGES:
                    ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme, device_scale_factor=1)
                    ctx.add_init_script(f"try{{localStorage.setItem('rp-mode','{scheme}')}}catch(e){{}}")
                    page = ctx.new_page(); errs = []
                    page.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
                    page.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
                    page.goto(f"http://127.0.0.1:{port}/{path}", wait_until="networkidle"); page.wait_for_timeout(2600)
                    sw = page.evaluate("document.documentElement.scrollWidth"); cw = page.evaluate("document.documentElement.clientWidth")
                    name = f"{pname}-{vname}-{scheme}"
                    page.screenshot(path=str(out / f"{name}-full.png"), full_page=True)
                    for i in range(3):
                        page.evaluate(f"window.scrollTo(0,{i*h})"); page.wait_for_timeout(500)
                        page.screenshot(path=str(out / f"{name}-s{i}.png"))
                    ok = sw <= cw and not errs; bad += (not ok)
                    print(name, "scrollWidth", sw, "clientWidth", cw, "OVERFLOW" if sw > cw else "ok", "| console:", errs[:5] or "clean")
                    ctx.close()
        b.close()
finally:
    srv.terminate()
sys.exit(1 if bad else 0)
