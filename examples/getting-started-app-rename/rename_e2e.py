"""Browser checks for the rename feature.

Needs a fresh server on :3000 seeded with: "Buy milk", "Renew passport before March",
"Call the landlord about the leaking tap".
"""
import json
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BASE = "http://localhost:3000"
OUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "e2e-output"
results = []
DEBUG = "--debug" in sys.argv


def check(name, fn):
    try:
        page.unroute_all(behavior="ignoreErrors")
        page.keyboard.press("Escape")
        fn()
        results.append(("PASS", name, ""))
    except Exception as e:  # report and keep going
        results.append(("FAIL", name, str(e).splitlines()[0][:200]))
        if DEBUG:
            print("DEBUG", name, page.locator("#root").inner_html()[:1500])


def api(method, path, body=None):
    req = urllib.request.Request(
        BASE + path, method=method, data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        raw = r.read()
        return json.loads(raw) if raw and raw != b"OK" else None


Path(OUT).mkdir(exist_ok=True)

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 360, "height": 800})
    page.set_default_timeout(4000)
    puts = []
    page.on("request", lambda r: puts.append(r.url) if r.method == "PUT" else None)
    page.goto(BASE)
    page.wait_for_selector(".item")

    check("AC1 edit control named with item",
          lambda: expect(page.get_by_role("button", name='Rename "Buy milk"')).to_be_visible())

    def ac2():
        page.get_by_role("button", name='Rename "Buy milk"').click()
        field = page.get_by_label('New name for "Buy milk"')
        expect(field).to_be_focused()
        expect(field).to_have_value("Buy milk")
    check("AC2 labelled field, focused, prefilled", ac2)

    def ac4():
        before = len(puts)
        page.keyboard.type("Buy oat milk")
        page.keyboard.press("Escape")
        expect(page.get_by_text("Buy milk", exact=True)).to_be_visible()
        expect(page.get_by_role("button", name='Rename "Buy milk"')).to_be_focused()
        assert len(puts) == before, "Escape sent a request"
    check("AC4 Escape cancels, no request, focus returns", ac4)

    def ac3():
        page.get_by_role("button", name='Rename "Buy milk"').click()
        page.keyboard.press("Control+A")
        page.keyboard.type("  Buy oat milk  ")
        page.keyboard.press("Enter")
        expect(page.get_by_text("Buy oat milk", exact=True)).to_be_visible()
        stored = [i["name"] for i in api("GET", "/items")]
        assert "Buy oat milk" in stored, stored
        expect(page.get_by_role("button", name='Rename "Buy oat milk"')).to_be_focused()
    check("AC3 Enter saves trimmed name, server confirms, focus returns", ac3)

    def ac3_pending():
        held = []
        page.route("**/items/*", lambda r: held.append(r) if r.request.method == "PUT" else r.continue_())
        page.get_by_role("button", name='Rename "Buy oat milk"').click()
        page.keyboard.press("Control+A")
        page.keyboard.type("Buy milk")
        page.get_by_role("button", name="Save").click()
        expect(page.get_by_role("button", name="Saving...")).to_be_disabled()
        expect(page.get_by_label('New name for "Buy oat milk"')).to_have_attribute("readonly", "")
        assert held, "PUT was not sent"
        held[0].continue_()
        expect(page.get_by_text("Buy milk", exact=True)).to_be_visible()
        page.unroute("**/items/*")
    check("AC3 pending state while saving", ac3_pending)

    def ac6():
        target = next(i for i in api("GET", "/items") if i["name"] == "Renew passport before March")
        page.get_by_role("button", name='Rename "Renew passport before March"').click()
        api("DELETE", f"/items/{target['id']}")
        page.keyboard.press("Control+A")
        page.keyboard.type("Renew passport in Feb")
        page.keyboard.press("Enter")
        expect(page.get_by_role("alert")).to_have_text("Item not found.")
        expect(page.get_by_label('New name for "Renew passport before March"')).to_have_value("Renew passport in Feb")
        page.get_by_role("button", name="Cancel").click()
    check("AC6 real 404 shown, user text kept", ac6)

    def ac7():
        page.route("**/items/*", lambda r: r.abort() if r.request.method == "PUT" else r.continue_())
        page.get_by_role("button", name='Rename "Call the landlord about the leaking tap"').click()
        page.keyboard.press("Control+A")
        page.keyboard.type("Call landlord")
        page.keyboard.press("Enter")
        expect(page.get_by_role("alert")).to_have_text("Could not reach the server. Try again.")
        expect(page.locator(".item .name", has_text="Call landlord")).to_have_count(0)
        page.unroute("**/items/*")
        page.get_by_role("button", name="Cancel").click()
    check("AC7 network failure shows error, no false success", ac7)

    def ac5_ui():
        page.route("**/items/*", lambda r: r.fulfill(status=400, json={"error": "Name cannot be empty."})
                   if r.request.method == "PUT" else r.continue_())
        page.get_by_role("button", name='Rename "Call the landlord about the leaking tap"').click()
        page.keyboard.press("Control+A")
        page.keyboard.type("x")
        page.keyboard.press("Enter")
        expect(page.get_by_role("alert")).to_have_text("Name cannot be empty.")
        page.unroute("**/items/*")
        page.get_by_role("button", name="Cancel").click()
    check("AC5 server 400 message rendered", ac5_ui)

    def ac5_whitespace():
        page.get_by_role("button", name='Rename "Call the landlord about the leaking tap"').click()
        page.keyboard.press("Control+A")
        page.keyboard.type("   ")
        expect(page.get_by_role("button", name="Save")).to_be_disabled()
        page.keyboard.press("Escape")
    check("AC5 whitespace-only cannot be submitted", ac5_whitespace)

    def add_whitespace():
        page.get_by_label("New item name").fill("   ")
        expect(page.get_by_role("button", name="Add Item")).to_be_disabled()
        page.get_by_label("New item name").fill("")
    check("Add form blocks whitespace-only", add_whitespace)

    def add_server_error():
        page.route("**/items", lambda r: r.fulfill(status=400, json={"error": "Name cannot be empty."})
                   if r.request.method == "POST" else r.continue_())
        page.get_by_label("New item name").fill("Pay rent")
        page.get_by_role("button", name="Add Item").click()
        expect(page.get_by_role("alert")).to_have_text("Name cannot be empty.")
        expect(page.locator(".item .name", has_text="Pay rent")).to_have_count(0)
        expect(page.get_by_role("button", name="Add Item")).to_be_enabled()
        page.unroute("**/items")
        page.get_by_label("New item name").fill("")
    check("Add form shows server error, no phantom item", add_server_error)

    def long_name():
        api("POST", "/items", {"name": "x" * 255})
        page.reload()
        page.wait_for_selector(".item")
        overflow = page.evaluate("document.documentElement.scrollWidth - innerWidth")
        assert overflow == 0, f"overflow {overflow}px"
    check("AC8 255-char unbroken name does not overflow at 360px", long_name)

    def ac7_timeout():
        slow = browser.new_page(viewport={"width": 360, "height": 800})
        slow.clock.install()
        slow.goto(BASE)
        slow.wait_for_selector(".item")
        held = []
        slow.route("**/items/*", lambda r: held.append(r) if r.request.method == "PUT" else r.continue_())
        slow.locator("button[aria-label^='Rename']").first.click()
        slow.keyboard.press("Control+A")
        slow.keyboard.type("Hung request")
        slow.keyboard.press("Enter")
        expect(slow.get_by_role("button", name="Saving...")).to_be_disabled()
        slow.clock.run_for(16000)
        expect(slow.get_by_role("alert")).to_have_text("The server took too long to respond. Try again.")
        expect(slow.get_by_role("button", name="Cancel")).to_be_enabled()
        slow.close()
    check("AC7 hung request times out and unlocks the form", ac7_timeout)

    page.screenshot(path=f"{OUT}/e2e-360-final.png", full_page=True)
    page.locator("button[aria-label^='Rename']").first.click()
    page.screenshot(path=f"{OUT}/e2e-360-editing.png")
    browser.close()

for r in results:
    print(*r, sep=" | ")
print(f"{sum(r[0] == 'PASS' for r in results)}/{len(results)} passed")
sys.exit(0 if all(r[0] == "PASS" for r in results) else 1)
