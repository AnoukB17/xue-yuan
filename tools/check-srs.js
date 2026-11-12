// Répétition espacée FSRS : intervalles successifs, effet d'une erreur, conversion des anciennes boîtes, plafonds
// Usage : node tools/check-srs.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, srs: { '爱': { b: 3, due: 0 }, '八': { b: 6, due: 0 } } })));
  await p.goto(await urlFor(path.resolve(process.argv[2] || 'index.html')));
  const r = await p.evaluate(() => {
    const today = dayNum(), out = {};
    // Simule une révision le jour prévu : on recule « last » de l'intervalle écoulé
    const review = (id, ok) => { const c = S.srs[id]; if (c) { const gap = c.due - c.last; c.last = today - gap; c.due = today; } grade(id, ok); return S.srs[id].due - today; };
    out.reussites = [];
    for (let k = 0; k < 7; k++) out.reussites.push(review('你', true));
    out.apresErreur = [review('你', false), review('你', true), review('你', true)];
    out.nouveauRate = [review('好', false), review('好', true), review('好', true)];
    const c = S.srs['爱']; fsrsCard(c); out.conversion = { 'boîte 3 (4 jours)': `stabilité ${c.s} j, difficulté ${c.d}` };
    out.maitrise = mastered();
    // Plafond des révisions : 400 mots en retard → 150 proposés aujourd'hui
    const ids = WORDS.slice(0, 400).map(w => w.id); ids.forEach(id => { S.srs[id] = { b: 2, s: 3, d: 5, last: today - 10, due: today - 1 }; });
    S.revDay = { day: today, n: 0 };
    out.plafondRevisions = `${dueWords().length} mots en retard → ${dueSorted().length} proposés aujourd'hui`;
    const first = dueSorted()[0]; out.premierPropose = `${first.h} (HSK ${first.l}, mémoire ${Math.round(retrievability(S.srs[first.id]) * 100)} %)`;
    S.newDay = { day: today, n: 20 }; out.seanceApres20Nouveaux = buildSeance().steps.map(s => s.t).join(', ');
    return out;
  });
  console.log('Intervalles après chaque réussite (jours) :', r.reussites.join(' → '));
  console.log('Puis une erreur et deux réussites :', r.apresErreur.join(' → '));
  console.log('Mot nouveau raté puis réussi deux fois :', r.nouveauRate.join(' → '));
  console.log('Conversion des anciennes boîtes :', JSON.stringify(r.conversion));
  console.log('Mots maîtrisés (stables ≥ 21 j) :', r.maitrise);
  console.log('Plafond :', r.plafondRevisions, '· le plus urgent :', r.premierPropose);
  console.log('Séance après 20 nouveaux mots aujourd\'hui :', r.seanceApres20Nouveaux || '(rien)');
  console.log(errs.length ? 'ERREURS JS : ' + errs.join(' | ') : 'aucune erreur JS'); await b.close();
})();
