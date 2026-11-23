"""Capture the integrated design at the states used for the owner review."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "shots"
OUT.mkdir(exist_ok=True)
CASES = [(320,725),(390,844),(667,375),(768,1024),(1440,900),(2560,1440)]


def run(browser, url):
    all_metrics = {}
    for width, height in CASES:
        context = browser.new_context(viewport={"width":width, "height":height}, has_touch=width<740,
                                      is_mobile=width<740, reduced_motion="reduce")
        page = context.new_page()
        page.set_default_timeout(8000)
        metrics = all_metrics[str(width)] = {}

        def visit(anchor):
            page.goto(url + anchor, wait_until="domcontentloaded")
            page.evaluate("document.fonts.ready")

        def shot(name):
            if width in (320,390,667,1440):
                page.screenshot(path=OUT / f"{width}-{name}.jpg", type="jpeg", quality=84)

        visit("#baku/budget")
        bag = page.locator("#cost-bags")
        bag.evaluate("input=>input.scrollIntoView({block:'start'})")
        bag.press("Tab")
        page.evaluate("new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
        metrics["focused_budget_clearance"] = page.evaluate("""()=>{
            const target = document.activeElement.getBoundingClientRect();
            const edge = [...document.querySelectorAll('.mast,.city-subnav,.budget-total')]
              .map(x=>x.getBoundingClientRect()).filter(x=>x.left<target.right && x.right>target.left)
              .map(x=>x.bottom);
            return Math.round(target.top-Math.max(...edge));
        }""")
        metrics["budget_total_height"] = round(page.locator(".budget-total").bounding_box()["height"],2)
        shot("budget")
        metrics["mast_min_width"] = min(round(x.bounding_box()["width"],2) for x in page.locator(".mast nav a").all())
        if page.locator(".chapter-menu-current").is_visible():
            metrics["mobile_current"] = page.locator(".chapter-menu-current").inner_text()
        shot("nav")

        visit("#baku/stays")
        first_stay = page.locator("[data-stay='0']")
        metrics["first_stay_action_top"] = round(first_stay.bounding_box()["y"],2)
        shot("stays")

        visit("#baku/walk")
        if width<740:
            page.locator("#route-select").select_option(index=1)
        else:
            page.locator("[data-route='1']").press("Enter")
        rect = page.locator(".mapbox").bounding_box()
        bar = page.locator(".city-subnav").bounding_box()
        edge = max(rect["y"], bar["y"] + bar["height"])
        metrics["walk_map_visible_pct"] = round(100 * max(0,min(height,rect["y"] + rect["height"])-edge)/rect["height"],1)
        shot("walk")

        visit("#baku/photos")
        page.locator("#gallery [data-photo-open]").press("Enter")
        picture = page.locator("#photo-dialog img")
        picture.evaluate("img=>img.decode()")
        metrics["photo_box"] = {k: round(v,2) for k,v in picture.bounding_box().items()}
        shot("photo")
        page.keyboard.press("Escape")

        visit("#baku/winter")
        page.locator("[data-winter-film=baku]").press("Enter")
        page.locator(".ss-stage").wait_for()
        metrics["winter_stage"] = {k: round(v,2) for k,v in page.locator(".ss-stage").bounding_box().items()}
        metrics["winter_detail_rendered_px"] = page.locator(".ss-stage").evaluate("""stage=>{
          const detail=stage.querySelector('.wf-story-detail'), transform=new DOMMatrix(getComputedStyle(stage).transform);
          return Math.round(parseFloat(getComputedStyle(detail).fontSize)*transform.a*10)/10;
        }""")
        shot("winter")
        page.keyboard.press("Escape")

        visit("#destinations")
        metrics["city_name_spread"] = page.locator(".city-name").evaluate_all(
            "rows=>Math.max(...rows.map(r=>r.getBoundingClientRect().left))-Math.min(...rows.map(r=>r.getBoundingClientRect().left))")
        page.locator("#atlas-toggle").click()
        page.locator(".has-globe canvas").wait_for()
        metrics["globe_visual"] = {k:round(v,2) for k,v in page.locator(".atlas-visual").bounding_box().items()}
        shot("atlas")

        visit("#compare")
        metrics["table_overflow_px"] = page.locator(".compare-scroll").evaluate("node=>node.scrollWidth-node.clientWidth")
        shot("compare")
        metrics["document_overflow_px"] = page.evaluate("document.documentElement.scrollWidth-innerWidth")
        context.close()
    return all_metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default="http://127.0.0.1:18768/")
    parser.add_argument("--browser", choices=("chrome","msedge"), default="chrome")
    args = parser.parse_args()
    with sync_playwright() as driver:
        browser = driver.chromium.launch(channel=args.browser)
        value = {"url": args.url, "browser": browser.version, "viewports": run(browser, args.url)}
        (HERE / "mobile-recheck.json").write_bytes((json.dumps(value,indent=2) + "\n").encode("utf-8"))
        browser.close()
