#!/usr/bin/env python3
"""Write a redirect stub for every row in redirects.tsv.

GitHub Pages cannot serve a 301, so each stub carries the three signals Google
actually reads, in the order it reads them: a rel=canonical naming the target, an
instant meta refresh (Google treats a 0-second refresh as a permanent redirect),
and a location.replace() that also carries the query string and hash across so a
gclid on an old ad link survives the hop.

Deliberately NOT noindex: noindex would tell Google to drop the old URL, which
throws away the link equity the redirect exists to pass on.
"""
import os, sys

ORIGIN = "https://coastaldemolitions.com"
ROOT = os.path.dirname(os.path.abspath(__file__)) + "/.."
MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "redirects.tsv")

TPL = """<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<title>Moved &ndash; Coastal Demolitions</title>
<link rel="canonical" href="{origin}{target}">
<meta http-equiv="refresh" content="0; url={origin}{target}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>location.replace("{target}" + location.search + location.hash);</script>
<style>body{{font-family:'Lexend Deca',Roboto,Arial,sans-serif;background:#101820;color:#fff;
display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;text-align:center}}
a{{color:#f2a900;font-weight:600}}</style>
</head>
<body><div><p>This page has moved.</p>
<p><a href="{target}">Continue to {target}</a></p></div></body>
</html>
"""

def rows():
    for line in open(MAP, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        yield parts[0], parts[1]

def dest_file(src):
    # "/a/b/" -> a/b/index.html ; "/contact.html" -> contact.html
    rel = src.lstrip("/")
    return os.path.join(ROOT, rel + "index.html" if src.endswith("/") else rel)

def main():
    written = 0
    for src, target in rows():
        path = dest_file(src)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(TPL.format(origin=ORIGIN, target=target))
        written += 1
    print("wrote %d redirect stubs" % written)

if __name__ == "__main__":
    main()
