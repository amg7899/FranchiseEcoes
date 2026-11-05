#!/usr/bin/env python3
"""Every picture of the site that shows the product, recoloured (tools/recolor.py), with the product's region
on photos (so car lights, the sunset and other red things stay) and all published sizes.

  mode=red (default since 2026-11-05, client: "back to red, a touch darker and more realistic, thin ribs on
           the panels, better lettering"): tools/redpaint.py – a deeper red everywhere; on the drawings
           (DRAW below) light from above, thin vertical ribs and the lettering set again.
  mode=green: the v3 trial's teal-green (TARGET_RGB in recolor.py), as published 2026-11-05 morning.

By default each picture is read in its ORIGINAL red version from the backup branch v2-night-glass (git), so
the script can be run again with another TARGET_RGB in recolor.py. Better sources (the client's PNGs) can be
given as name=path arguments:
  python3 -I tools/recolor_jobs.py [mode=red|green] [only=hero,og] [hero=… head-box=… head-mc=… side-chargers=… …]
(needs numpy + Pillow, and Inter for the lettering)
"""
import io, os, subprocess, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recolor import process
from redpaint import paint, face_ribs
from PIL import ImageDraw, ImageFont

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


# the drawings: rib spacing as a share of the body's width (about 9-10 cm on the real box) and the lettering,
# measured on the originals (text box and the E's cap top and height, all in 0..1 of the picture)
TEXT = 'ECOES MultiCharger'
DRAW = {
    'side-chargers': {'pitch': 1 / 34, 'text': TEXT, 'text_box': (.0925, .1355, .9249, .3120), 'cap': (.1432, .1330)},
    'side-doors': {'pitch': 1 / 34, 'text': TEXT, 'text_box': (.0931, .1335, .9233, .3073), 'cap': (.1436, .1285)},
    'cut-multicharger': {'pitch': 1 / 34, 'text': TEXT, 'text_box': (.3281, .1104, .9344, .2369), 'cap': (.1171, .0929)},
    'cut-box': {'pitch': 1 / 26, 'text': TEXT, 'text_box': (.1986, .2301, .8221, .3371), 'cap': (.2313, .0808)},
    'vending-open': {'pitch': 1 / 22},
    'vending-closed': {'pitch': 1 / 22},
    'box-vent': {'pitch': 0},
    'scene': {'bodies': [
        {'body': (.4581, .0352, .6775, .2279), 'pitch': 1 / 26, 'text': TEXT, 'text_box': (.4944, .0664, .6462, .0964), 'cap': (.0664, .0221)},
        {'body': (.4788, .5547, .6987, .7474), 'pitch': 1 / 26, 'text': TEXT, 'text_box': (.5156, .5859, .6675, .6159), 'cap': (.5859, .0221)}]},
}


# photos: the flat red sides (a box around each, in 0..1) that get ribs in perspective, and how many
FACES = {
    'hero': [((.525, .43, .76, .60), 34)],
    'og': [((.52, .42, .764, .60), 34)],
    'head-mc': [((.606, .338, .965, .644), 34)],
    'head-box': [((.49, .33, .75, .55), 26)],
    'on-trailer': [((.37, .12, .73, .50), 34)],
    'on-truck': [((.2, .07, .745, .52), 34)],
    # renders in containers: the lit side with the lettering and the shaded end of each box
    'cut-container': [((.411, .294, .676, .657), 34), ((.296, .294, .393, .655), 22), ((.772, .386, .946, .652), 34), ((.691, .386, .759, .65), 22)],
    'container20': [((.555, .337, .918, .701), 34), ((.357, .333, .491, .69), 22)],
    'lpg-container': [((.321, .413, .509, .76), 26), ((.264, .414, .307, .757), 13)],
}


def dark_labels(im, ink=(52, 66, 61)):
    """the Box scene's dimension lines and "50–100 m" labels were light for the night ground: dark ink again"""
    a = np.asarray(im.convert('RGBA')).astype(np.float64)
    W = im.width; s = W / 1600
    font = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
    for x0, y0, x1, y1 in [(190, 330, 430, 420), (1170, 330, 1410, 420)]:
        x0, y0, x1, y1 = [int(v * s) for v in (x0, y0, x1, y1)]
        reg = a[y0:y1, x0:x1]
        rows = np.where((reg[..., 3] > 100).sum(1) > 0)[0]
        runs = np.split(rows, np.where(np.diff(rows) > 1)[0] + 1)
        t = runs[0]; ty0, ty1 = y0 + t[0], y0 + t[-1] + 1
        cols = np.where((reg[t[0]:t[-1] + 1, :, 3] > 100).sum(0) > 0)[0]; tx0, tx1 = x0 + cols[0], x0 + cols[-1] + 1
        rest = a[ty1 + 1:y1, x0:x1]; m = rest[..., 3] > 8; rest[m, :3] = ink
        a[ty0 - 2:ty1 + 2, tx0 - 2:tx1 + 2] = 0
        h = ty1 - ty0
        img = Image.fromarray(a.round().astype(np.uint8), 'RGBA')
        txt = '50–100 m'; size = 6
        while True:
            f = ImageFont.truetype(font, size + 1); bb = f.getbbox(txt)
            if bb[3] - bb[1] > h * 1.02 or bb[2] - bb[0] > (tx1 - tx0) * 1.04: break
            size += 1
        f = ImageFont.truetype(font, size); bb = f.getbbox(txt)
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).text(((tx0 + tx1) / 2 - (bb[2] - bb[0]) / 2 - bb[0], ty0 - bb[1] + (h - (bb[3] - bb[1])) / 2), txt, font=f, fill=ink + (255,))
        img.alpha_composite(layer); a = np.asarray(img).astype(np.float64)
    return Image.fromarray(a.round().astype(np.uint8), 'RGBA')


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
    mode = overrides.pop('mode', 'red')
    for name, (base, sizes, fmts, backup_src, polys, excl) in JOBS.items():
        if only and name not in only:
            continue
        src = Image.open(overrides[name]) if name in overrides else from_backup(backup_src)
        if mode == 'red':
            big = paint(src, region=polys, exclude=excl, drawing=DRAW.get(name))
            if name == 'scene':
                big = dark_labels(big)
            for face, n in FACES.get(name, []):
                big = face_ribs(big, face, n, region=polys, exclude=excl)
        else:
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
