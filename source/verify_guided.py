"""Check the five optional guiding plans in a fresh phone browser."""
import argparse
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASELINES = {"baku": 8, "tbilisi": 7, "budapest": 8, "vienna": 8, "prague": 6}


def verify(browser, url, width, height):
    offline = url.startswith("file:")
    context = browser.new_context(viewport={"width":width, "height":height}, has_touch=True, is_mobile=True,
                                  offline=offline, reduced_motion="reduce")
    page = context.new_page()
    requests, errors = [], []
    page.on("request", lambda r: requests.append(r.url) if r.url.startswith(("https:", "http:")) else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    for city, days in BASELINES.items():
        page.goto(url + "#" + city + "/guides", wait_until="domcontentloaded")
        guide = page.locator("#guides")
        expect(guide).to_have_attribute("open", "")
        expect(guide.locator(":scope > summary")).to_be_focused()
        expect(page.locator(".day")).to_have_count(days)
        original = page.locator("#total-group").inner_text()
        expect(guide.locator(".guided-option")).to_have_count(2)
        for mode in ("day", "night"):
            option = guide.locator(f"[data-guide-plan='{mode}']")
            summary = option.locator("summary")
            if option.get_attribute("open") is None:
                summary.tap()
            expect(option).to_have_attribute("open", "")
            assert summary.bounding_box()["height"] >= 44
            assert option.locator(".guided-journey li").count() >= 2
            for link in option.locator(".guided-links a").all():
                assert urlparse(link.get_attribute("href")).scheme == "https"
                assert link.bounding_box()["height"] >= 44
        assert page.locator("#total-group").inner_text() == original
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert guide.get_by_text("Availability and prices for your dates are unconfirmed.", exact=False).is_visible()
        if city == "baku":
            href = guide.locator('a[href$="t517765/"]').get_attribute("href")
            assert urlparse(href).hostname == "www.getyourguide.com"
    assert not errors, errors
    assert not offline or not requests, requests
    context.close()
    print(f"{browser.version} {width} × {height}: all five guide choices passed. HTTP requests: {len(requests)}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=(ROOT / "index.html").as_uri())
    parser.add_argument("--browser", choices=("chrome", "msedge"), default="chrome")
    args = parser.parse_args()
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel=args.browser)
        for width, height in ((320,725),(390,844),(667,375)):
            verify(browser, args.url, width, height)
        browser.close()
