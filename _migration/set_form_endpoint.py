#!/usr/bin/env python3
"""Point the quote form at the lead Worker.

Usage:  python3 _migration/set_form_endpoint.py https://coastal-lead-form.<sub>.workers.dev

Run this once the Worker is deployed and you have its real URL. It refuses a
placeholder, because a form posting to a dead endpoint loses every lead silently
— which is the exact failure this whole migration is meant to end.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__)) + "/.."
ACTION = re.compile(r'action="(https://(?:formsubmit\.co|[^"]*workers\.dev)[^"]*)"')

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    url = sys.argv[1].rstrip("/")
    if not url.startswith("https://") or "REPLACE" in url.upper() or "example" in url:
        sys.exit("Refusing: %r is not a real endpoint." % url)

    changed = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "wp-content", "wp-includes")]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            html = open(path, encoding="utf-8", errors="ignore").read()
            if not ACTION.search(html):
                continue
            new = ACTION.sub('action="%s"' % url, html)
            # Mark it so the attribution script finds the form even if WPForms
            # classes ever change.
            new = new.replace('class="wpforms-validate wpforms-form"',
                              'class="wpforms-validate wpforms-form" data-coastal-lead')
            if new != html:
                open(path, "w", encoding="utf-8").write(new)
                changed.append(os.path.relpath(path, ROOT))

    if not changed:
        sys.exit("No form action found to change — check the form markup before going live.")
    print("Form endpoint set to %s on:" % url)
    for c in sorted(changed):
        print("  " + c)

if __name__ == "__main__":
    main()
