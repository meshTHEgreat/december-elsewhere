"""Measure the initial photo viewer and touch every control in both editions."""

import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SIZES = ((320, 725), (390, 844), (667, 375))
COUNTS = {"baku": 9, "tbilisi": 4, "budapest": 4, "vienna": 3, "prague": 4}
CONTROLS = {"close": "[data-photo-close]", "previous": "[data-gallery='-1']",
            "next": "[data-gallery='1']", "download": ".photo-download"}
FRAME = "() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))"
HASHES = {"online": "d09a0652e7e4c6c3e990420a1f8c675f32c19f29a29b0dabebdad7227f766b71",
          "offline": "93e786ba4833e97cdd9e461fe8afd485617e4d7d0f2cbcbb9c2f00651bc92340"}


def read_geometry(dialog):
    return dialog.evaluate("""(dialog, selectors) => {
        const rect = node => node.getBoundingClientRect().toJSON();
        const image = dialog.querySelector('img');
        const figure = dialog.querySelector('figure');
        const controls = Object.fromEntries(Object.entries(selectors).map(([label, selector]) => {
            const node = dialog.querySelector(selector);
            const box = rect(node);
            const samples = [
                [(box.left + box.right) / 2, (box.top + box.bottom) / 2],
                [box.left + 4, box.top + 4], [box.right - 4, box.top + 4],
                [box.left + 4, box.bottom - 4], [box.right - 4, box.bottom - 4],
            ];
            return [label, {box, samples, hits: samples.map(([x, y]) =>
                node.contains(document.elementFromPoint(x, y)))}];
        }));
        return {title: image.alt, image: rect(image), natural: [image.naturalWidth, image.naturalHeight],
                dialog: rect(dialog), figure: rect(figure), caption: rect(figure.querySelector('figcaption')),
                scroll: [dialog.scrollTop, figure.scrollTop], controls,
                locale: [document.documentElement.lang, getComputedStyle(dialog).direction]};
    }""", CONTROLS)


def fits(box, width, height):
    return 0 <= box["left"] <= box["right"] <= width and 0 <= box["top"] <= box["bottom"] <= height


def record_network(page, row):
    page.on("request", lambda request: row["http"].append(request.url)
            if request.url.startswith(("http:", "https:")) else None)
    page.on("response", lambda response: row["errors"].append(f"{response.status} {response.url}")
            if response.status >= 400 else None)
    page.on("pageerror", lambda error: row["errors"].append(str(error)))
    page.on("console", lambda message: row["errors"].append(message.text) if message.type == "error" else None)


def inspect(browser, url, width, height, edition):
    context = browser.new_context(offline=edition == "offline", locale="en-US",
                                  viewport={"width": width, "height": height}, has_touch=True,
                                  is_mobile=True, device_scale_factor=1, reduced_motion="reduce")
    page = context.new_page()
    page.set_default_timeout(7000)
    row = {"viewport": [width, height], "http": [], "errors": [], "photos": []}
    record_network(page, row)
    page.goto(url, wait_until="domcontentloaded")
    page.evaluate("document.fonts.ready")
    if width != 667:
        page.screenshot(path=HERE / f"{edition}-cover-{width}.jpg", type="jpeg", quality=85)
    for city, count in COUNTS.items():
        page.locator(f".city-tab[data-city='{city}']").tap()
        menu = page.locator(".chapter-menu")
        menu.locator("summary").tap()
        page.evaluate(FRAME)
        menu.locator("a[data-jump=photos]").tap()
        expect(page.locator("#photos h2")).to_be_focused()
        trigger = page.locator("#gallery [data-photo-open]")
        trigger.tap()
        dialog = page.locator("#photo-dialog")
        counter = dialog.locator(".gallery-tools .small")
        for index in range(1, count + 1):
            expect(counter).to_have_text(f"{index} / {count}")
            dialog.locator("img").evaluate("image => image.decode()")
            page.evaluate(FRAME)
            state = read_geometry(dialog)
            state.update(city=city, index=index)
            row["photos"].append(state)
            assert state["locale"] == ["en", "ltr"], state
            assert state["scroll"] == [0, 0], state
            assert fits(state["caption"], width, height), state
            assert state["caption"]["bottom"] <= state["figure"]["bottom"] + 0.5, state
            image, (natural_width, natural_height) = state["image"], state["natural"]
            assert natural_width > 0 and natural_height > 0 and fits(image, width, height), state
            assert abs(image["width"] / image["height"] - natural_width / natural_height) < .02, state
            for control in state["controls"].values():
                box = control["box"]
                assert fits(box, width, height) and box["width"] >= 44 and box["height"] >= 44, state
                assert all(control["hits"]), state
            if width == 667 and city in {"baku", "vienna"} and index == 1:
                page.screenshot(path=HERE / f"{edition}-{city}-667.jpg", type="jpeg", quality=90)

            def touch(label):
                page.touchscreen.tap(*state["controls"][label]["samples"][0])

            if width == 667:
                link = dialog.locator(CONTROLS["download"])
                filename = link.get_attribute("download")
                with page.expect_download() as event:
                    touch("download")
                download = event.value
                data = download.path().read_bytes()
                assert download.suggested_filename == filename and len(data) > 1000, state
                state["download"] = {"filename": filename, "bytes": len(data),
                                     "sha256": hashlib.sha256(data).hexdigest()}
                download.delete()
                touch("previous")
                expect(counter).to_have_text(f"{index - 1 or count} / {count}")
                dialog.locator("img").evaluate("image => image.decode()")
                previous_state = read_geometry(dialog)
                page.touchscreen.tap(*previous_state["controls"]["next"]["samples"][0])
                expect(counter).to_have_text(f"{index} / {count}")
                dialog.locator("img").evaluate("image => image.decode()")
                touch("close")
                expect(dialog).to_be_hidden()
                expect(trigger).to_be_focused()
                trigger.tap()
                expect(counter).to_have_text(f"{index} / {count}")
                dialog.locator("img").evaluate("image => image.decode()")
            touch("next")
            expect(counter).to_have_text(f"{index % count + 1} / {count}")
        page.keyboard.press("Escape")
        expect(dialog).to_be_hidden()
        expect(trigger).to_be_focused()
    assert len(row["photos"]) == 24 and not row["errors"], row["errors"]
    assert all(urlsplit(request).netloc == urlsplit(url).netloc for request in row["http"])
    assert edition != "offline" or not row["http"], row["http"]
    context.close()
    return row


def main(edition):
    url = "http://127.0.0.1:18768/" if edition == "online" else (ROOT / "index.html").as_uri()
    with urlopen(url) as response:
        digest = hashlib.sha256(response.read()).hexdigest()
    assert digest == HASHES[edition], digest
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel="chrome", downloads_path=HERE / "browser-downloads")
        evidence = {"browser": browser.version, "url": url, "sha256": digest, "results": []}
        for width, height in SIZES:
            evidence["results"].append(inspect(browser, url, width, height, edition))
            (HERE / f"photos-{edition}.json").write_text(json.dumps(evidence, separators=(",", ":")) + "\n",
                                                         encoding="utf-8")
            print(f"{edition} {width}x{height}: 24 initial photo states fit and all hit tests passed", flush=True)
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1])
