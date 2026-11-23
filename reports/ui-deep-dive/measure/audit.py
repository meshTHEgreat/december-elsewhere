"""Measure the supplied guide in a fresh Chromium browser. All distances are CSS pixels."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WIDTHS = [(320, 725), (390, 844), (667, 375), (768, 1024), (1440, 900), (2560, 1440)]
CITIES = ["baku", "tbilisi", "budapest", "vienna", "prague"]
SECTIONS = ["intro", "stays", "walk", "winter", "itinerary", "budget", "photos"]
MEASURE = (HERE / "measure.js").read_text(encoding="utf-8")


def audit(browser, url, widths, offline):
    results = []
    for width, height in widths:
        context = browser.new_context(
            viewport={"width": width, "height": height},
            reduced_motion="reduce",
            is_mobile=width < 740,
            has_touch=width < 740,
            offline=offline,
        )
        page = context.new_page()
        page.set_default_timeout(7000)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url, wait_until="domcontentloaded")
        page.evaluate("document.fonts.ready")
        page.locator(".city-tab").first.wait_for()

        def take(scope, label):
            values = page.evaluate(MEASURE, scope)
            values["stateName"] = label
            results.append(values)

        for scope in (".mast", "#top", "#destinations", "#compare", "#evidence", ".footer"):
            take(scope, "default")
        page.locator(".compare-details summary").press("Enter")
        take("#compare", "details expanded")
        for details in page.locator("#evidence details").all():
            details.locator("summary").press("Enter")
        take("#evidence", "sources open")

        for city in CITIES:
            page.locator(f".city-tab[data-city='{city}']").press("Enter")
            assert page.url.endswith("#" + city)
            take("#chapter", city + " cover")
            take(".city-subnav", city + " nav")
            compact = page.locator(".chapter-menu summary")
            if compact.is_visible():
                compact.press("Enter")
                take(".city-subnav", city + " menu open")
                compact.press("Enter")
            for section in SECTIONS:
                take("#" + section, city + " " + section)
            take(".chapter-end", city + " decision")
            page.locator(".flight-details summary").press("Enter")
            take("#intro", city + " flight details")
            page.locator("[data-stay='1']").press("Enter")
            take("#stays", city + " second stay")
            page.locator("#anchor-select").select_option(index=1)
            page.locator("[data-walk-style='diagram']").press("Enter")
            take("#walk", city + " alternate anchor and diagram")
            page.locator("[data-walk-style='satellite']").press("Enter")
            for option in page.locator(".winter-option").all()[1:]:
                option.press("Enter")
                take("#winter", city + " winter " + option.inner_text().splitlines()[0])
            page.locator(".day summary").last.press("Enter")
            take("#itinerary", city + " last day open")
            if page.locator("#guides").count():
                guide = page.locator("#guides")
                take("#guides", city + " local guides collapsed")
                guide.locator(":scope > summary").press("Enter")
                for mode in ("day", "night"):
                    option = guide.locator(f"[data-guide-plan='{mode}']")
                    if option.get_attribute("open") is None:
                        option.locator("summary").press("Enter")
                    take("#guides", city + " local guides " + mode)
                guide.locator(":scope > summary").press("Enter")
            if not page.locator(".car-costs").get_attribute("open"):
                page.locator(".car-costs summary").press("Enter")
            page.locator("#cost-car").fill("1240")
            take("#budget", city + " rental and edited")
            page.locator("#gallery [data-photo-open]").press("Enter")
            take("#photo-dialog", city + " photo open")
            page.keyboard.press("Escape")
            expect(page.locator("#gallery [data-photo-open]")).to_be_focused()
        for name in ("baku", "overview"):
            page.locator(f"[data-winter-film='{name}']").press("Enter")
            page.locator(".ss-stage").wait_for()
            take("#winter-film", name + " briefing poster")
            page.locator("[data-winter-close]").press("Enter")
        if errors:
            raise AssertionError(errors)
        context.close()
    return results


def findings(results):
    for state in results:
        prefix = f"{state['width']}×{state['height']} {state['stateName']} {state['scope']}"
        if state["documentOverflow"]:
            print(f"{prefix} | document overflow {state['documentOverflow']} px")
        for group in state["alignments"]:
            if group["spread"] > 1:
                print(f"{prefix} | {group['label']} spread {group['spread']} px")
        for target in state["targets"]:
            if target["width"] < 44 or target["height"] < 44:
                print(f"{prefix} | {target['element']} {target['name']} {target['width']}×{target['height']}")
        for region in state["scroll"]:
            if region["content"] - region["visible"] > 1:
                print(f"{prefix} | {region['element']} horizontal scroll {region['content'] - region['visible']} px")


if __name__ == "__main__":
    options = argparse.ArgumentParser(description=__doc__)
    options.add_argument("url")
    options.add_argument("--width", type=int, choices=[width for width, _ in WIDTHS])
    options.add_argument("--browser", default="chrome", choices=["chrome", "msedge"])
    options.add_argument("--out", type=Path, required=True)
    args = options.parse_args()
    matrix = [size for size in WIDTHS if not args.width or size[0] == args.width]
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel=args.browser)
        results = audit(browser, args.url, matrix, args.url.startswith("file:"))
        data = {"browser": browser.version, "url": args.url, "states": results}
        args.out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        findings(results)
        browser.close()
