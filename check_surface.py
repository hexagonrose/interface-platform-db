"""Exercise every uploaded phase and its Wulff models before deploying Pages."""
import json
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import expect, sync_playwright


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


site = Path(sys.argv[1])
records = json.loads((site / 'catalog.json').read_text())['records']
with ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=site)) as server, sync_playwright() as pw:
    Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'
    browser = pw.chromium.launch(executable_path=os.getenv('INTERFACE_CHROMIUM'), args=['--no-sandbox'])
    page = browser.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    for width in (390, 1440):
        page.set_viewport_size({'width':width, 'height':900})
        page.goto(url + '#interface')
        for record in records:
            if record['kind'] != 'surface' or len(record['materials'][0]) > 2:
                continue
            page.goto(url + '#' + record['id'])
            expect(page.locator('#title')).to_have_text(record['title'])
            expect(page.locator('#surface-load-status')).to_be_hidden()
            for model in record.get('wulff_comparison', {}):
                button = page.locator(f'[data-series-model="{model}"]')
                button.click()
                expect(button).to_have_attribute('aria-pressed', 'true')
                assert page.locator('#crystal-shape polygon').count() > 0
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), record['id']
        phase = next(r for r in records if r['id']=='gphase-surface-structures')
        page.goto(url + '#' + phase['id'])
        expect(page.locator('#title')).to_have_text(phase['title'])
        expect(page.locator('#value')).to_contain_text('양면 평균')
        page.locator('#view-slab').click()
        for facet in phase['surfaces']:
            page.locator('#facet-picker').select_option(facet['facet'])
            expect(page.locator('#slab-description')).to_contain_text('두 면 평균')
            assert page.evaluate('selectedFacet.atoms') == facet['atoms']
        for model in ('omni', 'nano', 'mace'):
            page.goto(url + '#grain-boundary?type=twist&model=' + model)
            expect(page.locator('#gb-map-title')).to_have_text('Σ5 Twist · 강체 이동 PES')
            gamma = json.loads((site/'catalog.json').read_text())['grain_boundary_models'][model]['twist']['gamma']
            expect(page.locator('#gb-map-value')).to_contain_text(f'{gamma:.3f} J/m²')
            page.locator('#gb-a').press('ArrowRight')
            expect(page.locator('#gb-map-value')).to_contain_text('Δγ')
        page.locator('#tab-solute').click()
        expect(page.locator('#tab-solute')).to_have_attribute('aria-selected', 'true')
    assert not errors, errors
