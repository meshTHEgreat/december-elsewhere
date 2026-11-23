"""Run the existing premium checks at all review widths, phone first."""
import hashlib
import json
import sys
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "source"))
import verify_premium as suite


def main(edition):
    url = "http://127.0.0.1:18768/" if edition == "online" else (ROOT / "index.html").as_uri()
    with urlopen(url) as response:
        sha256 = hashlib.sha256(response.read()).hexdigest()
    matrix = [(320, 725, True, True), (390, 844, True, False), (667, 375, True, True),
              (768, 1024, False, True), (1440, 900, False, False), (2560, 1440, False, False)]
    output = HERE / f"premium-{edition}"
    output.mkdir(exist_ok=True)
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel="chrome")
        evidence = {"browser": browser.version, "url": url, "sha256": sha256, "results": []}
        for device in matrix:
            row = suite.check_page(browser, url, *device, output)
            evidence["results"].append(row)
            print(json.dumps(row), flush=True)
        suite.check_fallback(browser, url)
        evidence["fallback"] = "passed"
        browser.close()
    (HERE / f"premium-rehearsal-{edition}.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
