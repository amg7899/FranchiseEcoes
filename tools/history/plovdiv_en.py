#!/usr/bin/env python3
"""English version of the Plovdiv 2003 Gold Medal diploma (site image plovdiv-2003.jpg, 583 x 822).
Works at 2x: the Bulgarian text is taken off (band rebuilt per column, paper by inpainting + the paper's own grain),
the English text is set in the closest fonts at the same places, sizes and colours, then the picture is scaled back.
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SC = 2
F = '/usr/share/fonts/truetype/'
FONT = {
    'serif': F + 'dejavu/DejaVuSerif.ttf',
    'sans': F + 'crosextra/Carlito-Regular.ttf',
    'it_serif_b': F + 'liberation/LiberationSerif-BoldItalic.ttf',
    'it_sans': F + 'liberation/LiberationSans-Italic.ttf',
    'medal': F + 'crosextra/Carlito-Regular.ttf',
}
rng = np.random.default_rng(7)

src = Image.open(sys.argv[1]).convert('RGB')
W, H = src.size
big = np.array(src.resize((W * SC, H * SC), Image.LANCZOS)).astype(np.float32)
ORIG = big.copy()

# --- paper grain: residual of a clean patch of paper (right of the "certifies that" line)
def grain_from(x0, y0, x1, y1, sigma=3.0):
    p = big[y0 * SC:y1 * SC, x0 * SC:x1 * SC]
    return p - cv2.GaussianBlur(p, (0, 0), sigma)
GRAIN = grain_from(452, 262, 572, 336)

def grain_tile(h, w):
    gh, gw = GRAIN.shape[:2]
    out = np.zeros((h, w, 3), np.float32)
    for y in range(0, h, gh // 2):
        for x in range(0, w, gw // 2):
            oy, ox = rng.integers(0, gh // 2), rng.integers(0, gw // 2)
            ph, pw = min(gh // 2, h - y), min(gw // 2, w - x)
            out[y:y + ph, x:x + pw] = GRAIN[oy:oy + ph, ox:ox + pw]
    return out

def erase(box, thr=16, grow=2, ctx=14, radius=3, cool=False, tb=5.0):
    """Take the text off the paper inside box (1x coords): mask what differs from the local paper, inpaint, add grain."""
    x0, y0, x1, y1 = [v * SC for v in box]
    c = ctx * SC
    X0, Y0, X1, Y1 = max(0, x0 - c), max(0, y0 - c), min(W * SC, x1 + c), min(H * SC, y1 + c)
    reg = big[Y0:Y1, X0:X1].copy()
    u8 = np.clip(reg, 0, 255).astype(np.uint8)
    bgm = cv2.medianBlur(u8, 31).astype(np.float32)
    lab = cv2.cvtColor(u8, cv2.COLOR_RGB2LAB).astype(np.float32)
    labb = cv2.cvtColor(bgm.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    d = np.sqrt(((lab - labb) ** 2).sum(axis=2))
    m = np.zeros(d.shape, np.uint8)
    if cool:   # blue-grey ink on warm paper and a warm brown drawing: only what is clearly bluer than its surroundings
        db = labb[..., 2] - lab[..., 2]
        sel = (db > tb) | ((d > thr) & (db > tb * 0.5))
    else:
        sel = d > thr
    m[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = sel[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0].astype(np.uint8)
    m = cv2.dilate(m, np.ones((2 * grow * SC + 1, 2 * grow * SC + 1), np.uint8))
    filled = cv2.inpaint(u8, m * 255, radius * SC, cv2.INPAINT_TELEA).astype(np.float32)
    soft = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2 * SC)[..., None]
    g = grain_tile(*reg.shape[:2])
    out = reg * (1 - soft) + (filled + g * 0.95) * soft
    big[Y0:Y1, X0:X1] = out

def rebuild_band(x0, x1, y0, y1, top=(92, 101)):
    """The brown band behind the title: per column the clean strip above the letters, its own texture tiled down."""
    X0, X1 = x0 * SC, x1 * SC
    t0, t1 = top[0] * SC, top[1] * SC
    strip = big[t0:t1, X0:X1]
    col = np.median(strip, axis=0)                               # band colour per column
    col = cv2.GaussianBlur(col[None], (0, 0), sigmaX=4 * SC, sigmaY=0.1)[0]
    tex = strip - col[None]                                      # its grain
    Y0, Y1 = y0 * SC, y1 * SC
    out = np.empty((Y1 - Y0, X1 - X0, 3), np.float32)
    th = tex.shape[0]
    for yy in range(0, Y1 - Y0, th):
        shift = int(rng.integers(0, X1 - X0))
        t = np.roll(tex, shift, axis=1)
        h = min(th, Y1 - Y0 - yy)
        out[yy:yy + h] = col[None] + t[:h]
    big[Y0:Y1, X0:X1] = out

def clone_period(x0, x1, y0, y1, period, src_end, feather=1.5):
    """Repeat a periodic drawing (the window row under the roof) over x0..x1 from the clean stretch ending at src_end."""
    X0, X1, Y0, Y1, P, E = x0 * SC, x1 * SC, y0 * SC, y1 * SC, round(period * SC), src_end * SC
    patch = np.empty((Y1 - Y0, X1 - X0, 3), np.float32)
    for x in range(X0, X1):
        k = -(-(x - E + 1) // P)
        patch[:, x - X0] = ORIG[Y0:Y1, x - k * P]
    w = np.ones((Y1 - Y0, 1, 1), np.float32)
    f = int(feather * SC)
    for i in range(f):
        w[i] = w[-1 - i] = (i + 1) / (f + 1)
    big[Y0:Y1, X0:X1] = big[Y0:Y1, X0:X1] * (1 - w) + patch * w

# ---------------------------------------------------------------- take the Bulgarian text off
rebuild_band(60, 394, 101, 167)                     # ДИПЛОМ
erase((56, 185, 284, 216))               # МЕЖДУНАРОДЕН
erase((56, 217, 168, 249))               # ПАНАИР
erase((60, 253, 143, 272))               # ПЛОВДИВ
erase((198, 291, 404, 317))              # УДОСТОВЕРЯВА, ЧЕ
erase((88, 340, 498, 366))                          # експонатът „Автомобил за аварийно-спасителна
erase((205, 362, 431, 386))                         # дейност BF 4x4 VRF“
erase((138, 384, 450, 408))                         # Изложител: „Булфайър“ ЕООД – София
erase((160, 437, 444, 466))              # Е НАГРАДЕН С ОТЛИЧИЕТО
erase((124, 489, 479, 535), thr=18)      # ЗЛАТЕН МЕДАЛ
erase((262, 616, 505, 640), thr=16)                 # Международен технически панаир (on paper)
erase((190, 614, 264, 641), thr=26, cool=True, tb=3, grow=3)  # На 59-ти (over the building: only the blue-grey ink)
clone_period(190, 266, 611, 628, 21, 193)          # and the window row under the roof, repeated from its clean part
erase((364, 636, 505, 655), thr=16)                 # 29.09. - 4.10. 2003 г.
erase((276, 744, 396, 763), thr=12)                 # Изпълнителен директор
erase((17, 296, 41, 800), thr=12, ctx=6)            # the vertical note on the left margin

out = Image.fromarray(np.clip(big, 0, 255).astype(np.uint8))

# ---------------------------------------------------------------- set the English text
def font(key, px): return ImageFont.truetype(FONT[key], round(px * SC))

def draw_text(text, key, px, color, anchor_xy, anchor='la', track=0.0, stretch=1.0, blur=0.5, alpha=0.96, rotate=0, fit=None, stroke=0):
    """Draw text on its own layer (tracking, horizontal stretch, a touch of scan softness), then lay it on the paper."""
    f = font(key, px)
    widths = [f.getlength(ch) for ch in text]
    if fit:   # tracking so the ink spans `fit` px (1x) after the stretch
        track = ((fit * SC / stretch) - sum(widths)) / (len(text) - 1) / SC
    total = sum(widths) + track * SC * (len(text) - 1)
    asc, desc = f.getmetrics()
    lay = Image.new('L', (int(total) + 8 * SC, asc + desc + 8 * SC), 0)
    d = ImageDraw.Draw(lay)
    x = 4 * SC
    for ch, wch in zip(text, widths):
        d.text((x, 4 * SC), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
        x += wch + track * SC
    if stretch != 1.0:
        lay = lay.resize((int(lay.width * stretch), lay.height), Image.LANCZOS)
    if blur: lay = lay.filter(ImageFilter.GaussianBlur(blur * SC / 2))
    if rotate: lay = lay.rotate(rotate, expand=True, resample=Image.BICUBIC)
    lay_np = np.array(lay).astype(np.float32) / 255 * alpha
    # anchor: x by 'l'/'m'/'r' on the ink box, y = baseline given (anchor_xy[1] is the baseline in 1x)
    bbox = lay.getbbox()
    ax, ay = anchor_xy[0] * SC, anchor_xy[1] * SC
    if rotate:   # anchor_xy = left and top of the ink box (the end of the line is its top when turned by 90°)
        left = ax - bbox[0]; top = ay - bbox[1]
    else:
        inkw = bbox[2] - bbox[0]
        if anchor[0] == 'l': left = ax - bbox[0]
        elif anchor[0] == 'm': left = ax - bbox[0] - inkw / 2
        else: left = ax - bbox[2]
        top = ay - (4 * SC + asc)                      # baseline at ay
    left, top = int(round(left)), int(round(top))
    base = np.array(out).astype(np.float32)
    h, w = lay_np.shape
    y0, x0 = max(0, top), max(0, left)
    y1, x1 = min(base.shape[0], top + h), min(base.shape[1], left + w)
    a = lay_np[y0 - top:y1 - top, x0 - left:x1 - left][..., None]
    base[y0:y1, x0:x1] = base[y0:y1, x0:x1] * (1 - a) + np.array(color, np.float32) * a
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

SLATE = (98, 101, 116)         # the blue-grey of the capitals
out = draw_text('DIPLOMA', 'serif', 60, (122, 113, 107), (66, 158), 'la', fit=318, stroke=1, alpha=0.93)
out = draw_text('INTERNATIONAL', 'sans', 33, SLATE, (59, 209), 'la', track=0.4, stretch=1.04)
out = draw_text('FAIR', 'sans', 33, SLATE, (59, 242), 'la', track=0.4, stretch=1.04)
out = draw_text('PLOVDIV', 'sans', 21, SLATE, (63, 269), 'la', track=0.3, stretch=1.04)
out = draw_text('CERTIFIES THAT', 'sans', 26, SLATE, (301, 311), 'ma', track=0.6, stretch=1.04)
INK = (66, 55, 52)
out = draw_text('the exhibit “Vehicle for Emergency and Rescue', 'it_serif_b', 20.5, INK, (296, 359), 'ma', alpha=0.95)
out = draw_text('Operations BF 4x4 VRF”', 'it_serif_b', 20.5, INK, (300, 380), 'ma', alpha=0.95)
out = draw_text('Exhibitor: “Bulfire” EOOD – Sofia', 'it_serif_b', 20.5, INK, (296, 402), 'ma', alpha=0.95)
out = draw_text('HAS BEEN AWARDED', 'sans', 26, SLATE, (302, 460), 'ma', track=0.6, stretch=1.04)
out = draw_text('GOLD MEDAL', 'medal', 54, (92, 96, 114), (128, 529), 'la', fit=344, stroke=1)
LIGHT = (112, 118, 134)
out = draw_text('at the 59th International Technical Fair', 'it_sans', 15.5, LIGHT, (501, 633), 'ra', alpha=1.0)
out = draw_text('29.09. – 4.10.2003', 'it_sans', 15.5, LIGHT, (501, 651), 'ra')
out = draw_text('Executive Director', 'it_sans', 11, (138, 136, 140), (336, 758), 'ma')
NOTE = (88, 92, 112)
out = draw_text('The winning candidate may not use the award “Gold Medal and Diploma” in any way', 'it_sans', 8.2, NOTE, (21, 369), rotate=90, blur=0.3)
out = draw_text('for a product other than the one stated in this diploma.', 'it_sans', 8.2, NOTE, (31, 369), rotate=90, blur=0.3)
out = draw_text('Translation from Bulgarian', 'it_sans', 9.5, (92, 86, 82), (568, 17), 'ra', blur=0.2)

res = out.resize((W, H), Image.LANCZOS)
res.save(sys.argv[2], quality=92)
print('saved', sys.argv[2], res.size)
