#!/usr/bin/env python3
"""Every picture of the site that shows the product, recoloured red -> teal-green (tools/recolor.py), with
the product's region on photos (so car lights, the sunset and other red things stay) and all published sizes.

By default each picture is read in its ORIGINAL red version from the backup branch v2-night-glass (git), so
the script can be run again with another TARGET_RGB in recolor.py. Better sources (the client's PNGs) can be
given as name=path arguments:
  python3 -I tools/recolor_jobs.py [only=hero,og] [hero=… head-box=… head-mc=… side-chargers=… …]
"""
import io, os, subprocess, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recolor import process

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BACKUP = 'v2-night-glass'
R = lambda x0, y0, x1, y1: [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
MC_TRAILER = [(x / 1672, y / 941) for x, y in [(1013, 318), (1608, 308), (1614, 606), (1478, 608), (1474, 668), (1290, 670), (1292, 606), (1013, 602)]]

# name: (published base, sizes, formats, source in the backup, include polygons or None for "all product", exclude)
JOBS = {
    'hero': ('assets/img/home/hero-bluehour-{w}', (800, 1200, 1672), ('webp', 'jpg'), 'assets/img/home/hero-bluehour-1672.jpg',
             [R(.522, .415, .762, .600), R(.759, .503, .815, .640)], [R(.7765, .5195, .8035, .6085)]),   # trailer + vending machine, not its shelves
    'head-mc': ('assets/img/v2/head-multicharger-{w}', (800, 1200, 1672, 2400, 3200), ('webp', 'jpg'), 'assets/img/v2/head-multicharger-3200.jpg', [MC_TRAILER], None),
    'head-box': ('assets/img/v2/head-box-{w}', (800, 1200, 1672), ('webp', 'jpg'), 'assets/img/v2/head-box-1672.jpg', [R(.488, .33, .748, .548)], None),
    'cut-container': ('assets/img/v2/cut-container-{w}', (640, 1100, 1600), ('webp',), 'assets/img/v2/cut-container-1600.webp', None, None),
    'cut-multicharger': ('assets/img/v2/cut-multicharger-{w}', (640, 1100, 1600), ('webp',), 'assets/img/v2/cut-multicharger-1600.webp', None, None),
    'cut-box': ('assets/img/v2/cut-box-{w}', (480, 960, 1400), ('webp',), 'assets/img/v2/cut-box-1400.webp', None, None),
    'side-chargers': ('assets/img/multicharger/side-chargers-{w}', (600, 919), ('webp', 'jpg'), 'assets/img/multicharger/side-chargers-919.jpg', None, None),
    'side-doors': ('assets/img/multicharger/side-doors-{w}', (600, 913), ('webp', 'jpg'), 'assets/img/multicharger/side-doors-913.jpg', None, None),
    'vending-open': ('assets/img/multicharger/vending-open-{w}', (419,), ('webp', 'jpg'), 'assets/img/multicharger/vending-open-419.jpg', [R(0, 0, .145, 1), R(.855, 0, 1, 1)], None),
    'vending-closed': ('assets/img/multicharger/vending-closed-{w}', (378,), ('webp', 'jpg'), 'assets/img/multicharger/vending-closed-378.jpg', None, None),
    'on-trailer': ('assets/img/multicharger/on-trailer-{w}', (700, 1167), ('webp', 'jpg'), 'assets/img/multicharger/on-trailer-1167.jpg', [R(.368, .115, .73, .505)], None),
    'on-truck': ('assets/img/multicharger/on-truck-{w}', (700, 1196), ('webp', 'jpg'), 'assets/img/multicharger/on-truck-1196.jpg', [R(.2, .06, .745, .52)], None),
    'container20': ('assets/img/multicharger/cut-container20-{w}', (636,), ('webp',), 'assets/img/multicharger/cut-container20-636.webp', None, None),
    'box-vent': ('assets/img/box/cut-box-vent-{w}', (440,), ('webp',), 'assets/img/box/cut-box-vent-440.webp', None, None),
    'lpg-container': ('assets/img/box/cut-lpg-container-{w}', (900, 1600), ('webp',), 'assets/img/box/cut-lpg-container-1600.webp', [R(.18, .25, .52, .95)], None),
    'scene': ('assets/img/box/cut-scene-{w}', (900, 1600), ('webp',), 'assets/img/box/cut-scene-1600.webp', None, None),
    'og': ('assets/img/og-image', (1200,), ('jpg',), 'assets/img/og-image.jpg', [R(.52, .405, .764, .598), R(.759, .499, .815, .646)], [R(.7765, .517, .8035, .612)]),
}


def from_backup(path):
    data = subprocess.run(['git', '-C', ROOT, 'show', f'{BACKUP}:{path}'], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(data))


def save(im, base, w, fmt):
    path = os.path.join(ROOT, (base.format(w=w) if '{w}' in base else base) + '.' + fmt)
    if fmt == 'jpg':
        im.convert('RGB').save(path, 'JPEG', quality=85 if w < 2400 else 82, optimize=True, progressive=True, subsampling=0)
    else:
        im.save(path, 'WEBP', quality=86 if w < 2400 else 80, method=6)
    return path


def run(overrides):
    written = []
    only = set(overrides.pop('only').split(',')) if 'only' in overrides else None
    for name, (base, sizes, fmts, backup_src, polys, excl) in JOBS.items():
        if only and name not in only:
            continue
        src = Image.open(overrides[name]) if name in overrides else from_backup(backup_src)
        big = process(src, polys=polys, exclude=excl)
        for w in sizes:
            im = big if big.width == w else big.resize((w, round(big.height * w / big.width)), Image.LANCZOS)
            for fmt in fmts:
                written.append(save(im, base, w, fmt))
        if name == 'hero':   # the Contact page head: the hero blurred and darkened, as before
            amb = big.convert('RGB').resize((1600, 900), Image.LANCZOS).filter(ImageFilter.GaussianBlur(30))
            amb = ImageEnhance.Brightness(amb).enhance(.612)
            for w in (800, 1600):
                im = amb if w == 1600 else amb.resize((800, 450), Image.LANCZOS)
                for fmt in ('webp', 'jpg'):
                    written.append(save(im, 'assets/img/v2/amb-hero-{w}', w, fmt))
        print(name, 'ok')
    return written


if __name__ == '__main__':
    overrides = dict(a.split('=', 1) for a in sys.argv[1:])
    files = run(overrides)
    print(len(files), 'files written')
