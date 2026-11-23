"""Browser checks for the mobile atlas shortcut, loading, and map recovery."""
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import sys
import unittest

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        if not isinstance(sys.exception(), ConnectionError):
            super().handle_error(request, client_address)


@contextmanager
def local_site():
    with QuietServer(("127.0.0.1", 0), partial(QuietHandler, directory=ROOT / "docs")) as server:
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}/"
        finally:
            server.shutdown()
            worker.join()


class AtlasUiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = local_site()
        cls.url = cls.site.__enter__()
        cls.addClassCleanup(cls.site.__exit__, None, None, None)
        cls.runner = sync_playwright().start()
        cls.addClassCleanup(cls.runner.stop)
        cls.browser = cls.runner.chromium.launch(channel="chrome")
        cls.addClassCleanup(cls.browser.close)

    def page(self, width=390, height=844):
        context = self.browser.new_context(
            viewport={"width": width, "height": height},
            is_mobile=True, has_touch=True, reduced_motion="reduce",
        )
        self.addCleanup(context.close)
        page = context.new_page()
        page.set_default_timeout(5000)
        page.goto(self.url)
        return page

    def test_shortcut_structure_and_keyboard_focus(self):
        template = (ROOT / "source/index.template").read_text(encoding="utf-8")
        self.assertTrue('class="atlas-jump" href="#atlas-panel"' in template, 'Missing map shortcut in the source template')
        self.assertRegex(template, r'class="atlas-panel" id="atlas-panel" tabindex="-1"')
        for width, height in ((320, 725), (390, 844), (667, 375)):
            with self.subTest(width=width):
                page = self.page(width, height)
                cities = page.locator("#city-index button")
                expect(cities).to_have_count(5)
                shortcut = page.get_by_role("link", name="Map & globe")
                expect(shortcut).to_be_visible()
                shortcut.press("Enter")
                panel = page.locator("#atlas-panel")
                expect(panel).to_be_focused()
                self.assertTrue(page.url.endswith("#atlas-panel"))
                page.keyboard.press("Tab")
                expect(page.get_by_label("City on map")).to_be_focused()
                page.get_by_label("City on map").select_option("prague")
                expect(page.locator("#atlas-open-label")).to_have_text("Read Prague")
                expect(page.locator("#atlas-distance")).to_have_text("3,580 km direct")
                expect(page.locator('#atlas-flat [data-pin=prague]')).to_have_class("is-active")

    def test_pending_and_failed_module(self):
        page = self.page()
        pending = []
        page.route("**/media/globe.js", lambda route: pending.append(route))
        toggle = page.locator("#atlas-toggle")
        with page.expect_request("**/media/globe.js"):
            toggle.press("Enter")
        try:
            expect(toggle).to_have_attribute("aria-disabled", "true")
            expect(page.locator("#atlas-feedback")).to_have_text("Loading globe", timeout=800)
            expect(page.get_by_label("City on map")).to_be_enabled()
            expect(toggle).to_be_focused()
        finally:
            pending[0].abort()
        expect(page.locator("#atlas-feedback")).to_have_text("Globe unavailable. Use the map.")
        expect(toggle).to_have_attribute("aria-pressed", "false")
        expect(toggle).to_be_enabled()
        expect(page.locator("#atlas-flat svg")).to_be_visible()

    def test_late_module_does_not_take_over_after_focus_moves(self):
        page = self.page(667, 375)
        pending = []
        page.route("**/media/globe.js", lambda route: pending.append(route))
        toggle = page.locator("#atlas-toggle")
        with page.expect_request("**/media/globe.js"):
            toggle.press("Enter")
        compare = page.locator('.mast a[href="#compare"]')
        try:
            expect(page.locator("#atlas-feedback")).to_have_text("Loading globe", timeout=800)
            compare.focus()
            expect(toggle).to_be_enabled()
            expect(toggle).to_have_text("View globe")
            expect(page.locator("#atlas-feedback")).to_have_text("")
            position = page.evaluate("scrollY")
        finally:
            pending[0].continue_()
        page.locator('script[src="media/globe.js"]').wait_for(state="detached")
        self.assertTrue(page.evaluate("() => typeof window.DecemberGlobe?.mount === 'function'"))
        expect(compare).to_be_focused()
        expect(page.locator("#atlas-globe canvas")).to_have_count(0)
        self.assertEqual(page.evaluate("scrollY"), position)

    def test_real_globe_keeps_selected_city_when_the_context_is_lost(self):
        page = self.page(667, 375)
        page.locator("#atlas-select").select_option("prague")
        toggle = page.locator("#atlas-toggle")
        toggle.press("Enter")
        canvas = page.locator("#atlas-globe canvas")
        expect(canvas).to_be_visible()
        expect(page.locator(".globe-pin.is-active")).to_have_text("Prague")
        expect(toggle).to_have_attribute("aria-pressed", "true")
        canvas.evaluate("canvas => canvas.dispatchEvent(new Event('webglcontextlost', {cancelable: true}))")
        expect(page.locator("#atlas-feedback")).to_have_text("Globe stopped. You can still use the map.", timeout=800)
        expect(page.locator("#atlas-flat svg")).to_be_visible()
        expect(page.locator("#atlas-select")).to_have_value("prague")
        expect(page.locator("#atlas-distance")).to_have_text("3,580 km direct")


if __name__ == "__main__":
    unittest.main()
