"""Read-only browser audit for the guide's published chrome and atlas."""
import argparse
import json
import os
import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


AREA = Path(__file__).resolve().parent
CITIES = ("baku", "tbilisi", "budapest", "vienna", "prague")
SECTIONS = ("intro", "stays", "walk", "winter", "itinerary", "budget", "photos")
SIZES = ((320, 725), (390, 844), (667, 375), (768, 1024), (1440, 900), (2560, 1440))
MEASURE = r"""() => {
  const visible = e => e && e.getClientRects().length && getComputedStyle(e).visibility === 'visible' && e.offsetWidth !== 0;
  const q = s => document.querySelector(s);
  const round = x => Math.round(x * 100) / 100;
  const elem = e => {
    const r = e.getBoundingClientRect();
    return {left:round(r.left),top:round(r.top),right:round(r.right),bottom:round(r.bottom),width:round(r.width),height:round(r.height)};
  };
  const box = (s) => visible(q(s)) ? elem(q(s)) : null;
  function lines(e) {
    const lookup = new Map(), tree = document.createTreeWalker(e, NodeFilter.SHOW_TEXT), range = document.createRange();
    for (let node = tree.nextNode(); node; node = tree.nextNode()) {
      for (let i = 0; i < node.length; i++) {
        range.setStart(node,i); range.setEnd(node,i+1);
        const r = range.getBoundingClientRect();
        if (r.width < 0.05 || !r.height) continue;
        const key = Math.round(r.bottom);
        let row = lookup.get(key);
        if (!row) { row = {y:key,text:"",left:r.left,right:r.right}; lookup.set(key,row); }
        row.text += node.data[i]; row.left = Math.min(row.left,r.left); row.right = Math.max(row.right,r.right);
      }
    }
    return [...lookup.values()].sort((a,b)=>a.y-b.y).map(r=>{
      const text=r.text.trim().replace(/\s+/g,' ');
      return {text, chars:[...text].length, topLineFromPage:r.y, left:round(r.left), width:round(r.right-r.left)};
    });
  }
  function luminance(color) {
    const channels = color.match(/[\d.]+/g)?.slice(0,3).map(Number);
    return !channels || channels.length < 3 ? null : channels.map(x => x / 255).map(x => x <= .04045 ?
      x / 12.92 : ((x + .055) / 1.055) ** 2.4).reduce((sum,n,i) => sum + n * [.2126,.7152,.0722][i],0);
  }
  function contrast(e) {
    const color = getComputedStyle(e).color, front = luminance(color);
    for (let layer=e; layer; layer=layer.parentElement) {
      const background = getComputedStyle(layer).backgroundColor;
      if (!background || background === 'rgba(0, 0, 0, 0)' || background === 'transparent') continue;
      const back = luminance(background); if (back == null || front == null) return null;
      return {color,background,ratio:round((Math.max(back,front)+.05)/(Math.min(back,front)+.05))};
    }
    return null;
  }
  const labels = '.mast .word,.mast nav a,.hero .eyebrow,.hero h1,.hero .hero-blurb,.hero .cover-action,.hero .cover-facts,.hero .cover-credit,.pick h2,.pick .section-lead,.city-name,.city-detail,.city-price,.atlas-bar label,.atlas-bar button,.atlas-footer span,.atlas-footer strong,.atlas-feedback,.city-subnav a,.chapter-menu summary,.footer a';
  const targetNodes = '.mast a,.hero a,.pick button,.pick select,.city-subnav a,.chapter-menu summary,.footer a';
  const targets = [...document.querySelectorAll(targetNodes)].filter(visible).map(e=>{
    const b=elem(e); return {name:e.textContent.trim(), tag:e.tagName, owner:e.closest('.mast,.hero,.pick,.city-subnav,.footer')?.className,width:b.width,height:b.height,contrast:!e.closest('.hero')?contrast(e):null};
  });
  const layout = Object.fromEntries(['.mast','.mast .word','.mast nav','.hero','.hero-inner','.hero .cover-credit',
    '.atlas-layout','.atlas-layout > div:first-child','#city-index','.atlas-panel','.atlas-bar','#atlas-select','#atlas-toggle','#atlas-visual','#atlas-open',
    '.city-subnav','.chapter-nav-inner','.chapter-jumps','.chapter-menu','.chapter-menu > div','.footer','.footer .wrap','.footer-actions'].map(s=>[s,box(s)]));
  const flatLabels = [...document.querySelectorAll('.atlas-pins text')].filter(visible).map(e=>{
    const m=e.getScreenCTM();
    return {name:e.textContent,...elem(e),nominalFontSize:round(parseFloat(getComputedStyle(e).fontSize) * m.a)};
  });
  return {width:innerWidth,height:innerHeight,dir:document.dir||getComputedStyle(document.body).direction,lang:document.documentElement.lang,
    overflow:document.documentElement.scrollWidth-innerWidth,layout,targets,flatLabels,
    lines:[...document.querySelectorAll(labels)].filter(visible).map(e=>({tag:e.tagName,name:e.textContent.trim(),lines:lines(e)})),
    cityRows:[...document.querySelectorAll('.city-tab')].map(e=>({name:e.querySelector('.city-name').textContent, row:elem(e),nameBox:elem(e.querySelector('.city-name')),priceBox:elem(e.querySelector('.city-price')),arrowBox:elem(e.querySelector('.city-arrow'))})),
    current:[...document.querySelectorAll('.city-subnav [aria-current]')].filter(visible).map(e=>e.dataset.jump)};
}"""
VISIBLE_BOX = r"""(selector) => {
  const e = document.querySelector(selector), r = e.getBoundingClientRect();
  const mast = document.querySelector('.mast').getBoundingClientRect();
  const height = Math.max(0, Math.min(innerHeight,r.bottom) - Math.max(mast.bottom,r.top));
  const midX = Math.max(0, Math.min(innerWidth-1,r.left+r.width/2)), midY = Math.max(0, Math.min(innerHeight-1,r.top+r.height/2));
  const hit = document.elementFromPoint(midX,midY);
  return {top:r.top,bottom:r.bottom,height:r.height,visibleHeight:height,hit:hit===e||e.contains(hit),mastBottom:mast.bottom};
}"""


def fresh(browser, width, height, *, reduced=True):
    return browser.new_context(
        viewport={"width": width, "height": height},
        has_touch=width <= 667,
        is_mobile=width <= 667,
        color_scheme="light",
        reduced_motion="reduce" if reduced else "no-preference",
        locale="en-US",
    )


def start(page, url):
    page.goto(url, wait_until="domcontentloaded")
    expect(page.locator(".city-tab")).to_have_count(5)
    page.evaluate("document.fonts.ready")


def screenshot(page, directory, label):
    page.screenshot(path=directory / "shots" / f"{label}.jpg", type="jpeg", quality=79, animations="disabled")


def atlas_focus(page):
    page.locator(".atlas-bar").evaluate("e=>e.scrollIntoView({block:'start',behavior:'instant'})")


def audit(browser, url, directory, width, height):
    context = fresh(browser, width, height)
    page = context.new_page()
    start(page, url)
    page.keyboard.press("Tab")
    skip = page.locator(".skip").evaluate("e=>({focused:e===document.activeElement, width:e.offsetWidth,height:e.offsetHeight})")
    page.locator(".skip").evaluate("e=>e.blur()")
    home = page.evaluate(MEASURE)
    screenshot(page, directory, f"{width}-cover")

    city_list = page.locator("#city-index")
    city_list.evaluate("e=>e.scrollIntoView({block:'start',behavior:'instant'})")
    screenshot(page, directory, f"{width}-city-list")
    before = page.evaluate(MEASURE)
    touch = width <= 667
    if not touch:
        page.locator(".city-tab[data-city='budapest']").hover()
        page.wait_for_timeout(290)
    hover = page.evaluate(MEASURE)["cityRows"]
    page.mouse.move(1,1)

    atlas_focus(page)
    atlas = page.evaluate(MEASURE)
    screenshot(page, directory, f"{width}-flat-atlas")
    previews = []
    for city in CITIES:
        page.locator("#atlas-select").select_option(city)
        previews.append({
            "id": city, "distance": page.locator("#atlas-distance").inner_text(),
            "label": page.locator("#atlas-open-label").inner_text(),
            "activePins": page.locator(".atlas-pins [data-pin].is-active").count(),
            "selectedStaticPin": page.locator(".atlas-pins [data-pin].is-active").get_attribute("data-pin"),
        })
    page.locator("#atlas-select").select_option("baku")
    unchanged_toggle = page.locator("#atlas-toggle").bounding_box()
    requests = []
    page.route("**/media/globe.js", lambda route: requests.append(route))
    page.locator("#atlas-toggle").press("Enter")
    expect(page.locator("#atlas-toggle")).to_have_text("Loading globe")
    loading = {
        "toggle": page.locator("#atlas-toggle").bounding_box(),
        "focused": page.locator("#atlas-toggle").evaluate("e=>e===document.activeElement"),
        "disabled": page.locator("#atlas-toggle").get_attribute("aria-disabled"),
        "status": page.locator("#atlas-feedback").inner_text(),
        "beforeToggle": unchanged_toggle,
    }
    screenshot(page, directory, f"{width}-atlas-loading")
    for attempt in range(15):
        if requests:
            break
        page.wait_for_timeout(40)
    for request in requests:
        request.continue_()
    expect(page.locator(".globe-canvas")).to_be_visible(timeout=8000)
    settled = page.locator("#atlas-toggle").evaluate("e=>({label:e.textContent,pressed:e.getAttribute('aria-pressed'),focused:e===document.activeElement})")
    globe = {
        "settled": settled, "toggleVisibility":page.evaluate(VISIBLE_BOX, "#atlas-toggle"),
        "canvasVisibility":page.evaluate(VISIBLE_BOX, ".globe-canvas"),
        "panel":page.locator(".atlas-panel").bounding_box(),
    }
    screenshot(page, directory, f"{width}-globe")
    for city in CITIES:
        page.locator("#atlas-select").select_option(city)
        expect(page.locator(".globe-pin.is-active")).to_have_text(city.capitalize())
    page.locator("#atlas-toggle").press("Enter")
    expect(page.locator(".globe-canvas")).to_have_count(0)
    expect(page.locator("#atlas-toggle")).to_have_text("View globe")
    page.locator("[data-open-preview]").press("Enter")
    expect(page.locator("#chapter h2")).to_have_text("Prague")
    expect(page.locator("#chapter h2")).to_be_focused()
    nav_states=[]
    for city in CITIES:
        for section in SECTIONS:
            page.evaluate("(hash)=>location.hash=hash",f"{city}/{section}")
            expect(page.locator("#chapter h2")).to_have_text(city.capitalize())
            expected_heading = page.locator(f"#{section} h2").first
            if expected_heading.count():
                expect(expected_heading).to_be_focused(timeout=3000)
            page.wait_for_timeout(45)
            nav_states.append({
                "city": city,"section":section, "hash":page.evaluate("location.hash"),
                "current":page.locator(".city-subnav [aria-current]:visible").all_inner_texts(),
                "focus":page.evaluate("document.activeElement.textContent.trim().slice(0,60)"),
                "nav":page.locator(".city-subnav").bounding_box(),
                "overflow":page.evaluate("document.documentElement.scrollWidth-innerWidth"),
            })
    page.evaluate("location.hash='baku/budget'")
    expect(page.locator("#chapter h2")).to_have_text("Baku")
    expect(page.locator("#budget h2")).to_be_focused(timeout=3000)
    nav = page.evaluate(MEASURE)
    screenshot(page, directory, f"{width}-chapter-chrome")
    menu = page.locator(".chapter-menu summary")
    menu_data = None
    if menu.is_visible():
        menu.press("Enter")
        expect(page.locator(".chapter-menu")).to_have_attribute("open", "")
        page.wait_for_timeout(70)
        menu_data=page.evaluate(MEASURE)
        menu_data["overlay"]=page.evaluate(VISIBLE_BOX, ".chapter-menu > div")
        menu_data["linksHit"]=page.locator(".chapter-menu a").evaluate_all("""all=>all.map(e=>{
          const r=e.getBoundingClientRect(), x=r.left+r.width/2,y=r.top+r.height/2;
          return {name:e.textContent,y,hit:document.elementFromPoint(x,y)===e};
        })""")
        screenshot(page,directory,f"{width}-chapter-menu")
        page.keyboard.press("Tab")
        menu_data["afterTab"]=page.evaluate("document.activeElement.textContent.trim()")
        page.keyboard.press("Escape")
        expect(menu).to_be_focused()
        expect(page.locator(".chapter-menu[open]")).to_have_count(0)
    page.locator(".footer").evaluate("e=>e.scrollIntoView({block:'end',behavior:'instant'})")
    footer=page.evaluate(MEASURE)
    screenshot(page,directory,f"{width}-footer")
    context.close()

    blocked = fresh(browser,width,height)
    blocked.add_init_script("""const old=HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext=function(type,...args) {
        return type.startsWith('webgl') ? null : old.call(this,type,...args);
      };""")
    fallback_page=blocked.new_page()
    start(fallback_page,url)
    atlas_focus(fallback_page)
    fallback_page.locator("#atlas-toggle").press("Enter")
    expect(fallback_page.locator("#atlas-feedback")).to_contain_text("static atlas")
    expect(fallback_page.locator("#atlas-flat svg")).to_be_visible()
    expect(fallback_page.locator(".globe-canvas")).to_have_count(0)
    fallback={"text":fallback_page.locator("#atlas-feedback").inner_text(),"controls":fallback_page.evaluate(MEASURE)}
    screenshot(fallback_page,directory,f"{width}-atlas-fallback")
    blocked.close()
    return {
        "viewport":[width,height],"lang":"en","dir":"ltr","skip":skip,"cover":home,
        "list":before,"hoverCityRows":hover,"atlas":atlas,"previews":previews,
        "loading":loading,"globe":globe,"chapterStates":nav_states,"chapter":nav,
        "menu":menu_data,"footer":footer,"fallback":fallback,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url",default="http://127.0.0.1:18768/")
    parser.add_argument("--width",type=int)
    parser.add_argument("--browser",choices=("chrome","msedge"),default="chrome")
    parser.add_argument("--output",type=Path,default=AREA)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/"shots").mkdir(exist_ok=True)
    runtime=AREA/"runtime"
    runtime.mkdir(exist_ok=True)
    os.environ["TEMP"]=os.environ["TMP"]=str(runtime)
    tempfile.tempdir=str(runtime)
    with sync_playwright() as runner:
        browser=runner.chromium.launch(channel=args.browser,args=["--enable-unsafe-swiftshader","--use-angle=swiftshader"])
        for width,height in SIZES:
            if args.width and width != args.width:
                continue
            result=audit(browser,args.url,args.output,width,height)
            (args.output/f"measure-{width}.json").write_text(
                json.dumps({"browser":browser.version,"url":args.url,"result":result},indent=2,ensure_ascii=False)+"\n",
                encoding="utf-8",
            )
            print(f"Measured {width} x {height}",flush=True)
        browser.close()
