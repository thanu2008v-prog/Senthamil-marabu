const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 420, height: 1600 } });
  const errs=[]; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type()==='error' && errs.push(m.text()));
  const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>' + require('fs').readFileSync(__dirname + '/noolvazhi.html','utf8') + '</body></html>';
  await p.setContent(html, { waitUntil: 'load' });
  await p.screenshot({ path: process.argv[2] + '/g.png', fullPage: true });
  await p.click('#tab-yappu'); await p.screenshot({ path: process.argv[2] + '/y.png', fullPage: true });
  console.log('errors', errs);
  await b.close();
})();
