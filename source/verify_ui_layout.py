"""Measured mobile-first CSS contracts for the offline file or a hosted guide."""
import argparse
from pathlib import Path
import re

from playwright.sync_api import sync_playwright

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=(ROOT / "index.html").as_uri())
    parser.add_argument("--browser", choices=("chrome", "msedge"), default="chrome")
    args = parser.parse_args()
    rules()
    with sync_playwright() as driver:
        browser = driver.chromium.launch(channel=args.browser)
        check(browser, args.url)
        print(f"Layout passed in {browser.version} at all six viewport sizes")
        browser.close()
