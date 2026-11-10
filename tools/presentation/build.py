#!/usr/bin/env python3
"""The ECOES Franchise presentation (PDF, 16:9 pages), built from the site's own pages, so every text,
figure and table is the client's approved one, word for word (nothing is retyped). Needs bs4.

  python3 tools/presentation/build.py            -> tools/presentation/bg.html, en.html
  node tools/presentation/render.js <lang> <out.pdf> [png-dir]   (with the site served on :8765)

Layout and colours follow the site (night glass): Unbounded light + Wix Madefor Text, the blue-hour
ground, glass panes, signal blue. Pages are 1280 x 720 CSS px (13.33 x 7.5 in, as a 16:9 deck).
"""
import base64, os, re
from bs4 import BeautifulSoup

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
HERE = os.path.join(ROOT, 'tools', 'presentation')
A = '../../'                                   # from tools/presentation/ to the site root
SITE = 'https://franchise.ecoes.eu/'                   # the own domain, live since 2026-11-06

# larger pictures for the PDF (the pages use small ones in their src, and srcset is dropped here)
UPGRADE = {'cut-multicharger-640.webp': 'cut-multicharger-1100.webp', 'cut-box-480.webp': 'cut-box-960.webp',
           'cut-container-640.webp': 'cut-container-1100.webp', 'on-trailer-700.jpg': 'on-trailer-1167.jpg',
           'on-truck-700.jpg': 'on-truck-1196.jpg', 'side-chargers-600.jpg': 'side-chargers-919.jpg',
           }


def load(rel):
    return BeautifulSoup(open(os.path.join(ROOT, rel), encoding='utf-8').read(), 'html.parser')


def inner(el):
    return el.decode_contents(formatter='minimal').strip().replace('\xa0', '&nbsp;')


def fix(markup):
    """paths relative to tools/presentation/, big pictures, no srcset/lazy loading"""
    markup = re.sub(r'\s(srcset|sizes|loading)="[^"]*"', '', markup)
    markup = re.sub(r'(src|href)="(?:\.\./)*(assets/)', r'\1="' + A + r'\2', markup)   # bg/… (../../) and the root page (none)
    for small, big in UPGRADE.items():
        markup = markup.replace('/' + small + '"', '/' + big + '"')
    return markup.replace('\xa0', '&nbsp;')


def src(img):
    return fix(f'src="{img["src"]}"')[5:-1]


def static_svg(rel):
    """a line drawing finished (no drawing animation in print), as a data URI; its still glow (since
    2026-11-09 in tools/glow/*-glow.svg, a picture under the lines on the site) is put back under the lines"""
    s = open(os.path.join(ROOT, rel), encoding='utf-8').read()
    glow = os.path.join(ROOT, 'tools', 'glow', os.path.basename(rel).replace('.svg', '-glow.svg'))
    if os.path.exists(glow):
        groups = ''.join(re.findall(r'<g class="glow[^"]*"[^>]*>.*?</g>', open(glow, encoding='utf-8').read(), re.S))
        s = s.replace('</defs>', '</defs>' + groups, 1)
    s = s.replace('</svg>', '<style>.draw{animation:none!important;stroke-dashoffset:0!important}'
                            '.fade{animation:none!important;opacity:1!important}'
                            '.glow{filter:none!important;opacity:.16!important}</style></svg>')   # a blur would be printed as big pictures
    return 'data:image/svg+xml;base64,' + base64.b64encode(s.encode('utf-8')).decode('ascii')


CSS = r'''
@page { size: 1280px 720px; margin: 0; }
:root { --ground: #112031; --hi: #edf2f4; --text: #c3ced5; --mute: #b0bfca; --signal: #4cc3ff;
  --signal-soft: rgba(76, 195, 255, .22); --line: rgba(255, 255, 255, .12);
  --fd: "Unbounded", "Segoe UI", Arial, sans-serif; --ft: "Wix Madefor Text", "Segoe UI", Arial, sans-serif; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; background: var(--ground); color: var(--text); font: 400 15px/1.55 var(--ft); -webkit-font-smoothing: antialiased; }
:lang(bg), :lang(bg) * { font-feature-settings: "locl" 0 !important; }
img { display: block; max-width: 100%; }
p { margin: 0 0 .75em; } p:last-child { margin-bottom: 0; }
b { color: var(--hi); font-weight: 600; }
h1, h2, h3, h4 { margin: 0; color: var(--hi); font-weight: 300; }
.slide {
  position: relative; width: 1280px; height: 720px; overflow: hidden; break-after: page; page-break-after: always;
  padding: 56px 72px 76px;
  background:
    radial-gradient(760px 520px at 92% 0%, rgba(70, 150, 190, .2), transparent 70%),
    radial-gradient(640px 460px at 0% 72%, rgba(190, 70, 60, .07), transparent 70%),
    radial-gradient(900px 640px at 60% 120%, rgba(56, 108, 150, .22), transparent 70%),
    var(--ground);
}
.slide:last-child { break-after: auto; page-break-after: auto; }
.body { position: relative; height: 100%; }
.foot { position: absolute; left: 72px; right: 72px; bottom: 22px; display: flex; align-items: center; justify-content: space-between;
  padding-top: 12px; border-top: 1px solid var(--line); font: 500 12.5px/1 var(--ft); letter-spacing: .03em; color: var(--mute); }
.foot .brand { display: flex; align-items: center; gap: 14px; }
.foot img { height: 26px; width: auto; }
.t { margin: 0 0 22px; font: 300 36px/1.12 var(--fd); letter-spacing: -.02em; text-wrap: balance; }
.t--s { font-size: 30px; margin-bottom: 18px; }
.sub { margin: 0 0 14px; font: 400 19px/1.3 var(--fd); color: var(--hi); }
.kind { display: block; font: 300 40px/1.1 var(--fd); letter-spacing: -.025em; color: var(--hi); }
.name { display: inline-flex; align-items: center; gap: 12px; margin-top: 14px; font: 400 16px/1.3 var(--fd); letter-spacing: .04em; color: var(--text); }
.name::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--signal); box-shadow: 0 0 0 4px var(--signal-soft); }
.lead { font-size: 17px; line-height: 1.55; color: var(--text); }
.glass { border-radius: 20px; background: linear-gradient(160deg, rgba(255, 255, 255, .085), rgba(255, 255, 255, .015) 46%), rgba(30, 50, 72, .36);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .14), inset 0 1px 0 rgba(255, 255, 255, .16); }
.cut { filter: drop-shadow(0 22px 22px rgba(0, 0, 0, .55)); }
.photo { border-radius: 16px; box-shadow: 0 0 0 1px rgba(255, 255, 255, .14); object-fit: cover; }
.cap { margin-top: 8px; font-size: 13.5px; line-height: 1.45; color: var(--mute); }
.dot-list { list-style: none; margin: 0; padding: 0; }
.dot-list li { position: relative; padding: 7px 0 7px 22px; border-top: 1px solid var(--line); font-size: 14px; line-height: 1.5; }
.dot-list li:last-child { border-bottom: 1px solid var(--line); }
.dot-list li::before { content: ""; position: absolute; left: 3px; top: 15px; width: 7px; height: 7px; border-radius: 50%; background: var(--signal); }

/* figures */
.chips { margin: 0; display: grid; gap: 12px; }
.chips--2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.chips--4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.chip { display: flex; flex-direction: column-reverse; justify-content: flex-end; padding: 16px 18px 14px; border-radius: 18px; }
.chip dd { margin: 0; font: 300 24px/1.15 var(--fd); letter-spacing: -.01em; color: var(--hi); }
.chip dt { margin-top: 6px; font-size: 14px; line-height: 1.4; color: var(--text); }

/* cover */
.cover { padding: 0; }
.cover-photo { position: absolute; top: 0; right: 0; width: 78%; height: 100%; object-fit: cover; object-position: 60% 55%; }
.cover-shade { position: absolute; inset: 0;
  background: linear-gradient(90deg, #0b1724 0%, #0b1724 22%, rgba(11, 23, 36, .82) 36%, rgba(11, 23, 36, .2) 58%, rgba(11, 23, 36, 0) 72%),
              linear-gradient(180deg, rgba(11, 23, 36, .55), rgba(11, 23, 36, 0) 22%, rgba(11, 23, 36, 0) 70%, rgba(11, 23, 36, .9)); }
.cover-text { position: absolute; left: 72px; top: 64px; bottom: 96px; width: 520px; display: flex; flex-direction: column; }
.cover-logo { height: 76px; width: auto; margin-bottom: auto; }
.cover h1 { font: 300 50px/1.08 var(--fd); letter-spacing: -.03em; color: var(--hi); text-wrap: balance; }
.cover .name { margin: 22px 0 26px; }
.cover-slogan { max-width: 30ch; font-size: 19px; line-height: 1.5; color: var(--text); }
.cover .foot { border-top-color: rgba(255, 255, 255, .16); }

/* join */
.join { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, .85fr); gap: 48px; align-items: center; height: 100%; }
.join .statement { margin: 0; font: 300 33px/1.3 var(--fd); letter-spacing: -.02em; color: var(--hi); text-wrap: balance; }
.punch { position: relative; margin: 34px 0 0; padding-left: 28px; font: 400 23px/1.3 var(--fd); color: var(--hi); }
.punch::before { content: ""; position: absolute; left: 0; top: .5em; width: 10px; height: 10px; border-radius: 50%; background: var(--signal); box-shadow: 0 0 0 5px var(--signal-soft); }
.join img { width: 100%; }

/* offer */
.offers { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px; }
.offer { display: flex; flex-direction: column; }
.offers { margin-top: 34px; }
.offer .img { height: 230px; display: flex; align-items: flex-end; justify-content: center; margin-bottom: -46px; position: relative; z-index: 1; }
.offer .img img { max-height: 230px; width: auto; }
.offer .glass { flex: 1; padding: 66px 26px 26px; }
.offer h3 { margin: 0 0 12px; font: 400 21px/1.25 var(--fd); }
.offer p { font-size: 15.5px; line-height: 1.6; }

/* two columns */
.cols { display: grid; gap: 40px; align-items: start; }
.cols--57 { grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); }
.cols--66 { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
.cols--75 { grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); }

/* pillars */
.pane { padding: 26px 28px; }
.pane-title { margin: 0 0 8px; font: 400 18px/1.3 var(--fd); color: var(--hi); }
.pillars { list-style: none; margin: 0; padding: 0; }
.pillars li { position: relative; padding: 14px 0 14px 60px; border-top: 1px solid var(--line); }
.pillars li:first-child { border-top: 0; }
.pillars li::before { content: attr(data-n); position: absolute; left: 0; top: 14px; min-width: 40px; height: 26px; padding: 0 9px; border-radius: 999px;
  display: grid; place-items: center; box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .3); font: 400 12.5px/1 var(--fd); color: var(--hi); }
.pillars h4 { margin: 0 0 4px; font: 400 16.5px/1.3 var(--fd); color: var(--hi); }
.pillars p { font-size: 14px; line-height: 1.5; }
.notice { position: relative; margin-top: 14px; padding: 14px 20px 14px 44px; border-radius: 16px; color: var(--hi); font-weight: 500; font-size: 14.5px; }
.notice::after { content: ""; position: absolute; left: 20px; top: 21px; width: 8px; height: 8px; border-radius: 50%; background: var(--signal); box-shadow: 0 0 0 4px var(--signal-soft); }

/* payments */
.pay { margin-top: 20px; }
.pay-ways { list-style: none; margin: 0 0 14px; padding: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.pay-way { display: flex; flex-direction: column; gap: 8px; }
.pay-icon { width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center;
  background: radial-gradient(closest-side, rgba(76, 195, 255, .18), rgba(76, 195, 255, .04)); box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .16); }
.pay-icon img { width: 46px; height: 46px; }
.pay-label { font: 400 13.5px/1.3 var(--fd); color: var(--hi); }
.pay-text { padding-top: 12px; border-top: 1px solid var(--line); font-size: 14px; line-height: 1.5; }

/* why: nine panes */
.tiles { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.tile { padding: 16px 20px 15px; border-radius: 18px; }
.tile h3 { margin: 0 0 6px; font: 400 15.5px/1.28 var(--fd); color: var(--hi); text-wrap: balance; }
.tile p { font-size: 13.5px; line-height: 1.48; }

/* MultiCharger and Box overview */
.over { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 6fr); gap: 40px; height: 100%; align-items: center; }
.over .lead { margin: 22px 0 26px; }
.over-photo { width: 100%; height: 470px; object-position: 90% 50%; }
.over-cut { width: 100%; max-height: 470px; object-fit: contain; }

/* twelve points */
.points { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
.point { display: flex; gap: 12px; align-items: flex-start; padding: 13px 15px; border-radius: 16px; }
.point-no { flex: none; min-width: 1.3em; font: 300 24px/1 var(--fd); color: var(--signal); letter-spacing: -.03em; }
.point p { font-size: 12.8px; line-height: 1.42; }

/* construction */
.shots { display: flex; gap: 14px; margin-bottom: 18px; }
.shots img { height: 190px; width: auto; }
.panes3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.panes3 .glass { padding: 16px 18px; font-size: 13.4px; line-height: 1.5; }
.panes3 b:first-child { display: block; margin-bottom: 6px; font: 400 15px/1.3 var(--fd); }

/* mobility and transport */
.mt { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 48px; }
.mt .two { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 14px; margin-top: 12px; }
.mt .two img.photo { width: 100%; height: 165px; }
.mt p { font-size: 15px; }
.cont { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.69fr); gap: 18px; align-items: end; margin-top: 12px; }
.cont img { width: 100%; }

/* charts */
.hbars { list-style: none; margin: 0; padding: 0; display: grid; gap: 14px; }
.hbar { display: grid; gap: 14px; grid-template-columns: 160px minmax(0, 1fr) 220px; align-items: center; }
.hbar-label { font-size: 15px; color: var(--text); }
.hbar-track { height: 14px; border-radius: 7px; background: rgba(255, 255, 255, .07); overflow: hidden; }
.hbar-fill { display: block; height: 100%; width: calc(var(--f) * 100%); border-radius: 7px; background: linear-gradient(90deg, rgba(255, 255, 255, .18), rgba(255, 255, 255, .42)); }
.hbar.is-on .hbar-fill { background: linear-gradient(90deg, rgba(76, 195, 255, .35), var(--signal)); }
.hbar-value { font: 400 14.5px/1.3 var(--fd); color: var(--hi); white-space: nowrap; }
.chart { padding: 24px 28px; }
.chart figcaption { margin-top: 14px; font-size: 13.5px; color: var(--mute); }
figure { margin: 0; }
.vlegend { display: flex; flex-wrap: wrap; gap: 6px 18px; margin: 0 0 14px; font-size: 13.5px; color: var(--text); }
.vkey::before { content: ""; display: inline-block; width: 11px; height: 11px; margin-right: 7px; border-radius: 3px; vertical-align: -1px; background: var(--signal); }
.vkey--1::before { background: rgba(255, 255, 255, .55); }
.vunit { margin-left: auto; color: var(--mute); }
.vbars { list-style: none; margin: 0; padding: 0; display: flex; align-items: stretch; gap: 16px; height: 230px; border-bottom: 1px solid rgba(255, 255, 255, .22); }
.vcol { flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; }
.vcol b { margin-bottom: 7px; font: 400 13px/1 var(--fd); color: var(--hi); white-space: nowrap; }
.vbar { width: 100%; height: calc((100% - 26px) * var(--f)); display: flex; flex-direction: column-reverse; border-radius: 8px 8px 2px 2px; overflow: hidden; }
.vseg { display: block; height: calc(var(--f) * 100%); background: linear-gradient(180deg, rgba(76, 195, 255, .95), rgba(76, 195, 255, .4)); }
.vseg--1 { background: rgba(255, 255, 255, .55); }
.vcol i { position: relative; top: 24px; height: 0; font-style: normal; font-size: 13px; color: var(--mute); white-space: nowrap; }
.vaxis { margin: 36px 0 0; text-align: center; font-size: 13px; color: var(--mute); }

/* tables */
table.pt { width: 100%; border-collapse: collapse; font-size: 14px; font-variant-numeric: tabular-nums; }
.pt th, .pt td { padding: 10px 10px; border-top: 1px solid var(--line); text-align: right; }
.pt thead th { border-top: 0; vertical-align: bottom; font-size: 12.5px; font-weight: 600; line-height: 1.35; color: var(--mute); }
.pt th:first-child, .pt td:first-child { text-align: left; }
.pt tbody th { font-weight: 600; color: var(--hi); white-space: nowrap; }
.pt td { color: var(--text); white-space: nowrap; }
.pt tr.on th, .pt tr.on td { color: var(--hi); background: rgba(76, 195, 255, .08); }
.pt tr.on th::before { content: ""; display: inline-block; width: 6px; height: 6px; margin: 0 8px 1px 0; border-radius: 50%; background: var(--signal); }
.tablepane { padding: 14px 18px 8px; }

/* comparison */
.cmp-label { margin: 0 0 8px; text-align: center; font: 400 13px/1.2 var(--fd); letter-spacing: .3em; text-transform: uppercase; color: var(--mute); }
.cmp-row { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); gap: 18px; align-items: center; }
.cmp-side { display: flex; align-items: center; justify-content: center; gap: 10px; }
.cmp-side img { min-width: 0; max-height: 150px; width: auto; max-width: 100%; object-fit: contain; filter: drop-shadow(0 18px 18px rgba(0, 0, 0, .55)); }
.cmp-side--ours img { max-width: calc(50% - 20px); }
.cmp-side--ours img:only-child { max-width: 100%; }
.cmp-eq { font: 300 46px/1 var(--fd); color: var(--hi); }
.cmp-plus { font: 300 30px/1 var(--fd); color: var(--mute); }
.cmp-cards { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 14px; margin-top: 18px; }
.cmp-card { padding: 16px 22px; border-radius: 18px; font-size: 14.5px; }
.cmp-card p { margin: 0 0 6px; }
.cmp-card--ours { box-shadow: inset 0 1px 0 rgba(255, 255, 255, .14), inset 0 0 0 1px rgba(76, 195, 255, .45); }
.cmp-card--ours b { color: var(--signal); }

/* certification */
.cert { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 16px; }
.cert li { position: relative; padding: 16px 20px 16px 64px; border-radius: 18px; }
.cert li::before { content: attr(data-n); position: absolute; left: 20px; top: 16px; width: 30px; height: 30px; border-radius: 50%;
  display: grid; place-items: center; box-shadow: inset 0 0 0 1px rgba(76, 195, 255, .6); font: 400 13px/1 var(--fd); color: var(--hi); }
.cert li.notice::before { content: none; }   /* the notice in the grid has no number: only its signal dot */
.cert h3 { margin: 0 0 4px; font: 400 16px/1.3 var(--fd); }
.cert p { font-size: 13.5px; line-height: 1.5; }

/* announcements and contacts */
.notices { margin: 0 0 14px; padding-left: 1.3em; font-size: 15px; line-height: 1.55; }
.notices li { margin-bottom: 8px; }
.notices li::marker { color: var(--signal); font-weight: 600; }
.note { font-size: 13.5px; color: var(--mute); }
.actions { display: flex; gap: 12px; margin-top: 18px; }
.btn { display: inline-flex; align-items: center; gap: 10px; min-height: 46px; padding: 10px 22px; border-radius: 999px; font: 600 15px/1.2 var(--ft); text-decoration: none; }
.btn--ice { background: #f2f5f7; color: #06090c; }
.btn--glass { color: var(--hi); background: rgba(255, 255, 255, .07); box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .22); }
.btn--glass::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--signal); box-shadow: 0 0 0 3px var(--signal-soft); }
.offices { display: grid; gap: 12px; }
.office { padding: 16px 20px; border-radius: 18px; font-style: normal; font-size: 13.5px; line-height: 1.5; }
.office h3 { margin: 0 0 2px; font: 400 16px/1.3 var(--fd); }
.office .kind { display: block; margin-bottom: 8px; font: 400 13.5px/1.4 var(--ft); letter-spacing: 0; color: var(--mute); }
.office .grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 4px 16px; }
.office a { color: var(--hi); text-decoration: none; }
.card-link { color: inherit; text-decoration: none; }   /* the site's cards are links (heading = link) since 2026-11-05 */
.office .lines a, .office .lines span[translate="no"] { white-space: nowrap; }
'''


def foot(company, n, total, logo):
    return (f'<div class="foot"><span class="brand"><img src="{logo}" alt="">'
            f'<span translate="no">{company}</span></span><span>{n} / {total}</span></div>')


def build(lang):
    p = '' if lang == 'en' else 'bg/'
    H = load(p + 'index.html'); F = load(p + 'franchise/index.html'); M = load(p + 'multicharger/index.html')
    B = load(p + 'multicharger-box/index.html'); C = load(p + 'contact-us/index.html')
    hm, fm, mm, bm, cm = (x.select_one('main') for x in (H, F, M, B, C))
    company = H.select_one('.footer-company').get_text(' ', strip=True)
    logo = A + 'assets/img/logo-night.svg'
    preorder = hm.select_one('.hero-actions .btn--ice').get_text(' ', strip=True)
    offer_txt = hm.select_one('.hero-actions .btn--signal').get_text(' ', strip=True)
    contacts = H.select_one('.main-nav a[href$="contact-us/"]').get_text(' ', strip=True)
    base = SITE + ('' if lang == 'en' else 'bg/')
    slides = []

    # 1 cover: the Home hero
    hero = hm.select_one('.hero-pane')
    slides.append(('cover', f'''
      <img class="cover-photo" src="{A}assets/img/home/hero-bluehour-1672.jpg" alt="">
      <div class="cover-shade"></div>
      <div class="cover-text">
        <img class="cover-logo" src="{logo}" alt="ECOES JV">
        <h1>{inner(hero.select_one('.hero-kind'))}</h1>
        <p class="name" translate="no">{inner(hero.select_one('.hero-name'))}</p>
        <p class="cover-slogan">{inner(hero.select_one('.hero-statement'))}</p>
      </div>'''))

    # 2 the invitation and the punchline, with the network globe
    it = hm.select_one('.intro-text')
    slides.append(('', f'''
      <div class="join">
        <div><p class="statement">{inner(it.select_one('.statement'))}</p>
          <p class="punch">{inner(it.select_one('.punchline a'))}</p></div>
        <img src="{static_svg('assets/img/v2/wire-globe-network.svg')}" alt="">
      </div>'''))

    # 3 what we offer
    off = hm.select_one('section.offer')
    cards = ''
    for c in off.select('.offer-card'):
        cards += (f'<article class="offer"><div class="img"><img class="cut" src="{src(c.select_one(".product img"))}" alt=""></div>'
                  f'<div class="glass"><h3>{inner(c.select_one("h3"))}</h3><p>{inner(c.select_one("p"))}</p></div></article>')
    slides.append(('', f'<h2 class="t">{inner(off.select_one(".section-title"))}</h2><div class="offers">{cards}</div>'))

    # 4 I. What is ECOES Franchise, the payments, the three pillars
    w = fm.select_one('#what')
    pay = w.select_one('.pay')
    ways = ''.join(f'<li class="pay-way"><span class="pay-icon"><img src="{src(li.select_one("img"))}" alt=""></span>'
                   f'<span class="pay-label">{inner(li.select_one(".pay-label"))}</span></li>' for li in pay.select('.pay-way'))
    cp = w.select_one('.cert-pane')
    pil = ''.join(f'<li data-n="{li["data-n"]}"><h4>{inner(li.select_one("h4"))}</h4><p>{inner(li.select_one("p"))}</p></li>'
                  for li in cp.select('.pillars li'))
    slides.append(('', f'''
      <div class="cols cols--57">
        <div><h2 class="t">{inner(w.select_one('.section-title'))}</h2>
          <p>{inner(w.select_one('.split-intro > p'))}</p>
          <div class="pay"><ul class="pay-ways">{ways}</ul><p class="pay-text">{inner(pay.select_one('.pay-text'))}</p></div></div>
        <div><div class="glass pane"><h3 class="pane-title">{inner(cp.select_one('.pane-title'))}</h3><ol class="pillars">{pil}</ol></div>
          <p class="glass notice">{inner(w.select_one('.notice'))}</p></div>
      </div>'''))

    # 5 why ECOES Franchise: the nine panes of Home
    why = hm.select_one('section.why')
    tiles = ''.join(f'<article class="glass tile"><h3>{inner(t.select_one("h3"))}</h3><p>{inner(t.select_one("p"))}</p></article>'
                    for t in why.select('.tile'))
    slides.append(('', f'<h2 class="t t--s">{inner(why.select_one(".section-title"))}</h2><div class="tiles">{tiles}</div>'))

    def chips(band, cls):
        return f'<dl class="chips {cls}">' + ''.join(
            f'<div class="glass chip"><dt>{inner(c.select_one("dt"))}</dt><dd>{inner(c.select_one("dd"))}</dd></div>'
            for c in band.select('.chip')) + '</dl>'

    # 6 ECOES MultiCharger: the page head, the key figures and the photo
    h1 = mm.select_one('h1')
    slides.append(('', f'''
      <div class="over">
        <div><h2><span class="kind">{inner(h1.select_one('.hero-kind'))}</span><span class="name" translate="no">{inner(h1.select_one('.hero-name'))}</span></h2>
          <p class="lead">{inner(mm.select_one('.lead-pane .hero-statement'))}</p>
          {chips(mm.select('.figures-band')[0], 'chips--2')}</div>
        <img class="photo over-photo" src="{A}assets/img/v2/head-multicharger-1672.jpg" alt="">
      </div>'''))

    # 7 I. What is ECOES MultiCharger: the twelve points
    wm = mm.select_one('#what')
    pts = ''.join(f'<li class="glass point"><span class="point-no">{pt.select_one(".point-no").get_text(strip=True)}</span>'
                  f'<p>{inner(pt.select_one("p"))}</p></li>' for pt in wm.select('.point'))
    slides.append(('', f'<h2 class="t t--s">{inner(wm.select_one(".section-title"))}</h2>'
                       f'<p class="sub">{inner(wm.select_one(".doc-sub"))}</p><ol class="points">{pts}</ol>'))

    # 8 III. Construction: the two sides and the three sections
    cs = mm.select_one('#construction')
    imgs = [i for i in cs.select('.gallery img')]
    pick = [imgs[0], imgs[1]]
    panes = ''.join(f'<p class="glass">{inner(x)}</p>' for x in cs.select('.panes .pane'))
    slides.append(('', f'''<h2 class="t t--s">{inner(cs.select_one('.section-title'))}</h2>
      <div class="shots">{''.join(f'<img class="photo" src="{src(i)}" alt="">' for i in pick)}</div>
      <div class="panes3">{panes}</div>'''))

    # 9 mobility and IV. transport
    mob = mm.select_one('#mobility')
    figs = mob.find_all_next('figure', limit=2)
    tr = mm.select_one('#transport')
    cfig = tr.select('.gallery figure')
    slides.append(('', f'''
      <div class="mt">
        <div><h2 class="t t--s">{inner(mob)}</h2><p>{inner(mob.find_next('p'))}</p>
          <div class="two">{''.join(f'<figure><img class="photo" src="{src(f.select_one("img"))}" alt=""><figcaption class="cap">{inner(f.select_one("figcaption"))}</figcaption></figure>' for f in figs)}</div></div>
        <div><h2 class="t t--s">{inner(tr.select_one('.section-title'))}</h2><p>{inner(tr.select_one('.prose'))}</p>
          <div class="cont">{''.join(f'<figure><img class="cut" src="{src(f.select_one("img"))}" alt=""></figure>' for f in cfig)}</div>
          <div class="cont" style="align-items:start;margin-top:10px">{''.join(f'<p class="cap">{inner(f.select_one("figcaption"))}</p>' for f in cfig)}</div></div>
      </div>'''))

    # 10 V. Financial profitability: the assumptions and the diesel prices
    pr = mm.select_one('#profitability')
    band = pr.select_one('.figures-band--inner')
    hb = pr.select_one('.hbars').find_parent('figure')
    slides.append(('', f'''<h2 class="t t--s">{inner(pr.select_one('.section-title'))}</h2>
      <p class="sub">{inner(band.select_one('.figures-title'))}</p>{chips(band, 'chips--4')}
      <figure class="glass chart" style="margin-top:18px"><ul class="hbars">{fix(inner(hb.select_one('.hbars')))}</ul>
        <figcaption>{inner(hb.select_one('figcaption'))}</figcaption></figure>'''))

    def table(t, on='50'):
        head = ''.join(f'<th>{inner(th)}</th>' for th in t.select('thead th'))
        rows = ''
        for tr_ in t.select('tbody tr'):
            cells = tr_.find_all(['th', 'td'])
            cls = ' class="on"' if tr_.get('data-load') == on else ''
            rows += f'<tr{cls}><th>{inner(cells[0])}</th>' + ''.join(f'<td>{inner(c)}</td>' for c in cells[1:]) + '</tr>'
        return f'<div class="glass tablepane"><table class="pt"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'

    # 11 3. Gross operating profit: the table, the chart and the client's sentence about 10 %
    gp = mm.select_one('#gross-profit')
    vb = mm.select_one('.vbars').find_parent('figure')
    ten = next(x for x in mm.select('p') if '10%' in x.get_text() and ('лизинг' in x.get_text() or 'leas' in x.get_text()))
    slides.append(('', f'''<h2 class="t t--s">{inner(gp)}</h2>
      <div class="cols" style="grid-template-columns:minmax(0,1.45fr) minmax(0,1fr);gap:24px">
        <div>{table(mm.select_one('.profit-table'))}<p class="glass notice" style="font-weight:400">{inner(ten)}</p></div>
        <figure class="glass chart" style="padding:20px 22px">{fix(inner(vb))}</figure>
      </div>'''))

    def compare(cmp):
        side = cmp.select('.compare-side')
        left = ''.join(f'<img src="{src(i)}" alt="">' for i in side[0].select('img'))
        ours = side[1].select('img')
        right = '<span class="cmp-plus">+</span>'.join(f'<img src="{src(i)}" alt="">' for i in ours)
        cards = cmp.select('.compare-card')
        return (f'<p class="cmp-label">{inner(cmp.select_one(".compare-label"))}</p>'
                f'<div class="cmp-row"><div class="cmp-side">{left}</div><span class="cmp-eq">=</span>'
                f'<div class="cmp-side cmp-side--ours">{right}</div></div>'
                f'<div class="cmp-cards"><div class="glass cmp-card">{inner(cards[0])}</div>'
                f'<div class="glass cmp-card cmp-card--ours">{inner(cards[1])}</div></div>')

    # 12 5. Investment profitability: a new truck = two MultiChargers
    iv = mm.select_one('#investment')
    ivp = iv.find_all_next('p', class_='prose', limit=2)
    slides.append(('', f'''<h2 class="t t--s">{inner(iv)}</h2><p style="max-width:92ch">{inner(ivp[1])}</p>
      <div style="margin-top:18px">{compare(mm.select_one('.compare'))}</div>'''))

    # 13 ECOES MultiCharger Box: the page head, the key figures and the cut-out
    bh = bm.select_one('h1')
    bw = bm.select_one('#what')
    slides.append(('', f'''
      <div class="over" style="grid-template-columns:minmax(0,6fr) minmax(0,5fr)">
        <div><h2><span class="kind" style="font-size:34px">{inner(bh.select_one('.hero-kind'))}</span><span class="name" translate="no">{inner(bh.select_one('.hero-name'))}</span></h2>
          <p class="lead" style="margin:18px 0 20px;font-size:16px">{inner(bm.select_one('.lead-pane .hero-statement'))}</p>
          {chips(bm.select('.figures-band')[0], 'chips--2')}</div>
        <img class="cut over-cut" src="{A}assets/img/v2/cut-box-960.webp" alt="">
      </div>'''))

    # 14 the Box: gross profit and investment (a taxi = one Box)
    bg_ = bm.select_one('#gross-profit')
    bi = bm.select_one('#investment')
    slides.append(('', f'''
      <div class="cols cols--66" style="gap:36px">
        <div><h2 class="t t--s">{inner(bg_.select_one('.section-title'))}</h2>{table(bm.select_one('.profit-table'))}</div>
        <div><h2 class="t t--s">{inner(bi.select_one('.section-title'))}</h2>{compare(bm.select_one('.compare'))}</div>
      </div>'''))

    # 15 LPG & PNG (methane)
    lp = bm.select_one('#lpg')
    lpp = lp.select('.prose')
    lpi = lp.select('img')
    bul = lp.select_one('.bullets')
    bul_intro = bul.find_previous('p', class_='prose')
    slides.append(('', f'''<h2 class="t t--s">{inner(lp.select_one('.section-title'))}</h2>
      <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:36px">
        <div><p class="sub">{inner(lp.select_one('#lpg-box'))}</p><p style="font-size:14.5px">{inner(lpp[0])}</p>
          <div style="display:flex;gap:18px;align-items:flex-end;justify-content:center;margin-top:10px">{''.join(f'<img class="cut" style="max-height:200px;width:auto" src="{src(i)}" alt="">' for i in lpi[:2])}</div></div>
        <div><p style="font-size:14.5px">{inner(bul_intro)}</p><ul class="dot-list">{inner(bul)}</ul></div>
      </div>'''))

    # 16 the five certification pillars
    ce = hm.select_one('section.cert')
    lis = ''.join(f'<li class="glass" data-n="{i + 1}"><h3>{inner(li.select_one("h3"))}</h3><p>{inner(li.select_one("p"))}</p></li>'
                  for i, li in enumerate(ce.select('li')))
    slides.append(('', f'''<h2 class="t t--s">{inner(ce.select_one('.section-title'))}</h2><ol class="cert">{lis}
      <li class="glass notice" style="padding:18px 22px 18px 48px;display:flex;align-items:center"><p>{inner(w.select_one('.notice'))}</p></li></ol>'''))

    # 17 announcements, pre-order and contacts
    an = hm.select_one('section.announce')
    nts = an.select('.notices li')
    offices = ''
    for o in cm.select('.office'):
        lines = [inner(li) for ul in o.select('.office-lines') for li in ul.select('li')]
        offices += (f'<address class="glass office"><h3>{inner(o.select_one("h2"))}</h3><span class="kind">{inner(o.select_one(".office-kind"))}</span>'
                    f'<div class="grid"><div class="lines">{"<br>".join(lines)}</div><div>{inner(o.select_one(".office-address"))}</div></div></address>')
    slides.append(('', f'''
      <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:40px">
        <div><h2 class="t t--s">{inner(an.select_one('.section-title'))}</h2>
          <ol class="notices"><li>{inner(nts[0])}</li><li>{inner(nts[1])}</li></ol>
          <p class="note">{inner(an.select_one('.form-note'))}</p>
          <div class="actions"><a class="btn btn--ice" href="{base}#pre-order">{preorder}</a>
            <a class="btn btn--glass" href="{base}contact-us/?topic=franchise#contact-form">{offer_txt}</a></div></div>
        <div><h2 class="t t--s">{contacts}</h2><div class="offices">{fix(offices)}</div></div>
      </div>'''))

    total = len(slides)
    body = ''
    for i, (cls, content) in enumerate(slides, 1):
        inside = content if cls == 'cover' else f'<div class="body">{content}</div>'
        body += f'<section class="slide {cls}">{inside}{foot(company, i, total, logo)}</section>\n'
    html = (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>ECOES Franchise</title>'
            f'<link rel="stylesheet" href="{A}assets/css/fonts.css"><style>{CSS}</style></head><body>{fix(body)}</body></html>')
    out = os.path.join(HERE, f'{lang}.html')
    # the cards' links point at the live pages (on the site they are relative: in the PDF they would lead nowhere)
    html = re.sub(r'(<a class="card-link" href=")([^"]*)"', lambda m: m.group(1) + base + m.group(2) + '"', html)
    open(out, 'w', encoding='utf-8').write(html)
    print('wrote', out, total, 'pages')


if __name__ == '__main__':
    for lang in ('bg', 'en'):
        build(lang)
