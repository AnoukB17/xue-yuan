// Vérifie l'examen blanc (version courte de chaque niveau, réponses au hasard)
// et la validation de niveau (réponses justes : les mots non vus doivent entrer dans les révisions).
const { chromium } = require('playwright');
const { urlFor } = require('./serve');

(async () => {
  const b = await chromium.launch(), p = await b.newPage({viewport: {width: 390, height: 844}});
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}})); window.__said = []; });
  await p.goto(await urlFor('index.html'));
  await p.evaluate(() => { window.speak = t => window.__said.push(t); });
  const levels = await p.evaluate(() => EXAM_LEVELS());
  console.log('niveaux proposés :', levels.join(', '));
  // Réponses : au hasard (examen) ou justes (validation)
  const play = async right => {
    for (let n = 0; n < 200; n++) {
      if (await p.$('#xs')) { await p.click('#xs'); continue; }
      if (await p.$('#xa')) return;
      if (await p.$('[data-i]')) { // ordre des mots
        while (await p.$('[data-i]:not([disabled])')) await p.click('[data-i]:not([disabled])');
        await p.click('#xv'); continue;
      }
      const target = right ? await p.evaluate(() => {
        const q = document.querySelector('#xb .prompt .q').textContent, h = document.querySelector('#xb .prompt .h')?.textContent;
        const opts = [...document.querySelectorAll('#xb .opt')].map(o => o.dataset.o);
        if (h) return opts.find(o => WORDS.some(w => w.h === h && firstSense(w) === o));
        const m = q.match(/« (.*) »/); if (m) return opts.find(o => WORDS.some(w => w.h === o && firstSense(w).toLowerCase() === m[1]));
        return opts.find(o => o === window.__said.at(-1));
      }) : null;
      if (target) await p.click(`#xb .opt[data-o="${target}"]`);
      else await p.click('#xb .opt >> nth=' + Math.floor(Math.random() * 3));
    }
    throw new Error('examen sans fin');
  };
  for (const l of levels) {
    await p.evaluate(l => go('examen', l + ':court'), l);
    await play(false);
    const r = await p.evaluate(() => [document.querySelector('#xb .h').textContent, [...document.querySelectorAll('#xb .stack .row')].map(r => r.textContent.trim()).join(' · ')]);
    console.log(`HSK ${l} version courte : ${r[0]} (${r[1]})`);
  }
  const l = levels[0];
  const before = await p.evaluate(l => WORDS.filter(w => w.l === l && S.srs[w.id]).length, l);
  await p.evaluate(l => go('examen', l + ':valider'), l);
  await play(true);
  const after = await p.evaluate(l => [WORDS.filter(w => w.l === l && S.srs[w.id]).length, WORDS.filter(w => w.l === l).length, document.querySelector('#xb .h').textContent, !!S.levelOk[l], LESSONS.filter(L => L.l === l).every(L => chunksOf(L).every((_, i) => chunkDone(L, i)))], l);
  console.log(`Validation HSK ${l} : ${after[2]} · validé ${after[3]} · mots en révision ${before} → ${after[0]} / ${after[1]} · leçons cochées ${after[4]}`);
  await p.evaluate(() => go('examen'));
  console.log('historique affiché :', await p.locator('text=Derniers essais').count() === 1);
  console.log(errs.length ? 'ERREURS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close();
  if (errs.length || !after[3]) process.exit(1);
})();
