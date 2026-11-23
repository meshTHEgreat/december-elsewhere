"""Reproduce the landscape preview return-focus state and classify runtime failures."""

import json
from playwright.sync_api import expect, sync_playwright

from inspect_candidate import HERE, ROOT, STORIES, settle, shot, visit


ONLINE = "http://127.0.0.1:18768/"
OFFLINE = (ROOT / "index.html").as_uri()


def landscape_focus(browser, url, mode, story):
    context = browser.new_context(viewport={"width": 667, "height": 375}, is_mobile=True, has_touch=True,
                                  offline=mode == "offline", reduced_motion="reduce")
    page = context.new_page()
    visit(page, url, "#baku/winter")
    trigger = page.locator(f"[data-winter-film={story}]")
    trigger.tap()
    close = page.locator("[data-winter-close]")
    expect(close).to_be_focused()
    states = []

    def measure(label):
        settle(page)
        states.append(close.evaluate("""(node, label) => {
          const close = node.getBoundingClientRect();
          const nav = document.querySelector('.city-subnav').getBoundingClientRect();
          const center = document.elementFromPoint(close.left + close.width/2, close.top + close.height/2);
          const active = document.activeElement;
          const controls = document.querySelector('.wf-scene-controls').getBoundingClientRect();
          return {label, focus: active.textContent.trim(), focus_visible: active.matches(':focus-visible'),
            close_top: close.top, close_bottom: close.bottom, close_center_hit: node.contains(center),
            nav_bottom: nav.bottom, scene_controls_top: controls.top, scene_controls_bottom: controls.bottom,
            scroll_y: scrollY};
        }""", label))

    measure("Touch open")
    page.keyboard.press("Tab")
    first = page.locator("#winter-film").get_by_role("button", name="Baku", exact=True)
    expect(first).to_be_focused()
    measure("Tab to first scene")
    page.keyboard.press("Enter")
    expect(page.locator(".wf-story-beat[data-current=yes] h3")).to_have_text("Baku")
    measure("Enter selects first scene")
    page.keyboard.press("Shift+Tab")
    expect(close).to_be_focused()
    measure("Shift+Tab returns to Close preview")
    shot(page, f"667-preview-{story}-return-focus-{mode}")
    page.keyboard.press("Enter")
    expect(trigger).to_be_focused()
    expect(page.locator("#winter-film")).to_be_hidden()
    context.close()
    return states


def invalid_runtime(browser, url, mode):
    context = browser.new_context(viewport={"width": 667, "height": 375}, offline=mode == "offline",
                                  reduced_motion="reduce")
    page = context.new_page()
    if mode == "online-blocked":
        page.route("**/media/winter-stage.js", lambda route: route.abort())
    if mode == "online-invalid":
        page.route("**/media/winter-stage.js", lambda route: route.fulfill(status=200, content_type="application/javascript", body=";"))
    visit(page, url, "#baku/winter")
    if mode == "offline":
        page.locator("#winter-stage-code").evaluate("node=>{node.textContent='null'}")
    trigger = page.locator("[data-winter-film=baku]")
    trigger.press("Enter")
    status = page.locator("#winter-film-message")
    expect(status).to_have_text("Preview unavailable. Read the winter plans above.")
    panel = page.locator("#winter-film")
    close = page.locator("[data-winter-close]")
    result = {"status": status.inner_text(), "empty_panel_visible": panel.is_visible(), "stage_count": panel.locator(".ss-stage").count(),
              "focus_stays_on_trigger": trigger.evaluate("node=>node===document.activeElement"),
              "winter_plans_visible": page.locator("#winter .winter-route").is_visible()}
    if panel.is_visible():
        close.press("Enter")
        expect(panel).to_be_hidden()
        expect(trigger).to_be_focused()
        result["empty_panel_closes"] = True
    context.close()
    return result


def main():
    report = {}
    with sync_playwright() as driver:
        browser = driver.chromium.launch(channel="msedge")
        report["browser"] = browser.version
        for mode, url in (("online", ONLINE), ("offline", OFFLINE)):
            report[f"preview_return_focus_{mode}"] = {story: landscape_focus(browser, url, mode, story) for story in STORIES}
        report["preview_runtime_failures"] = {mode: invalid_runtime(browser, url, mode)
            for mode, url in (("online-blocked", ONLINE), ("online-invalid", ONLINE), ("offline", OFFLINE))}
        browser.close()
    (HERE / "edge-states.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
