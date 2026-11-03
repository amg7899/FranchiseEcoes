#!/usr/bin/env python3
"""Draws the two glowing line motifs of the site (standard-library Python, no dependencies).

  assets/img/v2/wire-multicharger.svg  the ECOES MultiCharger on its trailer as a see-through
                                       wireframe (cabinet projection, so the side with the three
                                       DC chargers keeps its true shape)
  assets/img/v2/wire-globe.svg         the globe of the ECOES JV logo, with London and Sofia

Proportions follow the client's renders (box about 3.2 x 1.6 x 1.7 m on a tandem-axle trailer).
The lines draw themselves once when the image loads (images are lazy, so: when it comes into
view); prefers-reduced-motion shows them finished. Edit the numbers below and rerun:
  python3 tools/wireframes.py
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'assets', 'img', 'v2')
LINE = '#7fd8ff'      # the colour of the charger's ring light
GLOW = '#3fb8ff'

STYLE = f"""
  <style>
    .w {{ fill: none; stroke: {LINE}; stroke-linecap: round; stroke-linejoin: round; }}
    .glow {{ fill: none; stroke: {GLOW}; stroke-linecap: round; filter: url(#blur); opacity: .55; }}
    .back {{ opacity: .32; }}
    .faint {{ opacity: .18; }}
    .t {{ fill: {LINE}; font: 400 30px 'Unbounded', 'Segoe UI', Arial, sans-serif; letter-spacing: .5px; }}
    .node {{ fill: #eaf8ff; }}
    .draw {{ stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 2.2s cubic-bezier(.4,.1,.2,1) forwards; }}
    .fade {{ opacity: 0; animation: fade 1.2s ease-out 1.6s forwards; }}
    .d1 {{ animation-delay: .1s; }} .d2 {{ animation-delay: .5s; }} .d3 {{ animation-delay: .9s; }} .d4 {{ animation-delay: 1.3s; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    @keyframes fade {{ to {{ opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{ .draw {{ animation: none; stroke-dashoffset: 0; }} .fade {{ animation: none; opacity: 1; }} }}
  </style>
  <defs><filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter></defs>
"""

def fmt(v): return f'{v:.1f}'.rstrip('0').rstrip('.')

# ---------------------------------------------------------------- MultiCharger on its trailer
S = 230.0                 # px per metre
K, A = 0.42, math.radians(30)   # cabinet projection: depth drawn at 30 degrees, shortened
OX, OY = 170.0, 760.0     # origin on the canvas (x = rear of the box, y = ground)

def P(x, y, z):
    X = x + z * K * math.cos(A); Y = y + z * K * math.sin(A)
    return (OX + X * S, OY - Y * S)

def poly(points, closed=False):
    pts = [P(*p) for p in points]
    d = 'M' + ' L'.join(f'{fmt(a)} {fmt(b)}' for a, b in pts)
    return d + (' Z' if closed else '')

def circle_xy(cx, cy, z, r, n=48):
    pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z) for i in range(n)]
    return poly(pts, closed=True)

def multicharger():
    L, D = 3.2, 1.7            # box length and depth
    y0, y1 = 0.80, 2.40        # box bottom and top
    front, back, side, detail, chassis = [], [], [], [], []
    # box: near side (true shape), far side (dim), the four depth edges
    front.append(poly([(0, y0, 0), (L, y0, 0), (L, y1, 0), (0, y1, 0)], True))
    back.append(poly([(0, y0, D), (L, y0, D), (L, y1, D), (0, y1, D)], True))
    for x, y in [(0, y0), (L, y0), (L, y1), (0, y1)]:
        (side if (x, y) in [(L, y0), (L, y1), (0, y1)] else back).append(poly([(x, y, 0), (x, y, D)]))
    # galvanised frame inset and corner castings on the near side
    f = 0.07
    detail.append(poly([(f, y0 + f, 0), (L - f, y0 + f, 0), (L - f, y1 - f, 0), (f, y1 - f, 0)], True))
    for cx, cy in [(0, y0), (L, y0), (L, y1), (0, y1)]:
        sx = 0.16 if cx == 0 else -0.16; sy = 0.16 if cy == y0 else -0.16
        detail.append(poly([(cx, cy + sy, 0), (cx + sx, cy + sy, 0), (cx + sx, cy, 0)]))
    # roof panel seams (seen from above at the projection angle)
    for x in [0.8, 1.6, 2.4]:
        back.append(poly([(x, y1, 0), (x, y1, D)]))
    # three hatches with their DC chargers, ring lights and cables
    for i, cx in enumerate([0.62, 1.6, 2.58]):
        hw, hy0, hy1 = 0.31, 1.10, 1.80
        detail.append(poly([(cx - hw, hy0, 0), (cx + hw, hy0, 0), (cx + hw, hy1, 0), (cx - hw, hy1, 0)], True))
        detail.append(poly([(cx - hw + .04, hy0 + .04, 0.06), (cx + hw - .04, hy0 + .04, 0.06), (cx + hw - .04, hy1 - .04, 0.06), (cx - hw + .04, hy1 - .04, 0.06)], True))
        detail.append(poly([(cx - .15, 1.22, 0.06), (cx + .15, 1.22, 0.06), (cx + .15, 1.68, 0.06), (cx - .15, 1.68, 0.06)], True))
        detail.append(circle_xy(cx, 1.50, 0.06, 0.055, 32))
        # the cable hangs in a loop from the charger to its holster beside it
        a = P(cx - .02, 1.22, 0.06); b = P(cx + .2, 1.16, 0.02)
        c1 = P(cx - .06, 0.92, 0.0); c2 = P(cx + .26, 0.92, 0.0)
        detail.append(f'M{fmt(a[0])} {fmt(a[1])} C{fmt(c1[0])} {fmt(c1[1])} {fmt(c2[0])} {fmt(c2[1])} {fmt(b[0])} {fmt(b[1])}')
    # trailer: rails, cross members, drawbar, hitch, jockey wheel
    for z in [0.18, D - 0.18]:
        (chassis if z < 1 else back).append(poly([(-0.15, 0.72, z), (L + 0.15, 0.72, z)]))
        (chassis if z < 1 else back).append(poly([(-0.15, 0.62, z), (L + 0.15, 0.62, z)]))
    for x in [-0.15, 1.0, 2.2, L + 0.15]:
        back.append(poly([(x, 0.62, 0.18), (x, 0.62, D - 0.18)]))
    hitch = (L + 1.45, 0.58, D / 2)
    chassis.append(poly([(L + 0.15, 0.66, 0.18), hitch]))
    back.append(poly([(L + 0.15, 0.66, D - 0.18), hitch]))
    chassis.append(poly([(hitch[0] - .08, .58, hitch[2]), (hitch[0] + .14, .58, hitch[2])]))
    jx = L + 0.95
    chassis.append(poly([(jx, 0.64, D / 2), (jx, 0.16, D / 2)]))
    chassis.append(circle_xy(jx, 0.10, D / 2, 0.09, 28))
    # tandem axle: near wheels in full, far wheels dim; mudguard arc
    for wx in [1.15, 1.95]:
        for z, group in [(-0.03, chassis), (D + 0.03, back)]:
            group.append(circle_xy(wx, 0.36, z, 0.36))
            group.append(circle_xy(wx, 0.36, z, 0.22, 40))
            group.append(circle_xy(wx, 0.36, z, 0.06, 20))
            for k in range(5):
                t = 2 * math.pi * k / 5
                group.append(poly([(wx + .08 * math.cos(t), .36 + .08 * math.sin(t), z), (wx + .2 * math.cos(t), .36 + .2 * math.sin(t), z)]))
    arc = [(0.70 + 1.70 * i / 30, 0.78 + 0.05 * math.sin(math.pi * i / 30), -0.03) for i in range(31)]
    chassis.append(poly(arc))
    # floor: a faint grid under the trailer
    grid = []
    for z in [x * 0.5 for x in range(-1, 6)]:
        grid.append(poly([(-0.9, 0, z), (L + 2.2, 0, z)]))
    for x in [-0.9 + 0.5 * i for i in range(13)]:
        grid.append(poly([(x, 0, -0.5), (x, 0, 2.5)]))
    tx, ty = P(1.6, 2.06, 0)
    W, H = 1600, 900
    def group(paths, cls, w, delay):
        body = ''.join(f'<path pathLength="1" d="{d}"/>' for d in paths)
        return (f'<g class="glow {cls}" stroke-width="{w * 3}">{body}</g>'
                f'<g class="w draw {delay} {cls}" stroke-width="{w}">{body}</g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{STYLE}'
           f'<g class="w faint" stroke-width="1">{"".join(f"<path d=\"{d}\"/>" for d in grid)}</g>'
           + group(back, 'back', 1.4, 'd1') + group(chassis, '', 1.6, 'd1') + group(side, '', 1.6, 'd2')
           + group(front, '', 1.9, 'd2') + group(detail, '', 1.4, 'd3')
           + f'<text class="t fade" x="{fmt(tx)}" y="{fmt(ty)}" text-anchor="middle">ECOES MultiCharger</text></svg>')
    return svg

# ---------------------------------------------------------------- the globe of the logo
def globe():
    W = H = 900; cx = cy = 450; R = 300
    lon0, tilt = math.radians(14), math.radians(22)
    def proj(lat, lon):
        lat, lon = math.radians(lat), math.radians(lon) - lon0
        x = R * math.cos(lat) * math.sin(lon)
        y = R * (math.cos(tilt) * math.sin(lat) - math.sin(tilt) * math.cos(lat) * math.cos(lon))
        z = math.sin(tilt) * math.sin(lat) + math.cos(tilt) * math.cos(lat) * math.cos(lon)
        return cx + x, cy - y, z
    front, back = [], []
    def curve(pts):
        segs, cur, vis = [], [], None
        for x, y, z in pts:
            v = z >= 0
            if vis is None or v == vis: cur.append((x, y))
            else:
                if len(cur) > 1: segs.append((vis, cur))
                cur = [cur[-1], (x, y)]
            vis = v
        if len(cur) > 1: segs.append((vis, cur))
        for v, c in segs:
            (front if v else back).append('M' + ' L'.join(f'{fmt(a)} {fmt(b)}' for a, b in c))
    for lat in range(-60, 61, 20):
        curve([proj(lat, lon) for lon in range(-180, 181, 5)])
    for lon in range(-180, 180, 20):
        curve([proj(lat, lon) for lat in range(-90, 91, 5)])
    ring = 'M' + ' L'.join(f'{fmt(cx + 1.32 * R * math.cos(t) * math.cos(-0.32) - 0.34 * R * math.sin(t) * math.sin(-0.32))} '
                           f'{fmt(cy + 1.32 * R * math.cos(t) * math.sin(-0.32) + 0.34 * R * math.sin(t) * math.cos(-0.32))}'
                           for t in [2 * math.pi * i / 120 for i in range(121)])
    nodes = ''
    arcs = []
    places = [(51.5, -0.1), (42.7, 23.3)]     # London, Sofia: the two offices
    for lat, lon in places:
        x, y, z = proj(lat, lon)
        nodes += f'<circle class="node fade" cx="{fmt(x)}" cy="{fmt(y)}" r="5"/><circle class="w fade" cx="{fmt(x)}" cy="{fmt(y)}" r="13" stroke-width="1.2"/>'
    # the link between the two offices, lifted above the surface
    pts = []
    for i in range(41):
        t = i / 40
        lat = places[0][0] + (places[1][0] - places[0][0]) * t
        lon = places[0][1] + (places[1][1] - places[0][1]) * t
        x, y, z = proj(lat, lon)
        lift = 1 + 0.12 * math.sin(math.pi * t)
        pts.append((cx + (x - cx) * lift, cy + (y - cy) * lift))
    arcs.append('M' + ' L'.join(f'{fmt(a)} {fmt(b)}' for a, b in pts))
    def group(paths, cls, w, delay):
        body = ''.join(f'<path pathLength="1" d="{d}"/>' for d in paths)
        return (f'<g class="glow {cls}" stroke-width="{w * 3}">{body}</g>'
                f'<g class="w draw {delay} {cls}" stroke-width="{w}">{body}</g>')
    outline = f'M{cx - R} {cy} A{R} {R} 0 1 1 {cx + R} {cy} A{R} {R} 0 1 1 {cx - R} {cy}'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{STYLE}'
            + group(back, 'back', 1.1, 'd1') + group([outline], '', 1.8, 'd1') + group(front, '', 1.3, 'd2')
            + group([ring], 'back', 1.2, 'd3') + group(arcs, '', 1.8, 'd4') + nodes + '</svg>')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, svg in [('wire-multicharger.svg', multicharger()), ('wire-globe.svg', globe())]:
        with open(os.path.join(OUT, name), 'w', encoding='utf-8') as fh:
            fh.write(svg + '\n')
        print(name, len(svg) // 1024, 'KB')
