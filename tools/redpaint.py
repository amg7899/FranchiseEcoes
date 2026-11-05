#!/usr/bin/env python3
"""The product's red body, painted better (client, 2026-11-05: back to red everywhere, "a touch darker and
more realistic", "visible thin ribs that show the wall/panel of the box", "improve the box and the lettering,
it looks made in Paint – but keep this look, only better").

On the client's drawings (side views, front views, cut-outs) and photos, in this order:
  1. the old lettering is taken off the body (its pixels get the body colour of their row), where a text
     box is given;
  2. the red turns a touch deeper and calmer (tools/recolor.py in CIE Lab: hue, chroma and lightness move
     together, so frames, shading and edges stay);
  3. on drawings, the body gets light from above (a little brighter at the top, darker at the bottom) and
     thin vertical ribs, a dark groove with a light edge, as on a ribbed panel; they stop at the hatches,
     doors, chargers, frame and lettering, because they follow the body mask;
  4. the lettering is set again in the same place, size and width (Inter Bold, white, a faint shadow),
     drawn at 4x and reduced, so the edges are clean.
Needs numpy + Pillow (and Inter, /usr/share/fonts/opentype/inter). Used by tools/recolor_jobs.py (mode red).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from recolor import body_weight, recolor, region_mask, srgb_to_lin, lin_to_srgb

DEEP_RED = (172, 30, 34)       # a touch darker and calmer than the renders' (200, 20, 28)
FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'


def erase_text(rgb, w, box):
    """box = (x0, y0, x1, y1) in px: the non-body pixels inside it (the letters and their edges) get the
    median body colour of their row"""
    x0, y0, x1, y1 = box
    out = rgb.copy()
    # the letters with their anti-aliased edges: everything in the box that is not clean body, grown by 2 px
    m = (w[y0:y1, x0:x1] < .97).astype(np.uint8) * 255
    m = np.asarray(Image.fromarray(m).filter(ImageFilter.MaxFilter(5)), dtype=np.float64) / 255
    for y in range(y0, y1):
        row = rgb[y, x0:x1]; ww = w[y, x0:x1]
        # body colour of this row: from the box and a margin beside it
        ref = np.concatenate([rgb[y, max(0, x0 - 40):x0][w[y, max(0, x0 - 40):x0] > .97],
                              row[(ww > .97) & (m[y - y0] < .5)], rgb[y, x1:x1 + 40][w[y, x1:x1 + 40] > .97]])
        if not len(ref):
            continue
        col = np.median(ref, axis=0)
        k = m[y - y0][:, None]
        out[y, x0:x1] = row * (1 - k) + col * k
    return out


def light_and_ribs(rgb, w, bbox, pitch, scale, phase=.5):
    """light from above and thin vertical ribs, only where the body is (w)"""
    x0, y0, x1, y1 = bbox
    H, W = w.shape
    yy = np.arange(H)[:, None]; xx = np.arange(W)[None, :]
    t = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)
    f = 1.07 - .17 * t                                   # linear light: +7% at the top, -10% at the bottom
    sig = .55 * scale
    rib = np.zeros((1, W))
    n = int((x1 - x0) / pitch) if pitch else 0
    start = x0 + ((x1 - x0) - n * pitch) / 2 + phase * pitch if n else 0
    for i in range(n):
        c = start + i * pitch
        rib += -.30 * np.exp(-((xx - c) / sig) ** 2) + .20 * np.exp(-((xx - c - 1.7 * scale) / sig) ** 2)
    f = f * (1 + rib)
    lin = srgb_to_lin(rgb)
    lin = lin * (1 + w[..., None] * (f[..., None] - 1))
    return np.clip(lin_to_srgb(np.clip(lin, 0, 1)), 0, 1)


def letter(img, text, box, cap_top, cap_h, colour=(252, 252, 250), shadow=.28, ss=4):
    """set `text` so its caps start at (box x0, cap_top), its cap height is cap_h and its ink spans box x0..x1"""
    x0, _, x1, _ = box
    size = 20
    while True:
        f = ImageFont.truetype(FONT, size * ss)
        e = f.getbbox('E')
        if (e[3] - e[1]) / ss >= cap_h:
            break
        size += .25
    f = ImageFont.truetype(FONT, size * ss)
    e = f.getbbox('E')
    adv = [f.getlength(text[:i]) for i in range(len(text) + 1)]
    # tracking so that the ink spans the old width
    def ink(track):
        lay = Image.new('L', (int((adv[-1] + track * len(text)) + 40 * ss), int(size * ss * 1.6)), 0)
        d = ImageDraw.Draw(lay)
        for i, ch in enumerate(text):
            d.text((20 * ss + adv[i] + track * i, 0), ch, font=f, fill=255)
        bb = lay.getbbox()
        return lay, bb
    target = (x1 - x0) * ss
    lo, hi = -.2 * size * ss, .4 * size * ss
    for _ in range(30):
        mid = (lo + hi) / 2
        lay, bb = ink(mid)
        if bb[2] - bb[0] > target: hi = mid
        else: lo = mid
    lay, bb = ink((lo + hi) / 2)
    # place: ink left at x0, the E's top at cap_top
    W, H = img.size
    big = Image.new('L', (W * ss, H * ss), 0)
    ox = int(x0 * ss - bb[0]); oy = int(cap_top * ss - e[1])
    big.paste(lay, (ox, oy))
    mask = big.resize((W, H), Image.LANCZOS)
    out = img.convert('RGBA')
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(max(.8, cap_h / 40)))
        sh = Image.fromarray((np.asarray(sh, dtype=np.float64) * shadow).astype(np.uint8))
        layer = Image.new('RGBA', (W, H), (40, 6, 8, 0)); layer.putalpha(sh)
        out = Image.alpha_composite(out, layer.transform(layer.size, Image.AFFINE, (1, 0, -max(.6, cap_h / 60), 0, 1, -max(.8, cap_h / 45))))
    layer = Image.new('RGBA', (W, H), colour + (0,)); layer.putalpha(mask)
    return Image.alpha_composite(out, layer)


def paint(im, region=None, exclude=None, drawing=None):
    """im: PIL image (RGB or RGBA); region/exclude: polygons (0..1) for photos (colour only); drawing: one body
    or {'bodies': [...]}, each body a dict with 'pitch' (rib spacing as a share of the body width, 0 = no
    ribs), optional 'body' (x0, y0, x1, y1 in 0..1; default: the whole red area), optional 'text', 'text_box'
    (x0, y0, x1, y1 in 0..1) and 'cap' (cap top and cap height in 0..1 of the picture height)."""
    alpha = im.getchannel('A') if im.mode in ('RGBA', 'LA') else None
    rgb = np.asarray(im.convert('RGB'), dtype=np.float64) / 255
    W, H = im.size
    opaque = (np.asarray(alpha, dtype=np.float64) / 255 > .5) if alpha is not None else 1
    reg = region_mask(im.size, region, feather=max(1.5, W / 900), exclude=exclude) if region else None
    bodies = (drawing.get('bodies') or [drawing]) if drawing else []
    w0 = body_weight(rgb, reg) * opaque
    for b in bodies:
        if b.get('text'):
            tb = b['text_box']
            rgb = erase_text(rgb, w0, (int(tb[0] * W) - 3, int(tb[1] * H) - 3, int(tb[2] * W) + 3, int(tb[3] * H) + 3))
    rgb = recolor(rgb, reg, DEEP_RED)
    if bodies:
        w = body_weight(rgb, reg) * opaque
        scale = max(1.0, W / 900)
        for b in bodies:
            if 'body' in b:
                x0, y0, x1, y1 = b['body'][0] * W, b['body'][1] * H, b['body'][2] * W, b['body'][3] * H
            else:
                ys, xs = np.where(w > .8); x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
            inside = np.zeros_like(w); inside[int(y0):int(np.ceil(y1)) + 1, int(x0):int(np.ceil(x1)) + 1] = 1
            pitch = b.get('pitch', 0)
            rgb = light_and_ribs(rgb, w * inside, (x0, y0, x1, y1), pitch * (x1 - x0) if pitch else 0, scale)
    out = Image.fromarray((rgb * 255 + .5).astype(np.uint8))
    if alpha is not None:
        out.putalpha(alpha)
    for b in bodies:
        if b.get('text'):
            tb = b['text_box']; cap_top, cap_h = b['cap']
            out = letter(out, b['text'], (tb[0] * W, 0, tb[2] * W, 0), cap_top * H, cap_h * H)
    if alpha is not None:
        out.putalpha(alpha)
    elif out.mode != 'RGB':
        out = out.convert('RGB')
    return out


def face_ribs(im, face, n, region=None, exclude=None, ss=4):
    """ribs on a photo: `face` = (x0, y0, x1, y1) in 0..1, a box around one flat red side seen from the side
    (verticals stay vertical, the top and bottom edges may converge). Its top and bottom edges are found in the
    red mask and fitted as lines; the ribs are spaced as on the real panel, closer where the side is farther
    away (1-D perspective from the side's height at both ends), thinner there too, and follow the body mask."""
    alpha = im.getchannel('A') if im.mode in ('RGBA', 'LA') else None
    rgb = np.asarray(im.convert('RGB'), dtype=np.float64) / 255
    W, H = im.size
    reg = region_mask(im.size, region, feather=max(1.5, W / 900), exclude=exclude) if region else None
    w = body_weight(rgb, reg)
    if alpha is not None:
        w = w * (np.asarray(alpha, dtype=np.float64) / 255 > .5)
    fx0, fy0, fx1, fy1 = int(face[0] * W), int(face[1] * H), int(face[2] * W), int(face[3] * H)
    sub = w[fy0:fy1, fx0:fx1] > .6
    cols = np.where(sub.sum(0) > .25 * sub.shape[0])[0]
    if len(cols) < 10:
        return im
    xl, xr = fx0 + cols[0], fx0 + cols[-1]
    xs, tops, bots = [], [], []
    for c in cols[int(len(cols) * .06): int(len(cols) * .94)]:
        ys = np.where(sub[:, c])[0]
        xs.append(fx0 + c); tops.append(fy0 + ys[0]); bots.append(fy0 + ys[-1])
    xs = np.array(xs, float)
    kt = np.polyfit(xs, np.array(tops, float), 1); kb = np.polyfit(xs, np.array(bots, float), 1)
    top = lambda x: kt[0] * x + kt[1]; bot = lambda x: kb[0] * x + kb[1]
    hl, hr = bot(xl) - top(xl), bot(xr) - top(xr)
    dark = Image.new('L', (W * ss, H * ss), 0); light = Image.new('L', (W * ss, H * ss), 0)
    dd, dl = ImageDraw.Draw(dark), ImageDraw.Draw(light)
    for i in range(n):
        u = (i + .5) / n
        x = (xl * hl * (1 - u) + xr * hr * u) / (hl * (1 - u) + hr * u)       # 1-D perspective along the side
        hk = (bot(x) - top(x)) / max(hl, hr)
        lw = max(1, round(ss * max(.7, 1.1 * hk * W / 1600)))
        off = lw * 1.4
        dd.line([(x * ss, top(x) * ss), (x * ss, bot(x) * ss)], fill=255, width=lw)
        dl.line([(x * ss + off, top(x) * ss), (x * ss + off, bot(x) * ss)], fill=255, width=lw)
    dark = np.asarray(dark.resize((W, H), Image.LANCZOS), dtype=np.float64) / 255
    light = np.asarray(light.resize((W, H), Image.LANCZOS), dtype=np.float64) / 255
    f = 1 + w * (.18 * light - .26 * dark)
    lin = srgb_to_lin(rgb) * f[..., None]
    out = Image.fromarray((np.clip(lin_to_srgb(np.clip(lin, 0, 1)), 0, 1) * 255 + .5).astype(np.uint8))
    if alpha is not None:
        out.putalpha(alpha)
    return out
