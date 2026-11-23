"""Measure the landscape photo viewer immediately after a real touch input."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EDITIONS = {
    "online": ("http://127.0.0.1:18768/", "6531786a1a2e8c365cbfd3ff055f440cd3bfc04c9191b94ebbfe4cc40d85d48b"),
    "offline": ((ROOT / "index.html").as_uri(), "50ad87e74d97e873a66148c251cbcc2ce58ea7d0ee289d9328425efcb5411ff8"),
}


def run(browser, edition, url, expected_sha):
    with urlopen(url) as response:
        sha256 = hashlib.sha256(response.read()).hexdigest()
    assert expected_sha == sha256
    context = browser.new_context(offline=edition == "offline", is_mobile=True, has_touch=True,
                                  reduced_motion="reduce", viewport={"width": 667, "height": 375})
    page = context.new_page()
    page.goto(url + "#vienna/photos", wait_until="domcontentloaded")
    page.evaluate("document.fonts.ready")
    page.locator("#gallery [data-photo-open]").tap()
    dialog = page.locator("#photo-dialog")
    expect(dialog).to_be_visible()
    dialog.locator("img").evaluate("image => image.decode()")
    observed = dialog.evaluate("""node => {
        const next = node.querySelector('[data-gallery="1"]');
        const box = next.getBoundingClientRect();
        const x = (box.left + box.right) / 2;
        const y = (box.top + box.bottom) / 2;
        const hit = document.elementFromPoint(x, y);
        return {viewport: [innerWidth, innerHeight], dialogScrollTop: node.scrollTop,
                dialogScrollHeight: node.scrollHeight, dialogClientHeight: node.clientHeight,
                nextTop: box.top, nextBottom: box.bottom, nextCenter: [x, y],
                nextVisibleHeight: Math.min(box.bottom, innerHeight) - box.top,
                hitTestNextCenter: Boolean(hit && next.contains(hit))};
    }""")
    page.screenshot(path=HERE / f"clip-vienna-{edition}.jpg", type="jpeg", quality=90)
    dialog.press("ArrowRight")
    expect(dialog.locator(".gallery-tools .small")).to_contain_text("2 /")
    previous = dialog.get_by_role("button", name="Previous photo")
    previous.tap()  # Playwright scrolls the control into view before issuing this tap.
    expect(dialog.locator(".gallery-tools .small")).to_contain_text("1 /")
    observed["keyboardAndScrolledTouchWork"] = True
    context.close()
    return {"edition": edition, "sha256": sha256, **observed}


if __name__ == "__main__":
    with sync_playwright() as runner:
        browser = runner.chromium.launch(channel="chrome")
        result = {"browser": browser.version, "results": [
            run(browser, edition, *artifact) for edition, artifact in EDITIONS.items()
        ]}
        browser.close()
    print(json.dumps(result, indent=2))
    (HERE / "photo-clip-reproduction.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
