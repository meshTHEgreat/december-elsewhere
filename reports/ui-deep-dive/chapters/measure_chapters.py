"""Read-only live layout audit. Default output stays beside this script."""
import argparse
import gzip
import io
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import expect, sync_playwright


BASE = Path(__file__).resolve().parent
MEASURE = (BASE / "chapter-measure.js").read_text(encoding="utf-8")
SITES = ["baku", "tbilisi", "budapest", "vienna", "prague"]
VIEWPORTS = [(320, 725), (390, 844), (667, 375), (768, 1024), (1440, 900), (2560, 1440)]
WITNESSES = {
    "budapest": {320: {"cover"}},
    "baku": {
        320: {"stay-first", "walk-controls", "stage-baku", "winter-1", "photo-dialog"},
        390: {"walk-satellite", "stage-overview", "winter-1", "itinerary"},
        667: {"stage-baku", "stage-overview", "walk-controls", "photo-dialog", "flight-open"},
        768: {"walk-satellite", "winter-0", "stage-baku"},
        1440: {"arrival", "stage-baku", "stage-overview", "end"},
        2560: {"walk-satellite", "end"},
    },
    "tbilisi": {768: {"stay-first", "winter-0"}, 1440: {"stay-first", "winter-0"}},
    "vienna": {1440: {"stay-second", "walk-second"}},
    "prague": {320: {"itinerary"}, 667: {"flight-open", "photo-dialog"}, 1440: {"itinerary-expanded", "photo-dialog"}, 2560: {"photos"}},
}


def save_shot(page, path):
    screen = page.screenshot(type="jpeg", quality=84, animations="disabled")
    with Image.open(io.BytesIO(screen)) as image:
        image.thumbnail((1440, 1050))
        image.save(path, quality=75, optimize=True)


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--url", default="http://127.0.0.1:18768/")
    cli.add_argument("--browser", choices=("chrome", "msedge"), default="chrome")
    cli.add_argument("--widths", nargs="+", type=int, choices=[x[0] for x in VIEWPORTS])
    cli.add_argument("--output", type=Path, default=BASE)
    args = cli.parse_args()
    output = args.output.resolve()
    if BASE not in [output, *output.parents]:
        raise ValueError("Output must stay under the chapters notes directory.")
    shots = output / "shots"
    shots.mkdir(exist_ok=True, parents=True)
    report = {"viewports": [], "url": args.url, "language": "en", "dir": "ltr"}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=args.browser)
        report["browser"] = browser.version
        for width, height in VIEWPORTS:
            if args.widths and width not in args.widths:
                continue
            context = browser.new_context(viewport={"width": width, "height": height}, is_mobile=width < 768,
                                          has_touch=width < 768, reduced_motion="reduce")
            page = context.new_page()
            page.set_default_timeout(8000)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(args.url, wait_until="domcontentloaded")
            page.evaluate("document.fonts.ready")
            device = {"viewport": [width, height], "cities": [], "errors": errors}
            for city in SITES:
                city_data = {"city": city, "states": {}}
                page.locator(f".city-tab[data-city='{city}']").press("Enter")
                expect(page.locator(".chapter")).to_have_class(f"chapter chapter-{city}")
                city_data["landing_focus"] = page.locator(".chapter h2").evaluate("el => el === document.activeElement")

                def snap(selector, key, scroll=True):
                    if scroll:
                        page.locator(selector).evaluate("""el => {
                            if (el instanceof HTMLDialogElement) return;
                            const y = el.getBoundingClientRect().top + scrollY - 117;
                            window.scrollTo({top: Math.max(0,y), behavior:'instant'});
                        }""")
                    result = page.evaluate(MEASURE, selector)
                    city_data["states"][key] = result
                    if key in WITNESSES.get(city, {}).get(width, {}):
                        name = f"{city}-{width}-{key}.jpg"
                        save_shot(page, shots / name)
                        result["shot"] = f"shots/{name}"
                    return result

                snap(".chapter", "cover", scroll=False)
                snap("#intro", "arrival")
                page.locator(".flight-details").evaluate("el => el.open = true")
                snap(".arrival-facts", "flight-open")

                snap("#stays", "stay-head")
                snap(".stays", "stay-first")
                page.locator("[data-stay='1']").press("Enter")
                second = snap(".stays", "stay-second")
                second["selection_focus"] = page.locator("[data-stay='1']").evaluate("el => el === document.activeElement")
                if page.locator("#stays details").count():
                    page.locator("#stays details").evaluate("el => el.open = true")
                    snap("#stays details", "stay-alternatives")

                snap("#map", "walk-controls")
                snap(".route-layout", "walk-satellite")
                page.locator("[data-walk-style='diagram']").press("Enter")
                snap(".route-layout", "walk-diagram")
                page.locator("[data-walk-style='satellite']").press("Enter")
                page.locator("#anchor-select").select_option(index=1)
                if page.locator("#route-select").is_visible():
                    page.locator("#route-select").select_option(index=1)
                else:
                    page.locator("[data-route='1']").press("Enter")
                selected = page.locator(".map-stage").evaluate("el => ({top:el.getBoundingClientRect().top, note:el.querySelector('#route-note strong').textContent, active:document.activeElement.id || document.activeElement.textContent})")
                snap(".route-layout", "walk-second")["selection"] = selected
                if page.locator(".transport-notes").count():
                    snap(".transport-notes", "transport")

                snap("#winter", "winter-options")
                options = page.locator("[data-winter-option]")
                for alternative in range(max(1, options.count())):
                    if options.count():
                        options.nth(alternative).press("Enter")
                    snap(".winter-option-layout", f"winter-{alternative}")
                if city == "baku":
                    trigger = page.locator("[data-winter-photo]").first
                    trigger.press("Enter")
                    expect(page.locator("dialog")).to_be_visible()
                    snap("dialog", "winter-photo")
                    page.keyboard.press("Escape")
                    city_data["winter_photo_focus"] = trigger.evaluate("el => el === document.activeElement")
                    for film in ("baku", "overview"):
                        trigger = page.locator(f"[data-winter-film={film}]")
                        trigger.press("Enter")
                        expect(page.locator(".ss-stage")).to_be_visible()
                        film_data = snap(".winter-film", f"stage-{film}")
                        film_data["poster"] = page.locator("[data-story-index]").get_attribute("data-story-index")
                        film_data["layout"] = page.locator(".ss-stage").get_attribute("data-layout")
                        page.keyboard.press("Escape")
                        film_data["close_focus"] = trigger.evaluate("el => el === document.activeElement")

                snap("#itinerary", "itinerary")
                days = page.locator(".day")
                days.evaluate_all("els => els.forEach(day => day.open = true)")
                expanded = snap(".itinerary-layout", "itinerary-expanded")
                expanded["expanded_days"] = days.count()
                days.evaluate_all("els => els.forEach((day, index) => day.open = index === 0)")

                gallery = snap("#photos", "photos")
                gallery["photos"] = page.locator("#gallery .gallery-tools .small").inner_text()
                trigger = page.locator("[data-photo-open]")
                trigger.press("Enter")
                expect(page.locator("dialog")).to_be_visible()
                before = page.locator("dialog .gallery-tools .small").inner_text()
                page.keyboard.press("ArrowRight")
                after = page.locator("dialog .gallery-tools .small").inner_text()
                photo = snap("dialog", "photo-dialog")
                photo.update({"previous_slide": before, "current_slide": after})
                photo["inner_scroll"] = page.locator("dialog").evaluate("el => [el.scrollWidth-el.clientWidth, el.scrollHeight-el.clientHeight]")
                page.keyboard.press("Escape")
                photo["close_focus"] = trigger.evaluate("el => el === document.activeElement")
                ending = snap(".chapter-end", "end")
                ending["next"] = page.locator("[data-next-city]").get_attribute("data-next-city")
                device["cities"].append(city_data)
                print(f"{width} x {height} {city}: {len(city_data['states'])} states, {len(errors)} errors", flush=True)
            report["viewports"].append(device)
            context.close()
        browser.close()
    with gzip.open(output / "chapter-measurements.json.gz", "wt", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
