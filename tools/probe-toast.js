// Sonde : la notification invisible intercepte-t-elle les appuis ?
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 360, height: 780 } })).newPage();
  await p.route('**/*', r => /hanzi-writer@|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.goto('file://' + path.resolve(process.argv[2] || 'index.html'));
  await p.evaluate(() => { toast('Bienvenue dans Xué Yuán ! 欢迎！'); });
  await p.waitForTimeout(3200);
  console.log(await p.evaluate(() => { const t = document.querySelector('#toast'), r = t.getBoundingClientRect(); const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return { toast: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)], opacity: getComputedStyle(t).opacity, elementAuCentre: el.id || el.className }; }));
  await b.close();
})();
