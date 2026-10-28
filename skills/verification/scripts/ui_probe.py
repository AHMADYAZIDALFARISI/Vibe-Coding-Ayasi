#!/usr/bin/env python3
"""Load a page at several widths and report mechanical UI problems.

Usage: ui_probe.py <url> [--out DIR] [--widths 360,768,1280] [--ignore-host HOST ...]
Needs: Python Playwright with a Chromium build (pip install playwright; playwright install chromium).
Exit code: 0 clean, 1 issues found, 2 setup error.
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

AUDIT_JS = r"""
() => {
  const visible = el => {
    const s = getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && el.getClientRects().length > 0;
  };
  const describe = el => el.outerHTML.slice(0, 140);
  const named = el => Boolean(
    (el.getAttribute('aria-label') || '').trim() ||
    el.getAttribute('aria-labelledby') ||
    (el.getAttribute('title') || '').trim() ||
    (el.innerText || '').trim() ||
    el.querySelector('img[alt]:not([alt=""]), svg[aria-label], [aria-label]')
  );
  const out = {unlabeled_inputs: [], unnamed_controls: [], images_without_alt: [], small_targets: [],
               broken_aria_refs: [], duplicate_control_names: []};
  const names = {};
  document.querySelectorAll('input, select, textarea').forEach(el => {
    if (['hidden', 'submit', 'button', 'reset'].includes(el.type) || !visible(el)) return;
    const ok = (el.labels && el.labels.length) || el.getAttribute('aria-label') || el.getAttribute('aria-labelledby');
    if (!ok) out.unlabeled_inputs.push(describe(el));
  });
  document.querySelectorAll('button, a[href], [role="button"]').forEach(el => {
    if (!visible(el)) return;
    if (!named(el)) out.unnamed_controls.push(describe(el));
    const name = ((el.getAttribute('aria-label') || el.innerText || '').trim()).toLowerCase();
    if (name) names[name] = (names[name] || 0) + 1;
    const r = el.getBoundingClientRect();
    if (r.width < 24 || r.height < 24) out.small_targets.push(`${Math.round(r.width)}x${Math.round(r.height)} ${describe(el)}`);
  });
  Object.entries(names).forEach(([n, c]) => { if (c > 1) out.duplicate_control_names.push(`${c}x "${n}"`); });
  document.querySelectorAll('[aria-describedby], [aria-labelledby], [aria-controls]').forEach(el => {
    ['aria-describedby', 'aria-labelledby', 'aria-controls'].forEach(attr => {
      (el.getAttribute(attr) || '').split(/\s+/).filter(Boolean).forEach(id => {
        if (!document.getElementById(id)) out.broken_aria_refs.push(`${attr}="${id}" on ${describe(el)}`);
      });
    });
  });
  document.querySelectorAll('img').forEach(el => { if (!el.hasAttribute('alt')) out.images_without_alt.push(describe(el)); });
  const vp = document.querySelector('meta[name="viewport"]');
  const content = vp ? vp.content.replace(/\s/g, '').toLowerCase() : '';
  const max = /maximum-scale=([\d.]+)/.exec(content);
  out.zoom_blocked = /user-scalable=(no|0)/.test(content) || (max !== null && parseFloat(max[1]) < 2);
  out.horizontal_overflow_px = Math.max(0, document.documentElement.scrollWidth - window.innerWidth);
  return out;
}
"""


FOCUS_PROPS = ["outline-style", "outline-width", "outline-color", "box-shadow", "border-color",
               "background-color", "color", "text-decoration-line"]
MARK_JS = """(props) => {
  const sel = 'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])';
  return [...document.querySelectorAll(sel)].map((el, i) => {
    el.dataset.probeIdx = i;
    const s = getComputedStyle(el);
    return props.map(p => s.getPropertyValue(p));
  });
}"""
FOCUSED_JS = """(props) => {
  const el = document.activeElement;
  if (!el || el.dataset.probeIdx === undefined) return null;
  const s = getComputedStyle(el);
  return {idx: +el.dataset.probeIdx, styles: props.map(p => s.getPropertyValue(p)),
          hasText: Boolean((el.innerText || el.value || '').trim()),
          label: (el.getAttribute('aria-label') || el.innerText || el.tagName).trim().slice(0, 60)};
}"""


def focus_audit(page, max_tabs=25, settle_ms=300):
    """Tab through the page and flag controls whose focused style equals their resting style."""
    rest = page.evaluate(MARK_JS, FOCUS_PROPS)
    problems, seen = [], set()
    for _ in range(min(max_tabs, len(rest))):
        page.keyboard.press("Tab")
        page.wait_for_timeout(settle_ms)  # let CSS transitions finish before reading styles
        f = page.evaluate(FOCUSED_JS, FOCUS_PROPS)
        if not f or f["idx"] in seen:
            continue
        seen.add(f["idx"])
        changed = {p for p, a, b in zip(FOCUS_PROPS, rest[f["idx"]], f["styles"]) if a != b}
        if not changed:
            problems.append(f"no focus style: {f['label']}")
        elif changed == {"text-decoration-line"} and not f["hasText"]:
            problems.append(f"focus shown only as underline on an icon-only control: {f['label']}")
    return problems


def ignored(url, hosts):
    return bool(hosts) and urlparse(url).hostname in hosts


def probe(url, out_dir, widths, ignore_hosts=()):
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"url": url, "viewports": {}}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for w in widths:
            page = browser.new_page(viewport={"width": w, "height": 900})
            console, failed = [], []
            page.on("console", lambda m: console.append(m.text)
                    if m.type == "error" and not ignored(m.location.get("url", ""), ignore_hosts) else None)
            page.on("pageerror", lambda e, c=console: c.append(str(e)))
            skipped = []
            def record(entry, url_):
                (skipped if ignored(url_, ignore_hosts) else failed).append(entry)
            page.on("requestfailed", lambda r: record(f"{r.method} {r.url} {r.failure}", url_=r.url))
            page.on("response", lambda r: record(f"{r.status} {r.url}", url_=r.url) if r.status >= 400 else None)
            page.goto(url, wait_until="networkidle")
            shot = out_dir / f"probe-{w}.png"
            page.screenshot(path=str(shot), full_page=True)
            audit = page.evaluate(AUDIT_JS)
            audit.update(console_errors=console, failed_requests=failed, ignored_requests=skipped,
                         screenshot=str(shot))
            if w == max(widths):
                audit["focus_problems"] = focus_audit(page)
            report["viewports"][w] = audit
            page.close()
        browser.close()
    return report


def count_issues(report):
    n = 0
    for v in report["viewports"].values():
        n += len(v["unlabeled_inputs"]) + len(v["unnamed_controls"]) + len(v["images_without_alt"])
        n += len(v["broken_aria_refs"]) + len(v["duplicate_control_names"]) + len(v.get("focus_problems", []))
        n += len(v["console_errors"]) + len(v["failed_requests"]) + len(v["small_targets"])
        n += int(v["zoom_blocked"]) + int(v["horizontal_overflow_px"] > 0)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="ui-probe")
    ap.add_argument("--widths", default="360,768,1280")
    ap.add_argument("--ignore-host", action="append", default=[],
                    help="host whose failed requests are environmental (e.g. blocked fonts); reported, not counted")
    a = ap.parse_args()
    try:
        report = probe(a.url, Path(a.out), [int(x) for x in a.widths.split(",")], tuple(a.ignore_host))
    except ImportError:
        print("Playwright is not installed. See the usage line.", file=sys.stderr)
        return 2
    except Exception as e:  # unreachable URL, browser missing, navigation timeout
        print(f"Could not load {a.url}: {str(e).splitlines()[0]}", file=sys.stderr)
        return 2
    (Path(a.out) / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    issues = count_issues(report)
    print(f"\n{issues} issue(s). Screenshots in {a.out}/. Open them before claiming visual checks.")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
