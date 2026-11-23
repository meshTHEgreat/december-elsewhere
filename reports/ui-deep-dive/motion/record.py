"""Record the real opened guide, including landscape and manual scene choice."""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
raw = HERE / "runtime" / "recordings"
raw.mkdir(parents=True, exist_ok=True)
guide = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18768/"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    for mode, width, height, settle in (("baku", 390, 844, 10800), ("overview", 667, 375, 13700)):
        context = browser.new_context(viewport={"width":width,"height":height}, is_mobile=True,
                                      has_touch=True, reduced_motion="no-preference",
                                      record_video_dir=raw, record_video_size={"width":width,"height":height})
        page = context.new_page()
        video = page.video
        page.goto(guide+"#baku/winter",wait_until="domcontentloaded")
        page.locator(f"[data-winter-film={mode}]").click()
        stage = page.locator(".ss-stage")
        stage.wait_for()
        page.wait_for_timeout(settle)
        frames = page.locator("[data-winter-scene]")
        assert int(stage.locator("[data-story-index]").get_attribute("data-story-index")) == frames.count()-1
        frames.first.click()
        page.wait_for_timeout(450)
        assert stage.locator("[data-story-index]").get_attribute("data-story-index")=="0"
        page.keyboard.press("Escape")
        context.close()
        video.save_as(HERE/f"ui-preview-{mode}-{width}.webm")
    browser.close()
