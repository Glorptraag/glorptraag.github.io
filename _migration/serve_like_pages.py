#!/usr/bin/env python3
"""Serve the site the way GitHub Pages does, so the cutover can be rehearsed.

Differences from python -m http.server that actually matter here:
  * "/x" with a directory at x gets a 301 to "/x/", as Pages does
  * a miss serves 404.html with a real 404 status, which is what makes the
    rescue script on that page testable
  * paths are case-sensitive, as they are on Pages and were not on WP Engine
"""
import os, sys, posixpath
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlsplit, unquote

ROOT = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..")

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, *a):
        pass

    def send_head(self):
        path = unquote(urlsplit(self.path).path)
        local = os.path.join(ROOT, path.lstrip("/"))

        if not path.endswith("/") and os.path.isdir(local):
            self.send_response(301)
            self.send_header("Location", path + "/")
            self.end_headers()
            return None

        target = os.path.join(local, "index.html") if path.endswith("/") else local
        if not os.path.isfile(target):
            return self.not_found()
        return super().send_head()

    def not_found(self):
        page = os.path.join(ROOT, "404.html")
        body = open(page, "rb").read() if os.path.isfile(page) else b"404"
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return None

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    print("serving %s on http://127.0.0.1:%d (GitHub Pages semantics)" % (ROOT, port))
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
