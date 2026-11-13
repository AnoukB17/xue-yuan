// Vérifie l'écran Grammaire : liste des fiches, une fiche, ses deux questions, la fiche marquée comme travaillée.
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
(async () => {
  const b = await chromium.launch(), p = await b.newPage({viewport: {width: 390, height: 844}});
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}})));
  await p.goto(await urlFor('index.html'));
  await p.evaluate(() => go('grammaire')); await p.waitForSelector('[data-g]');
  console.log('fiches listées :', await p.locator('.grid [data-g]').count());
  await p.click('.lvl-head [data-g]'); await p.waitForSelector('#gq .opt');
  console.log('fiche ouverte :', await p.textContent('#gh'), '·', await p.locator('.ex').count(), 'exemples');
  const data = await p.evaluate(() => loadGrammar());
  for (let k = 0; k < 2; k++) {
    const q = await p.textContent('#gq .han'), g = data[1].find(x => x.q.some(y => y[0] === q)), ans = g.q.find(y => y[0] === q)[2][0];
    await p.click(`#gq .opt[data-o="${ans}"]`); await p.waitForTimeout(1000);
  }
  console.log('résultat :', (await p.textContent('#gq p')).trim(), '· marquée', await p.evaluate(() => Object.keys(S.gram).length === 1));
  await p.click('#gn'); await p.waitForSelector('#gq .opt'); console.log('fiche suivante :', await p.textContent('#gh'));
  await p.click('#gl'); await p.waitForSelector('[data-g]'); console.log('coche dans la liste :', await p.locator('.grid .label', {hasText: '✓'}).count() === 1);
  console.log(errs.length ? 'ERREURS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close(); if (errs.length) process.exit(1);
})();
