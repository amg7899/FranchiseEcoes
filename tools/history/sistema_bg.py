"""Bulgarian versions of the three SISTEMA certificates (About us → History), client 2026-11-24: every English line
taken off the scan and set again in Bulgarian at its place, in type matched to the original line (size from the ink
height of the same English text, width from its ink width). Logos, the company name, the ISO numbers, the
multilingual strip, the signature, seals, QR code and the address of the website stay as they are. A small note
"Превод от английски" (top right) marks the page as our translation.

  python3 tools/history/sistema_bg.py [debug-dir]     (from the repo root)

Writes assets/img/about/history/<cert>-bg.{jpg,webp} (1240 px), -600 and -300. Needs doctools.py beside it.
"""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doctools import Doc, FONTS

FONTS.update({
    'inter': '/usr/share/fonts/opentype/inter/Inter-Regular.otf',
})
HIST = 'assets/img/about/history/'
DEBUG = sys.argv[1] if len(sys.argv) > 1 else None

BAR = ('CERTIFICATE OF REGISTRATION', 'СЕРТИФИКАТ ЗА РЕГИСТРАЦИЯ')
CONF = ('It is confirmed that the management system', 'Потвърждава се, че системата за управление на')
ADDR = ('DISTR. ZAHARNA FABRIKA, BL.39, APP. 5, 1345 SOFIA, BULGARIA',
        'Ж.К. ЗАХАРНА ФАБРИКА, БЛ. 39, АП. 5, 1345 СОФИЯ, БЪЛГАРИЯ')
EVAL = ('has been evaluated and complies with the requirements', 'е оценена и отговаря на изискванията на')
VALID = ('This certificate is valid for the following activities', 'Този сертификат е валиден за следните дейности')
SCOPE_EN1 = 'DESIGN, PRODUCTION, AND SERVICING OF FIRE-FIGHTING AND OTHER SPECIAL-PURPOSE VEHICLES, AS WELL'
SCOPE_BG = ('ПРОЕКТИРАНЕ, ПРОИЗВОДСТВО И СЕРВИЗНО ОБСЛУЖВАНЕ НА ПРОТИВОПОЖАРНИ И ДРУГИ СПЕЦИАЛНИ АВТОМОБИЛИ, КАКТО И '
            'НА ЕЛЕКТРИЧЕСКИ И ГАЗОВИ КАМИОНИ И ТРАКТОРИ. КОНВЕРСИЯ НА МОБИЛНА ТЕХНИКА С ДИЗЕЛОВО ЗАДВИЖВАНЕ КЪМ '
            'ЕЛЕКТРИЧЕСКО ИЛИ ГАЗОВО ЗАДВИЖВАНЕ. ПРОИЗВОДСТВО И УПРАВЛЕНИЕ НА МОБИЛНИ И СТАЦИОНАРНИ ЗАРЯДНИ СТАНЦИИ ЗА '
            'ЕЛЕКТРИЧЕСКИ ПРЕВОЗНИ СРЕДСТВА.')
CERTNO = 'Certificate Number: SISTEMA-BUL/BEL-{}'
CERTNO_BG = 'Номер на сертификата: SISTEMA-BUL/BEL-{}'
DATES = [('Issue date: 24.11.2026', 'Дата на издаване: 24.11.2026'),
         ('Expiry date: 23.11.2027', 'Дата на изтичане: 23.11.2027'),
         ('Date of First Surveillance: 24.10.2027', 'Дата на първи надзорен одит: 24.10.2027'),
         ('Date of second surveillance: 24.10.2028', 'Дата на втори надзорен одит: 24.10.2028'),
         ('Recertification date: 24.10.2029', 'Дата на пресертифициране: 24.10.2029')]
MD = ('Director', 'Управляващ директор')
VERIFY = ('Verify the certificate:-', 'Проверете сертификата:')
SMALL_EN_LAST = 'Head-quarters: FF, SS-1914, Sector –H , LDA Colony, Kanpur Road, Lucknow-226012.'
SMALL_BG = ('Документацията на организацията и нейното внедряване са прегледани и е установено, че отговарят на '
            'съответните изисквания на стандарта. Този сертификат за регистрация се основава на оценката на посочения '
            'обхват, като организацията отговаря и за спазването на изискванията на съответния стандарт. При промяна '
            'в дейностите на дружеството този сертификат губи валидност. Валидността на сертификата зависи от '
            'успешното провеждане на надзорните одити преди определените срокове и той е валиден само след успешен '
            'надзор с писмо за продължаване, издадено от нас. QUALITY SISTEMA Certifications and Inspections Pvt Ltd., '
            'седалище: FF, SS-1914, Sector –H, LDA Colony, Kanpur Road, Lucknow-226012.')
NOTE = 'Превод от английски'

# search boxes (scan pixels) of the lines that differ in place between the three scans
CERTS = {
    'iso-9001-2015': dict(code='Q6447', system=('Quality Management System', 'Система за управление на качеството', 'dejavu-b'),
                          conf=(200, 250, 800, 292), eval=(200, 614, 800, 647), sys=(200, 701, 1210, 746),
                          valid=(200, 746, 800, 779), certno=(200, 1102, 800, 1138), dates=(200, 1145, 800, 1312)),
    'iso-14001-2015': dict(code='E6448', system=('Environmental Management System', 'Система за управление на околната среда', 'dejavu'),
                           conf=(200, 296, 800, 338), eval=(200, 606, 800, 640), sys=(200, 697, 1210, 745),
                           valid=(200, 746, 800, 778), certno=(200, 1133, 800, 1167), dates=(200, 1177, 800, 1343)),
    'iso-45001-2018': dict(code='O6449', system=('Occupational Health & Safety Management System',
                                                 'Система за управление на здравето и безопасността при работа', 'dejavu'),
                           conf=(200, 296, 800, 338), eval=(200, 614, 800, 647), sys=(200, 707, 1210, 754),
                           valid=(200, 755, 800, 786), certno=(200, 1133, 800, 1167), dates=(200, 1177, 800, 1343)),
}
COMMON = dict(bar=(215, 188, 990, 233), addr=(200, 476, 960, 514), scope=(200, 874, 1180, 1008),
              md=(355, 1512, 470, 1556), sig=(180, 1380, 560, 1560),
              verify=(820, 1568, 1210, 1600), small=(350, 1608, 1232, 1752))


# ------------------------------------------------------------------ measuring the original lines
def ink_mask(doc, box, light=False, thr=45):
    x0, y0, x1, y1 = box
    reg = np.asarray(doc.src, np.float32)[y0:y1, x0:x1].mean(axis=2)
    bg = np.median(reg)
    return ((reg - bg) if light else (bg - reg)) > thr


def ink_box(doc, box, light=False, thr=45):
    """Tight ink box and baseline (scan pixels) of the line inside box."""
    m = ink_mask(doc, box, light, thr)
    ys, xs = np.nonzero(m)
    x0, y0 = box[0], box[1]
    cols = [np.nonzero(m[:, c])[0].max() for c in range(m.shape[1]) if m[:, c].any()]
    base = y0 + int(np.median(cols)) + 1
    return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1), base


def bands(doc, box, light=False, thr=45, gap=2, frac=0.06):
    """The text lines inside box, as (y0, y1) row bands (scan pixels); rows with only a few ink pixels (the
    descenders and ascenders between close lines) count as empty."""
    m = ink_mask(doc, box, light, thr)
    cnt = m.sum(axis=1)
    rows = cnt > max(0, frac * cnt.max())
    out, start, empty = [], None, 0
    for i, r in enumerate(rows):
        if r:
            if start is None:
                start = i
            empty = 0
        elif start is not None:
            empty += 1
            if empty >= gap:
                out.append((box[1] + start, box[1] + i - empty + 1)); start = None
    if start is not None:
        out.append((box[1] + start, box[3]))
    return out


def rendered_ink(text, key, px):
    """Ink width and ink height above the baseline of text set in font key at px."""
    f = ImageFont.truetype(FONTS[key], px)
    im = Image.new('L', (int(f.getlength(text)) + 60, px * 3), 0)
    ImageDraw.Draw(im).text((30, px), text, font=f, fill=255)
    ys, xs = np.nonzero(np.asarray(im) > 110)
    return xs.max() + 1 - xs.min(), px + f.getmetrics()[0] - ys.min()


def fit(text, key, w, h, scale=4):
    """Size (scan px) and horizontal stretch that give text in font key the ink height above the baseline h
    and the ink width w."""
    px = h * 1.2
    for _ in range(8):
        _, hh = rendered_ink(text, key, max(4, round(px * scale)))
        px *= h / (hh / scale)
    ww, _ = rendered_ink(text, key, round(px * scale))
    return px, w / (ww / scale)


def colour(doc, box, light=False, pct=8):
    """The ink colour of a line: the mean of its darkest (lightest) pixels inside the tight box; pct=None for
    coloured type: the median of its most saturated pixels."""
    x0, y0, x1, y1 = box
    reg = np.asarray(doc.src, np.float32)[y0:y1, x0:x1].reshape(-1, 3)
    if pct is None:
        lab = cv2.cvtColor(reg.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
        chroma = np.hypot(lab[:, 1] - 128, lab[:, 2] - 128)
        sel = reg[chroma >= np.percentile(chroma, 94)]
        return tuple(int(v) for v in np.median(sel, axis=0))
    L = reg.mean(axis=1)
    sel = reg[L >= np.percentile(L, 100 - pct)] if light else reg[L <= np.percentile(L, pct)]
    return tuple(int(v) for v in sel.mean(axis=0))


# ------------------------------------------------------------------ one line: off and on again
def swap_line(doc, box, en, bg, key, light=False, shrink=None, erase_kw=None, pad=3, log=None, pct=8, size=None,
              col=None):
    (x0, y0, x1, y1), base = ink_box(doc, box, light)
    px, st = fit(en, key, x1 - x0, base - y0)
    col = col or colour(doc, (x0, y0, x1, y1), light, pct=pct)
    if size:
        px, st = size
    doc.erase((x0 - pad, y0 - pad, x1 + pad, y1 + pad), **(erase_kw or {}))
    doc.text(bg, key, px, col, (x0, base), 'l', stretch=st, shrink=shrink)
    if log is not None:
        log.append(f'{en[:28]!r}: ink {(x0, y0, x1, y1)} base {base} px {px:.1f} stretch {st:.3f} colour {col}')
    return px, st, base, x0


def signature_mask(doc, box):
    """The signature's strokes (thicker than the type) at work scale, for the whole page."""
    s = doc.sc
    x0, y0, x1, y1 = [v * s for v in box]
    L = doc.orig[y0:y1, x0:x1].mean(axis=2)
    dark = (L < 120).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5 * s, 5 * s))
    thick = cv2.morphologyEx(dark, cv2.MORPH_OPEN, k)
    near = cv2.dilate(thick, np.ones((3, 3), np.uint8))
    # the strokes' lighter insides and edges belong to them too
    closed = cv2.morphologyEx(near, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4 * s + 1, 4 * s + 1)))
    full = np.zeros(doc.a.shape[:2], bool)
    full[y0:y1, x0:x1] = ((near & dark) | (closed & (L < 215))).astype(bool)
    return full


def make(name, cfg, out_dir=HIST):
    doc = Doc(HIST + name + '.jpg', sc=2)
    doc.set_grain((930, 262, 1150, 330))
    log = []
    c = {**COMMON, **cfg}

    # the blue bar: white capitals on blue
    swap_line(doc, c['bar'], BAR[0], BAR[1], 'inter', light=True, shrink=748, log=log,
              erase_kw=dict(thr=30, grow=2, grain=0.3))
    swap_line(doc, c['conf'], CONF[0], CONF[1], 'carlito-b', log=log)
    swap_line(doc, c['addr'], ADDR[0], ADDR[1], 'carlito', shrink=980, log=log)
    swap_line(doc, c['eval'], EVAL[0], EVAL[1], 'carlito', log=log)
    en, bg, key = c['system']
    # the system's name in the colour of the ISO number above it (the same ink, in thicker strokes)
    iso_box, _ = ink_box(doc, (200, c['eval'][3] + 4, 900, c['sys'][1] - 1))
    swap_line(doc, c['sys'], en, bg, key, shrink=975, log=log, erase_kw=dict(thr=14), col=colour(doc, iso_box, pct=None))
    swap_line(doc, c['valid'], VALID[0], VALID[1], 'carlito', log=log)

    # the scope: four lines of condensed capitals, set again as a ragged paragraph at the same pitch
    sb = bands(doc, c['scope'])
    (sx0, sy0, sx1, sy1), sbase = ink_box(doc, (c['scope'][0], sb[0][0] - 1, c['scope'][2], sb[0][1] + 1))
    spx, sst = fit(SCOPE_EN1, 'carlito', sx1 - sx0, sbase - sy0)
    bases = [ink_box(doc, (c['scope'][0], b0 - 1, c['scope'][2], b1 + 1))[1] for b0, b1 in sb]
    pitch = (bases[-1] - bases[0]) / (len(bases) - 1)
    width = max(ink_box(doc, (c['scope'][0], b0 - 1, c['scope'][2], b1 + 1))[0][2] for b0, b1 in sb) - sx0
    scol = colour(doc, (sx0, sy0, sx1, sy1))
    doc.erase((sx0 - 4, sb[0][0] - 4, sx0 + width + 6, sb[-1][1] + 4))
    n = doc.paragraph(SCOPE_BG, 'carlito', spx, scol, sx0, bases[0], width, pitch, stretch=sst)
    log.append(f'scope: {len(sb)} lines → {n}, px {spx:.1f} stretch {sst:.3f} pitch {pitch:.1f} width {width}')

    swap_line(doc, c['certno'], CERTNO.format(c['code']), CERTNO_BG.format(c['code']), 'carlito', log=log)
    # the dates: one size for the five lines (the median of their fits)
    db = bands(doc, c['dates'])
    assert len(db) == 5, db
    dfits = []
    for (b0, b1), (en, _) in zip(db, DATES):
        (x0, y0, x1, y1), base = ink_box(doc, (c['dates'][0], b0 - 1, c['dates'][2], b1 + 1))
        dfits.append(fit(en, 'dejavu', x1 - x0, base - y0))
    dsize = (float(np.median([f[0] for f in dfits])), float(np.median([f[1] for f in dfits])))
    for (b0, b1), (en, bg) in zip(db, DATES):
        swap_line(doc, (c['dates'][0], b0 - 1, c['dates'][2], b1 + 1), en, bg, 'dejavu', log=log, size=dsize)

    # Managing Director: the tail of the signature crosses the top of the M. The signature stays, the paper under
    # the type is rebuilt, and the new words start where the M starts (119 px left of "Director" on these scans).
    (mx0, my0, mx1, my1), mbase = ink_box(doc, c['md'])
    mpx, mst = fit(MD[0], 'serif', mx1 - mx0, mbase - my0)
    mcol = colour(doc, (mx0, my0, mx1, my1))
    m_left = mx0 - 119
    sig = signature_mask(doc, c['sig'])
    doc.erase((m_left - 3, my0 - 3, mx1 + 3, mbase + 12), protect=sig, thr=40, grow=1)
    doc.text(MD[1], 'serif', mpx, mcol, (m_left, mbase), 'l', stretch=mst)
    log.append(f'MD: Director {(mx0, my0, mx1, my1)} base {mbase} px {mpx:.1f} stretch {mst:.3f} colour {mcol}')

    # Verify the certificate:- www.sistemacerts.com: the address stays, the words before it are set again
    m = ink_mask(doc, c['verify'])

    def longest_run(row):
        best, start = (0, 0), None
        for i, v in enumerate(list(row) + [False]):
            if v and start is None:
                start = i
            elif not v and start is not None:
                best = max(best, (i - start, start)); start = None
        return best
    runs = [longest_run(m[y]) for y in range(m.shape[0])]
    url_x0 = c['verify'][0] + max(runs)[1]                   # where the underline of the address starts
    lab_box, vbase = ink_box(doc, (c['verify'][0], c['verify'][1], url_x0 - 4, c['verify'][3]))
    vpx, vst = fit(VERIFY[0], 'carlito', lab_box[2] - lab_box[0], vbase - lab_box[1])
    vcol = colour(doc, lab_box)
    doc.erase((lab_box[0] - 3, lab_box[1] - 3, lab_box[2] + 2, lab_box[3] + 3))
    gap = url_x0 - lab_box[2]
    doc.text(VERIFY[1], 'carlito', vpx, vcol, (url_x0 - gap, vbase), 'r', stretch=vst)
    log.append(f'verify: label {lab_box} url_x0 {url_x0} px {vpx:.1f} stretch {vst:.3f} colour {vcol}')

    # the small print: six justified lines beside the QR code
    pb = bands(doc, c['small'], thr=60)
    lines = [ink_box(doc, (c['small'][0], b0 - 1, c['small'][2], b1 + 1), thr=60) for b0, b1 in pb]
    (lx0, ly0, lx1, ly1), lbase = lines[-1]
    ppx, pst = fit(SMALL_EN_LAST, 'carlito', lx1 - lx0, lbase - ly0)
    pbases = [b for _, b in lines]
    ppitch = (pbases[-1] - pbases[0]) / (len(pbases) - 1)
    px0 = min(b[0] for b, _ in lines)
    px1 = max(b[2] for b, _ in lines)
    pcol = colour(doc, lines[0][0])
    size = ppx
    while len(doc.wrap(SMALL_BG, 'carlito', size, px1 - px0, pst)) > len(lines):
        size *= 0.98
    doc.erase((px0 - 3, lines[0][0][1] - 3, px1 + 3, lines[-1][0][3] + 3), thr=30)
    doc.paragraph(SMALL_BG, 'carlito', size, pcol, px0, pbases[0], px1 - px0, ppitch, stretch=pst, justify=True)
    log.append(f'small: {len(lines)} lines, px {ppx:.1f} → {size:.1f} stretch {pst:.3f} pitch {ppitch:.1f} x {px0}–{px1}')

    doc.text(NOTE, 'carlito-i', 21, (96, 96, 104), (1212, 40), 'r')

    out = doc.save(out_dir + name + '-bg.jpg', quality=90)
    if DEBUG:
        os.makedirs(DEBUG, exist_ok=True)
        open(os.path.join(DEBUG, name + '.log'), 'w').write('\n'.join(log) + '\n')
        both = Image.new('RGB', (2480, 1754), 'white')
        both.paste(doc.src, (0, 0)); both.paste(out, (1240, 0))
        both.save(os.path.join(DEBUG, name + '-pair.jpg'), quality=88)
    return out


def sizes(name):
    base = HIST + name + '-bg'
    img = Image.open(base + '.jpg')
    img.save(base + '.webp', quality=86, method=6)
    for w in (600, 300):
        r = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
        r.save(f'{base}-{w}.jpg', quality=86)
        r.save(f'{base}-{w}.webp', quality=84, method=6)


if __name__ == '__main__':
    for name, cfg in CERTS.items():
        make(name, cfg)
        sizes(name)
        print('made', name + '-bg')
