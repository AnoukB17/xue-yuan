// Vocabulaire découpé : les mots des HSK 5-6 (data/vocab-avance.json) arrivent après le premier affichage.
// Vérifie : accueil affiché sans les attendre ; autre écran en attente puis rendu ; accueil mis à jour ; fichier absent = HSK 1-4 utilisables.
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
(async () => {
  const b = await chromium.launch(); let bad = 0;
  for (const mode of ['lent', 'absent']) {
    const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.addInitScript(() => localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {reasons: []}, srs: {'包括': {b: 1, s: 3, d: 5, last: 1, due: 1}}})));
    await p.route('**/*', async r => {
      const u = r.request().url();
      if (/hanzi|fonts/.test(u)) return r.abort();
      if (/vocab-avance/.test(u)) { if (mode === 'absent') return r.abort(); await new Promise(res => setTimeout(res, 1500)); }
      return r.continue();
    });
    await p.goto(await urlFor('index.html'));
    const home = await p.evaluate(() => [!!document.querySelector('#app').children.length, advLoaded, WORDS.length]);
    await p.evaluate(() => go('lecons'));
    const waiting = await p.evaluate(() => document.querySelector('#app').textContent.includes('Chargement du vocabulaire'));
    await p.waitForFunction(() => advLoaded); await p.waitForTimeout(100);
    const after = await p.evaluate(() => [WORDS.length, !!document.querySelector('.lvl-tabs'), [...document.querySelectorAll('.lvl-tabs .chip')].map(c => c.textContent).join(' '), learned().length]);
    await p.evaluate(() => go('accueil')); await p.waitForTimeout(100);
    const meters = await p.evaluate(() => document.querySelectorAll('.lvm').length);
    console.log(`[${mode}] accueil sans attendre : ${home[0]} (mots chargés : ${home[2]}, avancé prêt : ${home[1]}) · écran Leçons en attente : ${waiting} · ensuite : ${after[0]} mots, onglets ${after[2]} · mots appris reconnus : ${after[3]} · jauges accueil : ${meters} · erreurs : ${errs.length ? errs.join(' | ') : 'aucune'}`);
    if (!home[0] || errs.length || !after[1]) bad++;
    if (mode === 'lent' && (home[1] || !waiting || after[0] < 3600 || after[3] !== 1)) bad++;
    if (mode === 'absent' && after[0] !== 2024) bad++;
    await p.close();
  }
  await b.close();
  console.log(bad ? `${bad} problème(s)` : 'aucune erreur JS'); if (bad) process.exit(1);
})();
