"""Sample the combined release in fresh Chrome contexts and replay landscape hot spots."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from playwright.sync_api import expect, sync_playwright


OUT = Path(__file__).resolve().parent
GUIDED = OUT.parents[3] / 'december-guided'
WEB = 'http://127.0.0.1:18771/december-elsewhere/'
OFFLINE = (GUIDED / 'index.html').as_uri()
HASHES = {
    'web': 'cc8cdb7db4b3e055b16aff121cc69b09838be0ae8b57cb4d25fa40c5e131177c',
    'offline': '97fb156c67024730f0894985a7a27dcf2351d46245720b4e84fec26c4539fe2b',
}
BOOKING = ('https://www.getyourguide.com/baku-l1408/'
           'baku-gobustan-mud-volcano-fire-mount-temple-lunch-entry-t517765/')
BASELINES = {'baku': 8, 'tbilisi': 7, 'budapest': 8, 'vienna': 8, 'prague': 6}

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('landscape_review', OUT.parent / 'round-4' / 'chrome_review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
review.ROOT = GUIDED


def budget(page):
    return page.evaluate('''() => ({
      person: document.querySelector('#total-person').textContent,
      group: document.querySelector('#total-group').textContent,
      fields: [...document.querySelectorAll('#budget [data-cost]')].map(input => input.value)
    })''')


def frame_under_navigation(locator):
    locator.evaluate('''node => {
      const nav = document.querySelector('.city-subnav').getBoundingClientRect();
      scrollBy(0, node.getBoundingClientRect().top - nav.bottom - 14);
    }''')


def sample(browser, url, edition):
    page, traffic = review.make_page(browser, url, (390, 844))
    response = review.go(page, url + '#baku/itinerary')
    assert hashlib.sha256(response.body()).hexdigest() == HASHES[edition]
    records = []
    for city, days in BASELINES.items():
        if city != 'baku':
            page.goto(f'{url}#{city}/itinerary')
        expect(page.locator('#itinerary h2')).to_be_focused()
        expect(page.locator('.day')).to_have_count(days)
        guide = page.locator('#itinerary #guides')
        summary = guide.locator(':scope > summary')
        day = guide.locator('[data-guide-plan=day]')
        night = guide.locator('[data-guide-plan=night]')
        initial = budget(page)
        assert guide.get_attribute('open') is None
        expect(day.locator('h3')).to_be_hidden()
        expect(night.locator('h3')).to_be_hidden()
        summary.tap()
        expect(guide).to_have_attribute('open', '')
        if day.get_attribute('open') is None:
            day.locator('summary').press('Enter')
        expect(day.locator('h3')).to_be_visible()
        expect(night.locator('h3')).to_be_hidden()
        day_title = day.locator('h3').inner_text()
        if city == 'baku':
            assert day_title == 'Gobustan and the fire peninsula'
            expect(day.locator('.guided-journey li')).to_have_text(['Baku', 'Gobustan', 'Absheron', 'Baku'])
            link = day.get_by_role('link', name='Open your Baku tour on GetYourGuide')
            expect(link).to_have_attribute('href', BOOKING)
            expect(link).to_have_attribute('target', '_blank')
            if edition == 'web':
                frame_under_navigation(summary)
                review.visible(link, 390, 844, hit_test=True)
                page.screenshot(path=OUT / '390-baku-guide-day.png', animations='disabled')
        night.locator('summary').press('Enter')
        expect(night.locator('h3')).to_be_visible()
        expect(day.locator('h3')).to_be_hidden()
        night_title = night.locator('h3').inner_text()
        if city == 'baku':
            assert night_title == 'Sleep near Shahdag'
            expect(night.locator('.guided-journey li')).to_have_text(['Baku', 'Qusar or Shahdag', 'Laza if open', 'Baku'])
            if edition == 'web':
                frame_under_navigation(night.locator('summary'))
                page.screenshot(path=OUT / '390-baku-guide-night.png', animations='disabled')
        assert budget(page) == initial, city
        page.emulate_media(media='print')
        expect(guide).to_be_hidden()
        page.emulate_media(media='screen')
        update = guide.get_by_role('link', name='Update the budget')
        update.press('Enter')
        expect(page.locator('#budget h2')).to_be_focused()
        assert budget(page) == initial, city
        records.append({'city': city, 'days': days, 'day': day_title, 'night': night_title,
                        'budget_per_adult': initial['person'], 'budget_total': initial['group']})
    return {'canonical_baku_url': BOOKING, 'cities': records, **review.end(page, url, traffic)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('edition', choices=['web', 'offline'])
    args = parser.parse_args()
    url = WEB if args.edition == 'web' else OFFLINE
    with sync_playwright() as driver:
        browser = driver.chromium.launch(channel='chrome')
        output = {'browser': browser.version, 'url': url, 'sha256': HASHES[args.edition]}
        tasks = {
            'guide_sample': lambda: sample(browser, url, args.edition),
            'landscape_preview': lambda: review.landscape(browser, url, 'combined'),
            'stage_runtime_failure': lambda: review.runtime_error(browser, url),
            'landscape_photos': lambda: review.photo_actions(browser, url),
            'atlas': lambda: review.atlas(browser, url, 'combined'),
            'atlas_fallback': lambda: review.atlas(browser, url, 'combined', unavailable=True),
            'budget_compare_and_print': lambda: review.planning(browser, url, 'combined'),
        }
        for name, test in tasks.items():
            output[name] = test()
            print(f'{args.edition} {name}: passed', flush=True)
        browser.close()
    (OUT / f'sample-{args.edition}.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
