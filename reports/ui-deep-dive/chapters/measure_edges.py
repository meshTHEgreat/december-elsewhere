"""Measure chosen walks, photo letterboxing, and top-view stay choices."""
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from measure_chapters import BASE, SITES, VIEWPORTS


def main():
    shots = BASE / "shots"
    shots.mkdir(exist_ok=True)
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for width, height in VIEWPORTS:
            context = browser.new_context(viewport={"width": width, "height": height},
                                          is_mobile=width < 768, has_touch=width < 768,
                                          reduced_motion="reduce")
            page = context.new_page()
            page.goto("http://127.0.0.1:18768/", wait_until="domcontentloaded")
            page.evaluate("document.fonts.ready")
            for city in SITES:
                info = {"city": city, "width": width, "height": height}
                page.locator(f".city-tab[data-city='{city}']").press("Enter")
                page.goto(f"http://127.0.0.1:18768/#{city}/stays", wait_until="domcontentloaded")
                expect(page.locator("#stays h2")).to_be_focused()
                info["stay"] = page.evaluate("""() => {
                  const action = selector => [...document.querySelectorAll(selector)].map(el => Math.round(el.getBoundingClientRect().top));
                  const h = document.querySelector('#stays h2').getBoundingClientRect();
                  const shelf = document.querySelector('.outdoor-guide');
                  return {heading:Math.round(h.top), firstPrice:action('.price')[0], firstChoice:action('.stay button')[0],
                    buttons:action('.stay-cta'), titles:action('.stay h3'), prices:action('.stay .price'),
                    firstFacts:document.querySelector('.stay').innerText.slice(0,350),
                    beforeStay:Math.round(document.querySelector('.stay').getBoundingClientRect().top),
                    outdoorH:Math.round(shelf?.getBoundingClientRect().height || 0)};
                }""")
                if city in ("baku", "tbilisi", "prague") and width in (320, 390, 667, 1440, 2560):
                    page.screenshot(path=shots / f"{city}-{width}-stays-jump.jpg", type="jpeg", quality=70)
                choices = []
                for anchor in (0,1):
                    page.locator("#anchor-select").select_option(index=anchor)
                    route = page.locator("#route-select")
                    if not route.is_visible():
                        continue
                    route.evaluate("""el => el.closest('label').scrollIntoView({block:'start', behavior:'instant'})""")
                    lengths = route.locator("option").count()
                    for index in range(lengths):
                        route.select_option(index=index)
                        box = page.evaluate("""() => {
                          const el = document.getElementById('route-select');
                          const option = el.options[el.selectedIndex].textContent;
                          const cs = getComputedStyle(el);
                          const canvas = document.createElement('canvas').getContext('2d');
                          canvas.font = [cs.fontWeight,cs.fontSize,cs.fontFamily].join(' ');
                          const time = option.match(/ · .+$/)?.[0] || '';
                          const full = canvas.measureText(option).width;
                          const name = canvas.measureText(option.slice(0,option.length-time.length)).width;
                          const width = el.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 18;
                          const sticky = document.querySelector('.city-subnav').getBoundingClientRect().bottom;
                          const map = document.querySelector('.mapbox').getBoundingClientRect();
                          const trace = document.querySelector('.active-route')?.getBoundingClientRect();
                          const clipped = r => Math.max(0,Math.min(r.bottom,innerHeight)-Math.max(r.top,sticky));
                          const round = v => Math.round(v*10)/10;
                          return {option, usableWidth:round(width), fullText:round(full), name:round(name), note:document.querySelector('#route-note').innerText,
                            traceHeight:round(trace?.height || 0), traceVisible:trace ? round(clipped(trace)) : 0,
                            mapHeight:round(map.height), mapVisible:round(clipped(map)),
                            mapTop:round(map.top), stickyBottom:round(sticky), focus:document.activeElement.id,
                            documentOverflow: document.documentElement.scrollWidth - innerWidth,
                          };
                        }""")
                        box.update({"index": index, "anchor": anchor})
                        choices.append(box)
                        if city == "baku" and anchor == 1 and index == 0 and width in (320,390,667):
                            page.screenshot(path=shots / f"{city}-{width}-walk-choose.jpg", type="jpeg", quality=73)
                info["routeChoices"] = choices

                gallery = page.locator("[data-photo-open]")
                gallery.press("Enter")
                expect(page.locator("#photo-dialog")).to_be_visible()
                photo = page.locator(".lightbox-figure img")
                photo.evaluate("image=>image.decode()")
                info["photo"] = photo.evaluate("""img => {
                  const d = img.closest('dialog');
                  const r = img.getBoundingClientRect();
                  const scale = Math.min(r.width/img.naturalWidth,r.height/img.naturalHeight);
                  const box = selector => {
                    const rect=d.querySelector(selector).getBoundingClientRect();
                    return [Math.round(rect.top),Math.round(rect.bottom)];
                  };
                  return {alt:img.alt, rendered:[Math.round(img.naturalWidth*scale),Math.round(img.naturalHeight*scale)],
                    frame:[Math.round(r.width),Math.round(r.height)], firstArrow:box('.gallery-tools button'),
                    download:box('.photo-download'), close:box('[data-photo-close]'),
                    modalScroll:d.scrollHeight-d.clientHeight};
                }""")
                if city == "baku" and width in (320, 390, 667, 1440):
                    page.screenshot(path=shots / f"{city}-{width}-photo-open.jpg", type="jpeg", quality=74)
                page.keyboard.press("Escape")
                info["photo"]["restoredFocus"] = gallery.evaluate("el=>document.activeElement===el")
                results.append(info)
            context.close()
            print(f"{width} px", flush=True)
        browser.close()
    (BASE/"chapter-action-edges.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
