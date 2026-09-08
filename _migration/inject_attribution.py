#!/usr/bin/env python3
"""Add the attribution script to every real page.

Skips the redirect stubs (they are gone before a script could run) and any file
that already carries it, so the script is safe to re-run after a re-capture.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__)) + "/.."
TAG = '<script src="/assets/coastal-attribution.js" defer></script>'
SKIP_DIRS = {".git", "wp-content", "wp-includes", "_migration", "assets"}

def main():
    added = skipped = stubs = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            try:
                html = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if "coastal-attribution.js" in html:
                skipped += 1
                continue
            # Redirect stubs and the 404 handler manage themselves.
            if 'http-equiv="refresh"' in html:
                stubs += 1
                continue
            if "</head>" not in html:
                skipped += 1
                continue
            html = html.replace("</head>", "  " + TAG + "\n</head>", 1)
            open(path, "w", encoding="utf-8").write(html)
            added += 1
    print("attribution injected: %d added, %d already had it or unsuitable, %d redirect stubs skipped"
          % (added, skipped, stubs))

if __name__ == "__main__":
    main()
