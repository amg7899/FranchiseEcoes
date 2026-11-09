// The glow of the line drawings as still pictures (2026-11-09): tools/wireframes.py writes each drawing's glow
// (the blurred copy of its lines, which does not move) to tools/glow/*-glow.svg; this renders it in Chromium,
// so it looks exactly as the SVG blur filter did, and saves assets/img/v2/*-glow.webp: one colour (the glow's)
// with the light in the alpha channel. style.css shows it as the background of the drawing's <img>, under
// the lines that draw themselves. Rendered at 0.75x the drawing's own size (the largest drawing is shown about
// 1480 CSS px wide; a blurred glow enlarges without visible loss: at most 3 levels of 255 off in 99.9 % of
// the pixels against a sharp render, 2026-11-09). Needs Playwright (pre-installed in the
// cloud sessions) and Python with Pillow. Run from the repository root after tools/wireframes.py:
//   node tools/wireglow.js
const { chromium } = require('playwright');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const SRC = path.join(__dirname, 'glow');
const OUT = path.join(__dirname, '..', 'assets', 'img', 'v2');
const SCALE = .75;

(async () => {
  const browser = await chromium.launch();
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'wireglow-'));
  for (const file of fs.readdirSync(SRC).filter(f => f.endsWith('-glow.svg'))) {
    const svg = fs.readFileSync(path.join(SRC, file), 'utf8');
    const [, w, h] = svg.match(/width="(\d+)" height="(\d+)"/).map(Number);
    const colour = svg.match(/\.glow \{[^}]*stroke: (#[0-9a-fA-F]{6})/)[1];
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: SCALE });
    await page.setContent(`<html><body style="margin:0;background:transparent">
      <img src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}" width="${w}" height="${h}" style="display:block"></body></html>`);
    await page.waitForFunction(() => document.images[0].complete);
    const png = path.join(tmp, file.replace('.svg', '.png'));
    await page.screenshot({ path: png, omitBackground: true });
    await page.close();
    const webp = path.join(OUT, file.replace('.svg', '.webp'));
    // one colour everywhere (so the lossy colour planes carry nothing), the glow in a lossless alpha channel
    execFileSync('python3', ['-I', '-c', `
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGBA')
c = tuple(int(sys.argv[3][i:i + 2], 16) for i in (1, 3, 5))
out = Image.new('RGBA', im.size, c + (0,)); out.putalpha(im.getchannel('A'))
out.save(sys.argv[2], 'WEBP', quality=90, alpha_quality=100, method=6, exact=True)
`, png, webp, colour]);
    console.log(path.relative(process.cwd(), webp), Math.round(fs.statSync(webp).size / 1024), 'KB', `${Math.round(w * SCALE)}x${Math.round(h * SCALE)}`);
  }
  await browser.close();
  fs.rmSync(tmp, { recursive: true, force: true });
})();
