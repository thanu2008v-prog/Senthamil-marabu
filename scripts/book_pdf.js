// HTML → PDF (A5), பக்க எண்ணுடன். node scripts/book_pdf.js in.html out.pdf
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(inp), { waitUntil: 'load', timeout: 600000 });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({
    path: out, format: 'A5', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;text-align:center;font-size:8px;color:#555;"><span class="pageNumber"></span></div>',
    timeout: 0,
  });
  await b.close();
  console.log('PDF:', out);
})();
