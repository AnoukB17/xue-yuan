// Vérifie l'exercice sur les changements de ton (Mémo) et l'encadré de la leçon 1a
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 360, height: 780 }, deviceScaleFactor: 2 })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi-writer@|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true })));
  await p.goto('file://' + path.resolve('index.html') + '#memo');
  await p.click('#sgo');
  let n = 0;
  for (let k = 0; k < 30; k++) {
    if (await p.$('#sbx .feedback')) break;
    const c = await p.$('#cont'); if (c) { await c.click(); continue; }
    const ans = await p.evaluate(() => { const h = document.querySelector('#sbx .prompt .h').textContent; return SANDHI.find(x => x[0] === h)[2]; });
    if (n === 2) await p.click(`#sbx .opt:not([data-o="${ans}"])`); else await p.click(`#sbx .opt[data-o="${ans}"]`);
    if (n === 2) { await p.waitForSelector('#cont'); await p.locator('#sandhi').screenshot({ path: 'out/lot1/mobile-sandhi-erreur.png' }); }
    n++; await p.waitForTimeout(1000);
  }
  console.log('résultat :', await p.textContent('#sbx .feedback'));
  await p.goto('file://' + path.resolve('index.html') + '#lecons'); await p.evaluate(() => render('lecons', '1a'));
  await p.locator('.tipbox').nth(1).screenshot({ path: 'out/lot1/mobile-lecon1a-prononciation.png' });
  await p.click('.tipbox [data-go="memo"]'); console.log('lien vers Mémo :', await p.evaluate(() => current));
  console.log(errs.length ? errs : 'aucune erreur JS'); await b.close();
})();
