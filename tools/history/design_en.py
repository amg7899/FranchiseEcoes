"""English version of the Patent Office certificate No 6947 (industrial design "Противопожарен автомобил"),
About us → History, client 2026-11-24. The Bulgarian words are taken off the scan and set again in English at
their places; the INID codes "(15)", "(21)" …, the numbers and dates, "BG", the emblem, the border, the flag, the
signature, the comma before the title and the handwritten date stay as they are. The display lines (office, title,
"President", "Date") are set in Della Respira (SIL OFL, tools/history/fonts/), the closest open face to the
certificate's Art Nouveau lettering; the fields in Liberation Serif (metric twin of the Times New Roman on the
scan). A small note "Translation from Bulgarian" marks the page as our translation.

  python3 tools/history/design_en.py [preview.jpg]     (from the repo root)

Writes assets/img/about/history/design-6947-en.{jpg,webp} (599 px) and -300.
"""
import os, sys
import numpy as np, cv2
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doctools import Doc, FONTS

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS['della'] = os.path.join(HERE, 'fonts', 'della-respira-latin-400-normal.woff2')
HIST = 'assets/img/about/history/'

TITLE = (92, 84, 113)       # the navy-violet of the printed display lines
SIGN = (118, 110, 132)      # the lighter print of the signature block
LAB = (104, 93, 95)         # field labels (regular)
VAL = (86, 76, 79)          # field values (bold)

# Display lines: Della Respira's cap height is 0.80 em, so px = cap height on the scan / 0.80.
# Fields: Liberation Serif digits/capitals 0.66 em; the scan's digits are 7–7.5 px tall, so 11 px.
F = 11.0
CX = 311.5                  # the axis of the centred title lines (the emblem's and the old lines' middle)

# (erase box, text, font, px, colour, (x, baseline), anchor, extra). The boxes start right after the INID code's
# ")" and end before the kept value; labels that would run into their value are narrowed a little (squeeze).
ITEMS = [
    ((196, 140, 428, 161), 'PATENT OFFICE', 'della', 14.0, TITLE, (CX, 154), 'm', dict(track=1.4)),
    ((232, 162, 391, 183), 'of the Republic of Bulgaria', 'della', 11.3, TITLE, (CX, 174), 'm', dict(track=0.3)),
    ((134, 185, 490, 229), 'CERTIFICATE', 'della', 38.5, TITLE, (CX, 220), 'm', dict(track=2.0)),
    ((196, 226, 426, 250), 'OF INDUSTRIAL DESIGN', 'della', 16.2, TITLE, (CX, 244), 'm', dict(track=1.0)),
    # left column
    ((101, 292, 176, 305), 'Registered on', 'serif', F, LAB, (102, 300), 'l', {}),
    ((101, 304, 211, 318), 'Term of protection until', 'serif', F, LAB, (102, 313), 'l', {}),
    ((101, 328, 153, 341), 'Application No.', 'serif', F, LAB, (102, 337), 'l', dict(squeeze=165 - 102)),
    ((101, 341, 149, 353), 'Filed on', 'serif', F, LAB, (102, 350), 'l', {}),
    ((79, 367, 199, 380), 'Convention priority', 'serif', F, LAB, (81, 376), 'l', {}),
    ((102, 405, 198, 420), 'Application published', 'serif', F, LAB, (103, 415), 'l', dict(squeeze=203 - 103)),
    ((102, 420, 207, 431), 'Divided from application No.', 'serif', F, LAB, (104, 428), 'l', {}),
    ((102, 445, 211, 459), 'Number of designs:', 'serif', F, LAB, (104, 454), 'l', {}),
    ((102, 459, 250, 474), 'Industrial property', 'serif', F, LAB, (104, 467), 'l', {}),
    ((101, 473, 161, 483), 'representative', 'serif', F, LAB, (104, 478), 'l', {}),
    ((105, 484, 213, 496), 'Lyubomir Iliev Kosev', 'serif-b', F, VAL, (113, 492), 'l', {}),
    ((104, 496, 273, 507), '61a Knyaz Boris I St., fl. 2, office 8,', 'serif-b', F, VAL, (110, 503), 'l', {}),
    ((105, 507, 152, 518), 'P.O. Box 1162', 'serif-b', F, VAL, (112, 515), 'l', {}),
    ((105, 518, 176, 531), '1000 Sofia', 'serif-b', F, VAL, (111, 526), 'l', {}),
    ((103, 562, 218, 576), 'FIRE-FIGHTING', 'serif-b', F, VAL, (105, 572), 'l', {}),
    ((82, 576, 158, 590), 'VEHICLE', 'serif-b', F, VAL, (85, 585), 'l', {}),
    # right column
    ((335, 289, 372, 303), 'LOC:', 'serif', F, LAB, (337, 299), 'l', {}),
    ((338, 314, 411, 326), 'Holder(s):', 'serif', F, LAB, (340, 323), 'l', {}),
    ((337, 325, 441, 338), '"BULFIRE" EOOD', 'serif-b', F, VAL, (340, 335), 'l', {}),
    ((337, 338, 520, 350), '15 Shose Bankya Blvd., Republika quarter', 'serif-b', F, VAL, (340, 346), 'l', {}),
    ((338, 350, 406, 362), '1331 Sofia', 'serif-b', F, VAL, (341, 358), 'l', {}),
    ((337, 362, 397, 373), 'BULGARIA', 'serif-b', F, VAL, (340, 370), 'l', {}),
    ((339, 398, 385, 412), 'Designer(s):', 'serif', F, LAB, (341, 408), 'l', {}),
    ((340, 412, 456, 423), 'Atanas Mihaylov Gouchev', 'serif-b', F, VAL, (343, 419), 'l', {}),
    ((339, 423, 482, 434), 'Zaharna Fabrika quarter, bl. 39,', 'serif-b', F, VAL, (342, 430), 'l', {}),
    ((339, 434, 391, 446), 'entr. B, apt. 5', 'serif-b', F, VAL, (342, 442), 'l', {}),
    ((340, 446, 408, 457), '1309 Sofia', 'serif-b', F, VAL, (343, 453), 'l', {}),
    ((339, 457, 399, 468), 'BULGARIA', 'serif-b', F, VAL, (342, 464), 'l', {}),
    # signature block, right-aligned as on the scan; "К" stays (it reads the same in Latin), the comma moves along
    ((437, 619, 534, 640), 'President:', 'della', 14.0, SIGN, (528, 633), 'r', dict(track=0.5)),
    ((494, 695, 534, 714), 'Date:', 'della', 14.0, SIGN, (528, 709), 'r', dict(track=0.5)),
]
# "Манев": the signature's thin stroke crosses the top left of the М, so it is kept as a line (protect)
NAME = ((489, 639, 536, 658), 'Manev', 'della', 15.0, SIGN, (492, 654), ((492.5, 639.5), (482.0, 657.5), 2.6))
COMMA = (428, 623, 438, 644)      # the comma-like pen tick before "Председател:" (erased)
COMMA_INK = (428, 623, 436, 644)  # the tick alone (moved), without the edge of the П beside it


def cut_ink(doc, box):
    """The ink of a small mark as a darkening factor over its paper (work scale)."""
    s = doc.sc
    x0, y0, x1, y1 = [v * s for v in box]
    patch = doc.orig[y0:y1, x0:x1]
    paper = np.median(patch.reshape(-1, 3), axis=0)
    return np.clip(patch / paper, 0, 1)


def put_ink(doc, ink, box, dx):
    """Lay a cut mark down again dx scan px to the side of where it was."""
    s = doc.sc
    x0, y0, x1, y1 = [v * s for v in box]
    X0 = x0 + round(dx * s)
    doc.a[y0:y1, X0:X0 + (x1 - x0)] *= ink


NOTE = ('Translation from Bulgarian', 'sans-i', 9.5, (96, 90, 98), (531, 114), 'r')


def make(out=HIST + 'design-6947-en.jpg', preview=None):
    doc = Doc(HIST + 'design-6947.jpg', sc=4)
    doc.set_grain((432, 522, 528, 598), sigma=8.0)
    comma = cut_ink(doc, COMMA_INK)
    nbox, ntext, nkey, npx, ncol, nxy, (p0, p1, w) = NAME
    line = np.zeros(doc.a.shape[:2], np.uint8)
    cv2.line(line, tuple(round(v * doc.sc) for v in p0), tuple(round(v * doc.sc) for v in p1), 1, round(w * doc.sc))
    # every box in one fill (neighbouring lines never feed each other); a second, finer pass takes what is left
    boxes = [it[0] for it in ITEMS] + [COMMA, nbox]
    for thr in (18, 12):
        doc.erase(None, boxes=boxes, protect=line.astype(bool), thr=thr, grow=2.5, ctx=10, radius=2, median=21)
    for box, text, key, px, col, xy, anchor, extra in ITEMS:
        doc.text(text, key, px, col, xy, anchor, blur=0.45, **extra)
    # the comma before the title moves with it: 3 px before the first letter of "President:"
    pw = doc.measure('President:', 'della', 14.0, track=0.5)
    put_ink(doc, comma, COMMA_INK, (528 - pw - 4) - COMMA_INK[2])
    # (28): the value follows its longer English label
    lab = doc.measure('Number of designs:', 'serif', F)
    doc.text('one', 'serif-b', F, VAL, (104 + lab + 10, 454), 'l', blur=0.45)
    doc.text(ntext, nkey, npx, ncol, nxy, 'l', blur=0.45, track=0.3)
    t, key, px, col, xy, anchor = NOTE
    doc.text(t, key, px, col, xy, anchor, blur=0.3)
    img = doc.save(out, quality=90)
    if preview:
        both = Image.new('RGB', (1198, 816), 'white')
        both.paste(doc.src, (0, 0)); both.paste(img, (599, 0))
        both.save(preview, quality=90)
    return img


def sizes(base=HIST + 'design-6947-en'):
    img = Image.open(base + '.jpg')
    img.save(base + '.webp', quality=86, method=6)
    r = img.resize((300, round(img.height * 300 / img.width)), Image.LANCZOS)
    r.save(base + '-300.jpg', quality=86)
    r.save(base + '-300.webp', quality=84, method=6)


if __name__ == '__main__':
    make(preview=sys.argv[1] if len(sys.argv) > 1 else None)
    sizes()
    print('made design-6947-en')
