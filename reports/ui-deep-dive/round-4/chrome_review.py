"""Independent mobile geometry, interaction, and runtime checks for both packages."""

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
WIDTHS = ((320, 725), (390, 844), (667, 375), (768, 1024), (1440, 900), (2560, 1440))
SCENES = {
    'baku': ('Baku', 'Shahdag', 'Tufandag'),
    'overview': ('Baku', 'Tbilisi', 'Budapest', 'Vienna', 'Prague'),
}
HASH = {
    'web': '7f11a5268987a9e14ad12336378be0e0f160b8ca111b90b58af1978001d51715',
    'offline': '810972ed812b0dbd348b99f06c95d9f77c356a5af2d48a5397a44a232aa976e4',
}


def make_page(browser, url, sizes, reduced=True):
    width, height = sizes
    context = browser.new_context(
        offline=url.startswith('file:'), is_mobile=width < 740, has_touch=width < 740,
        viewport={'width': width, 'height': height}, accept_downloads=True,
        reduced_motion='reduce' if reduced else 'no-preference',
    )
    page = context.new_page()
    page.set_default_timeout(6500)
    traffic = {'http': [], 'errors': [], 'failed': []}
    page.on('request', lambda request: traffic['http'].append(request.url)
            if request.url.startswith(('http:', 'https:')) else None)
    page.on('response', lambda response: traffic['errors'].append(f'{response.status} {response.url}')
            if response.status >= 400 else None)
    page.on('requestfailed', lambda request: traffic['failed'].append((request.url[:160], request.failure)))
    page.on('pageerror', lambda error: traffic['errors'].append(str(error)))
    page.on('console', lambda message: traffic['errors'].append(message.text) if message.type == 'error' else None)
    return page, traffic


def go(page, url):
    response = page.goto(url, wait_until='domcontentloaded')
    assert response and response.ok, url
    page.evaluate('document.fonts.ready')
    assert page.evaluate('document.documentElement.scrollWidth === innerWidth'), url
    return response


def end(page, url, traffic):
    assert not traffic['errors'] and not traffic['failed'], traffic
    assert all(urlparse(path).netloc == urlparse(url).netloc for path in traffic['http']), traffic
    if url.startswith('file:'):
        assert not traffic['http'], traffic
    page.context.close()
    return {'http_requests': len(traffic['http']), 'errors': traffic['errors']}


def alignment(browser, url, edition):
    output = []
    for width, height in WIDTHS:
        page, traffic = make_page(browser, url, (width, height))
        response = go(page, url)
        assert hashlib.sha256(response.body()).hexdigest() == HASH[edition]
        values = page.evaluate('''() => {
          const box = element => element.getBoundingClientRect();
          const bounds = selector => box(document.querySelector(selector));
          const links = [...document.querySelectorAll('.mast nav a, .chapter-jumps a')]
            .map(box).filter(rect => rect.width && rect.height);
          return {
            names: [...document.querySelectorAll('.city-name')].map(element => box(element).left),
            atlas: [bounds('.atlas-layout').left, bounds('.atlas-layout').right],
            budgetY: [bounds('#total-person').top, bounds('#total-group').top],
            minimumLink: Math.min(...links.flatMap(rect => [rect.width, rect.height])),
            screen: [innerWidth, innerHeight, document.documentElement.scrollWidth],
            coverFactsBottom: bounds('.cover-facts').bottom,
          };
        }''')
        assert len(values['names']) == 5 and max(values['names']) - min(values['names']) <= 1, values
        assert abs(values['atlas'][0] + values['atlas'][1] - width) <= 2, values
        assert values['minimumLink'] >= 44 and values['screen'] == [width, height, width], values
        assert values['coverFactsBottom'] <= height, values
        if width <= 390:
            assert abs(values['budgetY'][0] - values['budgetY'][1]) <= 1, values
        if edition == 'web' and width == 320:
            page.locator('.hero .backdrop').evaluate('image => image.decode()')
            page.screenshot(path=OUT / '320-cover.png', animations='disabled')
        output.append({'size': [width, height], **values, **end(page, url, traffic)})
    return output


def visible(locator, width, height, top=0, hit_test=False):
    rect = locator.evaluate('''(element, check) => {
      const {top, right, bottom, left, width, height} = element.getBoundingClientRect();
      const points = [[left + 4, top + 4], [right - 4, top + 4], [left + 4, bottom - 4],
        [right - 4, bottom - 4], [left + width / 2, top + height / 2]];
      return {top, right, bottom, left, width, height,
        hit: !check || points.every(([x,y]) => element.contains(document.elementFromPoint(x, y)))};
    }''', hit_test)
    assert rect['width'] > 0 and rect['height'] > 0, rect
    assert rect['top'] >= top - 0.5 and rect['bottom'] <= height + 0.5, rect
    assert rect['left'] >= -0.5 and rect['right'] <= width + 0.5 and rect['hit'], rect
    if hit_test:
        assert rect['width'] >= 44 and rect['height'] >= 44, rect
    return rect


def landscape(browser, url, edition):
    page, traffic = make_page(browser, url, (667, 375))
    go(page, url + '#baku/winter')
    panel = page.locator('#winter-film')
    stage = panel.locator('.ss-stage')
    close = panel.get_by_role('button', name='Close preview')
    active = panel.locator('.wf-story-beat[data-current=yes]')
    output = []
    for name, scenes in SCENES.items():
        trigger = page.locator(f'[data-winter-film={name}]')
        trigger.tap()
        expect(close).to_be_focused()
        expect(active.locator('h3')).to_have_text(scenes[-1])
        buttons = panel.locator('[data-winter-scene]')
        expect(buttons).to_have_count(len(scenes))
        expect(buttons).to_have_text(list(scenes))
        buttons.first.tap()
        expect(buttons.first).to_be_focused()
        expect(active.locator('h3')).to_have_text(scenes[0])
        page.keyboard.press('Shift+Tab')
        expect(close).to_be_focused()
        nav_bottom = page.locator('.city-subnav').evaluate('node => node.getBoundingClientRect().bottom')
        close_box = visible(close, 667, 375, nav_bottom, hit_test=True)
        stage_box = visible(stage, 667, 375, nav_bottom)
        controls = [visible(button, 667, 375, nav_bottom, hit_test=True) for button in buttons.all()]
        assert stage_box['right'] <= close_box['left'], (stage_box, close_box)
        if edition == 'web':
            page.screenshot(path=OUT / f'667-{name}-reverse-focus.png', animations='disabled')
        for title, button in zip(scenes, buttons.all()):
            button.press('Enter')
            expect(active.locator('h3')).to_have_text(title)
            expect(button).to_have_attribute('aria-pressed', 'true')
            assert active.evaluate('''beat => {
              const bounds = el => el.getBoundingClientRect();
              const detail = bounds(beat.querySelector('.wf-story-detail'));
              const track = bounds(beat.parentElement.closest('.wf-story-editorial').querySelector('.wf-story-track'));
              const stage = bounds(beat.closest('.ss-stage'));
              return detail.bottom < track.top && track.bottom <= stage.bottom;
            }'''), (name, title)
        if name == 'baku':
            page.keyboard.press('Escape')
        else:
            close.tap()
        expect(panel).to_be_hidden()
        expect(stage).to_have_count(0)
        expect(trigger).to_be_focused()
        output.append({'mode': name, 'scene_titles': scenes, 'nav_bottom': nav_bottom, 'close': close_box,
                       'stage': stage_box, 'scene_controls': controls})
    return {'modes': output, **end(page, url, traffic)}


def playback(browser, url):
    page, traffic = make_page(browser, url, (390, 844), reduced=False)
    go(page, url + '#baku/winter')
    active = page.locator('.wf-story-beat[data-current=yes] h3')
    output = []
    for name, scenes in SCENES.items():
        trigger = page.locator(f'[data-winter-film={name}]')
        trigger.press('Enter')
        expect(active).to_have_text(scenes[0])
        expect(active).to_have_text(scenes[1], timeout=6500)
        page.locator('[data-winter-scene]').first.tap()
        expect(active).to_have_text(scenes[0])
        page.wait_for_timeout(3900)
        expect(active).to_have_text(scenes[0])
        page.locator('[data-winter-close]').press('Enter')
        expect(trigger).to_be_focused()
        output.append({'mode': name, 'advanced': scenes[1], 'manual_held': scenes[0]})
    return {'modes': output, **end(page, url, traffic)}


def runtime_error(browser, url):
    page, traffic = make_page(browser, url, (390, 844))
    go(page, url + '#baku/winter')
    page.evaluate('''() => { window.DecemberWinterStage = { mount() { throw Error('Test mount failure'); } }; }''')
    trigger = page.locator('[data-winter-film=baku]')
    trigger.press('Enter')
    notice = page.locator('#winter-film-message')
    expect(notice).to_have_text('Preview unavailable. Read the winter plans above.')
    expect(notice).to_be_visible()
    expect(page.locator('#winter-film')).to_be_hidden()
    expect(page.locator('.ss-stage')).to_have_count(0)
    expect(trigger).to_be_focused()
    assert trigger.get_attribute('aria-busy') is None
    return {'message': notice.inner_text(), **end(page, url, traffic)}


def photo_actions(browser, url):
    page, traffic = make_page(browser, url, (667, 375))
    go(page, url)
    dialog = page.locator('#photo-dialog')
    image = dialog.locator('img')
    close = dialog.locator('[data-photo-close]')
    previous = dialog.locator('[data-gallery="-1"]')
    following = dialog.locator('[data-gallery="1"]')
    download = dialog.locator('.photo-download')
    photos = page.evaluate('''() => {
      const book = JSON.parse(document.getElementById('dataset').textContent);
      return Object.fromEntries(Object.entries(book.photos)
        .map(([city, images]) => [city, images.map(({file}) => file)]));
    }''')
    for city, files in photos.items():
        page.locator(f'.city-tab[data-city={city}]').tap()
        trigger = page.locator('#gallery [data-photo-open]')
        trigger.tap()
        expect(dialog).to_be_visible()
        previous.tap()
        expect(download).to_have_attribute('download', files[-1])
        following.tap()
        for filename in files:
            expect(download).to_have_attribute('download', filename)
            image.evaluate('node => node.decode()')
            for action in (close, previous, following, download):
                visible(action, 667, 375, hit_test=True)
            with page.expect_download() as event:
                download.tap()
            received = event.value
            assert received.suggested_filename == filename, received.suggested_filename
            assert received.path().read_bytes() == (ROOT / 'assets' / filename).read_bytes(), filename
            following.tap()
        expect(download).to_have_attribute('download', files[0])
        close.tap()
        expect(dialog).to_be_hidden()
        expect(trigger).to_be_focused()
    assert sum(map(len, photos.values())) == 24, photos
    return {'downloads_matched_packaged_bytes': photos, **end(page, url, traffic)}


def atlas(browser, url, edition, unavailable=False):
    page, traffic = make_page(browser, url, (390, 844))
    if unavailable:
        page.add_init_script('''const context = HTMLCanvasElement.prototype.getContext;
          HTMLCanvasElement.prototype.getContext = function (mode, ...args) {
            return mode.startsWith('webgl') ? null : context.call(this, mode, ...args);
          };''')
    go(page, url)
    shortcut = page.get_by_role('link', name='Map & globe')
    shortcut.press('Enter')
    expect(page.locator('#atlas-panel')).to_be_focused()
    page.keyboard.press('Tab')
    chooser = page.get_by_label('City on map')
    expect(chooser).to_be_focused()
    chooser.select_option('vienna')
    toggle = page.locator('#atlas-toggle')
    toggle.tap()
    if unavailable:
        expect(page.locator('#atlas-feedback')).to_have_text('Globe unavailable. Use the map.')
        expect(page.locator('#atlas-flat svg')).to_be_visible()
        expect(page.locator('#atlas-globe canvas')).to_have_count(0)
    else:
        expect(page.locator('#atlas-globe canvas')).to_be_visible()
        expect(page.locator('.globe-pin.is-active')).to_have_text('Vienna')
        if edition == 'web':
            page.screenshot(path=OUT / '390-mobile-globe.png', animations='disabled')
    page.locator('[data-open-preview]').tap()
    heading = page.locator('#chapter h2')
    expect(heading).to_have_text('Vienna')
    expect(heading).to_be_focused()
    expect(page.locator('#atlas-globe canvas')).to_have_count(0)
    assert page.url.endswith('#vienna')
    return {'fallback': unavailable, 'city': heading.inner_text(), **end(page, url, traffic)}


def planning(browser, url, edition):
    page, traffic = make_page(browser, url, (320, 725))
    go(page, url + '#baku/budget')
    expect(page.locator('#budget h2')).to_be_focused()
    page.locator('#cost-food').fill('1044')
    updated = page.locator('#total-person').inner_text()
    assert updated.startswith('SAR ')
    page.locator('.mast [href="#compare"]').press('Enter')
    page.locator('#left-city').select_option('baku')
    page.locator('#right-city').select_option('prague')
    expect(page.locator('#compare-0-person')).to_have_text(updated)
    expect(page.locator('#compare-mark-value-0')).to_have_text(updated)
    page.goto(url + '#baku/itinerary')
    expect(page.locator('#itinerary h2')).to_be_focused()
    days = page.locator('.day').count()
    opened = page.locator('.day[open]').count()
    page.evaluate('''() => { window.printEvents = []; for (const name of ['beforeprint','afterprint']) {
      addEventListener(name, () => printEvents.push([name, document.querySelectorAll('.day[open]').length]));
    } }''')
    result = page.pdf(format='A4')
    assert result.startswith(b'%PDF-') and len(result) > 20000
    assert page.evaluate('printEvents') == [['beforeprint', days], ['afterprint', opened]]
    return {'budget_per_adult': updated, 'printed_days': days, 'open_after_print': opened,
            'pdf_bytes': len(result), **end(page, url, traffic)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', choices=['web', 'offline'], required=True)
    parser.add_argument('--url', default='http://127.0.0.1:18768/')
    parser.add_argument('--only', choices=['landscape', 'alignment', 'playback', 'runtime_error', 'photo_actions', 'atlas',
                                         'map_fallback', 'planning'])
    args = parser.parse_args()
    url = args.url if args.edition == 'web' else (ROOT / 'index.html').as_uri()
    checks = {
        'landscape': lambda browser: landscape(browser, url, args.edition),
        'alignment': lambda browser: alignment(browser, url, args.edition),
        'playback': lambda browser: playback(browser, url),
        'runtime_error': lambda browser: runtime_error(browser, url),
        'photo_actions': lambda browser: photo_actions(browser, url),
        'atlas': lambda browser: atlas(browser, url, args.edition),
        'map_fallback': lambda browser: atlas(browser, url, args.edition, unavailable=True),
        'planning': lambda browser: planning(browser, url, args.edition),
    }
    with sync_playwright() as driver:
        browser = driver.chromium.launch(channel='chrome')
        report = {'browser': browser.version, 'edition': args.edition, 'url': url, 'sha256': HASH[args.edition]}
        for name, check in checks.items():
            if not args.only or name == args.only:
                report[name] = check(browser)
                print(f'{args.edition} {name}: passed', flush=True)
        browser.close()
    suffix = f'-{args.only}' if args.only else ''
    (OUT / f'independent-{args.edition}{suffix}.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
