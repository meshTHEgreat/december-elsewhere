"""Fresh-browser regression pass for the delivered file. Usage: python source/verify.py output.json."""
import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
rep = {}
url = (root / 'index.html').as_uri()
with sync_playwright() as runner:
    chromium_path = os.environ.get('DECEMBER_CHROMIUM_PATH')
    options = {'executable_path': chromium_path} if chromium_path else {}
    browser = runner.chromium.launch(**options)
    for width, height in [(1440, 900), (390, 844), (768, 1024)]:
        ctx = browser.new_context(offline=True, viewport={'width':width,'height':height}, reduced_motion='reduce',
                                  is_mobile=width==390, has_touch=width==390)
        page = ctx.new_page()
        errors, request_urls = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda msg: errors.append(msg.text) if msg.type=='error' else None)
        page.on('request', lambda req: request_urls.append(req.url) if req.url.startswith(('http:', 'https:')) else None)
        page.goto(url, wait_until='load')
        assert page.title().startswith('December')
        assert page.locator('.city-tab').count()==5
        page.evaluate('document.fonts.ready')
        city_details=[]
        for i in range(5):
            button = page.locator('.city-tab').nth(i)
            if width == 390:
                button.tap()
            else:
                button.focus()
                button.press('Enter')
            assert page.locator('.chapter .backdrop').evaluate(
                "async image => { await image.decode(); return image.naturalWidth > 0; }"
            )
            assert page.locator('.stay').count()>=2
            assert page.locator('.day').count()>=6
            page.locator('.day summary').nth(1).click()
            assert page.locator('.day').nth(1).get_attribute('open') is not None
            assert page.locator('.mapbox polyline').count()>0
            if page.locator('[data-route]').count()>1:
                disclosure = page.locator('.walk-list-disclosure summary')
                if disclosure.is_visible():
                    disclosure.click()
                page.locator('[data-route="1"]').click()
                assert page.locator('[data-route="1"]').get_attribute('aria-pressed')=='true'
            if page.locator('#anchor-select option').count()>1:
                page.locator('#anchor-select').select_option(index=1)
                assert page.locator('#anchor-select').evaluate('(s)=>s.selectedIndex')==1
            if page.locator('[data-gallery="1"]').count():
                page.locator('[data-gallery="1"]').click()
                assert '2 /' in page.locator('.gallery-tools').inner_text()
            page.locator('[data-stay="1"]').click()
            assert page.locator('[data-stay="1"]').get_attribute('aria-pressed')=='true'
            read_total=lambda: int(page.locator('#total-group').inner_text().split()[-1].replace(',',''))
            previous=read_total()
            field=page.locator('#cost-food')
            field.fill(str(int(field.input_value())+101))
            assert read_total()==previous+303
            previous=read_total()
            page.locator('.car-costs summary').click()
            page.locator('#cost-car').fill('300')
            assert read_total()==previous+300
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 2')
            city_details.append({'city':page.locator('#chapter h2').inner_text(),'stays':page.locator('.stay').count(),'days':page.locator('.day').count()})
        page.locator('#left-city').select_option('vienna')
        assert page.locator('#compare th').nth(1).inner_text()=='Vienna'
        page.reload(wait_until='load')
        assert page.locator('#chapter h2').inner_text()=='Prague'
        assert page.locator('#cost-car').input_value()=='300'
        assert page.locator('#left-city').input_value()=='vienna'
        page.locator('[data-reset]').click()
        assert page.locator('.car-costs').get_attribute('open') is None
        assert page.locator('#cost-car').input_value()=='0'
        assert not errors, errors
        assert not request_urls, request_urls
        rep[str(width)]={'cities':city_details,'network_requests':len(request_urls),'console_errors':len(errors),
                         'fresh_context':True,'persistence':True,'offline':True,'budget_and_map_interactions':True}
        ctx.close()
    rep['browser']=browser.version
    browser.close()
Path(sys.argv[1]).write_text(json.dumps(rep, indent=2)+'\n')
print(json.dumps(rep,indent=2))
