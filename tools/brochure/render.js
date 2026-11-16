// The two-page brochure to PDF (A4) and one PNG per page for previews, with the site served on :8765:
//   node tools/brochure/render.js <lang> <out.pdf> [png-dir]
// Reports any page whose content runs past its bottom edge.
const { chromium } = require('playwright');
(async () => {
  const [lang, out, pngDir] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 2 });
  await p.goto(`http://127.0.0.1:8765/tools/brochure/${lang}.html`, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.page')].map((pg, i) => {
    const bottom = pg.getBoundingClientRect().bottom; let worst = 0, what = '';
    for (const el of pg.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      if (r.height && r.bottom > bottom - 2 && r.bottom - bottom > worst) { worst = r.bottom - bottom; what = el.className || el.tagName; }
    }
    const sh = pg.scrollHeight - pg.clientHeight;
    return (worst > 0 || sh > 1) ? `page ${i + 1}: ${Math.round(Math.max(worst, sh))}px over (${what})` : null;
  }).filter(Boolean));
  console.log(over.length ? over.join('\n') : 'both pages fit');
  if (pngDir) {
    const pages = await p.$$('.page');
    for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: `${pngDir}/page-${i + 1}.png` });
  }
  await p.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
  console.log('pdf', out);
})();
