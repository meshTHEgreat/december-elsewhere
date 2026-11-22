"""Browser release checks. Usage: python source/verify_premium.py URL --browser chrome."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CITY_IDS = ("baku", "tbilisi", "budapest", "vienna", "prague")
MONEY = lambda text: int("".join(ch for ch in text if ch.isdigit()))


def checked_assets(page, selector):
    for image in page.locator(selector).all():
        image.scroll_into_view_if_needed()
        image.evaluate("async image => {await image.decode(); if (!image.naturalWidth) throw Error('Empty photo');}")


def check_page(browser, url, width, height, mobile, reduced, output):
    offline = urlparse(url).scheme == "file"
    origin = urlparse(url).netloc
    context = browser.new_context(offline=offline, viewport={"width": width, "height": height},
                                  is_mobile=mobile, has_touch=mobile,
                                  device_scale_factor=3 if mobile else 1,
                                  reduced_motion="reduce" if reduced else "no-preference")
    page = context.new_page()
    page.set_default_timeout(8000)
    errors, request_urls = [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("response", lambda response: errors.append(f"{response.status} {response.url}") if response.status >= 400 else None)
    page.on("console", lambda entry: errors.append(entry.text) if entry.type == "error" else None)
    page.on("request", lambda request: request_urls.append(request.url) if request.url.startswith(("http:", "https:")) else None)
    response = page.goto(url, wait_until="domcontentloaded")
    assert response.ok
    page.evaluate("document.fonts.ready")
    expect(page.locator(".city-tab")).to_have_count(5)
    assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
    expect(page.locator(".cover-facts")).to_contain_text("5–12 December 2026")
    assert page.locator(".cover-facts").bounding_box()["y"] + page.locator(".cover-facts").bounding_box()["height"] <= height
    checked_assets(page, ".hero .backdrop")
    assert all(urlparse(request).netloc == origin for request in request_urls)
    assert not any(request.endswith("globe.js") for request in request_urls)
    page.locator("#atlas-toggle").click()
    expect(page.locator("#atlas-visual")).to_have_class("atlas-visual has-globe")
    canvas = page.locator("#atlas-globe canvas")
    expect(canvas).to_be_visible()
    assert canvas.evaluate("(canvas) => canvas.width <= canvas.clientWidth * 1.5 + 1")
    page.locator("#atlas-select").select_option("prague")
    expect(page.locator("#atlas-open-label")).to_have_text("Read Prague")
    expect(page.locator(".globe-pin.is-active")).to_have_text("Prague")
    expect(page.locator("#atlas-distance")).to_have_text("3,580 km direct")
    if output and width in (390, 1440):
        page.locator("#atlas-visual").screenshot(path=output/f"globe-{width}.png")
    page.locator("[data-open-preview]").click()
    expect(page.locator("#chapter h2")).to_be_focused()
    expect(canvas).to_have_count(0)
    assert page.url.endswith("#prague")

    dataset = page.evaluate("""() => {
        const book = JSON.parse(document.getElementById('dataset').textContent);
        const photos = Object.fromEntries(Object.entries(book.photos).map(([city, images]) =>
            [city, images.map(({url, licenseUrl}) => ({url, licenseUrl}))]));
        return {cities: book.cities, photos};
    }""")
    facts = {city["id"]: city for city in dataset["cities"]}
    counts = {"cities": 0, "stays": 0, "days": 0, "photos": 0, "routes": 0}
    for city in CITY_IDS:
        target = page.locator(f".city-tab[data-city='{city}']")
        target.tap() if mobile else target.press("Enter")
        expect(page.locator("#chapter h2")).to_have_text(facts[city]["city"])
        expect(page.locator("#chapter h2")).to_be_focused()
        counts["cities"] += 1
        checked_assets(page, ".chapter img,.neighborhood-photo img,.journey-photo img")
        assert all("→" in leg and "MED" in leg for leg in page.locator(".flight-leg > strong").all_inner_texts())
        assert not page.locator("#stays").get_by_text("[object Object]", exact=False).count()
        for index in (0, 1):
            page.locator(f"[data-stay='{index}']").click()
            expect(page.locator(f"[data-stay='{index}']")).to_have_attribute("aria-pressed", "true")
            expected = facts[city]["stays"][index]
            expect(page.locator("#cost-stay")).to_have_value(str(expected["price"]))
            assert page.locator(".stay").nth(index).locator("a").get_attribute("href") == expected["url"]
            counts["stays"] += 1
        for anchor in range(2):
            page.locator("#anchor-select").select_option(index=anchor)
            routes = page.locator("[data-route]")
            paths = page.locator(".mapbox polyline")
            assert routes.count() == paths.count()
            for index in range(routes.count()):
                route = routes.nth(index)
                if mobile and width < 673:
                    page.locator("#route-select").select_option(str(index))
                else:
                    route.press("Enter")
                expect(route).to_have_attribute("aria-pressed", "true")
                expect(page.locator("#route-note strong")).to_have_text(route.locator("strong").inner_text())
                assert page.locator(".active-route").evaluate("(path) => path.getTotalLength()") > 0
                counts["routes"] += 1
        for index, day in enumerate(page.locator(".day").all()):
            if index:
                day.locator("summary").press("Enter")
            expect(day.locator(".stops")).to_be_visible()
            counts["days"] += 1
        for picture in dataset["photos"][city]:
            checked_assets(page, "#gallery img")
            expect(page.locator("#gallery a").nth(0)).to_have_attribute("href", picture["url"])
            expect(page.locator("#gallery a").nth(1)).to_have_attribute("href", picture["licenseUrl"])
            counts["photos"] += 1
            page.locator("[data-gallery='1']").click()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

    if mobile and width < 673:
        page.locator("#chapter").evaluate("(el) => el.scrollIntoView({block:'start'})")
        menu = page.locator(".chapter-menu summary")
        menu.tap()
        expect(page.locator(".chapter-menu")).to_have_attribute("open", "")
        assert all(0 <= item.bounding_box()["y"] <= height - 44 for item in page.locator(".chapter-menu a").all())
        menu.press("Escape")
        expect(menu).to_be_focused()
        assert page.locator(".chapter-menu").get_attribute("open") is None

    photo = page.locator("[data-photo-open]")
    photo.click()
    expect(page.locator("dialog")).to_be_visible()
    page.locator("[data-photo-close]").press("ArrowRight")
    expect(page.locator("dialog .gallery-tools .small")).to_contain_text("2 /")
    page.keyboard.press("Escape")
    expect(photo).to_be_focused()
    expect(page.locator("dialog")).not_to_be_visible()

    page.locator("#left-city").select_option("prague")
    baseline = MONEY(page.locator("#total-group").inner_text())
    field = page.locator("#cost-food")
    new_food = str(int(field.input_value()) + 100)
    field.fill(new_food)
    expect(page.locator("#compare-0-group")).to_have_text(page.locator("#total-group").inner_text())
    assert MONEY(page.locator("#total-group").inner_text()) == baseline + 300
    page.reload(wait_until="domcontentloaded")
    expect(page.locator("#cost-food")).to_have_value(new_food)
    expect(page.locator("#left-city")).to_have_value("prague")
    page.locator("[data-reset]").click()
    if reduced:
        assert page.evaluate("document.getAnimations().length") == 0

    assert counts == {"cities": 5, "stays": 10, "days": 37, "photos": 17, "routes": 55}, counts
    assert not errors, errors
    assert not offline or not request_urls, request_urls
    if not offline:
        assert all(urlparse(request).netloc == origin for request in request_urls)
        assert page.locator("a[download]").get_attribute("href") == "offline.html"
    info = {"viewport": [width, height], "emulated_touch": mobile, "reduced_motion": reduced,
            "offline": offline, "requests": len(request_urls), "checks": counts, "errors": errors}
    context.close()
    return info


def check_fallback(browser, url):
    context = browser.new_context(offline=url.startswith("file:"))
    context.add_init_script("""const get = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function (type, ...args) {
          return type.startsWith('webgl') ? null : get.call(this, type, ...args);
        };""")
    page = context.new_page()
    page.goto(url)
    page.locator("#atlas-toggle").click()
    expect(page.get_by_role("status")).to_contain_text("static atlas")
    expect(page.locator("#atlas-flat svg")).to_be_visible()
    expect(page.locator("#atlas-globe canvas")).to_have_count(0)
    page.locator("#atlas-select").select_option("vienna")
    page.locator("[data-open-preview]").click()
    expect(page.locator("#chapter h2")).to_have_text("Vienna")
    context.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=(ROOT / "index.html").as_uri())
    parser.add_argument("--browser", choices=("chrome", "msedge"), default="chrome")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel=args.browser)
        device_matrix = [(1440, 900, False, False), (390, 844, True, True), (740, 360, True, False)]
        evidence = [check_page(browser, args.url, *device, args.output) for device in device_matrix]
        check_fallback(browser, args.url)
        print(json.dumps({"browser": browser.version, "url": args.url, "fallback": "passed",
                          "offline_sha256": hashlib.sha256((ROOT / "index.html").read_bytes()).hexdigest(),
                          "results": evidence}, indent=2))
        browser.close()
