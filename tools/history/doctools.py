"""Shared tools for the translated versions of the About us documents (client, 2026-11-24): take the text off a scan
without harming what is around it, and set the translation in matching type at the same places.

  doc = Doc('scan.jpg', sc=2)          # work at sc x the scan's size, for clean edges
  doc.erase((x0, y0, x1, y1))          # the text inside the box (scan pixels): mask, inpaint, the paper's own grain
  doc.text('…', 'carlito', 28, (30, 30, 30), (x, baseline), 'l', stretch=0.88)
  doc.save('out.jpg')                  # back at the scan's size

Needs numpy, opencv-python (cv2) and Pillow. Fonts: the system's Liberation, Carlito, DejaVu and Free fonts
(all with Cyrillic and Latin).
"""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = '/usr/share/fonts/truetype/'
FONTS = {
    'carlito': F + 'crosextra/Carlito-Regular.ttf', 'carlito-b': F + 'crosextra/Carlito-Bold.ttf',
    'carlito-i': F + 'crosextra/Carlito-Italic.ttf',
    'sans': F + 'liberation/LiberationSans-Regular.ttf', 'sans-b': F + 'liberation/LiberationSans-Bold.ttf',
    'sans-i': F + 'liberation/LiberationSans-Italic.ttf',
    'serif': F + 'liberation/LiberationSerif-Regular.ttf', 'serif-b': F + 'liberation/LiberationSerif-Bold.ttf',
    'serif-i': F + 'liberation/LiberationSerif-Italic.ttf', 'serif-bi': F + 'liberation/LiberationSerif-BoldItalic.ttf',
    'dejavu': F + 'dejavu/DejaVuSans.ttf', 'dejavu-b': F + 'dejavu/DejaVuSans-Bold.ttf',
    'dejavu-serif': F + 'dejavu/DejaVuSerif.ttf', 'dejavu-serif-b': F + 'dejavu/DejaVuSerif-Bold.ttf',
    'free-serif-b': F + 'freefont/FreeSerifBold.ttf',
}


class Doc:
    def __init__(self, path, sc=2, seed=7):
        self.src = Image.open(path).convert('RGB')
        self.W, self.H = self.src.size
        self.sc = sc
        self.a = np.array(self.src.resize((self.W * sc, self.H * sc), Image.LANCZOS)).astype(np.float32)
        self.orig = self.a.copy()
        self.rng = np.random.default_rng(seed)
        self.grain = None

    # --------------------------------------------------------------- background
    def set_grain(self, box, sigma=3.0):
        """The paper's own texture, from a clean patch (scan pixels)."""
        x0, y0, x1, y1 = [v * self.sc for v in box]
        p = self.a[y0:y1, x0:x1]
        self.grain = p - cv2.GaussianBlur(p, (0, 0), sigma)

    def _grain(self, h, w):
        if self.grain is None:
            return np.zeros((h, w, 3), np.float32)
        g = self.grain; gh, gw = g.shape[:2]; hh, hw = max(1, gh // 2), max(1, gw // 2)
        out = np.zeros((h, w, 3), np.float32)
        for y in range(0, h, hh):
            for x in range(0, w, hw):
                oy, ox = self.rng.integers(0, gh - hh + 1), self.rng.integers(0, gw - hw + 1)
                ph, pw = min(hh, h - y), min(hw, w - x)
                out[y:y + ph, x:x + pw] = g[oy:oy + ph, ox:ox + pw]
        return out

    def erase(self, box, thr=16, grow=2, ctx=14, radius=3, keep=None, cool=False, tb=5.0, median=31, grain=0.95,
              protect=None, boxes=None, period=None, lp=2.5):
        """Take the text off inside box (scan pixels): what differs from the local paper is masked, inpainted and given
        the paper's grain. keep: boxes (scan pixels) left as they are. protect: a bool array at work scale (the whole
        page) of pixels to keep, e.g. a signature crossing the text: they are painted over with the rest, so the
        paper is rebuilt clean under them, and then put back on top."""
        s = self.sc
        if boxes:                       # several boxes at once: one fill, so neighbouring lines never feed each other
            box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        x0, y0, x1, y1 = [v * s for v in box]
        c = ctx * s
        X0, Y0, X1, Y1 = max(0, x0 - c), max(0, y0 - c), min(self.W * s, x1 + c), min(self.H * s, y1 + c)
        reg = self.a[Y0:Y1, X0:X1].copy()
        u8 = np.clip(reg, 0, 255).astype(np.uint8)
        k = median * s // 2 * 2 + 1
        bg = cv2.medianBlur(u8, min(k, 255 if k > 255 else k))
        lab = cv2.cvtColor(u8, cv2.COLOR_RGB2LAB).astype(np.float32)
        labb = cv2.cvtColor(bg, cv2.COLOR_RGB2LAB).astype(np.float32)
        d = np.sqrt(((lab - labb) ** 2).sum(axis=2))
        if cool:
            db = labb[..., 2] - lab[..., 2]
            sel = (db > tb) | ((d > thr) & (db > tb * 0.5))
        else:
            sel = d > thr
        m = np.zeros(d.shape, np.uint8)
        for bx in (boxes or [box]):
            bx0, by0, bx1, by1 = [v * s for v in bx]
            m[by0 - Y0:by1 - Y0, bx0 - X0:bx1 - X0] = sel[by0 - Y0:by1 - Y0, bx0 - X0:bx1 - X0]
        g = max(1, int(round(grow * s)))
        m = cv2.dilate(m, np.ones((2 * g + 1, 2 * g + 1), np.uint8))
        clip = np.zeros_like(m)
        for bx in (boxes or [box]):
            bx0, by0, bx1, by1 = [v * s for v in bx]
            clip[by0 - Y0:by1 - Y0, bx0 - X0:bx1 - X0] = 1
        m = m * clip
        for kb in (keep or []):
            kx0, ky0, kx1, ky1 = [v * s for v in kb]
            m[max(0, ky0 - Y0):max(0, ky1 - Y0), max(0, kx0 - X0):max(0, kx1 - X0)] = 0
        pr = None
        if protect is not None:
            pr = protect[Y0:Y1, X0:X1].astype(np.uint8)
            # painted over in the whole region (the fill must not take its colour from them) and put back below;
            # their surroundings only inside the boxes, so kept type next to them outside stays untouched
            m = np.maximum(m, np.maximum(pr, cv2.dilate(pr, np.ones((4 * s + 1, 4 * s + 1), np.uint8)) * clip))
        filled = cv2.inpaint(u8, m * 255, radius * s, cv2.INPAINT_TELEA).astype(np.float32)
        if period:
            # a printed lattice: the fill's fine texture is copied from the nearest clean place one or more lattice
            # periods away (period = the lattice's vectors (dy, dx) in scan px), over the inpainted low frequencies
            filled = cv2.GaussianBlur(filled, (0, 0), lp * s) + self._lattice(reg, m, period, lp)
            grain = 0
        soft = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0 * s)[..., None]
        out = reg * (1 - soft) + (filled + self._grain(*reg.shape[:2]) * grain) * soft
        if pr is not None:
            ps = cv2.GaussianBlur(pr.astype(np.float32), (0, 0), 0.4 * s)[..., None]
            out = out * (1 - ps) + np.minimum(out, reg) * ps
        self.a[Y0:Y1, X0:X1] = out

    def _lattice(self, reg, m, period, lp, reach=5):
        s = self.sc
        hp = reg - cv2.GaussianBlur(reg, (0, 0), lp * s)
        bad = cv2.dilate(m, np.ones((4 * s + 1, 4 * s + 1), np.uint8)) > 0
        # only the lattice may be copied: lines, frames, stamps and other strong detail are no source
        mag = np.abs(hp).max(axis=2)
        amp = 1.4826 * np.median(mag[~bad]) + 1e-3
        strong = (mag > 3.5 * amp).astype(np.uint8)
        bad |= cv2.dilate(strong, np.ones((3 * s + 1, 3 * s + 1), np.uint8)) > 0
        H, W = m.shape
        (ay, ax), (by, bx) = period
        shifts = sorted({(round((i * ay + j * by) * s), round((i * ax + j * bx) * s))
                         for i in range(-reach, reach + 1) for j in range(-reach, reach + 1)} - {(0, 0)},
                        key=lambda v: v[0] ** 2 + v[1] ** 2)
        out = np.zeros_like(reg)
        need = m > 0
        have = np.zeros_like(need)
        for dy, dx in shifts:
            if have[need].all():
                break
            ys0, ys1 = max(0, -dy), min(H, H - dy)
            xs0, xs1 = max(0, -dx), min(W, W - dx)
            if ys1 <= ys0 or xs1 <= xs0:
                continue
            src_ok = np.zeros_like(need)
            src_ok[ys0:ys1, xs0:xs1] = ~bad[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
            take = need & ~have & src_ok
            if take.any():
                shifted = np.zeros_like(reg)
                shifted[ys0:ys1, xs0:xs1] = hp[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
                out[take] = shifted[take]
                have |= take
        return out

    def fill(self, box, color, grain=0.0):
        """Fill a box (scan pixels) with a flat colour (e.g. inside a coloured bar)."""
        x0, y0, x1, y1 = [v * self.sc for v in box]
        self.a[y0:y1, x0:x1] = np.array(color, np.float32)[None, None] + self._grain(y1 - y0, x1 - x0) * grain

    def sample(self, box, dark=True, pct=6):
        """The ink colour in a box (scan pixels): the mean of its darkest (or lightest) pct %."""
        x0, y0, x1, y1 = box
        reg = self.orig[y0 * self.sc:y1 * self.sc, x0 * self.sc:x1 * self.sc].reshape(-1, 3)
        L = reg.mean(axis=1)
        sel = reg[L <= np.percentile(L, pct)] if dark else reg[L >= np.percentile(L, 100 - pct)]
        return tuple(int(v) for v in sel.mean(axis=0))

    def tight(self, box, thr=40):
        """The ink's own box inside box (scan pixels)."""
        x0, y0, x1, y1 = box
        reg = self.orig[y0 * self.sc:y1 * self.sc, x0 * self.sc:x1 * self.sc]
        bgc = np.median(reg.reshape(-1, 3), axis=0)
        d = np.sqrt(((reg - bgc) ** 2).sum(axis=2)) > thr
        ys, xs = np.nonzero(d)
        if not len(xs):
            return box
        s = self.sc
        return (x0 + xs.min() // s, y0 + ys.min() // s, x0 + (xs.max() + s) // s, y0 + (ys.max() + s) // s)

    # --------------------------------------------------------------- type
    def font(self, key, px):
        return ImageFont.truetype(FONTS.get(key, key), max(1, round(px * self.sc)))

    def measure(self, text, key, px, stretch=1.0, track=0.0):
        f = self.font(key, px)
        return (sum(f.getlength(ch) for ch in text) + track * self.sc * (len(text) - 1)) * stretch / self.sc

    def text(self, text, key, px, color, xy, anchor='l', stretch=1.0, track=0.0, fit=None, shrink=None, stroke=0,
             alpha=1.0, blur=0.35, rotate=0, underline=False, squeeze=None):
        """Set one line. xy = (x, baseline) in scan pixels; anchor l/m/r on the ink. fit: track to that ink width;
        shrink: the most width the line may take (then the size goes down to fit); squeeze: the same, but the letters
        get narrower instead (at most to 88 %, then the size goes down)."""
        s = self.sc
        if squeeze:
            w = self.measure(text, key, px, stretch, track)
            if w > squeeze:
                k = squeeze / w
                stretch *= max(k, 0.88)
                if k < 0.88:
                    px *= k / 0.88
        if shrink:
            w = self.measure(text, key, px, stretch, track)
            if w > shrink:
                px = px * shrink / w
        f = self.font(key, px)
        widths = [f.getlength(ch) for ch in text]
        if fit and len(text) > 1:
            track = ((fit * s / stretch) - sum(widths)) / (len(text) - 1) / s
        total = sum(widths) + track * s * (len(text) - 1)
        asc, desc = f.getmetrics()
        pad = 6 * s
        lay = Image.new('L', (int(total) + 2 * pad, asc + desc + 2 * pad), 0)
        d = ImageDraw.Draw(lay)
        x = pad
        for ch, wch in zip(text, widths):
            d.text((x, pad), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
            x += wch + track * s
        if underline:
            uy = pad + asc + max(1, int(px * s * 0.09))
            d.line((pad, uy, x - track * s, uy), fill=255, width=max(1, int(px * s * 0.06)))
        if stretch != 1.0:
            lay = lay.resize((max(1, int(lay.width * stretch)), lay.height), Image.LANCZOS)
        if blur:
            lay = lay.filter(ImageFilter.GaussianBlur(blur * s))
        if rotate:
            lay = lay.rotate(rotate, expand=True, resample=Image.BICUBIC)
        bb = lay.getbbox()
        if not bb:
            return
        ax, ay = xy[0] * s, xy[1] * s
        if rotate:
            left, top = ax - bb[0], ay - bb[1]
        else:
            iw = bb[2] - bb[0]
            left = ax - bb[0] if anchor == 'l' else (ax - bb[0] - iw / 2 if anchor == 'm' else ax - bb[2])
            top = ay - (pad + asc)
        left, top = int(round(left)), int(round(top))
        A = np.array(lay).astype(np.float32) / 255 * alpha
        h, w = A.shape
        y0, x0 = max(0, top), max(0, left)
        y1, x1 = min(self.a.shape[0], top + h), min(self.a.shape[1], left + w)
        a = A[y0 - top:y1 - top, x0 - left:x1 - left][..., None]
        self.a[y0:y1, x0:x1] = self.a[y0:y1, x0:x1] * (1 - a) + np.array(color, np.float32) * a

    def wrap(self, text, key, px, width, stretch=1.0):
        """Break text into lines that fit width (scan pixels)."""
        words, lines, cur = text.split(' '), [], ''
        for wd in words:
            t = (cur + ' ' + wd).strip()
            if cur and self.measure(t, key, px, stretch) > width:
                lines.append(cur); cur = wd
            else:
                cur = t
        if cur:
            lines.append(cur)
        return lines

    def paragraph(self, text, key, px, color, x, y, width, lead, stretch=1.0, justify=False, **kw):
        """Set a wrapped paragraph from baseline y, line distance lead; justify: all lines but the last fill width."""
        lines = self.wrap(text, key, px, width, stretch)
        for i, ln in enumerate(lines):
            if justify and i < len(lines) - 1 and ' ' in ln:
                words = ln.split(' ')
                gap = (width - sum(self.measure(wd, key, px, stretch) for wd in words)) / (len(words) - 1)
                cx = x
                for wd in words:
                    self.text(wd, key, px, color, (cx, y + i * lead), 'l', stretch=stretch, **kw)
                    cx += self.measure(wd, key, px, stretch) + gap
            else:
                self.text(ln, key, px, color, (x, y + i * lead), 'l', stretch=stretch, **kw)
        return len(lines)

    def clone_period(self, x0, x1, y0, y1, period, src_end, feather=1.5):
        """Repeat a periodic drawing over x0..x1 (scan pixels) from the clean stretch that ends at src_end."""
        s = self.sc
        X0, X1, Y0, Y1, P, E = x0 * s, x1 * s, y0 * s, y1 * s, round(period * s), src_end * s
        patch = np.empty((Y1 - Y0, X1 - X0, 3), np.float32)
        for x in range(X0, X1):
            k = -(-(x - E + 1) // P)
            patch[:, x - X0] = self.orig[Y0:Y1, x - k * P]
        w = np.ones((Y1 - Y0, 1, 1), np.float32)
        fz = int(feather * s)
        for i in range(fz):
            w[i] = w[-1 - i] = (i + 1) / (fz + 1)
        self.a[Y0:Y1, X0:X1] = self.a[Y0:Y1, X0:X1] * (1 - w) + patch * w

    def save(self, path, quality=90):
        img = Image.fromarray(np.clip(self.a, 0, 255).astype(np.uint8)).resize((self.W, self.H), Image.LANCZOS)
        img.save(path, quality=quality)
        return img
