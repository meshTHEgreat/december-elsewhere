"""Tab through the edited budgets with settled sticky chrome."""

import json
from playwright.sync_api import sync_playwright
from review_photos import FRAME, HERE, ROOT, SIZES


def inspect(browser, url, size):
    width, height = size
    context = browser.new_context(viewport={"width": width, "height": height}, offline=url.startswith('file:'),
                                  is_mobile=True, has_touch=True, reduced_motion='no-preference', locale='en-US')
    page = context.new_page()
    page.goto(url + '#baku/budget', wait_until='domcontentloaded')
    page.evaluate('document.fonts.ready')
    page.locator('#budget .car-costs summary').press('Enter')
    for field in page.locator('#budget [data-cost]').all():
        field.fill('150000')
    page.locator('#budget h2').focus()
    controls = []
    for _ in range(page.locator('#budget input, #budget button, #budget summary').count()):
        page.keyboard.press('Tab')
        page.evaluate(FRAME)
        observe = page.evaluate("""() => {
            const el = document.activeElement;
            const {left, right, top, bottom} = el.getBoundingClientRect();
            const x = (left + right) / 2;
            return {name: el.id || el.textContent.trim(), top, bottom, budget: !!el.closest('#budget'),
                visible: [top + 2, bottom - 2].every(y => el.contains(document.elementFromPoint(x, y)))};
        }""")
        controls.append(observe)
    context.close()
    return {'size': size, 'controls': controls}


def main():
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel='chrome')
        result = {}
        for edition, url in [('online', 'http://127.0.0.1:18768/'), ('offline', (ROOT / 'index.html').as_uri())]:
            result[edition] = [inspect(browser, url, size) for size in SIZES]
        (HERE / 'budget-focus.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        browser.close()
    fails = [(edition, row['size'], entry) for edition, rows in result.items() for row in rows
             for entry in row['controls'] if not (entry['budget'] and entry['visible'])]
    print(json.dumps(fails))
    assert not fails, fails


if __name__ == '__main__':
    main()
