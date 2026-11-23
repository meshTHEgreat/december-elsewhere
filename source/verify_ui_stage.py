"""Check real Stageshow previews in the standalone guide, without a network."""
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError, expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
GUIDE = (ROOT / "index.html").as_uri() + "#baku/winter"
BRIEFINGS = {
    "baku": ["Baku", "Shahdag", "Tufandag"],
    "overview": ["Baku", "Tbilisi", "Budapest", "Vienna", "Prague"],
}


def current_scene(panel):
    return panel.locator(".wf-story-beat[data-current=yes] h3")


def open_preview(page, mode):
    trigger = page.locator(f"[data-winter-film={mode}]")
    trigger.press("Enter")
    panel = page.locator("#winter-film")
    expect(panel).to_be_visible()
    return trigger, panel


def check_landscape(browser):
    page = browser.new_page(
        viewport={"width": 667, "height": 375}, has_touch=True, offline=True, reduced_motion="reduce"
    )
    page.set_default_timeout(7000)
    page.goto(GUIDE)
    trigger, panel = open_preview(page, "baku")
    close = panel.get_by_role("button", name="Close preview")
    expect(close).to_be_focused()
    stage = panel.locator(".ss-stage")
    close_top = close.bounding_box()["y"]
    chrome_bottom = page.locator(".city-subnav").evaluate("(nav) => nav.getBoundingClientRect().bottom")
    bounds = stage.bounding_box()
    assert chrome_bottom <= close_top <= bounds["y"]
    assert bounds["height"] <= 206 and bounds["y"] + bounds["height"] <= 375
    assert stage.locator(".wf-story-detail").first.evaluate(
        """note => {
          const font = parseFloat(getComputedStyle(note).fontSize);
          const stage = note.closest('.ss-stage');
          return font * stage.getBoundingClientRect().width / stage.offsetWidth >= 13.5;
        }"""
    )
    page.keyboard.press("Tab")
    expect(panel.get_by_role("button", name="Baku", exact=True)).to_be_focused()
    page.keyboard.press("Escape")
    expect(panel).to_be_hidden()
    expect(trigger).to_be_focused()
    assert 0 <= trigger.bounding_box()["y"] < 331
    page.close()


def check_reduced_motion(browser):
    page = browser.new_page(
        viewport={"width": 390, "height": 844}, has_touch=True, offline=True, reduced_motion="reduce"
    )
    requests = []
    page.on("request", lambda request: requests.append(request.url) if request.url.startswith("http") else None)
    page.set_default_timeout(7000)
    page.goto(GUIDE)
    expect(page.get_by_role("heading", name="Winter previews")).to_be_visible()
    for mode, scenes in BRIEFINGS.items():
        trigger, panel = open_preview(page, mode)
        stage = panel.locator(".ss-stage")
        expect(stage).to_have_attribute("data-layout", "compact")
        expect(current_scene(panel)).to_have_text(scenes[-1])
        for title in scenes:
            button = panel.get_by_role("button", name=title, exact=True)
            button.press("Enter")
            expect(current_scene(panel)).to_have_text(title)
            expect(button).to_have_attribute("aria-pressed", "true")
            assert button.bounding_box()["height"] >= 44
        panel.get_by_role("button", name="Close preview").click()
        expect(trigger).to_be_focused()
    assert not requests
    page.close()


def check_manual_playback(browser):
    page = browser.new_page(viewport={"width": 390, "height": 844}, has_touch=True, offline=True)
    page.set_default_timeout(7000)
    page.goto(GUIDE)
    _, panel = open_preview(page, "baku")
    expect(current_scene(panel)).to_have_text("Baku")
    expect(current_scene(panel)).to_have_text("Shahdag", timeout=6000)
    start = panel.get_by_role("button", name="Baku", exact=True)
    start.press("Enter")
    expect(current_scene(panel)).to_have_text("Baku")
    page.wait_for_timeout(3700)
    expect(current_scene(panel)).to_have_text("Baku")
    page.close()


def check_source_rule():
    stylesheet = (ROOT / "source/winter-stage.css").read_text(encoding="utf-8")
    assert ".wf-story--shallow .wf-story-detail" in stylesheet
    assert ".wf-scene-button" in stylesheet
    assert "@media (prefers-reduced-motion: reduce)" in stylesheet


def main():
    failures = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome")
        for check in (check_landscape, check_reduced_motion, check_manual_playback):
            try:
                check(browser)
            except (AssertionError, TimeoutError) as error:
                failures.append(check.__name__)
                print(f"FAIL {check.__name__}: {error}")
            else:
                print(f"PASS {check.__name__}")
        browser.close()
    try:
        check_source_rule()
    except AssertionError:
        failures.append("check_source_rule")
        print("FAIL check_source_rule")
    else:
        print("PASS check_source_rule")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
