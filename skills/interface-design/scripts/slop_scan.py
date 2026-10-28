#!/usr/bin/env python3
"""Flag UI patterns that often indicate template or AI-generated output.

Advisory only. Every hit needs a human or agent decision.
Usage: slop_scan.py <path> [<path> ...] [--strict]
Exit code is 1 with --strict when anything is flagged, else 0.
"""
import re
import sys
from pathlib import Path

EXTENSIONS = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".jsx", ".tsx",
              ".js", ".ts", ".vue", ".svelte", ".astro"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "coverage", "vendor"}
MAX_BYTES = 300_000  # skip minified vendor bundles

RULES = [
    ("gradient", re.compile(r"(linear|radial|conic)-gradient\(|bg-gradient-to-", re.I),
     "Gradient: does it carry meaning or brand?"),
    ("glass", re.compile(r"backdrop-filter\s*:\s*blur|backdrop-blur", re.I),
     "Glass effect: check contrast and purpose"),
    ("glow", re.compile(r"box-shadow\s*:[^;]*0\s+0\s+\d{2,}px[^;]*(rgba?\(|#)", re.I),
     "Glow shadow: decorative?"),
    ("lorem", re.compile(r"lorem ipsum", re.I), "Placeholder copy"),
    ("fake-metric", re.compile(r"\b\d+(\.\d+)?\s*[kKmM]?\+\s*(users|customers|developers|teams|downloads)\b"
                               r"|\b99\.9+%\s*uptime", re.I),
     "Metric claim: is there a real source?"),
    ("fake-loading", re.compile(r"setTimeout\([^)]*set(Loading|IsLoading|Success)", re.I),
     "Timer-driven loading or success state"),
    ("zoom-block", re.compile(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b", re.I),
     "Viewport blocks zoom (WCAG 1.4.4)"),
    ("todo-handler", re.compile(r"on\w+\s*=\s*\{\s*\(\)\s*=>\s*\{\s*\}\s*\}|console\.log\(['\"]clicked", re.I),
     "Empty or placeholder event handler"),
]


def iter_files(paths):
    for root in paths:
        p = Path(root)
        if p.is_file():
            yield p
            continue
        for f in p.rglob("*"):
            if f.is_file() and f.suffix.lower() in EXTENSIONS and not (set(f.parts) & SKIP_DIRS):
                yield f


def scan(paths):
    hits = []
    for f in iter_files(paths):
        if f.stat().st_size > MAX_BYTES or ".min." in f.name:
            continue
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            for rule, rx, hint in RULES:
                if rx.search(line):
                    hits.append((str(f), n, rule, hint, line.strip()[:120]))
    return hits


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    hits = scan(args)
    for path, n, rule, hint, text in hits:
        print(f"{path}:{n}: [{rule}] {hint}\n    {text}")
    print(f"\n{len(hits)} candidate(s). Review each; the scanner does not decide.")
    return 1 if hits and "--strict" in argv else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
