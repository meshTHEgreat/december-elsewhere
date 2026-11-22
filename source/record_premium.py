"""Capture the cover, chapter index, five chapters and two actual interactions."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from playwright.sync_api import expect, sync_playwright


def sheet(inputs, destination, size=(360, 225)):
    columns = 3
    rows = (len(inputs) + columns - 1) // columns
    w, h = size
    canvas = Image.new("RGB", (columns * w, rows * (h + 24)), "#101d19")
    ink = ImageDraw.Draw(canvas)
    for index, (name, path) in enumerate(inputs):
        x, y = index % columns * w, index // columns * (h + 24)
        with Image.open(path) as original:
            frame = ImageOps.contain(original.convert("RGB"), size)
            canvas.paste(frame, (x + (w - frame.width) // 2, y))
        ink.text((x + 9, y + h + 4), name, fill="#fffaf0")
    canvas.save(destination, quality=87, optimize=True)


def capture(browser, url, output, width, height):
    scratch = output / f"frames-{width}"
    scratch.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(viewport={"width": width, "height": height}, has_touch=width < 500,
                                  is_mobile=width < 500, record_video_dir=scratch,
                                  record_video_size={"width": width, "height": height})
    page = context.new_page()
    recording = page.video
    page.goto(url)
    page.evaluate("document.fonts.ready")
    page.locator(".hero img").evaluate("image => image.decode()")
    page.wait_for_timeout(850)
    cover = scratch / "cover.png"
    page.screenshot(path=cover)
    page.locator(".hero .cover-action").click()
    page.wait_for_timeout(350)
    atlas = scratch / "atlas.png"
    page.screenshot(path=atlas)
    page.locator("#atlas-toggle").click()
    expect(page.locator("#atlas-globe canvas")).to_be_visible()
    page.locator("#atlas-select").select_option("prague")
    page.wait_for_timeout(700)
    globe = scratch / "globe.png"
    page.screenshot(path=globe)
    page.locator("[data-open-preview]").click()
    page.wait_for_timeout(900)
    page.locator("#walk").evaluate("(walk) => walk.scrollIntoView()")
    page.wait_for_timeout(300)
    if width < 500:
        page.locator("#route-select").select_option(index=1)
    else:
        page.locator("[data-route='1']").click()
    page.wait_for_timeout(950)
    route = scratch / "route.png"
    page.screenshot(path=route)
    context.close()
    recording.save_as(output / f"atlas-and-walk-{width}.webm")

    context = browser.new_context(viewport={"width": width, "height": height},
                                  is_mobile=width < 500, has_touch=width < 500)
    page = context.new_page()
    page.goto(url)
    page.evaluate("document.fonts.ready")
    stills = [("Opening", cover), ("Destination atlas", atlas), ("Three.js globe", globe), ("A walk in Prague", route)]
    for city in ("baku", "tbilisi", "budapest", "vienna", "prague"):
        page.locator(f".city-tab[data-city='{city}']").click()
        page.wait_for_timeout(850)
        expect(page.locator(".chapter img")).to_have_class("backdrop is-ready")
        frame = scratch / f"chapter-{city}.png"
        page.screenshot(path=frame)
        stills.append((city.title(), frame))
    sheet(stills, output / f"chapter-contact-{width}.jpg",
          (360, 225) if width > 500 else (180, 390))
    page.locator("#walk").evaluate("(walk) => walk.scrollIntoView()")
    if width < 500:
        page.locator("#route-select").select_option(index=1)
    else:
        page.locator("[data-route='1']").click()
    page.locator(".active-route").evaluate("""line => {
        const drawing = line.getAnimations()[0];
        drawing.pause();
        drawing.currentTime = 0;
    }""")
    frames = []
    for ms in (0, 80, 160, 320, 520, 780):
        page.locator(".active-route").evaluate("(line, time) => line.getAnimations()[0].currentTime = time", ms)
        frame = scratch / f"route-{ms}.png"
        page.locator(".mapbox").screenshot(path=frame)
        frames.append((f"{ms} ms", frame))
    sheet(frames, output / f"route-motion-{width}.jpg", (360, 210) if width > 500 else (220, 130))
    context.close()


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("url")
parser.add_argument("output", type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
with sync_playwright() as runner:
    chrome = runner.chromium.launch(channel="chrome")
    capture(chrome, args.url, args.output, 1440, 900)
    capture(chrome, args.url, args.output, 390, 844)
    chrome.close()
