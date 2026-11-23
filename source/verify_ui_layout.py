"""Measured mobile-first CSS contracts for the offline file or a hosted guide."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def rules():
    css = (ROOT / "source/styles.css").read_text(encoding="utf-8")
    winter = (ROOT / "source/winter.css").read_text(encoding="utf-8")
    assert re.search(r"--touch-target:\s*2\.75rem", css), "Shared 44 px touch target"
    assert re.search(r"\.lightbox-figure img\s*{[^}]*height:\s*auto", css), "Intrinsic dialog image height"
    assert re.search(r"\.compare-target\s*{[^}]*var\(--muted\)", winter), "Contrasting budget band"
    assert re.search(r"\.source-action\s*{[^}]*var\(--touch-target\)", css), "Evidence links use the shared target"


def check(browser, url):
    for size in [(320, 725), (390, 844), (667, 375), (768, 1024), (1440, 900), (2560, 1440)]:
        width, height = size
        context = browser.new_context(viewport={"width": width, "height": height}, has_touch=width < 740,
                                      is_mobile=width < 740, reduced_motion="reduce", offline=url.startswith("file:"))
        page = context.new_page()
        page.goto(url + "#baku/photos", wait_until="domcontentloaded")
        page.evaluate("document.fonts.ready")
        for link in page.locator(".mast nav a, .chapter-jumps a:visible").all():
            size = link.bounding_box()
            assert size["height"] >= 44 and size["width"] >= 44, (width, link.inner_text(), size)
        assert page.evaluate("""() => {
          const starts = [...document.querySelectorAll('.city-name')].map(title=>title.getBoundingClientRect().left);
          return Math.max(...starts) - Math.min(...starts) <= 1;
        }"""), width
        photo = page.locator("#gallery [data-photo-open]")
        photo.press("Enter")
        image = page.locator("#photo-dialog img")
        image.evaluate("img=>img.decode()")
        assert image.evaluate("""img => {
          const r = img.getBoundingClientRect();
          return Math.abs(r.width / r.height - img.naturalWidth / img.naturalHeight) < .025;
        }"""), width
        page.keyboard.press("Escape")
        assert photo.evaluate("button=>button === document.activeElement")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), width
        if width <= 390:
            amounts = [page.locator(selector).bounding_box()["y"] for selector in ("#total-person", "#total-group")]
            assert abs(amounts[0] - amounts[1]) <= 1, (width, "budget amount baselines", amounts)
        detail = page.locator("#evidence details").first
        detail.locator("summary").press("Enter")
        assert detail.locator("a.source-action").count() >= 17
        for link in detail.locator("a.source-action").all():
            size = link.bounding_box()
            assert size["width"] >= 44 and size["height"] >= 44, (width, size)
        if width == 667:
            page.locator("#atlas-toggle").click()
            page.locator(".atlas-visual.has-globe").wait_for()
            visual = page.locator(".atlas-visual").bounding_box()
            mast = page.locator(".mast").bounding_box()
            assert visual["y"] >= mast["y"] + mast["height"] - 1, visual
            assert visual["y"] + visual["height"] < height + 1, visual
            assert .9 * height >= page.locator(".atlas-panel").bounding_box()["height"]
        context.close()


def check_landscape_photo_controls(browser, url):
    counts = Counter(photo["city"] for photo in json.loads((ROOT / "source/photography.json").read_text(encoding="utf-8")))
    context = browser.new_context(viewport={"width": 667, "height": 375}, has_touch=True, is_mobile=True,
                                  reduced_motion="reduce", offline=url.startswith("file:"))
    page = context.new_page()
    page.goto(url, wait_until="domcontentloaded")
    page.evaluate("document.fonts.ready")
    for city, count in counts.items():
        page.locator(f".city-tab[data-city='{city}']").tap()
        page.locator("#gallery [data-photo-open]").tap()
        viewer = page.locator("#photo-dialog")
        for index in range(count):
            viewer.locator("img").evaluate("img=>img.decode()")
            for selector in ("[data-photo-close]", "[data-gallery='-1']", "[data-gallery='1']", ".photo-download"):
                rect = viewer.locator(selector).bounding_box()
                assert rect and rect["height"] >= 44 and rect["y"] >= 0 and rect["y"] + rect["height"] <= 375.5, (city, index, selector, rect)
            viewer.locator("[data-gallery='1']").press("Enter")
        page.keyboard.press("Escape")
        expect(page.locator("#gallery [data-photo-open]")).to_be_focused()
    context.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=(ROOT / "index.html").as_uri())
    parser.add_argument("--browser", choices=("chrome", "msedge"), default="chrome")
    parser.add_argument("--photos-only", action="store_true")
    args = parser.parse_args()
    rules()
    with sync_playwright() as driver:
        browser = driver.chromium.launch(channel=args.browser)
        if not args.photos_only:
            check(browser, args.url)
        check_landscape_photo_controls(browser, args.url)
        print(f"Layout and landscape photo controls passed in {browser.version}")
        browser.close()
