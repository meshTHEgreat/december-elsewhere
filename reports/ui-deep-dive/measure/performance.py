"""Measure cold phone loads against the supplied hosted build."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("url")
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
observations = []

with sync_playwright() as runner:
    browser = runner.chromium.launch(channel="chrome")
    for attempt in range(3):
        context = browser.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        context.add_init_script("""window.metrics={lcp:0,cls:0};
          new PerformanceObserver(list=>{for(const e of list.getEntries()) window.metrics.lcp=Math.round(e.startTime)})
            .observe({type:'largest-contentful-paint',buffered:true});
          new PerformanceObserver(list=>{for(const e of list.getEntries()) if(!e.hadRecentInput) window.metrics.cls+=e.value})
            .observe({type:'layout-shift',buffered:true});""")
        page = context.new_page()
        session = context.new_cdp_session(page)
        session.send("Emulation.setCPUThrottlingRate", {"rate":4})
        session.send("Network.enable")
        session.send("Network.setCacheDisabled", {"cacheDisabled":True})
        session.send("Network.emulateNetworkConditions", {"offline":False, "latency":150,
                     "downloadThroughput":200000, "uploadThroughput":93750, "connectionType":"cellular4g"})
        page.goto(args.url, wait_until="load")
        page.evaluate("document.fonts.ready")
        page.evaluate("new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
        initial = page.evaluate("""()=>{
           const nav=performance.getEntriesByType('navigation')[0], res=performance.getEntriesByType('resource');
           return {...window.metrics, documentReadyMs:Math.round(nav.domContentLoadedEventEnd),
                    transferredBytes:nav.transferSize+res.reduce((total,item)=>total+item.transferSize,0),
                    lazyLibraries:!res.some(item=>item.name.endsWith('globe.js')||item.name.endsWith('winter-stage.js'))};
        }""")
        observations.append(initial)
        context.close()
    browser.close()

data = {"url":args.url,"viewport":[390,844],"cpuThrottle":4,"latencyMs":150,"downstreamMbps":1.6,
        "browser":"Chrome with Playwright, fresh context per observation","observations":observations}
args.output.write_bytes((json.dumps(data,indent=2) + "\n").encode("utf-8"))
