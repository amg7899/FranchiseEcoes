"""The MultiCharger page head (assets/img/v2/head-multicharger-*), as published since 2026-11-04.
Client: the AI upscale looked "too obviously AI-edited"; the trailer and the pickup are fine, the ground,
the plants and the landscape are the problem (ChatGPT's smeared "worm" textures). So, as a photographer
would shoot it: the trailer, the pickup, the SUV and the cables stay sharp (polygons below, in the
original's pixels); the ground's fine artificial texture is calmed (shapes and light kept); the ground and
the landscape go softly out of focus by their distance, in focus at the trailer's wheels (a ground plane
seen from eye height: the blur grows linearly with the row's distance from the focus band); then one even
film grain. Not part of the site. Needs numpy, pillow, scipy (see tools/upscale.py for the venv).

  python -I tools/head-dof.py <original.png> <esrgan-x4.png> <out-3200.png> 9 12 "" 0.3
Then resize to 800/1200/1672/2400/3200, WebP + JPEG 4:4:4.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

src, x4p, out = sys.argv[1:4]
R_FAR = float(sys.argv[4]) if len(sys.argv) > 4 else 9.0     # px at 3200: sky, mountains, the far plain
R_NEAR = float(sys.argv[5]) if len(sys.argv) > 5 else 9.0    # px at 3200: the bottom edge (nearest ground)
MASK_OUT = sys.argv[6] if len(sys.argv) > 6 else None

W = 3200
o = Image.open(src).convert('RGB')
k = W / o.width
H = round(o.height * k)
lan = np.asarray(o.resize((W, H), Image.LANCZOS), dtype=np.float32)
ai = np.asarray(Image.open(x4p).convert('RGB').resize((W, H), Image.LANCZOS), dtype=np.float32)
base = lan * 0.65 + ai * 0.35
orig = base.copy()

# ---- what stays sharp (original coordinates)
TRAILER = [(1013, 318), (1608, 308), (1614, 606), (1478, 608), (1474, 668), (1290, 670), (1292, 606), (1013, 602)]
PICKUP = [(522, 600), (522, 560), (528, 515), (545, 503), (590, 494), (622, 486), (660, 458), (690, 440),
          (720, 433), (800, 430), (845, 432), (856, 440), (858, 477), (940, 477), (958, 480), (960, 520),
          (930, 523), (860, 520), (800, 525), (770, 545), (760, 600), (700, 645), (600, 640), (540, 625)]
ANTENNA = [(725, 434), (732, 402), (738, 402), (732, 434)]
SUV = [(722, 600), (735, 565), (760, 540), (780, 530), (810, 518), (870, 510), (950, 511), (1020, 511),
       (1050, 520), (1080, 535), (1100, 553), (1122, 558), (1125, 585), (1145, 595), (1157, 625), (1160, 690),
       (1150, 722), (1120, 728), (1035, 735), (1025, 770), (985, 772), (960, 745), (900, 745), (800, 742),
       (790, 765), (740, 765), (722, 735)]
CABLES = [[(1002, 612), (1030, 640), (1060, 672), (1095, 703), (1130, 718), (1170, 722), (1210, 714),
           (1245, 690), (1268, 650), (1282, 600), (1290, 540), (1290, 505)],
          [(1467, 505), (1472, 560), (1485, 600), (1495, 625)]]

m = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(m)
for poly in (TRAILER, PICKUP, ANTENNA, SUV):
    d.polygon([(x * k, y * k) for x, y in poly], fill=255)
for line in CABLES:
    d.line([(x * k, y * k) for x, y in line], fill=255, width=round(8 * k), joint='curve')
hard = np.asarray(m, dtype=np.float32) / 255
# keep the subject's colours out of the blurred ground (normalised convolution), and blend with a soft edge
excl = np.asarray(m.filter(ImageFilter.MaxFilter(9)), dtype=np.float32) / 255
soft = np.asarray(m.filter(ImageFilter.GaussianBlur(1.6)), dtype=np.float32) / 255
if MASK_OUT:
    m.save(MASK_OUT)

# ---- the blur for each row: a ground plane seen from eye height, in focus at the trailer's wheels
y = np.arange(H) / H
Y_H, F0, F1 = 350 / 941, 0.68, 0.72          # horizon; the band in focus (the trailer stands there)
r = np.where(y <= Y_H, R_FAR,
     np.where(y < F0, R_FAR * (F0 - y) / (F0 - Y_H),
     np.where(y <= F1, 0.0, R_NEAR * (y - F1) / (1 - F1))))

# ---- the ground and the plants: keep their shapes and light, calm ChatGPT's fine "worm" texture
#      (high frequencies kept at HF_KEEP below the horizon, outside the vehicles)
HF_KEEP = float(sys.argv[7]) if len(sys.argv) > 7 else 0.3
keep0 = 1 - excl
low = np.stack([gaussian_filter(base[..., c] * keep0, 2.6) for c in range(3)], axis=-1)
den0 = gaussian_filter(keep0, 2.6)[..., None]
low = np.where(den0 > 1e-3, low / np.maximum(den0, 1e-3), base)
yy = (np.arange(H) / H)[:, None]
ground = np.clip((yy - (350 / 941 + 0.01)) / 0.04, 0, 1) * (1 - soft)
hf = 1 - (1 - HF_KEEP) * ground
base = low + (base - low) * hf[..., None]

levels = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12]
levels = [l for l in levels if l <= max(R_FAR, R_NEAR) + 1.5]
keep = 1 - excl
stack = []
for lv in levels:
    if lv == 0:
        stack.append(base.copy()); continue
    s = lv / 2
    num = np.stack([gaussian_filter(base[..., c] * keep, s) for c in range(3)], axis=-1)
    den = gaussian_filter(keep, s)[..., None]
    blurred = np.where(den > 1e-3, num / np.maximum(den, 1e-3), base)
    stack.append(blurred)
    print('blur', lv, flush=True)
lv = np.array(levels, dtype=np.float32)
idx = np.clip(np.searchsorted(lv, r) - 1, 0, len(lv) - 2)
t = np.clip((r - lv[idx]) / (lv[idx + 1] - lv[idx]), 0, 1)
bg = np.empty_like(base)
for row in range(H):
    i = idx[row]
    bg[row] = stack[i][row] * (1 - t[row]) + stack[i + 1][row] * t[row]
res = soft[..., None] * orig + (1 - soft[..., None]) * bg

# ---- one even grain over the whole picture (as on film), a little stronger in the mid-tones
rng = np.random.default_rng(7)
n = gaussian_filter(rng.normal(0, 1, (H, W)).astype(np.float32), 0.55)
n = n / n.std() * 2.2
lum = res.mean(axis=2, keepdims=True) / 255
res = res + n[..., None] * (0.55 + 1.8 * lum * (1 - lum))
Image.fromarray(res.clip(0, 255).round().astype(np.uint8)).save(out)
print('done', out, W, H)
