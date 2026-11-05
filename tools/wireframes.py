#!/usr/bin/env python3
"""Draws the two glowing line motifs of the site (standard-library Python, no dependencies).

  assets/img/v2/wire-multicharger.svg  the ECOES MultiCharger on its trailer as a see-through
                                       wireframe (cabinet projection, so the side with the three
                                       DC chargers keeps its true shape)
  assets/img/v2/wire-globe.svg         the globe of the ECOES JV logo, with London and Sofia
  assets/img/v2/wire-globe-network.svg the same globe as a built network: cities in the markets of the
                                       visualisation, linked; the network grows from Sofia when it loads
                                       (ECOES Franchise page head, client 2026-11-04)

Proportions follow the client's renders (box about 3.2 x 1.6 x 1.7 m on a tandem-axle trailer).
The lines draw themselves once when the image loads (images are lazy, so: when it comes into
view); prefers-reduced-motion shows them finished. Edit the numbers below and rerun:
  python3 tools/wireframes.py
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'assets', 'img', 'v2')
# colours: v3 "mint" (the lines glow on the deep green screens of the light theme, 2026-11-05) or v2 "blue"
# (the charger's ring light on the night ground); WIRE_THEME=blue python3 tools/wireframes.py for the v2 set
PALETTES = {'mint': ('#a6f4d2', '#2fd896', '#f0fff8'), 'blue': ('#7fd8ff', '#3fb8ff', '#eaf8ff')}
LINE, GLOW, NODE = PALETTES[os.environ.get('WIRE_THEME', 'mint')]

STYLE = f"""
  <style>
    .w {{ fill: none; stroke: {LINE}; stroke-linecap: round; stroke-linejoin: round; }}
    .glow {{ fill: none; stroke: {GLOW}; stroke-linecap: round; filter: url(#blur); opacity: .55; }}
    .back {{ opacity: .32; }}
    .faint {{ opacity: .18; }}
    .t {{ fill: {LINE}; font: 400 30px 'Unbounded', 'Segoe UI', Arial, sans-serif; letter-spacing: .5px; }}
    .node {{ fill: {NODE}; }}
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
OX, OY = 250.0, 760.0     # origin on the canvas (x = rear of the box, y = ground); centres the trailer

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

# ---------------------------------------------------------------- the globe as a network (ECOES Franchise)
# Cities in the markets the visualisation names (Europe, the Middle East, Asia, Africa, Latin America),
# in order of priority: a city too close to one already placed (on the drawing) is left out.
CITIES = [
    (42.7, 23.3), (51.5, -0.1),                                    # Sofia, London: the two offices
    # Europe
    (48.9, 2.35), (40.4, -3.7), (38.7, -9.1), (52.5, 13.4), (52.2, 21.0), (41.9, 12.5), (48.2, 16.4),
    (44.4, 26.1), (37.98, 23.7), (41.0, 28.98), (50.45, 30.5), (59.3, 18.1), (59.9, 10.75), (60.2, 24.9),
    (53.35, -6.26), (45.5, 9.2), (55.75, 37.6), (53.55, 10.0), (52.37, 4.9), (45.76, 4.84), (37.39, -5.98),
    (41.15, -8.6), (40.85, 14.27), (47.5, 19.04), (45.8, 15.98), (53.9, 27.56), (56.95, 24.1), (55.68, 12.57),
    (55.95, -3.19), (40.64, 22.94), (43.2, 27.9), (39.93, 32.86), (38.42, 27.14), (46.48, 30.72), (64.1, -21.9),
    # the Middle East and Asia
    (41.7, 44.8), (35.7, 51.4), (25.2, 55.3), (24.7, 46.7), (24.9, 67.0), (28.6, 77.2), (19.1, 72.9),
    (41.3, 69.2), (43.2, 76.9), (40.4, 49.87), (31.95, 35.93), (33.89, 35.5), (29.37, 47.98), (23.59, 58.38),
    (21.49, 39.19), (32.65, 51.67), (34.53, 69.17), (31.55, 74.34), (51.17, 71.43), (12.97, 77.59), (33.3, 44.4),
    # Africa
    (30.0, 31.2), (33.6, -7.6), (36.75, 3.06), (36.8, 10.2), (6.5, 3.4), (5.6, -0.2), (14.7, -17.4),
    (-1.3, 36.8), (9.0, 38.7), (15.6, 32.5), (-4.3, 15.3), (-8.8, 13.2), (-26.2, 28.0), (-33.9, 18.4),
    (-6.8, 39.3), (12.6, -8.0), (13.5, 2.1), (12.1, 15.0), (-15.4, 28.3), (-18.9, 47.5), (9.08, 7.4),
    (4.05, 9.7), (5.36, -4.0), (32.89, 13.19), (32.12, 20.07), (0.35, 32.58), (2.05, 45.32), (-11.66, 27.48),
    (-17.83, 31.05), (-25.97, 32.57), (-22.56, 17.08), (-29.86, 31.02), (0.42, 9.47), (18.08, -15.98),
    (11.59, 43.15), (31.63, -8.0),
    # Latin America
    (-23.5, -46.6), (-22.9, -43.2), (-8.0, -34.9), (-12.97, -38.5), (-3.73, -38.52), (-15.79, -47.88),
    (-1.46, -48.5),
]
NET_MIN = 30          # px on the 900 canvas between two cities
NET_K = 3             # each city also links to its nearest neighbours
NET_MAX = 30          # degrees: the longest link between neighbours
# long links between hubs, lifted higher above the surface (Sofia, London, Dubai, Johannesburg, Lisbon, Sao Paulo, Delhi, Lagos)
HUBS = [((51.5, -0.1), (25.2, 55.3)), ((42.7, 23.3), (-26.2, 28.0)), ((38.7, -9.1), (-23.5, -46.6)),
        ((25.2, 55.3), (28.6, 77.2)), ((42.7, 23.3), (6.5, 3.4))]

def network_globe():
    W = H = 900; cx = cy = 450; R = 300
    lon0, tilt = math.radians(14), math.radians(22)
    def rot(v):
        # world unit vector -> view (x right, y up, z towards the viewer)
        x, y, z = v
        lon = math.atan2(y, x) - lon0; lat = math.asin(max(-1, min(1, z)))
        X = math.cos(lat) * math.sin(lon)
        Y = math.cos(tilt) * math.sin(lat) - math.sin(tilt) * math.cos(lat) * math.cos(lon)
        Z = math.sin(tilt) * math.sin(lat) + math.cos(tilt) * math.cos(lat) * math.cos(lon)
        return X, Y, Z
    def unit(lat, lon):
        lat, lon = math.radians(lat), math.radians(lon)
        return (math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat))
    def scr(v, lift=1.0):
        X, Y, Z = rot(v)
        return cx + R * lift * X, cy - R * lift * Y, Z
    # the globe itself, as on the logo, a little quieter so the network leads
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
        curve([scr(unit(lat, lon)) for lon in range(-180, 181, 5)])
    for lon in range(-180, 180, 20):
        curve([scr(unit(lat, lon)) for lat in range(-90, 91, 5)])
    ring = 'M' + ' L'.join(f'{fmt(cx + 1.32 * R * math.cos(t) * math.cos(-0.32) - 0.34 * R * math.sin(t) * math.sin(-0.32))} '
                           f'{fmt(cy + 1.32 * R * math.cos(t) * math.sin(-0.32) + 0.34 * R * math.sin(t) * math.cos(-0.32))}'
                           for t in [2 * math.pi * i / 120 for i in range(121)])
    # the cities: on the visible side, not crowding each other
    nodes = []
    for lat, lon in CITIES:
        v = unit(lat, lon); x, y, z = scr(v)
        if z < 0.2: continue
        if all(math.hypot(x - a, y - b) >= NET_MIN for _, a, b in nodes):
            nodes.append((v, x, y))
    n = len(nodes)
    ang = lambda i, j: math.acos(max(-1, min(1, sum(a * b for a, b in zip(nodes[i][0], nodes[j][0])))))
    # links: a spanning tree (the network is one) plus the nearest neighbours, never crossing on the drawing
    edges = []
    def crosses(i, j):
        p1, p2 = nodes[i][1:], nodes[j][1:]
        for a, b in edges:
            if len({i, j, a, b}) < 4: continue
            q1, q2 = nodes[a][1:], nodes[b][1:]
            d = lambda o, p, q: (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
            if d(p1, p2, q1) * d(p1, p2, q2) < 0 and d(q1, q2, p1) * d(q1, q2, p2) < 0: return True
        return False
    inside, rest = {0}, set(range(1, n))
    while rest:
        i, j = min(((i, j) for i in inside for j in rest), key=lambda e: ang(*e))
        edges.append((i, j)); inside.add(j); rest.discard(j)
    for i in range(n):
        for j in sorted((j for j in range(n) if j != i), key=lambda j: ang(i, j))[:NET_K]:
            if (i, j) in edges or (j, i) in edges or ang(i, j) > math.radians(NET_MAX): continue
            if not crosses(i, j): edges.append((i, j))
    # the order in which the network grows: outwards from Sofia
    adj = {i: [] for i in range(n)}
    for a, b in edges: adj[a].append(b); adj[b].append(a)
    depth, queue = {0: 0}, [0]
    while queue:
        a = queue.pop(0)
        for b in adj[a]:
            if b not in depth: depth[b] = depth[a] + 1; queue.append(b)
    T0, STEP, DUR = 1.2, .2, .8
    links, glows, dots = [], [], []
    longest = max(ang(a, b) for a, b in edges)
    for a, b in edges:
        if depth[b] < depth[a]: a, b = b, a
        va, vb = nodes[a][0], nodes[b][0]; th = ang(a, b)
        steps = max(10, int(th / math.radians(1.2)))
        lift_h = 0.015 + 0.075 * th / longest          # long links arc a little above the surface
        pts = []
        for k in range(steps + 1):
            t = k / steps
            f1 = math.sin((1 - t) * th) / math.sin(th); f2 = math.sin(t * th) / math.sin(th)
            v = tuple(f1 * p + f2 * q for p, q in zip(va, vb))
            x, y, _ = scr(v, 1 + lift_h * math.sin(math.pi * t))
            pts.append((x, y))
        d = 'M' + ' L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts)
        delay = T0 + STEP * depth[a]
        links.append(f'<path class="draw link" pathLength="1" style="animation-delay:{delay:.2f}s" d="{d}"/>')
    hubs = []
    for k, (pa, pb) in enumerate(HUBS):
        va, vb = unit(*pa), unit(*pb)
        th = math.acos(max(-1, min(1, sum(p * q for p, q in zip(va, vb)))))
        steps = max(16, int(th / math.radians(1.5)))
        pts = []
        for m in range(steps + 1):
            t = m / steps
            f1 = math.sin((1 - t) * th) / math.sin(th); f2 = math.sin(t * th) / math.sin(th)
            v = tuple(f1 * p + f2 * q for p, q in zip(va, vb))
            x, y, _ = scr(v, 1 + 0.16 * math.sin(math.pi * t))
            pts.append((x, y))
        d = 'M' + ' L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts)
        hubs.append(f'<path class="draw link hub" pathLength="1" style="animation-delay:{T0 + 1.1 + .3 * k:.2f}s" d="{d}"/>')
    for i, (v, x, y) in enumerate(nodes):
        delay = T0 - .2 if i == 0 else T0 + STEP * (depth[i] - 1) + DUR * .75
        st = f' style="animation-delay:{delay:.2f}s"'
        if i < 2:   # the two offices
            dots.append(f'<circle class="node fade"{st} cx="{fmt(x)}" cy="{fmt(y)}" r="5.5"/>'
                        f'<circle class="w fade"{st} cx="{fmt(x)}" cy="{fmt(y)}" r="14" stroke-width="1.3"/>')
        else:
            dots.append(f'<circle class="node fade"{st} cx="{fmt(x)}" cy="{fmt(y)}" r="3.6"/>'
                        f'<circle class="w fade"{st} cx="{fmt(x)}" cy="{fmt(y)}" r="8.5" stroke-width="1" stroke-opacity=".55"/>')
    def group(paths, cls, w, delay):
        body = ''.join(f'<path pathLength="1" d="{d}"/>' for d in paths)
        return (f'<g class="glow {cls}" stroke-width="{w * 3}">{body}</g>'
                f'<g class="w draw {delay} {cls}" stroke-width="{w}">{body}</g>')
    outline = f'M{cx - R} {cy} A{R} {R} 0 1 1 {cx + R} {cy} A{R} {R} 0 1 1 {cx - R} {cy}'
    extra = ('<style>.quiet { opacity: .45; } .back.quiet { opacity: .16; } .link { animation-duration: .8s; }'
             ' .hub { animation-duration: 1.4s; } .net-glow { opacity: .5; } .hubs { opacity: .85; }</style>')
    print('network:', n, 'cities,', len(edges), 'links +', len(hubs), 'hub arcs,', max(depth.values()), 'steps from Sofia')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{STYLE}{extra}'
            + group(back, 'back quiet', 1.1, 'd1') + group([outline], '', 1.8, 'd1') + group(front, 'quiet', 1.3, 'd2')
            + group([ring], 'back', 1.2, 'd3')
            + f'<g class="glow net-glow" stroke-width="4.5">{"".join(links)}</g>'
            + f'<g class="w" stroke-width="1.6">{"".join(links)}</g>'
            + f'<g class="glow net-glow hubs" stroke-width="4">{"".join(hubs)}</g>'
            + f'<g class="w hubs" stroke-width="1.3">{"".join(hubs)}</g>'
            + ''.join(dots) + '</svg>')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, svg in [('wire-multicharger.svg', multicharger()), ('wire-globe.svg', globe()),
                      ('wire-globe-network.svg', network_globe())]:
        with open(os.path.join(OUT, name), 'w', encoding='utf-8') as fh:
            fh.write(svg + '\n')
        print(name, len(svg) // 1024, 'KB')
