"""Read-only Playwright walkthrough of planning, print and Sources."""
import argparse
from io import BytesIO
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


AREA = Path(__file__).resolve().parent
VIEWPORTS = [(320,725),(390,844),(667,375),(768,1024),(1440,900),(2560,1440)]
CITIES = ["baku","tbilisi","budapest","vienna","prague"]
URL = "http://127.0.0.1:18768/"
MEASURE = r"""({selector, prose, groups}) => {
    const root = document.querySelector(selector);
    const round = n => Math.round(n * 100) / 100;
    const visual = el => {
      if (!el?.getClientRects().length || getComputedStyle(el).visibility !== "visible") return false;
      for (let details=el.closest("details:not([open])");details;details=details.parentElement.closest("details:not([open])")) {
        if (el !== details && !details.querySelector(":scope > summary")?.contains(el)) return false;
      }
      return true;
    };
    const rect = el => {
      const b = el.getBoundingClientRect();
      return Object.fromEntries(Object.entries({x:b.x,y:b.y,w:b.width,h:b.height,right:b.right,bottom:b.bottom})
        .map(([k,v])=>[k,round(v)]));
    };
    const text = el => el.textContent.replace(/\s+/g," ").trim();
    const ref = el => (el.id ? "#" + el.id : el.tagName.toLowerCase()) + " " + text(el).slice(0,78);
    const lines = el => {
      const nodes = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      const range = document.createRange();
      const metrics = [];
      for (let node=nodes.nextNode(); node; node=nodes.nextNode()) {
        if (!node.data.trim()) continue;
        for (let i=0; i<node.length; i++) {
          range.setStart(node,i);
          range.setEnd(node,i+1);
          const b=range.getBoundingClientRect();
          if (b.width === 0 || b.height === 0) continue;
          let line=metrics.find(l=>Math.abs(l.y-b.top)<6);
          if (!line) {
            line={y:b.top,minX:b.left,maxX:b.right,raw:""};
            metrics.push(line);
          }
          line.raw += node.data[i];
          line.minX=Math.min(line.minX,b.left);
          line.maxX=Math.max(line.maxX,b.right);
        }
      }
      return metrics.sort((a,b)=>a.y-b.y).map(l=>{
        const lineText=l.raw.replace(/\s+/g," ").trim();
        return {chars:[...lineText].length, text:lineText, width:round(l.maxX-l.minX)};
      });
    };
    const unique = new Map();
    for (const [kind,s] of Object.entries(prose)) {
      unique.set(kind,[...root.querySelectorAll(s)].filter(visual).map(el => ({ref:ref(el),box:rect(el),lines:lines(el)})));
    }
    const alignment = groups.map(([name,s,edge]) => {
      const values=[...root.querySelectorAll(s)].filter(visual).map(el=>[ref(el),rect(el)[edge]]);
      const coords=values.map(([,coord])=>coord);
      return {name,edge,spread:coords.length>1?round(Math.max(...coords)-Math.min(...coords)):null,values};
    });
    const interactive = [...root.querySelectorAll("a[href],button,input,select,summary")].filter(visual).map(el=>{
      const box=rect(el);
      return {ref:ref(el),box,small:box.h<44||box.w<44};
    });
    const ap = el => getComputedStyle(el);
    const channels = css => css.match(/[0-9.]+/g).map(Number);
    const rgb = ([r,g,b]) => [r,g,b].map(n=>n/255).map(v=>v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4));
    const lum = (css) => {const [r,g,b]=rgb(channels(css));return .2126*r+.7152*g+.0722*b;};
    const contrast = selector => {
      const el=root.querySelector(selector);
      if (!el || !visual(el)) return null;
      let background=el;
      while(background && channels(ap(background).backgroundColor)[3]===0) background=background.parentElement;
      if (!background) return null;
      const a=lum(ap(el).color), b=lum(ap(background).backgroundColor);
      return {target:selector,color:ap(el).color,background:ap(background).backgroundColor,ratio:round((Math.max(a,b)+.05)/(Math.min(a,b)+.05))};
    };
    const columns = [...root.querySelectorAll(".budget-fields label")].filter(visual).map(el=>{
       const [label,input]=el.children;
       const a=rect(label),b=rect(input);
       return {label:ref(label),labelWidth:a.w,inputWidth:b.w,centerOffset:round((a.y+a.h/2)-(b.y+b.h/2))};
    });
    const box=rect(root);
    const compare=root.querySelector(".compare-scroll");
    const sticky=root.querySelector(".budget-total");
    const screen=innerWidth;
    const mast=document.querySelector(".mast");
    const nav=document.querySelector(".city-subnav");
    const panels=[...root.querySelectorAll(":scope > *, tbody > tr, .compare-depth > section")].filter(visual)
      .filter(el=>el.getBoundingClientRect().bottom> Math.max(0,nav?.getBoundingClientRect()?.bottom||mast.getBoundingClientRect().bottom)
               && el.getBoundingClientRect().top < innerHeight).map(ref);
    return {box,viewport:[screen,innerHeight],left:box.x,right:round(screen-box.right),fontReady:document.fonts.status,
      paragraphs:Object.fromEntries(unique),alignment,interactive,columns,panels,scroll:scrollY,
      contrast:[".section-lead",".budget-total .meta",".budget-total strong",".budget-total .small","label small","tbody td"].map(contrast).filter(Boolean),
      rootOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
      table:compare?{client:compare.clientWidth,scroll:compare.scrollWidth,overflow:compare.scrollWidth-compare.clientWidth}:null,
      sticky:sticky?{box:rect(sticky),position:ap(sticky).position,mast:rect(mast),nav:rect(nav)}:null};
}"""

PROSE = {
  "budget":{"help":".section-lead,.budget-total p","label":".budget-fields label span,.budget-actions button,.car-costs summary", "title":"h2,.budget-total strong,#total-person"},
  "compare":{"help":".section-lead,.compare-budget-visual p,.compare-depth dd","label":".compare-controls label,summary,thead th,tbody th,tbody td","title":"h2"},
  "evidence":{"help":".section-lead,details > p,li","title":"h2,summary"}
}
RAILS = {
  "budget":[["section rail","h2,.section-lead,.budget-layout,.budget-actions","x"],
            ["field labels",".budget-fields > label > span","x"],
            ["amount input starts",".budget-fields input","x"],["amount input ends",".budget-fields input","right"]],
  "compare":[["section rail","h2,.section-lead,.compare-controls,.compare-budget-visual,.compare-scroll,.compare-details","x"],
             ["first/second label top",".compare-controls label","y"],["table first money column","thead th:nth-child(2),tbody td:nth-child(2)","x"],
             ["table second money column","thead th:nth-child(3),tbody td:nth-child(3)","x"]],
  "evidence":[["section rail","h2,.section-lead,details > summary","x"]]
}


def measure(page, area):
    return page.evaluate(MEASURE, {"selector": f"#{area}", "prose": PROSE[area], "groups": RAILS[area]})


def view(page, selector, margin):
    page.locator(selector).evaluate("(node,margin) => scrollTo(0,scrollY+node.getBoundingClientRect().top-margin)", margin)
    page.evaluate("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")


def shot(page, name):
    picture = Image.open(BytesIO(page.screenshot(animations="disabled",timeout=10000))).convert("RGB")
    picture.thumbnail((1440,1100))
    picture.save(AREA/"shots"/f"{name}.jpg",quality=81,optimize=True)


def calc(page):
    group = page.locator("#total-group").inner_text()
    return int("".join(ch for ch in group if ch.isdigit()))


STICKY_FOCUS = """()=> {
  const focus=document.activeElement;
  const bounds=focus.getBoundingClientRect();
  const card=document.querySelector(".budget-total").getBoundingClientRect();
  const nav=document.querySelector(".city-subnav").getBoundingClientRect();
  const cover=Math.max(0,Math.min(bounds.right,card.right)-Math.max(bounds.left,card.left))>0;
  return {id:focus.id||focus.textContent.trim(),top:Math.round(bounds.top),height:Math.round(bounds.height),
    cardBottom:Math.round(card.bottom),navBottom:Math.round(nav.bottom),
    maskedPx:cover?Math.round(Math.max(0,Math.min(bounds.bottom,card.bottom)-Math.max(bounds.top,card.top))):0};
}"""


def print_days(page):
    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
    page.emulate_media(media="print")
    trace={"openDays":page.locator(".day[open]").count(),"allDays":page.locator(".day").count()}
    page.emulate_media(media="screen")
    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
    trace["restoredDays"]=page.locator(".day[open]").count()
    return trace


def collect(browser, url, selected_widths, shots):
    data = {"browser":browser.version,"url":url,"language":"en LTR","widths":{}}
    for width,height in VIEWPORTS:
        if selected_widths and width not in selected_widths:
            continue
        context = browser.new_context(viewport={"width":width,"height":height},is_mobile=width<=667,
                                      has_touch=width<=667,device_scale_factor=1,reduced_motion="reduce")
        page = context.new_page()
        page.set_default_timeout(7000)
        page.goto(url,wait_until="domcontentloaded")
        page.evaluate("document.fonts.ready")
        size = {"width":width,"height":height,"budgets":{},"comparison":{},"sources":{}}
        for city in CITIES:
            page.locator(f'.city-tab[data-city="{city}"]').press("Enter")
            view(page,"#budget", 128)
            start = measure(page, "budget")
            if shots and (city == "baku" or (width in (320,390) and city=="budapest")):
                shot(page, f"{width}-budget-{city}")
            view(page,".budget-layout > div > .budget-fields", 114)
            page.locator("#cost-flight").press("Tab")
            focus=page.evaluate(STICKY_FOCUS)
            if shots and city=="baku" and width in (320,390):
                shot(page,f"{width}-budget-{city}-focus")
            first = calc(page)
            food = page.locator("#cost-food")
            old = int(food.input_value())
            food.fill(str(old+101))
            food.press("Tab")
            assert calc(page)==first+303
            status_after_edit=page.locator("#total p").inner_text()
            page.locator(".car-costs summary").press("Enter")
            page.locator("#cost-car").fill("349")
            page.locator("#cost-car").press("Tab")
            assert calc(page)==first+652
            view(page, ".car-costs", 128)
            open_rental=measure(page,"budget")
            overlap=page.evaluate("""() => {
              const b=document.querySelector(".budget-total").getBoundingClientRect();
              const s=document.querySelector(".car-costs summary").getBoundingClientRect();
              const right=Math.min(s.right,b.right), left=Math.max(s.left,b.left);
              return right > left
                ? Math.round(Math.max(0,Math.min(s.bottom,b.bottom)-Math.max(s.top,b.top))*100)/100 : 0;
            }""")
            if shots and city=="baku":
                shot(page,f"{width}-budget-{city}-rental")
            page.locator("#cost-fuel").fill("-3")
            page.locator("#cost-fuel").press("Tab")
            assert page.locator("#cost-fuel").input_value()=="0"
            page.locator("#cost-cover").fill("200000")
            page.locator("#cost-cover").press("Tab")
            assert page.locator("#cost-cover").input_value()=="150000"
            status_after_cap=page.locator("#total p").inner_text()
            page.locator("#cost-cover").fill("")
            page.locator("#cost-cover").press("Tab")
            assert page.locator("#cost-cover").input_value()=="0"
            page.locator("[data-reset]").press("Enter")
            assert calc(page)==first
            assert page.locator("[data-reset]").evaluate("node=>node===document.activeElement")
            size["budgets"][city]={"default":start,"rental":open_rental,"overlap":overlap,
                                   "totals":[first,first+303,first+652,calc(page)],
                                   "statusAfterEdit":status_after_edit,"statusAfterCap":status_after_cap,
                                   "focus":focus,"print":print_days(page)}
        view(page,"#compare", 72)
        size["comparison"]["default"]=measure(page,"compare")
        if shots:
            shot(page, f"{width}-compare")
            if width in (320,390):
                view(page,".compare-scroll",72)
                shot(page, f"{width}-compare-table")
        page.locator("#left-city").select_option("budapest")
        page.locator("#right-city").select_option("prague")
        page.locator(".compare-details summary").press("Enter")
        view(page,".compare-details", 72)
        size["comparison"]["expanded"]=measure(page,"compare")
        if shots:
            shot(page, f"{width}-compare-expanded")
        for city in CITIES:
            page.locator("#left-city").select_option(city)
            page.locator("#right-city").select_option(city)
            assert page.locator(".compare-details").get_attribute("open") is not None
            size["comparison"][f"same-{city}"]=measure(page,"compare")
        view(page,"#evidence", 72)
        size["sources"]["closed"]=measure(page,"evidence")
        if shots:
            shot(page,f"{width}-sources")
        for i in range(page.locator("#evidence summary").count()):
            panel=page.locator("#evidence details").nth(i)
            summary=panel.locator("summary")
            summary.press("Enter")
            key=summary.inner_text()
            panel.evaluate("(node)=>scrollTo(0,scrollY+node.getBoundingClientRect().top-72)")
            size["sources"][key]=measure(page,"evidence")
            if shots and i in (0,5,6):
                shot(page,f"{width}-sources-panel{i}")
            summary.press("Enter")
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        page.emulate_media(media="print")
        size["print"]={"openDays":page.locator(".day[open]").count(),
                       "allDays":page.locator(".day").count(),
                       "budget":measure(page,"budget"),"compare":measure(page,"compare")}
        view(page, "#budget", 10)
        if shots:
            shot(page,f"{width}-print")
        page.emulate_media(media="screen")
        page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        size["print"]["restoredDays"]=page.locator(".day[open]").count()
        data["widths"][width]=size
        context.close()
        print("measured",width)
    return data


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url",default=URL)
    parser.add_argument("--widths",nargs="*",type=int)
    parser.add_argument("--no-shots",action="store_true")
    parser.add_argument("--output",default="planning-metrics.json")
    args=parser.parse_args()
    with sync_playwright() as p:
        browser=p.chromium.launch(channel="chrome")
        evidence=collect(browser,args.url,args.widths,not args.no_shots)
        browser.close()
    (AREA/args.output).write_bytes((json.dumps(evidence,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf-8"))
