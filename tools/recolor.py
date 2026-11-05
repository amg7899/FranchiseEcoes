#!/usr/bin/env python3
"""Recolour the product's red body to the client's teal-green (v3 trial, client 2026-11-05: "the ECOES boxes
in all visualisations in green, like this one"; their example body is about #014549).

Works in CIE Lab: pixels in the red hue window (and inside the product's region on photos, so car lights,
the sunset, the LPG pump and other red things stay) get their hue turned to teal, their chroma scaled to the
target's, and their lightness lowered in proportion to how red they are, so the white lettering, the grey
frame, the shading and the anti-aliased letter edges stay natural (no pink fringes). Needs numpy + Pillow.

  python3 -I tools/recolor.py <in> <out> [region polygons as "x,y x,y …;x,y …" in 0..1 of the picture]
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

TARGET_RGB = (6, 76, 76)          # the body colour aimed at (the client's example, a touch lighter for the light pages)
BODY_RGB = (200, 20, 28)          # the typical red of the renders


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)


M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
MI = np.linalg.inv(M)
WHITE = np.array([0.95047, 1.0, 1.08883])


def rgb_to_lab(rgb):
    xyz = srgb_to_lin(rgb) @ M.T / WHITE
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)


def lab_to_rgb(lab):
    fy = (lab[..., 0] + 16) / 116; fx = fy + lab[..., 1] / 500; fz = fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], axis=-1)
    xyz = np.where(f > 6 / 29, f ** 3, 3 * (6 / 29) ** 2 * (f - 4 / 29)) * WHITE
    return np.clip(lin_to_srgb(xyz @ MI.T), 0, 1)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def lch(rgb):
    lab = rgb_to_lab(np.asarray(rgb, dtype=np.float64).reshape(1, 3) / 255)[0]
    return lab[0], float(np.hypot(lab[1], lab[2])), float(np.degrees(np.arctan2(lab[2], lab[1])) % 360)


def body_weight(rgb, region=None):
    """how much each pixel is the red body (0..1): the red hue window, enough chroma, inside the region"""
    lab = rgb_to_lab(rgb)
    C = np.hypot(lab[..., 1], lab[..., 2]); H = np.degrees(np.arctan2(lab[..., 2], lab[..., 1])) % 360
    w = smooth(2, 12, H) * (1 - smooth(48, 60, H)) * smooth(10, 26, C)
    return w * region if region is not None else w


def recolor(rgb, region=None, target=None):
    """rgb: HxWx3 floats 0..1; region: HxW weights 0..1 (None = the whole picture is product);
    target: the body colour aimed at (default TARGET_RGB)"""
    Lb, Cb, Hb = lch(BODY_RGB)
    Lt, Ct, Ht = lch(target or TARGET_RGB)
    lab = rgb_to_lab(rgb)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.hypot(a, b); H = np.degrees(np.arctan2(b, a)) % 360
    # the red window: crimson to red (about 8–52°), oranges, ambers and yellows stay
    hue_w = smooth(2, 12, H) * (1 - smooth(48, 60, H))
    w = hue_w * smooth(10, 26, C)
    if region is not None:
        w = w * region
    k = np.clip(C / Cb, 0, 1.25)                       # how much of the pixel is the red body
    H2 = np.radians(H + (Ht - Hb)); C2 = C * (Ct / Cb)
    L2 = L + (Lt - Lb) * np.clip(k, 0, 1)
    new = lab_to_rgb(np.stack([L2, C2 * np.cos(H2), C2 * np.sin(H2)], axis=-1))
    return rgb * (1 - w[..., None]) + new * w[..., None]


def region_mask(size, polys, feather=2.0, exclude=None):
    """polygons in 0..1 of the picture; `exclude` polygons are cut out again (e.g. a vending machine's window)"""
    W, H = size
    m = Image.new('L', size, 0); d = ImageDraw.Draw(m)
    for poly in polys:
        d.polygon([(x * W, y * H) for x, y in poly], fill=255)
    for poly in exclude or []:
        d.polygon([(x * W, y * H) for x, y in poly], fill=0)
    if feather:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(m, dtype=np.float64) / 255


def parse(spec):
    return [[tuple(float(v) for v in pt.split(',')) for pt in poly.split()] for poly in spec.split(';') if poly.strip()]


def process(src, dst=None, polys=None, exclude=None, target=None):
    im = src if isinstance(src, Image.Image) else Image.open(src)
    alpha = im.getchannel('A') if im.mode in ('RGBA', 'LA') else None
    rgb = np.asarray(im.convert('RGB'), dtype=np.float64) / 255
    reg = region_mask(im.size, polys, feather=max(1.5, im.size[0] / 900), exclude=exclude) if polys else None
    out = Image.fromarray((recolor(rgb, reg, target) * 255 + .5).astype(np.uint8))
    if alpha is not None:
        out.putalpha(alpha)
    return out


if __name__ == '__main__':
    src, dst = sys.argv[1:3]
    polys = parse(sys.argv[3]) if len(sys.argv) > 3 else None
    out = process(src, dst, polys)
    out.save(dst)
    print('wrote', dst, out.size)
