// Vérifie « J'ai obtenu un HSK » : formulaire, équivalence ancien / nouveau HSK, contrôle de 20 mots,
// mots comptés comme connus, niveau mis à jour, diplôme affiché dans « Moi » et conservé par la fusion des comptes.
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
const fails = [];
const check = (ok, msg) => { console.log((ok ? '✓ ' : '✗ ') + msg); if (!ok) fails.push(msg); };
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 390, height: 844}}); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { if (!sessionStorage.getItem('s')) { sessionStorage.setItem('s', 1); localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}, level: 1})); } });
  await p.goto(await urlFor('index.html') + '#objectifs'); await p.waitForSelector('[data-go="diplome"]');
  check(true, '« Moi » : bouton « J\'ai obtenu un HSK »');
  await p.click('[data-go="diplome"]'); await p.waitForSelector('#dpf');
  check(await p.isDisabled('#dpgo'), 'sans niveau choisi, le contrôle ne démarre pas');
  const eq = await p.evaluate(() => [1, 2, 3, 4, 5, 6].map(l => diplomaEquiv(l, '2.0')));
  console.log('  ancien HSK 1..6 → nouveau HSK :', eq.join(', '));
  check(eq.every((x, i) => x <= i + 1) && eq.every((x, i) => !i || x >= eq[i - 1]), 'équivalence ancien → nouveau HSK : jamais au-dessus, croissante');

  // Échec au contrôle (on répond « au hasard ») : diplôme gardé, niveau retenu, mots ratés en révision
  await p.click('[data-dl="3"]'); await p.fill('#dpd', '2025-06'); await p.fill('#dps', '245'); await p.click('#dpgo');
  await p.waitForSelector('#dpz .opt');
  check(await p.locator('#dpz .opt').count() >= 2, 'contrôle lancé');
  for (let i = 0; i < 120 && !(await p.locator('.act h1').count()); i++) {
    await p.evaluate(() => { const o = [...document.querySelectorAll('#dpz .opt:not([disabled])')]; if (o.length) o[o.length - 1].click(); else { document.querySelector('#dpz #cont')?.click(); } });
    await p.waitForTimeout(120);
  }
  await p.waitForSelector('.act h1', {timeout: 15000});
  const r1 = await p.evaluate(() => ({h: document.querySelector('.act h1').textContent, lvl: S.level, dip: S.diplomas, known2: WORDS.filter(w => w.l <= 2).every(w => S.srs[w.id]), any3: WORDS.filter(w => w.l === 3).filter(w => S.srs[w.id]).length, newDay: S.newDay}));
  console.log('  résultat :', r1.h, '· niveau', r1.lvl, '· HSK3 vus', r1.any3);
  check(/HSK 3/.test(r1.h) && r1.dip.length === 1 && r1.dip[0].score === 245 && r1.dip[0].date === '2025-06', 'diplôme enregistré (niveau, date, score)');
  check(r1.lvl >= 3 && r1.known2, 'niveau mis à jour, mots des niveaux en dessous comptés comme connus');
  check(!r1.newDay || r1.newDay.n === 0, 'le contrôle ne consomme pas les nouveaux mots du jour');

  // Réussite (contrôle simulé à 18/20) : HSK 4 → niveau suivant, mots du niveau connus
  await p.evaluate(() => { window.runQuizIn = (box, words, o) => o.onDone(18, 20); go('diplome'); });
  await p.waitForSelector('#dpf'); await p.click('[data-dl="4"]'); await p.click('#dpgo'); await p.waitForSelector('.act h1');
  const r2 = await p.evaluate(() => ({lvl: S.level, known4: WORDS.filter(w => w.l <= 4).every(w => S.srs[w.id]), ok: !!S.levelOk[4], n: S.diplomas.length}));
  check(r2.lvl === 5 && r2.known4 && r2.ok && r2.n === 2, 'contrôle réussi : niveau suivant (HSK 5), HSK 1 à 4 connus, niveau validé');

  // Ancien HSK 6 : compté selon son vocabulaire
  await p.evaluate(() => go('diplome')); await p.waitForSelector('#dpf'); await p.click('[data-dl="6"]'); await p.click('[data-dv="2.0"]');
  check(/compté ici comme le/.test(await p.textContent('#dpf')), 'ancien HSK : explication de l\'équivalence affichée');

  await p.evaluate(() => go('objectifs')); await p.waitForSelector('.pill.dipl');
  check(await p.locator('.pill.dipl').count() === 2, 'diplômes affichés dans « Moi »');
  const m = await p.evaluate(() => mergeStates({updated: 1, srs: {}, diplomas: [{l: 2, v: '3.0'}]}, {updated: 2, srs: {}, diplomas: [{l: 4, v: '2.0'}]}).diplomas.length);
  check(m === 2, 'fusion des comptes : les diplômes des deux appareils sont gardés');
  check(!errs.length, errs.length ? 'ERREURS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close(); if (fails.length) process.exit(1);
})();
