#!/usr/bin/env python3
"""Emit /url-index.json: every path the static site can serve.

The 404 page loads this and tries to rescue a request before giving up, which is
how a site with no server-side redirects still covers casing variants, old
WordPress permalink shapes and near-miss slugs.
"""
import os, json

ROOT = os.path.dirname(os.path.abspath(__file__)) + "/.."
SKIP_PREFIX = ("/wp-content/", "/wp-includes/", "/wp-json/", "/_migration/", "/.git/")

paths = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "wp-content", "wp-includes", "_migration")]
    for name in filenames:
        if name != "index.html":
            continue
        rel = os.path.relpath(os.path.join(dirpath, name), ROOT).replace(os.sep, "/")
        path = "/" + rel[: -len("index.html")]
        if any(path.startswith(p) for p in SKIP_PREFIX):
            continue
        paths.append(path)

paths = sorted(set(paths))
out = os.path.join(ROOT, "url-index.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(paths, fh, separators=(",", ":"))
print("wrote %s with %d paths" % (out, len(paths)))
