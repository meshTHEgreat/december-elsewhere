"""Record independent touch, keyboard, geometry and print checks for this candidate."""
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SIZES = [(320, 725), (390, 844), (667, 375)]
CITIES = {"baku": "Baku", "tbilisi": "Tbilisi", "budapest": "Budapest", "vienna": "Vienna", "prague": "Prague"}
STAGES = {"baku": ["Baku", "Shahdag", "Tufandag"], "overview": list(CITIES.values())}
FRAME = "() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))"
RECT = "node => {const {x,y,width,height,bottom,right} = node.getBoundingClientRect(); return {x,y,width,height,bottom,right};}"


def check_phone(browser, url, size, output):
    width, height = size
    offline = url.startswith("file:")
    output = output / str(width)
    output.mkdir(parents=True, exist_ok=True)
    reduced = width != 390
    context = browser.new_context(offline=offline, viewport={"width": width, "height": height},
                                  is_mobile=True, has_touch=True, device_scale_factor=1,
                                  reduced_motion="reduce" if reduced else "no-preference")
    page = context.new_page()
    page.set_default_timeout(6500)
    requests, errors, failures = [], [], []
    page.on("request", lambda request: requests.append(request.url) if request.url.startswith("http") else None)
    page.on("response", lambda response: errors.append(f"{response.status} {response.url}") if response.status >= 400 else None)
    page.on("pageerror", lambda error: errors.append(str(error)))
    data = {"width": width, "height": height, "reduced_motion": reduced, "errors": errors, "failures": failures}

    def visit(hash_value=""):
        page.goto(url + hash_value, wait_until="domcontentloaded")
        page.evaluate("document.fonts.ready")
        page.evaluate(FRAME)

    def shot(name):
        page.screenshot(path=output / f"{name}.jpg", type="jpeg", quality=83, scale="css")

    def bounds(selector):
        return page.locator(selector).evaluate(RECT)

    def check(label, condition, observed):
        if not condition:
            failures.append({"check": label, "observed": observed})

    visit()
    shot("cover")
    page.get_by_role("link", name="Explore cities").tap()
    page.wait_for_timeout(550 if not reduced else 50)
    shot("cities")
    page.get_by_role("link", name="Map & globe").press("Enter")
    expect(page.locator("#atlas-panel")).to_be_focused()
    expect(page.locator("#atlas-flat svg")).to_be_visible()
    shot("atlas-flat")
    page.locator("#atlas-toggle").tap()
    expect(page.locator("#atlas-globe canvas")).to_be_visible()
    page.locator("#atlas-select").select_option("vienna")
    expect(page.locator(".globe-pin.is-active")).to_have_text("Vienna")
    data["atlas"] = {"map": bounds("#atlas-visual"), "open": bounds("#atlas-open"), "mast": bounds(".mast")}
    shot("atlas-globe")
    page.locator("#atlas-open").tap()
    expect(page.locator("#chapter h2")).to_have_text("Vienna")
    expect(page.locator("#chapter h2")).to_be_focused()
    expect(page.locator("#atlas-globe canvas")).to_have_count(0)

    data["chapters"] = {}
    for city, title in CITIES.items():
        page.locator(f".city-tab[data-city={city}]").tap()
        expect(page.locator("#chapter h2")).to_have_text(title)
        expect(page.locator("#chapter h2")).to_be_focused()
        page.locator("#chapter img").evaluate("image => image.decode()")
        page.wait_for_timeout(525 if not reduced else 0)
        shot(f"chapter-{city}")
        summary = page.locator(".chapter-menu summary")
        summary.press("Enter")
        menu = page.locator(".chapter-menu")
        expect(menu).to_have_attribute("open", "")
        page.evaluate(FRAME)
        menu_items = menu.locator("a").evaluate_all("nodes=>nodes.map(a=>[a.textContent,a.getBoundingClientRect().toJSON()])")
        check(f"{city} menu", all(0 <= item[1]["top"] and item[1]["bottom"] <= height for item in menu_items), menu_items)
        if city == "baku":
            shot("chapter-menu")
        menu.get_by_role("link", name="Photos").tap()
        expect(page.locator("#photos h2")).to_be_focused()
        expect(summary).to_contain_text("Photos")
        trigger = page.locator("#gallery [data-photo-open]")
        trigger.tap()
        dialog = page.locator("#photo-dialog")
        expect(dialog).to_be_visible()
        expect(dialog.locator("[data-photo-close]")).to_be_focused()
        images = []
        length = int(dialog.locator(".gallery-tools .small").inner_text().split("/")[1])
        for index in range(length):
            image = dialog.locator("img")
            image.evaluate("image => image.decode()")
            metrics = dialog.evaluate("""node => {
              const image = node.querySelector('img'), caption = node.querySelector('figcaption');
              const name = el => el.getAttribute('aria-label') || el.innerText;
              const box = el => el.getBoundingClientRect().toJSON();
              const actions = [...node.querySelectorAll('button, a[download]')];
              return {title: image.alt, dialog: box(node), image: box(image), caption: box(caption),
                      natural: [image.naturalWidth, image.naturalHeight],
                      actions: actions.map(el => ({name: name(el), box: box(el)}))};
            }""")
            images.append(metrics)
            boxes = [metrics["caption"], *(action["box"] for action in metrics["actions"])]
            check(f"{city} photo {index + 1} controls and caption", all(
                box["top"] >= 0 and box["bottom"] <= height and box["left"] >= 0 and box["right"] <= width for box in boxes
            ), metrics)
            if index == 0 or any(box["bottom"] > height or box["top"] < 0 for box in boxes):
                shot(f"photo-{city}-{index+1}")
            dialog.press("ArrowRight")
        page.keyboard.press("Escape")
        expect(dialog).to_be_hidden()
        expect(trigger).to_be_focused()
        data["chapters"][city] = {"menu_items": menu_items, "photo_count": length, "photos": images}

    visit("#baku/budget")
    page.locator(".car-costs summary").press("Enter")
    data["budget"] = []
    fields = page.locator("#budget [data-cost]").all()
    for field in fields:
        field.fill("150000")
    expect(page.locator("#total-person")).to_have_text("SAR 1,400,000")
    expect(page.locator("#total-group")).to_have_text("SAR 4,200,000")
    fields[0].focus()
    for selector in ["#budget [data-cost]", "#budget summary", "#budget button"]:
        for control in page.locator(selector).all():
            control.focus()
            page.evaluate(FRAME)
            observed = control.evaluate("""node => {
              const rect = node.getBoundingClientRect();
              const x = (rect.left + rect.right) / 2;
              const hit = y => {
                const el = document.elementFromPoint(x, y);
                return el === node || node.contains(el);
              };
              return {control: node.id || node.textContent.trim(), top: rect.top, bottom: rect.bottom,
                      topHit: hit(rect.top + 2), bottomHit: hit(rect.bottom - 2)};
            }""")
            data["budget"].append(observed)
            check("budget focused control shows full hit area", observed["topHit"] and observed["bottomHit"], observed)
    page.locator("#cost-bags").focus()
    page.evaluate(FRAME)
    shot("budget-edited-focus")
    page.locator("[data-reset]").press("Enter")
    expect(page.locator("[data-reset]")).to_be_focused()
    expect(page.locator("#cost-bags")).not_to_have_value("150000")

    visit("#baku/walk")
    page.locator("#route-select").select_option(index=1)
    page.locator(".walk-basemap").evaluate("image => image.decode()")
    shot("walk-satellite")
    points = page.locator(".active-route").get_attribute("points")
    page.locator("[data-walk-style=diagram]").tap()
    expect(page.locator(".walk-basemap")).to_be_hidden()
    expect(page.locator(".active-route")).to_have_attribute("points", points)
    shot("walk-diagram")

    data["stages"] = {}
    visit("#baku/winter")
    for presentation, names in STAGES.items():
        trigger = page.locator(f"[data-winter-film={presentation}]")
        trigger.tap()
        close = page.locator("[data-winter-close]")
        expect(close).to_be_focused()
        stage = page.locator(".ss-stage")
        beat = stage.locator(".wf-story-beat[data-current=yes] h3")
        expect(beat).to_have_text(names[-1] if reduced else names[0])
        page.wait_for_timeout(600 if not reduced else 0)
        data["stages"][presentation] = {"initial": bounds(".ss-stage"), "scenes": []}
        shot(f"stage-{presentation}-open")
        if not reduced:
            expect(beat).to_have_text(names[1], timeout=6500)
        for index, name in enumerate(names):
            control = page.get_by_role("button", name=name, exact=True).and_(page.locator(".wf-scene-button"))
            control.tap()
            expect(beat).to_have_text(name)
            expect(control).to_have_attribute("aria-pressed", "true")
            stage.locator("img[data-current=yes]").evaluate("image => image.decode()")
            page.wait_for_timeout(390 if not reduced else 0)
            detail = bounds(".wf-story-beat[data-current=yes] .wf-story-detail")
            track = bounds(".wf-story-track")
            stage_box = bounds(".ss-stage")
            check(f"{presentation} {name} detail fits", detail["bottom"] < track["y"] and track["bottom"] < stage_box["bottom"],
                  {"detail": detail, "track": track, "stage": stage_box})
            data["stages"][presentation]["scenes"].append({"name": name, "detail": detail, "track": track, "stage": stage_box})
            if index == 0 or width == 667:
                shot(f"stage-{presentation}-{index+1}")
        if not reduced:
            page.locator(".wf-scene-button").first.press("Enter")
            expect(beat).to_have_text(names[0])
            page.wait_for_timeout(3650)
            expect(beat).to_have_text(names[0])
        page.keyboard.press("Escape")
        expect(stage).to_have_count(0)
        expect(trigger).to_be_focused()

    visit("#compare")
    page.locator("#left-city").select_option("vienna")
    page.locator("#right-city").select_option("prague")
    page.locator(".compare-details summary").press("Enter")
    shot("compare")
    scroll = page.locator(".compare-scroll").evaluate("element => element.scrollWidth - element.clientWidth")
    check("compare fits", scroll == 0, scroll)
    page.locator("#photos-credit summary").press("Enter")
    page.locator("#photos-credit summary").evaluate("node => node.scrollIntoView({block:'center'})")
    shot("sources")

    visit("#prague/budget")
    before = page.locator(".day[open]").count()
    days = page.locator(".day").count()
    page.evaluate("""() => {
      window.printProbe = [];
      for (const type of ['beforeprint', 'afterprint']) {
        window.addEventListener(type, () => window.printProbe.push([type, document.querySelectorAll('.day[open]').length]));
      }
    }""")
    pdf = page.pdf(format="A4")
    data["pdf"] = {"bytes": len(pdf), "events": page.evaluate("window.printProbe")}
    check("print expands every day and restores current state", pdf.startswith(b"%PDF-") and
          data["pdf"]["events"] == [["beforeprint", days], ["afterprint", before]], data["pdf"])
    if not offline and width == 320:
        with page.expect_download() as event:
            page.locator(".footer a[download]").tap()
        data["download"] = hashlib.sha256(event.value.path().read_bytes()).hexdigest()
        check("hosted download equals standalone", data["download"] == hashlib.sha256((ROOT / "index.html").read_bytes()).hexdigest(),
              data["download"])
    check("no runtime or HTTP errors", not errors, errors)
    if offline:
        check("offline never requests HTTP(S)", not requests, requests)
    else:
        check("online requests only same origin", {urlsplit(request).netloc for request in requests} == {urlsplit(url).netloc}, requests)
    data["http_requests"] = len(requests)
    data["viewport_overflow"] = page.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("document fits", data["viewport_overflow"] == 0, data["viewport_overflow"])
    context.close()
    return data


def main(edition):
    url = "http://127.0.0.1:18768/" if edition == "online" else (ROOT / "index.html").as_uri()
    output = HERE / f"mobile-{edition}"
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel="chrome")
        report = {"url": url, "browser": browser.version, "results": []}
        for size in SIZES:
            report["results"].append(check_phone(browser, url, size, output))
            (HERE / f"mobile-{edition}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            result = report["results"][-1]
            print(size, "failures:", [(failure["check"], failure["observed"]) for failure in result["failures"]], flush=True)
        browser.close()
    return int(any(result["failures"] for result in report["results"]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
