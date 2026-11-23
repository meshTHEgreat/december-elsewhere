"""Run the installed Taste inspector on the guide's rendered opening and chapter."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--inspector", type=Path, required=True)
parser.add_argument("--url", default="http://127.0.0.1:18768/")
args = parser.parse_args()
inspect = args.inspector.read_text(encoding="utf-8") + "\n; window.lyCheck()"

with sync_playwright() as runner:
    browser = runner.chromium.launch(channel="chrome")
    output = {"browser": browser.version, "url": args.url, "sizes":[]}
    for width, height in ((320,725),(390,844),(667,375),(768,1024),(1440,900),(2560,1440)):
        ctx = browser.new_context(viewport={"width":width,"height":height}, reduced_motion="reduce")
        page = ctx.new_page()
        page.goto(args.url, wait_until="domcontentloaded")
        page.evaluate("document.fonts.ready")
        state = page.evaluate(inspect)
        state["documentOverflow"] = page.evaluate("document.documentElement.scrollWidth-innerWidth")
        state["coverActionFits"] = page.locator(".hero .cover-action").evaluate("n=>n.getBoundingClientRect().bottom<=innerHeight")
        output["sizes"].append(state)
        ctx.close()
    browser.close()
(HERE/"taste-layout-final.json").write_bytes((json.dumps(output,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
for state in output["sizes"]:
    print(state["vw"],state["vh"],len(state["findings"]),state["documentOverflow"],state["coverActionFits"])
