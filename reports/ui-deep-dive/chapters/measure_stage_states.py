"""Read-only Stageshow success, loading and failure geometry."""
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from measure_chapters import BASE, VIEWPORTS, save_shot

URL = "http://127.0.0.1:18768/#baku/winter"
STAGE = "**/winter-stage.js"


def measure(page, selector):
    return page.evaluate("""selector => {
      const node = document.querySelector(selector);
      const r = node.getBoundingClientRect();
      const subnav = document.querySelector('.city-subnav').getBoundingClientRect().bottom;
      const active = document.activeElement;
      const a = active.getBoundingClientRect();
      const shown = q => Math.max(0,Math.min(q.bottom,innerHeight)-Math.max(q.top,subnav));
      return {body:node.innerText.slice(0,300), y:Math.round(r.top),h:Math.round(r.height),
        visible:Math.round(shown(r)),active:active.innerText,activeVisible:Math.round(shown(a)),activeY:Math.round(a.top)};
    }""", selector)


def main():
    shots = BASE / "shots"
    shots.mkdir(exist_ok=True)
    results = []
    with sync_playwright() as p:
        chromium = p.chromium.launch(channel="chrome")
        for width, height in VIEWPORTS:
            case = {"viewport": [width, height]}
            for failed in (False, True):
                context = chromium.new_context(viewport={"width":width,"height":height}, is_mobile=width<768,
                                               has_touch=width<768, reduced_motion="reduce" if failed else "no-preference")
                page = context.new_page()
                page.goto(URL, wait_until="domcontentloaded")
                page.evaluate("document.fonts.ready")
                trigger = page.locator("[data-winter-film='baku']")
                trigger.focus()
                if failed:
                    captured = []
                    page.route(STAGE, lambda route: captured.append(route))
                trigger.press("Enter")
                if failed:
                    message = page.locator("#winter-film-message")
                    expect(message).to_have_text("Loading visual briefing")
                    trigger_css = page.locator("[data-winter-film='baku']")
                    expect(trigger_css).to_have_attribute("aria-busy","true")
                    case["loading"] = measure(page, "#winter-film-message")
                    if width == 390:
                        save_shot(page, shots / f"baku-{width}-stage-loading.jpg")
                    assert len(captured) == 1
                    captured.pop().abort()
                    expect(message).to_contain_text("The visual briefing could not load")
                    case["error"] = measure(page, "#winter-film-message")
                    if width == 390:
                        save_shot(page, shots / f"baku-{width}-stage-error.jpg")
                else:
                    expect(page.locator(".ss-stage")).to_be_visible()
                    case["open"] = measure(page, ".ss-stage")
                    state = page.locator("[data-story-index]")
                    expect(state).to_have_attribute("data-story-index", "1", timeout=6000) if width in (390,667) else None
                    if width in (390,667):
                        save_shot(page, shots / f"baku-{width}-stage-open.jpg")
                    page.keyboard.press("Tab")
                    case["afterTab"] = measure(page, ".ss-stage")
                    case["frame"] = state.get_attribute("data-story-index")
                    # Re-focus trigger to test the documented Escape path.
                    trigger.focus()
                    page.keyboard.press("Escape")
                    expect(trigger).to_be_focused()
                    case["escaped"] = page.locator(".ss-stage").count() == 0
                context.close()
            results.append(case)
        chromium.close()
    (BASE/"stage-states.json").write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
