"""Viewport-sized crops of a rendered page for visual inspection. Usage: slices.py <outdir> [page, default app.html#enbdx] [screens, default 5]"""
import sys, subprocess, time, pathlib
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent / "web"; port = 8766
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.2)
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
path = sys.argv[2] if len(sys.argv) > 2 else "app.html#enbdx"; n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
tag = path.replace(".html", "").replace("#", "-")
specs = [("desktop-light", 1440, 900, "light"), ("phone-dark", 390, 844, "dark")]
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h, scheme in specs:
            ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme); page = ctx.new_page()
            page.goto(f"http://127.0.0.1:{port}/{path}", wait_until="networkidle"); page.wait_for_timeout(2500)
            for i in range(n):
                page.evaluate(f"window.scrollTo(0,{i*h})"); page.wait_for_timeout(400)
                page.screenshot(path=str(out / f"{tag}-{name}-{i}.png"))
            ctx.close()
        b.close()
finally: srv.terminate()
print("done")
