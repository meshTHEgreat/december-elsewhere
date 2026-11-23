"""Independent Edge release inspection for December, Elsewhere."""

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SIZES = ((320, 725), (390, 844), (667, 375), (768, 1024), (1440, 900), (2560, 1440))
CITIES = ("baku", "tbilisi", "budapest", "vienna", "prague")
STORIES = {"baku": ("Baku", "Shahdag", "Tufandag"),
           "overview": ("Baku", "Tbilisi", "Budapest", "Vienna", "Prague")}
CONTROL_BOXES = """nodes => nodes.map(node => {
  const r = node.getBoundingClientRect();
  const view = visualViewport;
  const hits = [r.left + 2, (r.left + r.right) / 2, r.right - 2].every(x =>
    [r.top + 2, (r.top + r.bottom) / 2, r.bottom - 2].every(y =>
      node.contains(document.elementFromPoint(x,y))));
  return { name: node.getAttribute('aria-label') || node.textContent.trim(),
    width: r.width, height: r.height, clearance: Math.min(r.left, r.top,
    view.width - r.right, view.height - r.bottom), hits };
})"""


def monitored(context):
    page = context.new_page()
    page.set_default_timeout(7000)
    observations = {"requests": [], "failures": [], "warnings": []}
    page.on("request", lambda request: observations["requests"].append(request.url)
            if urlparse(request.url).scheme in ("http", "https") else None)
    page.on("requestfailed", lambda request: observations["failures"].append(
        {"url": request.url, "failure": request.failure}) if urlparse(request.url).scheme in ("http", "https") else None)
    page.on("response", lambda response: observations["failures"].append(
        {"url": response.url, "status": response.status}) if response.status >= 400 else None)
    page.on("pageerror", lambda error: observations["failures"].append(str(error)))
    page.on("console", lambda event: observations["failures" if event.type == "error" else "warnings"].append(event.text)
            if event.type in ("error", "warning") else None)
    return page, observations


def visit(page, url, fragment=""):
    page.goto(url + fragment, wait_until="domcontentloaded")
    page.evaluate("document.fonts.ready")


def settle(page):
    page.evaluate("new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")


def shot(page, name):
    page.screenshot(path=HERE / f"{name}.jpg", type="jpeg", quality=88)


def numeric(text):
    return int("".join(character for character in text if character.isdigit()))


def inspect_size(browser, url, width, height):
    offline = url.startswith("file:")
    compact = width <= 667
    context = browser.new_context(viewport={"width": width, "height": height}, is_mobile=compact,
                                  has_touch=compact, reduced_motion="reduce", offline=offline)
    page, traffic = monitored(context)
    evidence = {"viewport": [width, height]}
    capture = not offline

    visit(page, url)
    assert page.locator("html").evaluate("node=>getComputedStyle(node).direction") == "ltr"
    page.keyboard.press("Tab")
    expect(page.get_by_role("link", name="Skip to guide")).to_be_focused()
    assert page.locator(".mast nav a").evaluate_all("nodes => nodes.every(n => n.offsetWidth >= 44 && n.offsetHeight >= 44)")
    assert page.locator(".hero img").evaluate("async node => {await node.decode(); return node.naturalWidth}")
    if capture and width == 390:
        shot(page, "390-cover")

    visit(page, url, "#baku/budget")
    person = page.locator("#total-person")
    group = page.locator("#total-group")
    evidence["budget_amount_tops"] = [node.bounding_box()["y"] for node in (person, group)]
    if compact:
        assert abs(evidence["budget_amount_tops"][0] - evidence["budget_amount_tops"][1]) <= 1
    bag = page.locator("#cost-bags")
    bag.focus()
    bag.evaluate("node=>node.scrollIntoView({block:'start'})")
    page.keyboard.press("Tab")
    settle(page)
    evidence["budget_focus"] = page.evaluate("""() => {
      const focus = document.activeElement;
      const r = focus.getBoundingClientRect();
      return { id: focus.id, y: r.top, bottom: r.bottom,
        hit: focus.contains(document.elementFromPoint((r.left + r.right) / 2, r.top + 2)) };
    }""")
    assert evidence["budget_focus"]["hit"] and evidence["budget_focus"]["id"].startswith("cost-")
    if capture and width == 320:
        shot(page, "320-budget-keyboard")
    initial = numeric(group.inner_text())
    food = page.locator("#cost-food")
    edit = str(int(food.input_value()) + 37)
    food.fill(edit)
    assert numeric(group.inner_text()) == initial + 111
    if compact:
        visit(page, url, "#baku/budget")
        menu = page.locator(".chapter-menu summary")
        expect(menu).to_contain_text("Budget")
        menu.tap()
        settle(page)
        entries = page.locator(".chapter-menu a").evaluate_all(CONTROL_BOXES)
        assert len(entries) == 7 and all(row["hits"] and row["clearance"] >= -0.5 for row in entries), entries
        evidence["menu_min_edge"] = min(row["clearance"] for row in entries)
        page.locator(".chapter-menu a[data-jump=stays]").tap()
    else:
        page.locator(".chapter-jumps a[data-jump=stays]").press("Enter")
    expect(page.locator("#stays h2")).to_be_focused()
    assert page.url.endswith("#baku/stays")
    stay = page.locator("[data-stay='1']")
    stay.tap() if compact else stay.press("Enter")
    expect(stay).to_have_attribute("aria-pressed", "true")
    assert page.locator("#cost-stay").input_value() != "0"
    evidence["stay_actions_before_notes"] = page.locator(".stay").evaluate_all("nodes=>nodes.every(n=>n.querySelector('.stay-cta').compareDocumentPosition(n.querySelector('.stay-notes'))===4)")
    assert evidence["stay_actions_before_notes"]
    if capture and width == 390:
        shot(page, "390-stay-selected")

    visit(page, url, "#baku/walk")
    anchor = page.locator("#anchor-select")
    anchor.select_option(index=1)
    expect(anchor).to_be_focused()
    if compact:
        picker = page.locator("#route-select")
        picker.select_option(index=1)
        expect(picker).to_be_focused()
        expect(page.locator("#route-note strong")).to_contain_text(picker.locator("option:checked").inner_text())
        assert page.locator(".walk-list-disclosure").get_attribute("open") is None
        page.locator(".walk-list-disclosure summary").tap()
    route = page.locator("[data-route='2']")
    route.tap() if compact else route.press("Enter")
    expect(route).to_be_focused()
    expect(route).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#route-note strong")).to_have_text(route.locator("strong").inner_text())
    active_route = page.locator(".active-route").get_attribute("points")
    page.locator("[data-walk-style=diagram]").press("Enter")
    expect(page.locator(".walk-basemap")).to_be_hidden()
    page.locator("[data-walk-style=satellite]").press("Enter")
    expect(page.locator(".walk-basemap")).to_be_visible()
    assert page.locator(".walk-basemap").evaluate("async node=>{await node.decode();return node.naturalWidth}") >= 260
    expect(page.locator(".active-route")).to_have_attribute("points", active_route)
    if width == 667:
        page.locator("#route-select").select_option(index=0)
        evidence["landscape_walk_box"] = page.locator(".mapbox").bounding_box()
        box = evidence["landscape_walk_box"]
        assert box["y"] >= page.locator(".city-subnav").evaluate("node=>node.getBoundingClientRect().bottom") - 1
        assert box["y"] + box["height"] <= height + 1
        if capture:
            shot(page, "667-walk")

    visit(page, url, "#baku/itinerary")
    day = page.locator(".day").last
    day.locator("summary").press("Enter")
    expect(day.locator(".stops")).to_be_visible()
    assert page.locator(".day[open]").count() == 2
    if width == 1440:
        page.evaluate("""() => {
          window.printTest = [];
          for (const name of ['beforeprint', 'afterprint']) {
            addEventListener(name, () => printTest.push([name, document.querySelectorAll('.day[open]').length]));
          }
        }""")
        proof = page.pdf(format="A4")
        evidence["print"] = {"bytes": len(proof), "day_states": page.evaluate("printTest")}
        assert proof.startswith(b"%PDF-") and len(proof) > 20000
        assert evidence["print"]["day_states"] == [["beforeprint", page.locator(".day").count()], ["afterprint", 2]]

    for mode, scenes in STORIES.items():
        visit(page, url, "#baku/winter")
        trigger = page.locator(f"[data-winter-film={mode}]")
        trigger.tap() if compact else trigger.press("Enter")
        close = page.get_by_role("button", name="Close preview")
        expect(close).to_be_focused()
        stage = page.locator("#winter-film .ss-stage")
        expect(stage).to_be_visible()
        evidence[f"{mode}_stage"] = stage.bounding_box()
        expect(stage.locator(".wf-story-beat[data-current=yes] h3")).to_have_text(scenes[-1])
        for title in scenes:
            scene = page.locator("#winter-film").get_by_role("button", name=title, exact=True)
            scene.press("Enter")
            expect(scene).to_have_attribute("aria-pressed", "true")
            expect(stage.locator(".wf-story-beat[data-current=yes] h3")).to_have_text(title)
            assert scene.bounding_box()["height"] >= 44
        assert stage.evaluate("stage=>stage.getAnimations({subtree:true}).length") == 0
        if width == 667:
            box = stage.bounding_box()
            assert box["y"] >= 0 and box["y"] + box["height"] <= height + 1
            if capture:
                shot(page, f"667-preview-{mode}")
        page.keyboard.press("Escape")
        expect(stage).to_have_count(0)
        expect(trigger).to_be_focused()

    visit(page, url, "#destinations")
    city_geometry = page.locator(".city-tab").evaluate_all("""nodes => nodes.map(row => {
      const name = row.querySelector('.city-name').getBoundingClientRect();
      const price = row.querySelector('[id^=pick-price]').getBoundingClientRect();
      return [name.left, price.right];
    })""")
    evidence["city_rail_spread"] = [max(values) - min(values) for values in zip(*city_geometry)]
    assert max(evidence["city_rail_spread"]) <= 1
    if compact:
        page.get_by_role("link", name="Map & globe").press("Enter")
        expect(page.locator("#atlas-panel")).to_be_focused()
        page.keyboard.press("Tab")
        expect(page.locator("#atlas-select")).to_be_focused()
    page.locator("#atlas-select").select_option("prague")
    page.locator("#atlas-toggle").press("Enter")
    canvas = page.locator("#atlas-globe canvas")
    expect(canvas).to_be_visible()
    expect(page.locator(".globe-pin.is-active")).to_have_text("Prague")
    evidence["globe_visual"] = page.locator("#atlas-visual").bounding_box()
    if width == 667:
        rect = evidence["globe_visual"]
        assert rect["y"] >= page.locator(".mast").evaluate("node=>node.getBoundingClientRect().bottom") - 1
        assert rect["y"] + rect["height"] <= height + 1
        if capture:
            shot(page, "667-webgl")
    if width in (390, 667):
        canvas.evaluate("node=>node.dispatchEvent(new Event('webglcontextlost',{cancelable:true}))")
        expect(page.locator("#atlas-flat svg")).to_be_visible()
        expect(page.locator("#atlas-feedback")).to_contain_text("Globe stopped")
        expect(page.locator("#atlas-distance")).to_have_text("3,580 km direct")
    page.locator("#atlas-open").press("Enter")
    expect(page.locator("#chapter h2")).to_have_text("Prague")
    expect(page.locator("#chapter h2")).to_be_focused()

    visit(page, url, "#compare")
    select = page.locator("#left-city")
    select.select_option("baku")
    expect(select).to_be_focused()
    page.locator("#right-city").select_option("vienna")
    expect(page.locator("#compare-mark-value-0")).to_have_text(page.locator("#compare-0-person").inner_text())
    evidence["comparison_scroll_px"] = page.locator(".compare-scroll").evaluate("node=>node.scrollWidth-node.clientWidth")
    assert evidence["comparison_scroll_px"] <= 1
    page.locator(".compare-details summary").press("Enter")
    page.locator("#evidence details summary").first.press("Enter")
    assert page.locator(".source-action:visible").evaluate_all("nodes=>nodes.length && nodes.every(n=>n.offsetWidth>=44&&n.offsetHeight>=44)")
    if capture and width == 2560:
        visit(page, url, "#compare")
        shot(page, "2560-comparison")
    evidence["document_overflow_px"] = page.evaluate("document.documentElement.scrollWidth-innerWidth")
    assert evidence["document_overflow_px"] <= 1

    expected_origin = urlparse(url).netloc
    assert set(urlparse(request).netloc for request in traffic["requests"]) <= ({expected_origin} if not offline else set())
    assert not traffic["failures"], traffic["failures"]
    evidence["traffic"] = {"requests": len(traffic["requests"]), "failures": traffic["failures"],
                           "warnings": sorted(set(traffic["warnings"]))}
    context.close()
    return evidence


def first_open_photo(browser, url):
    offline = url.startswith("file:")
    context = browser.new_context(viewport={"width": 667, "height": 375}, has_touch=True, is_mobile=True,
                                  offline=offline, reduced_motion="reduce", accept_downloads=True)
    page, traffic = monitored(context)
    recorded = []
    for city in CITIES:
        visit(page, url, f"#{city}/photos")
        viewer = page.locator("#photo-dialog")
        opener = page.locator("#gallery [data-photo-open]")
        total = int(page.locator("#gallery .gallery-tools .small").inner_text().split("/")[1])
        for index in range(total):
            opener.tap()
            expect(viewer.locator("[data-photo-close]")).to_be_focused()
            image = viewer.locator("img")
            native = image.evaluate("async node => {await node.decode(); return [node.naturalWidth,node.naturalHeight];}")
            expect(viewer.locator(".gallery-tools .small")).to_have_text(f"{index + 1} / {total}")
            controls = viewer.locator("[data-photo-close], [data-gallery], .photo-download").evaluate_all(CONTROL_BOXES)
            assert len(controls) == 4
            assert all(row["hits"] and row["clearance"] >= -0.5 and min(row["width"], row["height"]) >= 44
                       for row in controls), (city, index, controls)
            download = viewer.locator(".photo-download")
            filename = download.get_attribute("download")
            with page.expect_download() as event:
                download.tap()
            artifact = event.value
            assert artifact.suggested_filename == filename
            assert artifact.path().read_bytes() == (ROOT / "assets" / filename).read_bytes()
            figure = viewer.locator(".lightbox-figure").evaluate("node=>({height:node.clientHeight, scroll:node.scrollHeight})")
            recorded.append({"city": city, "index": index + 1, "file": filename, "native": native, "controls": controls, "figure": figure})
            if (city, index) == ("vienna", 0):
                shot(page, f"667-photo-vienna-{'offline' if offline else 'online'}")
            if index % 2:
                viewer.locator("[data-photo-close]").tap()
            else:
                page.keyboard.press("Escape")
            expect(opener).to_be_focused()
            page.locator("#gallery [data-gallery='1']").tap()
    assert len(recorded) == 24 and not traffic["failures"], traffic["failures"]
    if offline:
        assert not traffic["requests"], traffic["requests"]
    context.close()
    return recorded


def failure_states(browser, url):
    offline = url.startswith("file:")
    context = browser.new_context(offline=offline, viewport={"width": 667, "height": 375}, reduced_motion="reduce")
    context.add_init_script("""const context = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, ...args) {
      return type.startsWith('webgl') ? null : context.apply(this, [type, ...args]);
    };""")
    page = context.new_page()
    if not offline:
        page.route("**/media/winter-stage.js", lambda route: route.abort())
    visit(page, url)
    page.locator("#atlas-toggle").press("Enter")
    expect(page.locator("#atlas-feedback")).to_have_text("Globe unavailable. Use the map.")
    expect(page.locator("#atlas-flat svg")).to_be_visible()
    page.locator("#atlas-select").select_option("vienna")
    page.locator("#atlas-open").press("Enter")
    expect(page.locator("#chapter h2")).to_have_text("Vienna")
    visit(page, url, "#baku/winter")
    if offline:
        page.locator("#winter-stage-code").evaluate("node=>{node.textContent='null'}")
    trigger = page.locator("[data-winter-film=baku]")
    trigger.press("Enter")
    expect(trigger).to_be_focused()
    expect(page.locator("#winter-film-message")).to_have_text("Preview unavailable. Read the winter plans above.")
    expect(page.locator("#winter-film")).to_be_hidden()
    expect(page.locator("#winter .winter-route")).to_be_visible()
    context.close()
    return {"webgl_denied": "flat map and chapter navigation", "stage_unavailable": "status and winter plans"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("online", "offline"))
    parser.add_argument("--part", choices=("sizes", "photos", "fallbacks"), required=True)
    args = parser.parse_args()
    url = "http://127.0.0.1:18768/" if args.mode == "online" else (ROOT / "index.html").as_uri()
    if args.mode == "online":
        with urlopen(url) as response:
            delivered = response.read()
        assert delivered == (ROOT / "docs/index.html").read_bytes()
        with urlopen(url + "offline.html") as response:
            assert response.read() == (ROOT / "index.html").read_bytes()
    else:
        delivered = (ROOT / "index.html").read_bytes()
    with sync_playwright() as driver:
        browser = driver.chromium.launch(channel="msedge")
        results = {"browser": browser.version, "url": url, "sha256": hashlib.sha256(delivered).hexdigest()}
        failures = {}
        if args.part == "sizes":
            by_size = results["results"] = {}
            for width, height in SIZES:
                try:
                    by_size[width] = inspect_size(browser, url, width, height)
                except Exception as error:
                    failures[width] = repr(error)
                    print(f"FAIL {width}x{height} {error!r}", flush=True)
                else:
                    print(f"PASS {width}x{height}", flush=True)
        elif args.part == "photos":
            results["results"] = first_open_photo(browser, url)
        else:
            results["results"] = failure_states(browser, url)
        results["failures"] = failures
        browser.close()
    (HERE / f"{args.part}-{args.mode}.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    assert not failures, failures


if __name__ == "__main__":
    main()
