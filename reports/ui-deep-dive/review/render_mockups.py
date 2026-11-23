"""Capture the static proposal sketches, including measured spec overlays."""
from pathlib import Path
from playwright.sync_api import sync_playwright

AREA = Path(__file__).resolve().parent
SHOTS = AREA / "shots"
GUIDE = "http://127.0.0.1:18768/"
MOCKS = "http://127.0.0.1:18769/reports/ui-deep-dive/review/mockups.html"

SHOTS.mkdir(exist_ok=True)
with sync_playwright() as runner:
    browser = runner.chromium.launch(channel="chrome")
    page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    page.goto(GUIDE + "#baku/walk", wait_until="domcontentloaded")
    page.locator(".walk-basemap").evaluate("image=>image.decode()")
    page.locator(".mapbox").screenshot(path=SHOTS / "mock-map.jpg", type="jpeg", quality=85)
    page.locator("#atlas-toggle").click()
    page.locator(".has-globe canvas").wait_for()
    page.locator("#atlas-visual").screenshot(path=SHOTS / "mock-globe.jpg", type="jpeg", quality=85)
    page.locator("[data-winter-film=baku]").press("Enter")
    page.locator(".ss-stage").screenshot(path=SHOTS / "mock-stage.jpg", type="jpeg", quality=85)
    for index in range(1, 9):
        width = 667 if index in (3, 5, 6) else 390
        page.set_viewport_size({"width": width, "height": 844})
        ident = f"UI-{index:02d}"
        page.goto(MOCKS + "?" + str(width) + "#"+ident, wait_until="load")
        page.evaluate("document.fonts.ready")
        page.locator("#"+ident).screenshot(path=SHOTS / (ident+".jpg"), type="jpeg", quality=87)
        page.goto(MOCKS + "?spec-"+str(width)+"#"+ident, wait_until="load")
        page.locator(".spec").wait_for()
        page.locator("#"+ident).screenshot(path=SHOTS / (ident+"-spec.jpg"), type="jpeg", quality=84)
    browser.close()
