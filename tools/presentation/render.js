// The presentation to PDF (and one PNG per page for previews), with the site served on :8765:
//   node tools/presentation/render.js <lang> <out.pdf> [png-dir]
// Also reports any page whose content runs past its frame (so text never hides under the footer).
const { chromium } = require('playwright');
(async () => {
  const [lang, out, pngDir] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
  await p.goto(`http://127.0.0.1:8765/tools/presentation/${lang}.html`, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.slide')].map((s, i) => {
    const foot = s.querySelector('.foot').getBoundingClientRect().top;
    let worst = 0, what = '';
    for (const el of s.querySelectorAll('.body *, .cover-text *')) {
      const r = el.getBoundingClientRect();
      if (r.width && r.bottom > foot - 4 && r.bottom - foot > worst) { worst = r.bottom - foot; what = el.className || el.tagName; }
      if (el.scrollHeight > el.clientHeight + 2 && getComputedStyle(el).overflow === 'hidden') { worst = Math.max(worst, 1); what = 'clipped ' + (el.className || el.tagName); }
    }
    return worst > 0 ? `page ${i + 1}: ${Math.round(worst)}px over (${what})` : null;
  }).filter(Boolean));
  console.log(over.length ? over.join('\n') : 'all pages fit');
  if (pngDir) {
    const n = await p.evaluate(() => document.querySelectorAll('.slide').length);
    for (let i = 0; i < n; i++) {
      const el = (await p.$$('.slide'))[i];
      await el.screenshot({ path: `${pngDir}/page-${String(i + 1).padStart(2, '0')}.png` });
    }
  }
  await p.pdf({ path: out, width: '1280px', height: '720px', printBackground: true, preferCSSPageSize: true });
  await b.close();
  console.log('pdf', out);
})();
