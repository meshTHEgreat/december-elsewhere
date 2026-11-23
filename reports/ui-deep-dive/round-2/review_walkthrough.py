"""Review live transitions and representative trip-planning screens in Chrome."""

import hashlib
import json
import sys
import time

from playwright.sync_api import expect, sync_playwright

from review_photos import FRAME, HASHES, HERE, ROOT, COUNTS, record_network


STORIES = {"baku": ("Baku", "Shahdag", "Tufandag"),
           "overview": ("Baku", "Tbilisi", "Budapest", "Vienna", "Prague")}


def visit(page, url, fragment=""):
    page.goto(url + fragment, wait_until="domcontentloaded")
    page.evaluate("document.fonts.ready")
    page.evaluate(FRAME)


def shot(page, edition, name):
    page.screenshot(path=HERE / f"{edition}-{name}.jpg", type="jpeg", quality=86)


def story(page, edition, width, mode, reduced):
    trigger = page.locator(f"[data-winter-film={mode}]")
    trigger.tap()
    start = time.monotonic()
    panel = page.locator("#winter-film")
    stage = panel.locator(".ss-stage")
    close = panel.get_by_role("button", name="Close preview")
    expect(close).to_be_focused()
    headline = stage.locator(".wf-story-beat[data-current=yes] h3")
    titles = STORIES[mode]
    result = {"reduced_motion": reduced, "natural_scenes": [], "manual_scenes": []}
    if reduced:
        expect(headline).to_have_text(titles[-1])
        stage.locator("img[data-current=yes]").evaluate("img => img.decode()")
        page.evaluate(FRAME)
        result["poster"] = titles[-1]
        if mode == "baku":
            shot(page, edition, f"stage-poster-{width}")
    else:
        for index, title in enumerate(titles):
            expect(headline).to_have_text(title, timeout=6500)
            stage.locator("img[data-current=yes]").evaluate("img => img.decode()")
            result["natural_scenes"].append([title, round(time.monotonic() - start, 3)])
            if index == 1:
                page.wait_for_timeout(600)
                shot(page, edition, f"stage-{mode}-moving-{width}")
    for title in titles:
        button = panel.get_by_role("button", name=title, exact=True)
        button.press("Enter")
        expect(headline).to_have_text(title)
        expect(button).to_have_attribute("aria-pressed", "true")
        stage.locator("img[data-current=yes]").evaluate("img => img.decode()")
        boxes = headline.evaluate("""heading => {
            const box = node => node.getBoundingClientRect().toJSON();
            return [box(heading.parentElement.querySelector('.wf-story-detail')),
                    box(heading.closest('.wf-story-editorial').querySelector('.wf-story-track')),
                    box(heading.closest('.ss-stage'))];
        }""")
        detail, timetable, scene = boxes
        assert detail['bottom'] <= timetable['top'] and timetable['bottom'] <= scene['bottom'], (title, boxes)
        result["manual_scenes"].append({"title": title, "detail_bottom": detail['bottom'],
                                        "track_top": timetable['top'], "scene_bottom": scene['bottom']})
    if not reduced:
        panel.get_by_role("button", name=titles[0], exact=True).tap()
        page.wait_for_timeout(3500)
        expect(headline).to_have_text(titles[0])
        result["manual_pauses_playback"] = True
    page.keyboard.press("Escape")
    expect(panel).to_be_hidden()
    expect(trigger).to_be_focused()
    return result


def mobile_extras(page, url, edition, width):
    height = page.viewport_size["height"]
    menus = {}
    visit(page, url)
    page.get_by_role("link", name="Explore cities").tap()
    page.get_by_role("link", name="Map & globe").press("Enter")
    expect(page.locator("#atlas-panel")).to_be_focused()
    expect(page.locator("#atlas-flat svg")).to_be_visible()
    page.locator("#atlas-toggle").tap()
    expect(page.locator("#atlas-globe canvas")).to_be_visible()
    shot(page, edition, f"globe-{width}")
    page.locator("#atlas-select").select_option("vienna")
    page.locator("#atlas-open").tap()
    expect(page.locator("#chapter h2")).to_have_text("Vienna")
    expect(page.locator("#chapter h2")).to_be_focused()
    for city in COUNTS:
        page.locator(f".city-tab[data-city={city}]").tap()
        summary = page.locator(".chapter-menu summary")
        summary.press("Enter")
        page.evaluate(FRAME)
        links = page.locator(".chapter-menu a").evaluate_all("links => links.map(link => link.getBoundingClientRect().toJSON())")
        assert len(links) == 7 and all(0 <= link['left'] < link['right'] <= width and
                                      0 <= link['top'] < link['bottom'] <= height for link in links), (city, links)
        menus[city] = links
        page.locator(".chapter-menu a[data-jump=stays]").press("Enter")
        expect(page.locator("#stays h2")).to_be_focused()
        if city == "baku" and width == 390:
            shot(page, edition, "stays-390")
    if width == 390:
        visit(page, url, "#baku/walk")
        page.locator("#route-select").select_option(index=1)
        page.locator(".walk-basemap").evaluate("image => image.decode()")
        shot(page, edition, "walk-390")
        visit(page, url, "#baku/budget")
        page.locator(".car-costs summary").press("Enter")
        for field in page.locator("#budget [data-cost]").all():
            field.fill("150000")
        expect(page.locator("#total-person")).to_have_text("SAR 1,400,000")
        expect(page.locator("#total-group")).to_have_text("SAR 4,200,000")
        page.locator("#cost-bags").focus()
        page.evaluate(FRAME)
        shot(page, edition, "budget-390")
        visit(page, url, "#compare")
        page.locator("#left-city").select_option("prague")
        page.locator("#right-city").select_option("vienna")
        page.locator(".compare-details summary").press("Enter")
        assert page.locator(".compare-scroll").evaluate("el => el.scrollWidth === el.clientWidth")
        shot(page, edition, "compare-390")
    return menus


def inspect(browser, url, edition, width, height):
    mobile = width <= 667
    reduced = width != 390
    context = browser.new_context(offline=edition == "offline", locale="en-US", has_touch=mobile,
                                  is_mobile=mobile, viewport={"width": width, "height": height},
                                  reduced_motion="reduce" if reduced else "no-preference")
    page = context.new_page()
    page.set_default_timeout(7000)
    row = {"viewport": [width, height], "http": [], "errors": []}
    record_network(page, row)
    if mobile:
        row["menus"] = mobile_extras(page, url, edition, width)
    if width in (1440, 2560):
        visit(page, url)
        shot(page, edition, f"cover-{width}")
        visit(page, url, "#prague/intro")
        shot(page, edition, f"arrival-{width}")
    if width in (390, 667):
        visit(page, url, "#baku/winter")
        row["stories"] = {mode: story(page, edition, width, mode, reduced) for mode in STORIES}
    if width == 320:
        visit(page, url, "#prague/itinerary")
        before = page.locator(".day[open]").count()
        day_count = page.locator(".day").count()
        page.evaluate("""() => {
            window.printEvents = [];
            for (const label of ['beforeprint', 'afterprint']) window.addEventListener(label, () => {
                window.printEvents.push([label, document.querySelectorAll('.day[open]').length]);
            });
        }""")
        pdf = page.pdf(format="A4")
        events = page.evaluate("window.printEvents")
        assert pdf.startswith(b"%PDF-") and events == [["beforeprint", day_count], ["afterprint", before]], events
        row["print"] = {"pdf_bytes": len(pdf), "events": events}
        if edition == "online":
            with page.expect_download() as event:
                page.locator(".footer a[download]").tap()
            download = event.value
            row["standalone_download_sha256"] = hashlib.sha256(download.path().read_bytes()).hexdigest()
            assert row["standalone_download_sha256"] == HASHES["offline"], row
            download.delete()
    assert not row["errors"], row["errors"]
    assert edition != "offline" or not row["http"], row["http"]
    context.close()
    return row


def main(edition):
    url = "http://127.0.0.1:18768/" if edition == "online" else (ROOT / "index.html").as_uri()
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel="chrome", downloads_path=HERE / "browser-downloads")
        output = {"url": url, "browser": browser.version, "results": []}
        for width, height in [(320, 725), (390, 844), (667, 375), (1440, 900), (2560, 1440)]:
            output["results"].append(inspect(browser, url, edition, width, height))
            (HERE / f"walkthrough-{edition}.json").write_text(json.dumps(output, separators=(",", ":")) + "\n",
                                                               encoding="utf-8")
            print(f"{edition} {width}x{height}: walkthrough passed", flush=True)
        browser.close()


if __name__ == '__main__':
    main(sys.argv[1])
