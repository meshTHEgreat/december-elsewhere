"""Exercise the approved mobile app changes against the packaged guide."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "source" / "travel-data.json").read_text(encoding="utf-8"))
MAPS = json.loads((ROOT / "source" / "travel-maps.json").read_text(encoding="utf-8"))
PHOTOS = json.loads((ROOT / "source" / "photography.json").read_text(encoding="utf-8"))


def city_link(page, url, city, section):
    page.goto(f"{url}#{city}/{section}", wait_until="domcontentloaded")
    expect(page.locator(f"#{section} h2")).to_be_focused()


def visible_amount_lines(amount):
    return amount.evaluate("""node => {
      const text = document.createRange();
      text.selectNodeContents(node);
      return text.getClientRects().length;
    }""")


def budget(page, url, layouts):
    city_link(page, url, "baku", "budget")
    expect(page.locator(".budget-total-amount")).to_have_count(2)
    expect(page.locator(".budget-total-amount .meta").first).to_have_text("Per adult")
    expect(page.locator(".budget-total-amount .meta").last).to_have_text("Total for three")
    expect(page.locator(".budget-help")).to_contain_text("contingency")
    car = page.locator(".car-costs")
    car.locator("summary").press("Enter")
    fields = page.locator("#budget [data-cost]")
    expect(fields).to_have_count(14)
    for field in fields.all():
        field.fill("150000")
    expect(page.locator("#total-person")).to_have_text("SAR 1,400,000")
    expect(page.locator("#total-group")).to_have_text("SAR 4,200,000")
    if layouts:
        for amount in page.locator(".budget-total-amount strong").all():
            assert visible_amount_lines(amount) == 1
        field = page.locator("#cost-bags")
        page.locator(".budget-fields").first.evaluate("(node) => node.scrollIntoView({block:'start'})")
        field.focus()
        page.wait_for_function("""() => {
          const target = document.activeElement.getBoundingClientRect();
          const overlays = ['.mast', '.city-subnav', '#total'].map(s => document.querySelector(s).getBoundingClientRect());
          return target.top >= Math.max(...overlays.map(rect => rect.bottom)) + 7.75;
        }""")
        assert field.bounding_box()["y"] + field.bounding_box()["height"] <= page.viewport_size["height"]
    page.locator("[data-reset]").click()
    assert page.locator("#cost-bags").input_value() != "150000"


def nav(page, url, _):
    names = {"intro": "Arrival", "stays": "Stays", "walk": "Walks", "winter": "Winter",
             "itinerary": "Itinerary", "budget": "Budget", "photos": "Photos"}
    for section, label in names.items():
        city_link(page, url, "baku", section)
        expect(page.locator(".chapter-menu-current")).to_contain_text(label)
        expect(page.locator(".chapter-menu summary")).to_have_accessible_name(
            re.compile(rf"(?=.*{label})(?=.*Baku)"))
    for section in ("stays", "itinerary", "photos"):
        expect(page.locator(f"#{section} h2")).to_have_text(names[section])
    summary = page.locator(".chapter-menu summary")
    summary.press("Enter")
    page.locator(".chapter-menu [data-jump=budget]").press("Enter")
    expect(page.locator(".chapter-menu-current")).to_contain_text("Budget")
    page.go_back()
    expect(page.locator(".chapter-menu-current")).to_contain_text("Photos")


def walks(page, url, layouts):
    widths = page.viewport_size
    for city, mapping in MAPS.items():
        city_link(page, url, city, "walk")
        expect(page.locator(".route-layout > .walk-picker-rail #anchor-select")).to_have_count(1)
        details = page.locator(".walk-list-disclosure")
        assert details.get_attribute("open") is None
        expect(details.locator("summary")).to_have_text("All walk times")
        details.locator("summary").press("Enter")
        for anchor_id, anchor in enumerate(mapping["anchors"]):
            page.locator("#anchor-select").select_option(index=anchor_id)
            expect(details).to_have_attribute("open", "")
            chooser = page.locator("#route-select")
            for index, route in enumerate(anchor["routes"]):
                chooser.select_option(str(index))
                assert " min" not in chooser.locator("option:checked").inner_text()
                expect(chooser).to_be_focused()
                expect(details).to_have_attribute("open", "")
                expect(page.locator("#route-note strong")).to_have_text(route["name"])
                expect(page.locator("#route-note .route-time small")).to_have_text("Estimated walk")
                expect(page.locator(".mapbox .active-route")).to_have_count(1)
                href = page.get_by_role("link", name="Open in Google Maps").get_attribute("href")
                query = parse_qs(urlparse(href).query)
                assert query["origin"] == [",".join(map(str, anchor["start"]))]
                assert query["destination"] == [",".join(map(str, route["point"]))]
                if layouts and widths["width"] == 667:
                    page.wait_for_function("""() => {
                      const map = document.querySelector('.mapbox').getBoundingClientRect();
                      const pin = document.querySelector('.city-subnav').getBoundingClientRect();
                      const visible = Math.min(map.bottom, innerHeight) - Math.max(map.top, pin.bottom);
                      const trace = document.querySelector('.active-route').getBoundingClientRect();
                      return visible / map.height >= .9 && trace.top >= pin.bottom && trace.bottom <= innerHeight;
                    }""")
        row = details.locator("[data-route]").first
        row.press("Enter")
        expect(row).to_be_focused()
        expect(details).to_have_attribute("open", "")


def stays(page, url, layouts):
    for city in DATA:
        city_link(page, url, city["id"], "stays")
        cards = page.locator(".stays > .stay")
        expect(cards).to_have_count(2)
        if page.locator("#stays .outdoor-guide").count():
            assert page.locator(".stays").evaluate(
                "node => Boolean(node.compareDocumentPosition(node.parentElement.querySelector('.outdoor-guide')) & Node.DOCUMENT_POSITION_FOLLOWING)")
        for index, stay in enumerate(city["stays"]):
            card = cards.nth(index)
            expect(card.locator(".stay-price-note")).to_contain_text("23 Nov 2026")
            expect(card.locator(".outdoor-space")).to_be_visible()
            expect(card.locator(".stay-notes summary")).to_have_text("Listing notes")
            assert card.locator(".stay-cta").evaluate(
                "node => Boolean(node.compareDocumentPosition(node.parentElement.querySelector('.stay-notes')) & Node.DOCUMENT_POSITION_FOLLOWING)")
            expect(card.get_by_role("link", name="Listing & photos")).to_have_attribute("href", stay["url"])
        first = cards.first.locator("[data-stay]")
        if layouts and page.viewport_size["width"] == 390:
            assert first.bounding_box()["y"] < page.viewport_size["height"]
        second = cards.nth(1).locator("[data-stay]")
        second.click()
        expect(second).to_have_text("Stay selected")
        expect(second).to_be_focused()
        expect(page.locator("#cost-stay")).to_have_value(str(city["stays"][1]["price"]))


def compare_and_sources(page, url, layouts):
    page.goto(url + "#compare", wait_until="domcontentloaded")
    expect(page.locator("#compare .section-lead")).to_have_text("Choose two cities. Edit budgets to update the estimates.")
    expect(page.locator("#compare tbody th").filter(has_text="Local travel")).to_have_count(1)
    expect(page.locator("#compare tbody th").filter(has_text="Meals")).to_have_count(1)
    page.locator("#right-city").select_option("budapest")
    expect(page.locator("#compare-1-outdoor")).to_contain_text("confirm access")
    if layouts:
        assert page.locator(".compare-scroll").evaluate("el => el.scrollWidth <= el.clientWidth")
    for idx, city in enumerate(DATA):
        disclosure = page.locator("#evidence details").nth(idx)
        disclosure.locator("summary").press("Enter")
        urls = disclosure.locator("a.source-action").evaluate_all("links => links.map(link => link.href)")
        expected_urls = [source["url"] for source in city["sources"] if source["url"].startswith("https://")]
        assert len(urls) == len(expected_urls)
        assert set(urls) == set(expected_urls)
    credits = page.locator("#photos-credit")
    credits.locator("summary").press("Enter")
    expect(credits.locator(".source-actions")).to_have_count(len(PHOTOS))
    expect(credits.locator(".source-action")).to_have_count(2 * len(PHOTOS))
    expect(page.locator(".source-methods section")).to_have_count(3)
    if layouts:
        for link in page.locator("#evidence a.source-action:visible").all():
            size = link.bounding_box()
            assert size["width"] >= 44 and size["height"] >= 44


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", nargs="?", default=(ROOT / "index.html").as_uri())
    parser.add_argument("--layouts", action="store_true", help="Also test the integrated stylesheet geometry")
    parser.add_argument("--only", choices=["budget", "nav", "walks", "stays", "compare"])
    args = parser.parse_args()
    url = args.url.rstrip("/")
    if not url.endswith(".html"):
        url += "/"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome")
        for width, height, name, check in (
                (320, 725, "budget", budget), (390, 844, "nav", nav),
                (667, 375, "walks", walks), (390, 844, "stays", stays),
                (320, 725, "compare", compare_and_sources)):
            if args.only and name != args.only:
                continue
            context = browser.new_context(offline=urlparse(url).scheme=="file",
                                          is_mobile=True, has_touch=True,
                                          viewport={"width":width, "height":height},
                                          reduced_motion="reduce")
            page = context.new_page()
            page.set_default_timeout(4000)
            check(page, url, args.layouts)
            assert page.evaluate("innerWidth >= document.documentElement.scrollWidth")
            print(f"{name} at {width} × {height}: passed", flush=True)
            context.close()
        browser.close()
