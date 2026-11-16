#!/usr/bin/env python3
"""The two-page ECOES Franchise brochure (A4), a short ad for e-mail and print (client, 2026-11-16: "a 2-page PDF with
the best slogans and the strongest points of both variants; the full-site PDF freezes the system").
Every sentence is taken from the site's own pages (EN + BG), so the brochure says exactly what the site says.

  python3 tools/brochure/build.py              -> tools/brochure/bg.html, en.html (+ img/, generated)
  node tools/brochure/render.js <lang> <out.pdf> [png-dir]     (site served on :8765, e.g. scratch serve.sh)

Light on purpose: JPEG pictures sized for A4 at about 150 dpi, a vector QR code, the site's two fonts (subset by Chromium);
no blur, no transparency, so the PDF stays well under 1 MB and opens at once.
"""
import os, re, html
from bs4 import BeautifulSoup
from PIL import Image
import segno

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
HERE = os.path.join(ROOT, 'tools', 'brochure')
A = '../../'
SITE = 'https://franchise.ecoes.eu/'

def load(rel):
    return BeautifulSoup(open(os.path.join(ROOT, rel), encoding='utf-8').read(), 'html.parser')
def txt(el):
    return ' '.join(el.get_text(' ', strip=True).split()).replace(' ,', ',').replace(' !', '!').replace(' .', '.') if el else ''
def esc(s): return html.escape(s, quote=False)

def images():
    os.makedirs(os.path.join(HERE, 'img'), exist_ok=True)
    out = {}
    hero = Image.open(os.path.join(ROOT, 'assets/img/home/hero-bluehour-1672.jpg')).convert('RGB')
    hero = hero.resize((1240, round(hero.height * 1240 / hero.width)), Image.LANCZOS)
    hero.save(os.path.join(HERE, 'img/hero.jpg'), quality=80, optimize=True, progressive=True); out['hero'] = 'img/hero.jpg'
    mc = Image.open(os.path.join(ROOT, 'assets/img/v2/cut-multicharger-1100.webp')).convert('RGBA')
    bg = Image.new('RGBA', mc.size, (255, 255, 255, 255)); bg.alpha_composite(mc)
    bg = bg.convert('RGB').resize((780, round(mc.height * 780 / mc.width)), Image.LANCZOS)
    bg.save(os.path.join(HERE, 'img/mobile.jpg'), quality=82, optimize=True); out['mobile'] = 'img/mobile.jpg'
    bx = Image.open(os.path.join(ROOT, 'assets/img/v2/head-box3-1672.jpg')).convert('RGB')
    w, h = bx.size; box = bx.crop((int(w * .30), int(h * .20), int(w * .98), int(h * .70)))   # the truck with the Box at the hotel
    box = box.resize((780, round(box.height * 780 / box.width)), Image.LANCZOS)
    box.save(os.path.join(HERE, 'img/box.jpg'), quality=80, optimize=True); out['box'] = 'img/box.jpg'
    return out

def texts(lang):
    p = 'bg/' if lang == 'bg' else ''
    home = load(p + 'index.html').find('main')
    t = {}
    t['kicker'] = txt(home.select_one('.hero h1 .hero-kind')) or txt(home.select_one('.hero h1'))
    t['slogan'] = txt(home.select_one('.hero .hero-statement'))
    intro = txt(home.select_one('.intro p'))
    t['intro'] = intro
    t['punch'] = txt(home.select_one('.intro .punchline'))
    cards = home.select('.offer-card')
    t['mobile'] = (txt(cards[1].select_one('h3')), txt(cards[1].select_one('p')))
    t['box'] = (txt(cards[2].select_one('h3')), txt(cards[2].select_one('p')))
    t['figs'] = [(txt(c.select_one('dd')), txt(c.select_one('dt'))) for c in home.select('.figures-band--home .chip')]
    why = home.select('.why .tiles > *')
    def pane(i):
        el = why[i]; h = el.select_one('h3'); ps = el.select('p')
        return (txt(h), ' '.join(txt(x) for x in ps))
    t['why'] = [pane(i) for i in range(len(why))]
    t['profit_title'] = txt(home.select_one('#profit .section-title, #profit h2'))
    rows = home.select('#profit table tbody tr') or load(p + 'multicharger/index.html').select('#gross-profit table tbody tr')
    t['mob_month'] = [round((float(r['data-dc']) + float(r['data-service'])) * 30) for r in rows]
    box = load(p + 'multicharger-box/index.html')
    t['box_month'] = [round((float(r['data-dc']) + float(r['data-service'])) * 30) for r in box.select('#gross-profit table tbody tr')]
    t['box_auto'] = txt(box.select('#what .prose b')[-1])
    t['box_cards'] = [txt(c) for c in box.select('.compare-card')]
    fin = load(p + 'financing/index.html')
    t['fin_title'] = txt(fin.select_one('#page-title'))
    t['fin'] = [txt(h) for h in fin.select('.pillars h3')]
    t['lead'] = txt(fin.select_one('.closing .lead')); t['statement'] = txt(fin.select_one('.closing .statement'))
    fr = txt(load(p + 'franchise/index.html').find('main'))
    m = re.search(r'(Всички плащания|All payments)[^.]*\.', fr); t['pay'] = m.group(0) if m else ''
    lis = [txt(li) for li in home.select('#pre-order li')]
    sales = next(x for x in lis if x.startswith(('Продажбите на', 'Sales of the')))
    sales = re.match(r'^(.*?(?:сертификация|certification process)\.)', sales).group(1)
    orders = next(x for x in lis if x.startswith(('Поръчките за доставка', 'Orders for delivery')))
    t['ann'] = [sales, orders]
    t['preorder'] = 'Предварителна заявка' if lang == 'bg' else 'Pre-order'
    foot = load(p + 'contact-us/index.html').select_one('footer')
    t['foot'] = txt(foot)
    return t

def num(v, lang): return f'{v:,}'.replace(',', '.') if lang == 'bg' else f'{v:,}'

def page(lang, t, img):
    L = lang == 'bg'
    why = {h: d for h, d in t['why'] if h}
    pick_bg = ['Там, където няма зарядни станции', 'Готов сертифициран актив вместо години разработка', 'Мобилен, стационарен или смесен режим',
               'Около 20% допълнителни приходи', 'Резервно захранване и стационарна зарядна станция', 'Хардуер, софтуер и дистанционна поддръжка']
    pick_en = ['Where there are no charging stations', 'A ready certified asset instead of years of development', 'Mobile, stationary or mixed mode',
               'About 20% additional revenue', 'Backup power and a stationary charging station', 'Hardware, software and remote support']
    reasons = [(h, why[h]) for h in (pick_bg if L else pick_en)]
    payback = next((h for h, d in t['why'] if re.search(r'(около 5 месеца|about 5 months)', h)), '')
    mob_sentence = next((d for h, d in t['why'] if h == payback), '')
    mob_sentence = re.sub(r'^[\d.,%\s]+', '', mob_sentence)
    box50 = next((c for c in t['box_cards'] if '50%' in c), '')
    m = re.match(r'(.*?(?:месец|a month))\s*(.*)$', box50); box_sent, box_pay = (m.group(1) + '.', m.group(2).rstrip('.')) if m else (box50, '')
    if not L: box_sent = box_sent.replace('.00 EUR', ' EUR')
    loads = [10, 25, 50, 75, 100]
    def bars(vals):
        top = 60000
        return ('<div class="chart"><ol class="bars">' + ''.join(f'<li style="--f:{v / top:.4f}"><b>{num(v, lang)}</b></li>' for v in vals)
                + '</ol><ol class="axis">' + ''.join(f'<li>{l}%</li>' for l in loads) + '</ol></div>')
    qr = segno.make(SITE + ('bg/' if L else '') + '#pre-order', error='m')
    qr_svg = qr.svg_inline(scale=3, dark='#062925', light=None, border=0)
    phones_bg = [('Моб./WhatsApp', '+359 889988042'), ('Телефон и WhatsApp', '+44 7460659111')]
    phones_en = [('Mobile/WhatsApp', '+359 889988042'), ('Phone & WhatsApp', '+44 7460659111')]
    phones = phones_bg if L else phones_en
    cities = ('София', 'Лондон') if L else ('Sofia', 'London')
    unit = 'EUR на месец' if L else 'EUR a month'
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><title>ECOES Franchise</title>
<style>
@font-face {{ font-family: "Unbounded"; font-weight: 200 700; src: url("{A}assets/fonts/unbounded-cyrillic.woff2") format("woff2"); unicode-range: U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116; }}
@font-face {{ font-family: "Unbounded"; font-weight: 200 700; src: url("{A}assets/fonts/unbounded-latin.woff2") format("woff2"); unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }}
@font-face {{ font-family: "Wix Madefor Text"; font-weight: 400 800; src: url("{A}assets/fonts/wix-madefor-text-cyrillic.woff2") format("woff2"); unicode-range: U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116; }}
@font-face {{ font-family: "Wix Madefor Text"; font-weight: 400 800; src: url("{A}assets/fonts/wix-madefor-text-latin.woff2") format("woff2"); unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }}
@page {{ size: A4; margin: 0; }}
:root {{ --haze:#f2f6f3; --paper:#ffffff; --ink:#0b1d19; --text:#22302c; --mute:#3b4a45; --pine:#0d4a44; --deep:#062925; --mint:#a6f4d2; --leaf:#1fa36c; --line:#d5e2dc; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
:lang(bg), :lang(bg) * {{ font-feature-settings: "locl" 0; }}
body {{ font-family: "Wix Madefor Text", sans-serif; color: var(--text); background: var(--haze); font-size: 10pt; line-height: 1.45; }}
.page {{ width: 210mm; height: 297mm; padding: 11mm 13mm 9.5mm; position: relative; overflow: hidden; background: var(--haze); page-break-after: always; display: flex; flex-direction: column; }}
.page:last-child {{ page-break-after: auto; }}
.top {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 7mm; }}
.top img {{ height: 13mm; }}
.top .url {{ font-family: "Unbounded"; font-weight: 500; font-size: 9pt; color: var(--pine); }}
.kicker {{ font-family: "Unbounded"; font-weight: 500; font-size: 11pt; color: var(--pine); margin-bottom: 3mm; }}
h1 {{ font-family: "Unbounded"; font-weight: 500; font-size: 21pt; line-height: 1.16; color: var(--ink); letter-spacing: -.01em; max-width: 172mm; }}
.hero {{ margin: 6mm 0 5mm; height: 82mm; border-radius: 5mm; overflow: hidden; }}
.hero img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 62%; display: block; }}
.intro {{ font-size: 11.5pt; line-height: 1.5; color: var(--text); max-width: 176mm; }}
.products {{ display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; margin-top: 6mm; flex: 1; }}
.prod {{ background: var(--paper); border-radius: 4mm; padding: 5mm 5mm 5.5mm; border: .3mm solid var(--line); display: flex; flex-direction: column; }}
.prod .pic {{ height: 38mm; display: flex; align-items: center; justify-content: center; margin-bottom: 4mm; border-radius: 2.5mm; overflow: hidden; }}
.prod .pic img {{ max-width: 100%; max-height: 100%; display: block; }}
.prod .pic--photo img {{ width: 100%; height: 100%; object-fit: cover; }}
.prod h2 {{ font-family: "Unbounded"; font-weight: 500; font-size: 11.5pt; line-height: 1.2; color: var(--ink); margin-bottom: 2mm; }}
.prod p {{ font-size: 9.6pt; line-height: 1.45; }}
.prod p + p {{ margin-top: 2mm; }}
.prod .auto {{ font-weight: 700; color: var(--pine); }}
.figs {{ margin-top: 5mm; background: var(--deep); border-radius: 4mm; display: grid; grid-template-columns: repeat(4, 1fr); padding: 5mm 6mm; gap: 4mm; }}
.figs div {{ border-left: .3mm solid rgba(166,244,210,.35); padding-left: 3.5mm; }}
.figs dd {{ font-family: "Unbounded"; font-weight: 400; font-size: 14pt; color: #ffffff; line-height: 1.15; white-space: nowrap; }}
.figs dt {{ font-size: 8.4pt; line-height: 1.3; color: #c3dad1; margin-top: 1.2mm; }}
/* page 2 */
.profit {{ background: var(--deep); color: #dceae4; border-radius: 5mm; padding: 6mm 7mm 5mm; }}
.profit h2 {{ font-family: "Unbounded"; font-weight: 500; font-size: 13pt; line-height: 1.2; color: #ffffff; margin-bottom: 4mm; }}
.pcols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8mm; }}
.pcol {{ display: flex; flex-direction: column; }}
.pcol .name {{ font-family: "Unbounded"; font-weight: 500; font-size: 9.5pt; color: var(--mint); margin-bottom: 2mm; }}
.pcol .big {{ font-family: "Unbounded"; font-weight: 300; font-size: 26pt; line-height: 1; color: #ffffff; letter-spacing: -.01em; }}
.pcol .big small {{ font-size: 12pt; font-weight: 400; color: #c3dad1; margin-left: 1.5mm; letter-spacing: 0; }}
.pcol .cap {{ font-size: 8.4pt; line-height: 1.38; margin-top: 1.8mm; color: #c3dad1; }}
.pcol .pay {{ font-weight: 700; font-size: 9.2pt; color: #ffffff; margin-top: 1.2mm; }}
.chart {{ margin-top: auto; padding-top: 3mm; }}
.bars, .axis {{ list-style: none; display: grid; grid-template-columns: repeat(5, 1fr); gap: 2.5mm; }}
.bars {{ align-items: end; height: 14mm; border-bottom: .3mm solid rgba(166,244,210,.4); }}
.bars li {{ position: relative; height: calc(var(--f) * 10mm); background: var(--mint); border-radius: 1mm 1mm 0 0; }}
.bars b {{ position: absolute; left: -2mm; right: -2mm; bottom: 100%; margin-bottom: .7mm; text-align: center; font-weight: 600; font-size: 7pt; line-height: 1.2; color: #dceae4; white-space: nowrap; }}
.axis {{ margin-top: 1mm; text-align: center; font-size: 7pt; line-height: 1.3; color: #c3dad1; }}
.paynote {{ margin-top: 4mm; font-size: 8.4pt; color: #c3dad1; border-top: .3mm solid rgba(166,244,210,.25); padding-top: 3mm; }}
.page--2 {{ justify-content: space-between; gap: 4mm; }}
.reasons {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3mm 7mm; }}
.reasons h3 {{ font-family: "Unbounded"; font-weight: 500; font-size: 9pt; line-height: 1.25; color: var(--ink); margin-bottom: 1.2mm; padding-left: 4mm; position: relative; }}
.reasons h3::before {{ content: ""; position: absolute; left: 0; top: 1.3mm; width: 2mm; height: 2mm; border-radius: 50%; background: var(--leaf); }}
.reasons p {{ font-size: 8.2pt; line-height: 1.34; padding-left: 4mm; color: var(--mute); }}
.finance {{ background: var(--paper); border: .3mm solid var(--line); border-radius: 4mm; padding: 4mm 5mm; }}
.finance h2 {{ font-family: "Unbounded"; font-weight: 500; font-size: 9.6pt; color: var(--pine); margin-bottom: 2.2mm; }}
.finance ul {{ list-style: none; display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.8mm 4.5mm; }}
.finance li {{ font-size: 8.3pt; line-height: 1.33; padding-left: 4mm; position: relative; }}
.finance li::before {{ content: ""; position: absolute; left: 0; top: 1.4mm; width: 1.8mm; height: 1.8mm; border-radius: 50%; background: var(--leaf); }}
.closing .lead {{ font-size: 10pt; color: var(--mute); margin-bottom: 1.2mm; }}
.closing .statement {{ font-family: "Unbounded"; font-weight: 500; font-size: 11pt; line-height: 1.3; color: var(--pine); }}
.cta {{ display: grid; grid-template-columns: 1fr auto; gap: 6mm; align-items: end; border-top: .3mm solid var(--line); padding-top: 4mm; }}
.cta .ann p {{ font-size: 8.5pt; line-height: 1.38; }}
.cta .ann p + p {{ margin-top: 1.4mm; font-weight: 700; color: var(--pine); }}
.cta .contacts {{ margin-top: 2.6mm; display: flex; flex-wrap: wrap; gap: 1mm 6mm; font-size: 8.5pt; }}
.cta .contacts span b {{ font-weight: 600; color: var(--ink); }}
.qr {{ text-align: center; }}
.qr svg {{ width: 25mm; height: 25mm; display: block; margin: 0 auto 1.5mm; }}
.qr p {{ font-family: "Unbounded"; font-weight: 500; font-size: 8pt; color: var(--pine); line-height: 1.3; }}
.qr p small {{ display: block; font-family: "Wix Madefor Text"; font-weight: 500; font-size: 7.6pt; color: var(--mute); }}
</style></head><body>
<section class="page">
  <div class="top"><img src="{A}assets/img/logo.svg" alt="ECOES JV"><span class="url">franchise.ecoes.eu</span></div>
  <p class="kicker">{esc(t['kicker'])}</p>
  <h1>{esc(t['slogan'])}</h1>
  <figure class="hero"><img src="{img['hero']}" alt=""></figure>
  <p class="intro">{esc(t['intro'])}</p>
  <div class="products">
    <article class="prod"><div class="pic"><img src="{img['mobile']}" alt=""></div><h2>{esc(t['mobile'][0])}</h2><p>{esc(t['mobile'][1])}</p></article>
    <article class="prod"><div class="pic pic--photo"><img src="{img['box']}" alt=""></div><h2>{esc(t['box'][0])}</h2><p>{esc(t['box'][1])}</p><p class="auto">{esc(t['box_auto'])}</p></article>
  </div>
  <dl class="figs">{''.join(f'<div><dd>{esc(a)}</dd><dt>{esc(b)}</dt></div>' for a, b in t['figs'])}</dl>
</section>
<section class="page page--2">
  <div class="profit">
    <h2>{esc(t['punch'])}</h2>
    <div class="pcols">
      <div class="pcol"><p class="name">ECOES MultiCharger Mobile</p><p class="big">{num(t['mob_month'][2], lang)}<small>EUR</small></p>
        <p class="cap">{esc(mob_sentence)}</p><p class="pay">{esc(payback)}</p>{bars(t['mob_month'])}</div>
      <div class="pcol"><p class="name">ECOES MultiCharger Box</p><p class="big">{num(t['box_month'][2], lang)}<small>EUR</small></p>
        <p class="cap">{esc(box_sent)}</p><p class="pay">{esc(box_pay)}</p>{bars(t['box_month'])}</div>
    </div>
    <p class="paynote">{esc(t['pay'])}</p>
  </div>
  <div class="reasons">{''.join(f'<div><h3>{esc(h)}</h3><p>{esc(d)}</p></div>' for h, d in reasons)}</div>
  <div class="finance"><h2>{esc(t['fin_title'])}</h2><ul>{''.join(f'<li>{esc(x)}</li>' for x in t['fin'])}</ul></div>
  <div class="closing"><p class="lead">{esc(t['lead'])}</p><p class="statement">{esc(t['statement'])}</p></div>
  <div class="cta">
    <div class="ann"><p>{esc(t['ann'][0])}</p><p>{esc(t['ann'][1])}</p>
      <div class="contacts"><span><b>sales@ecoes.eu</b></span><span><b>ecoes@ecoes.eu</b></span>
        <span>{cities[0]}: {phones[0][0]} <b>{phones[0][1]}</b></span><span>{cities[1]}: {phones[1][0]} <b>{phones[1][1]}</b></span></div></div>
    <div class="qr">{qr_svg}<p>{esc(t['preorder'])}<small>franchise.ecoes.eu</small></p></div>
  </div>
</section>
</body></html>'''

if __name__ == '__main__':
    img = images()
    for lang in ('bg', 'en'):
        t = texts(lang)
        open(os.path.join(HERE, lang + '.html'), 'w', encoding='utf-8').write(page(lang, t, img))
        print('wrote', lang, '|', t['kicker'][:40], '|', t['punch'][:40], '|', len(t['why']), 'why panes')
