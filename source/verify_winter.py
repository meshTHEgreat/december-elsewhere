"""Verify the winter field guide in a fresh browser. Pass a Pages URL for online checks."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def verify(browser, url, output):
    offline = url.startswith("file:")
    cases = [(320, 725, True), (390, 844, False), (667, 375, True), (1440, 900, False)]
    results = []
    for width, height, reduced in cases:
        context = browser.new_context(offline=offline, viewport={"width": width, "height": height},
                                      has_touch=width<740, is_mobile=width<740, accept_downloads=True,
                                      reduced_motion="reduce" if reduced else "no-preference")
        page = context.new_page()
        problems, requests = [], []
        page.on("pageerror", lambda error: problems.append(str(error)))
        page.on("console", lambda message: problems.append(message.text) if message.type=="error" else None)
        page.on("request", lambda request: requests.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        page.on("response", lambda response: problems.append(f"{response.status} {response.url}") if response.status>=400 else None)
        page.goto(url, wait_until="domcontentloaded")
        expect(page.locator(".city-tab")).to_have_count(5)
        assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
        assert not any(path.endswith("winter-stage.js") for path in requests)
        page.locator(".mast [data-jump='winter']").click()
        assert page.url.endswith("#baku/winter")
        expect(page.locator("#winter h2")).to_be_focused()
        for name, route, status in [
            ("Baku", "Sabir Garden", "snow in Baku as rare"),
            ("Shahdag", "Qusar (Gusar)", "Opening soon"),
            ("Tufandag", "Gabala", "not verified")
        ]:
            option = page.get_by_role("button", name=name, exact=False).and_(page.locator("[data-winter-option]"))
            option.click()
            expect(option).to_have_attribute("aria-pressed", "true")
            expect(page.locator(".winter-route")).to_contain_text(route)
            expect(page.locator(".winter-option-facts")).to_contain_text(status)
            page.locator(".winter-figure img").evaluate("image=>image.decode()")
        photo = page.locator("[data-winter-photo]")
        photo.click()
        expect(page.locator("dialog")).to_be_visible()
        expect(page.locator("dialog img")).to_have_attribute("alt", "Tufandag resort cable lift near Gabala in January 2014")
        if width in (390, 1440):
            with page.expect_download() as event:
                page.locator("dialog .photo-download").click()
            downloaded = event.value
            assert downloaded.suggested_filename == "baku-tufandag.webp"
            assert downloaded.path().read_bytes() == (ROOT/"assets"/"baku-tufandag.webp").read_bytes()
        page.keyboard.press("Escape")
        expect(photo).to_be_focused()

        for mode, count in [("baku", 3), ("overview", 5)]:
            trigger=page.locator(f"[data-winter-film='{mode}']")
            trigger.press("Enter")
            stage=page.locator("#winter-film-stage .ss-stage")
            expect(stage).to_be_visible()
            assert stage.bounding_box()["width"]<=width
            if width <= 390:
                expect(stage).to_have_attribute("data-layout", "compact")
                assert stage.locator(".wf-story-image").bounding_box()["width"] >= stage.bounding_box()["width"] - 1
            if width == 1440:
                expect(stage).to_have_attribute("data-layout", "wide")
            frame=stage.locator("[data-story-index]")
            expect(frame).to_have_attribute("data-story-index", str(count-1) if reduced else "0")
            if not reduced:
                expect(frame).to_have_attribute("data-story-index", "1", timeout=6500)
            else:
                assert page.evaluate("document.querySelector('.ss-stage').getAnimations({subtree:true}).length") == 0
            assert stage.locator(".wf-story-beat[data-current='yes']").evaluate("""beat => {
                const story = beat.closest('.ss-stage').getBoundingClientRect();
                const track = story.height && beat.closest('.wf-story-editorial').querySelector('.wf-story-track').getBoundingClientRect();
                const detail = beat.querySelector('.wf-story-detail').getBoundingClientRect();
                return detail.bottom < track.top && track.bottom <= story.bottom;
            }""")
            if output and width in (390,1440):
                stage.screenshot(path=output/f"stage-{mode}-{width}.png")
            page.locator("[data-winter-close]").press("Enter")
            expect(trigger).to_be_focused()
            expect(stage).to_have_count(0)

        for city in ("baku","tbilisi","budapest","vienna","prague"):
            page.locator(f"[data-city='{city}']").click()
            expect(page.locator(".outdoor-space")).to_have_count(2)
            expect(page.locator("#winter .winter-official a").first).to_have_attribute("target", "_blank")
            assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
            map_preview = page.locator(".mapbox")
            raster = map_preview.locator(".walk-basemap")
            raster.scroll_into_view_if_needed()
            raster.evaluate("image=>image.decode()")
            assert raster.evaluate("image=>image.naturalWidth") >= 260
            original = page.locator(".active-route").get_attribute("points")
            page.locator("[data-walk-style='diagram']").click()
            expect(raster).not_to_be_visible()
            expect(page.locator(".active-route")).to_have_attribute("points",original)
            page.locator("[data-walk-style='satellite']").click()
            expect(raster).to_be_visible()
            expect(page.locator(".active-route")).to_have_attribute("points",original)
            for anchor in range(2):
                page.locator("#anchor-select").select_option(index=anchor)
                assert map_preview.evaluate("""box => {
                    const edge = box.getBoundingClientRect();
                    const photo = box.querySelector('img').getBoundingClientRect();
                    return photo.top <= edge.top + 2 && photo.left <= edge.left + 2
                        && photo.bottom >= edge.bottom - 2 && photo.right >= edge.right - 2;
                }"""), (city, anchor)
            expect(page.get_by_role("link", name="Open in Google Maps")).to_have_attribute("target","_blank")
            expect(page.get_by_role("link", name="Apple Maps")).to_have_attribute("target","_blank")
            if output and width in (390,1440) and city in ("baku","prague"):
                page.locator(".map-stage").screenshot(path=output/f"selected-walk-{city}-{width}.png")

        page.locator("#left-city").select_option("prague")
        page.locator("#cost-food").fill("1001")
        expect(page.locator("#compare-mark-value-0")).to_have_text(page.locator("#compare-0-person").inner_text())
        assert not problems, problems
        assert not offline or not requests
        if not offline:
            assert set(urlparse(path).netloc for path in requests) == {urlparse(url).netloc}
            assert len([path for path in requests if path.endswith("winter-stage.js")]) == 1
        results.append({"viewport":[width,height], "reduced_motion":reduced,
                        "winter_briefings":2, "satellite_cities":5, "requests":len(requests), "errors":problems})
        context.close()
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=(ROOT/"index.html").as_uri())
    parser.add_argument("--browser", default="chrome", choices=("chrome","msedge"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel=args.browser)
        report = {"browser":browser.version, "offline":args.url.startswith("file:"),
                  "standalone_sha256":hashlib.sha256((ROOT/"index.html").read_bytes()).hexdigest(),
                  "results":verify(browser,args.url,args.output)}
        print(json.dumps(report,indent=2))
        browser.close()
