#!/usr/bin/env python3
"""Cache busting: every page links its CSS and JS with ?v=<first 8 hex of the file's SHA-1>, so a visitor's
browser fetches a changed file at once instead of reusing its cached copy (GitHub Pages lets browsers keep
files for 10 minutes, and a normal reload does not re-check them). Run it after every change to a CSS or JS
file, before committing (standard-library Python, idempotent):
  python3 tools/bust.py
"""
import glob, hashlib, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ASSETS = ['assets/css/style.css', 'assets/css/eco.css', 'assets/css/fonts.css', 'assets/js/main.js', 'assets/js/forms.js', 'assets/js/gallery.js', 'assets/js/vault.js']

def version(path):
    with open(os.path.join(ROOT, path), 'rb') as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:8]

versions = {a: version(a) for a in ASSETS if os.path.exists(os.path.join(ROOT, a))}
pages = sorted(set(glob.glob(os.path.join(ROOT, '*.html')) + glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)))
changed = 0
for page in pages:
    if '/.claude/' in page or '/tools/' in page:
        continue
    with open(page, encoding='utf-8') as fh:
        s = fh.read()
    o = s
    for asset, v in versions.items():
        # ../assets/css/style.css or ../../assets/css/style.css, with or without an old ?v=
        s = re.sub(r'((?:\.\./)*' + re.escape(asset) + r')(\?v=[0-9a-f]+)?(")', r'\1?v=' + v + r'\3', s)
    if s != o:
        with open(page, 'w', encoding='utf-8') as fh:
            fh.write(s)
        changed += 1
print('versions:', ', '.join(f'{os.path.basename(a)}={v}' for a, v in versions.items()), '| pages changed:', changed)
