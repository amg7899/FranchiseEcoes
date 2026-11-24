"""Bulgarian version of the Ministry of Defence certificate SK No 0062/2007 (NATO AQAP 2110), About us → History,
client 2026-11-24. The English lines are taken off the scan and set again in Bulgarian at their places, in Liberation
Serif Bold / Bold Italic (metric twin of the Times New Roman on the scan); the red title in Unbounded (the site's own
display face) with the scan's red, inline and shadow. The paper's printed lattice is rebuilt from its own repeats
(doctools: period), the blue signatures and the stamp are kept where the new type crosses them (protect), and the
crest, logo, frame, "BULFIRE LTD", the numbers and "г." stay. "Превод от английски" marks it as our translation.
The wording follows the site's Bulgarian (About us: "отговаря на съюзническата публикация AQAP 2110 на НАТО").

  python3 tools/history/aqap_bg.py [preview.jpg]     (from the repo root)

Writes assets/img/about/history/aqap-2110-bg.{jpg,webp} (599 px) and -300.
"""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doctools import Doc, FONTS
import sistema_bg as S

FONTS['unbounded'] = 'assets/fonts/unbounded-cyrillic.woff2'
HIST = 'assets/img/about/history/'
CX = 310.5                          # the axis of the centred lines
LATTICE = ((5, 0), (0, 14))         # the printed lattice repeats every 5 px down and 14 px across (autocorrelation)
INK = (62, 59, 66)

# (search box, the English on the scan (for the size), the Bulgarian, font)
LINES = [
    ((150, 114, 470, 134), 'MINISTRY OF DEFENCE', 'МИНИСТЕРСТВО НА ОТБРАНАТА', 'serif-b'),
    ((150, 136, 470, 152), 'OF THE REPUBLIC OF BULGARIA', 'НА РЕПУБЛИКА БЪЛГАРИЯ', 'serif-b'),
    ((200, 320, 420, 336), 'Series  SK No 0062/2007', 'Серия SK № 0062/2007', 'serif-b'),
    ((200, 348, 420, 366), 'This is to certify that', 'С настоящото се удостоверява, че', 'serif-bi'),
    ((190, 366, 430, 382), 'the Quality Management System of', 'системата за управление на качеството на', 'serif-b'),
    ((190, 420, 430, 434), '15 Bansko shose Str., 1331 Sofia, Bulgaria', 'ул. „Банско шосе“ 15, 1331 София, България', 'serif-b'),
    ((130, 436, 490, 455), 'has been assessed and is in compliance with', 'е оценена и отговаря на', 'serif-b'),
    ((130, 456, 490, 478), 'NATO`s Allied Publication AQAP 2110', 'съюзническата публикация AQAP 2110 на НАТО', 'serif-bi'),
    ((220, 486, 400, 502), 'Scope of certification:', 'Обхват на сертификацията:', 'serif-b'),
    ((230, 609, 390, 625), '31st January 2007', '31 януари 2007 г.', 'serif-b'),
]
SCOPE = (((100, 505, 520, 521), (100, 521, 520, 535), (100, 536, 520, 549)),
         'Design, production and servicing of fire-fighting, lifting and other special',
         'Проектиране, производство и сервизно обслужване на противопожарни, подемни и други специални автомобили, '
         'пожарогасително оборудване, летищно наземно обслужващо оборудване и аварийно-спасително оборудване.')
APPROVAL = ((190, 555, 430, 569), 'Original approval date: 31st January 2007',
            ('Дата на първоначално одобрение: ', '31 януари 2007 г.'))
PROVIDED = (((90, 574, 525, 588), (90, 588, 525, 602)),
            'Provided that the Supplier\'s Quality Management System is constant and successful in',
            'При условие че системата за управление на качеството на доставчика функционира постоянно и успешно, '
            'този сертификат е валиден за срок от две години, считано от:')
SIGNERS = [((100, 632, 285, 647), 'Government Quality Assurance', 'Орган за държавно осигуряване'),
           ((150, 647, 230, 661), 'Authority', 'на качеството'),
           ((360, 632, 520, 647), 'Deputy Minister of Defence', 'Заместник-министър на отбраната')]
FEB = ((412, 711, 457, 726), 'February', 'февруари')       # in "19 February 2007 г.": only the month changes
FOOTER = [((88, 740, 532, 750), 'Bulgaria, 1092 Sofia, 3 Dyakon Ignatii Str., Military Standardization, Quality and Codification Directorate',
           'България, 1092 София, ул. „Дякон Игнатий“ 3, Дирекция „Военна стандартизация, качество и кодификация“'),
          ((140, 750, 480, 761), 'Phone: (+359 2) 9220870; Fax: (+359 2) 9814985, e-mail: msdepdir@mod.bg',
           'Тел.: (+359 2) 9220870; факс: (+359 2) 9814985, e-mail: msdepdir@mod.bg')]
TITLE = ((102, 270, 524, 314), 'СЕРТИФИКАТ')
RED, SHADOW, INLINE = (158, 60, 54), (124, 40, 38), (240, 190, 188)
NOTE = ('Превод от английски', 'sans-i', 9.5, (88, 84, 96), (523, 101), 'r')


def measure(doc, box, en, key, thr=80):
    (x0, y0, x1, y1), base = S.ink_box(doc, box, thr=thr)
    px, st = S.fit(en, key, x1 - x0, base - y0)
    return dict(box=(int(x0), int(y0), int(x1), int(y1)), base=base, px=px, stretch=st)


def blue_ink(doc):
    """The blue of the signatures and the stamp (at work scale), kept where the new type passes under it."""
    lab = cv2.cvtColor(np.clip(doc.orig, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.int16)
    m = ((lab[..., 2] - 128) < -10) & (lab[..., 0] < 215)
    return cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)


def red_title(doc, text, box, cap):
    """The red title: fill, a light inline 1.4 px inside the edge, a darker shadow 2 px down and right."""
    s = doc.sc
    f = doc.font('unbounded', cap / 0.7)
    try:
        f.set_variation_by_axes([700])
    except Exception:
        pass
    w = f.getlength(text)
    asc, desc = f.getmetrics()
    pad = 8 * s
    lay = Image.new('L', (int(w) + 2 * pad, asc + desc + 2 * pad), 0)
    ImageDraw.Draw(lay).text((pad, pad), text, font=f, fill=255)
    bb = lay.getbbox()
    G = np.asarray(lay.crop(bb), np.float32) / 255
    h, gw = G.shape
    # size to the old word's ink: same height, at most its width
    x0, y0, x1, y1 = [v * s for v in box]
    scale = min((y1 - y0) / h, (x1 - x0) / gw)
    G = cv2.resize(G, (round(gw * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    h, gw = G.shape
    cxw = CX * s
    top, left = y0 + ((y1 - y0) - h) // 2, round(cxw - gw / 2)
    def lay_on(mask, colour, dy=0, dx=0):
        Y0, X0 = top + dy, left + dx
        a = mask[..., None]
        doc.a[Y0:Y0 + h, X0:X0 + gw] = doc.a[Y0:Y0 + h, X0:X0 + gw] * (1 - a) + np.array(colour, np.float32) * a
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * round(r * s) + 1, 2 * round(r * s) + 1))
    sh = cv2.GaussianBlur(G, (0, 0), 0.5 * s)
    lay_on(sh * 0.95, SHADOW, round(2.0 * s), round(2.0 * s))
    lay_on(G, RED)
    inner = cv2.erode(G, k(1.3))
    ring = np.clip(inner - cv2.erode(G, k(2.1)), 0, 1)
    lay_on(cv2.GaussianBlur(ring, (0, 0), 0.35 * s) * 0.9, INLINE)


def make(out=HIST + 'aqap-2110-bg.jpg', preview=None, log=None):
    doc = Doc(HIST + 'aqap-2110.jpg', sc=4)
    blue = blue_ink(doc)
    jobs, boxes = [], []

    for box, en, bg, key in LINES:
        m = measure(doc, box, en, key)
        jobs.append((bg, key, m['px'], m['stretch'], m['base'], 'm', CX))
        boxes.append(m['box'])
        if log is not None:
            log.append(f'{en[:30]!r}: {m}')

    # the scope: three centred lines at the old baselines
    sm = [measure(doc, b, SCOPE[1] if i == 0 else 'x', 'serif-bi') if i == 0 else S.ink_box(doc, b, thr=80)
          for i, b in enumerate(SCOPE[0])]
    spx, sst = sm[0]['px'], sm[0]['stretch']
    sbases = [sm[0]['base']] + [b for _, b in sm[1:]]
    sboxes = [sm[0]['box']] + [tuple(int(v) for v in bb) for bb, _ in sm[1:]]
    swidth = max(b[2] - b[0] for b in sboxes)
    size = spx
    while len(doc.wrap(SCOPE[2], 'serif-bi', size, swidth, sst)) > 3:
        size *= 0.985
    slines = doc.wrap(SCOPE[2], 'serif-bi', size, swidth, sst)
    for ln, base in zip(slines, sbases):
        jobs.append((ln, 'serif-bi', size, sst, base, 'm', CX))
    boxes += sboxes

    # original approval date: the label bold, the date bold italic, centred together
    am = measure(doc, APPROVAL[0], APPROVAL[1], 'serif-b')
    boxes.append(am['box'])
    lab_bg, date_bg = APPROVAL[2]
    wl = doc.measure(lab_bg, 'serif-b', am['px'], am['stretch'])
    wd = doc.measure(date_bg, 'serif-bi', am['px'], am['stretch'])
    ax = CX - (wl + wd) / 2
    jobs.append((lab_bg, 'serif-b', am['px'], am['stretch'], am['base'], 'l', ax))
    jobs.append((date_bg, 'serif-bi', am['px'], am['stretch'], am['base'], 'l', ax + wl))

    # "Provided that …": two centred lines
    pm = measure(doc, PROVIDED[0][0], PROVIDED[1], 'serif-b')
    pb2 = S.ink_box(doc, PROVIDED[0][1], thr=80)
    boxes += [pm['box'], tuple(int(v) for v in pb2[0])]
    pwidth = pm['box'][2] - pm['box'][0]
    size = pm['px']
    while len(doc.wrap(PROVIDED[2], 'serif-b', size, pwidth, pm['stretch'])) > 2:
        size *= 0.985
    for ln, base in zip(doc.wrap(PROVIDED[2], 'serif-b', size, pwidth, pm['stretch']), (pm['base'], pb2[1])):
        jobs.append((ln, 'serif-b', size, pm['stretch'], base, 'm', CX))

    # the signers, centred on the old lines
    for box, en, bg in SIGNERS:
        m = measure(doc, box, en, 'serif-b')
        boxes.append(m['box'])
        jobs.append((bg, 'serif-b', m['px'], m['stretch'], m['base'], 'm', (m['box'][0] + m['box'][2]) / 2,
                     max(m['box'][2] - m['box'][0] + 14, 172)))

    fm = measure(doc, FEB[0], FEB[1], 'serif')
    boxes.append(fm['box'])
    feb_job = (FEB[2], 'serif', fm['px'], fm['stretch'], fm['base'], 'l', fm['box'][0], fm['box'][2] - fm['box'][0])

    # footer
    for box, en, bg in FOOTER:
        m = measure(doc, box, en, 'serif-b', thr=70)
        boxes.append(m['box'])
        jobs.append((bg, 'serif-b', m['px'], m['stretch'], m['base'], 'm', (m['box'][0] + m['box'][2]) / 2,
                     m['box'][2] - m['box'][0] + 6))

    # the red title
    tb, _ = S.ink_box(doc, TITLE[0], thr=60)
    boxes.append(tuple(int(v) for v in tb))

    pad = [(b[0] - 3, b[1] - 3, b[2] + 3, b[3] + 3) for b in boxes[:-1]]
    # "February": not a pixel further right than its own y, the 2 of 2007 starts 3 px after it
    fb = fm['box']
    pad[boxes.index(fb)] = (fb[0] - 3, fb[1] - 3, fb[2] + 2, fb[3] + 3)
    tpad = (tb[0] - 4, tb[1] - 4, tb[2] + 4, tb[3] + 4)
    for thr in (18, 12):
        doc.erase(tpad, thr=thr, grow=3.0, ctx=12, radius=2, median=31, period=LATTICE)
        doc.erase(None, boxes=pad, protect=blue, thr=thr, grow=2.0, ctx=10, radius=2, median=25, period=LATTICE)

    # letters of the red title: same height as the old ones (cap 34 px), at most their width
    red_title(doc, TITLE[1], (tb[0] + 4, tb[1] + 1, tb[2] - 4, tb[3] - 4), 34)

    for job in jobs + [feb_job]:
        text, key, px, st, base, anchor, x = job[:7]
        squeeze = job[7] if len(job) > 7 else None
        doc.text(text, key, px, INK, (x, base), anchor, stretch=st, blur=0.4, squeeze=squeeze)
    t, key, px, col, xy, anchor = NOTE
    doc.text(t, key, px, col, xy, anchor, blur=0.3)
    # the blue ink back on top where the new type ran under it
    s = doc.sc
    keep = cv2.GaussianBlur(blue.astype(np.float32), (0, 0), 0.4 * s)[..., None]
    doc.a = doc.a * (1 - keep) + np.minimum(doc.a, doc.orig) * keep

    img = doc.save(out, quality=90)
    if preview:
        both = Image.new('RGB', (1198, 816), 'white')
        both.paste(doc.src, (0, 0)); both.paste(img, (599, 0))
        both.save(preview, quality=90)
    return img


def sizes(base=HIST + 'aqap-2110-bg'):
    img = Image.open(base + '.jpg')
    img.save(base + '.webp', quality=86, method=6)
    r = img.resize((300, round(img.height * 300 / img.width)), Image.LANCZOS)
    r.save(base + '-300.jpg', quality=86)
    r.save(base + '-300.webp', quality=84, method=6)


if __name__ == '__main__':
    make(preview=sys.argv[1] if len(sys.argv) > 1 else None)
    sizes()
    print('made aqap-2110-bg')
