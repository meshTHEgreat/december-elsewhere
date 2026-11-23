"""Run the premium browser release checks on the six frozen viewports."""

import hashlib
import json
import sys
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'source'))
from verify_premium import check_fallback, check_page


VIEWS = [(320, 725, True, True), (390, 844, True, False), (667, 375, True, True),
         (768, 1024, False, True), (1440, 900, False, False), (2560, 1440, False, False)]


def main(edition):
    url = 'http://127.0.0.1:18768/' if edition == 'online' else (ROOT / 'index.html').as_uri()
    with urlopen(url) as response:
        sha256 = hashlib.sha256(response.read()).hexdigest()
    output = HERE / f'premium-{edition}.json'
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel='chrome')
        results = {'browser': browser.version, 'url': url, 'sha256': sha256, 'results': []}
        for view in VIEWS:
            state = check_page(browser, url, *view, None)
            results['results'].append(state)
            output.write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
            print(json.dumps(state), flush=True)
        check_fallback(browser, url)
        results['fallback'] = 'passed'
        output.write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
        browser.close()


if __name__ == '__main__':
    main(sys.argv[1])
