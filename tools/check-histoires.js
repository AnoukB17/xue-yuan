// Vérifie l'écran Histoires : liste, lecture d'une histoire, traductions, vocabulaire, questions, histoire marquée comme lue.
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
(async () => {
  const b = await chromium.launch(), p = await b.newPage({viewport: {width: 390, height: 844}});
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}})); });
  await p.goto(await urlFor('index.html'));
  await p.evaluate(() => { window.speechSynthesis.speak = u => setTimeout(() => u.onend && u.onend(), 20); });
  await p.evaluate(() => go('histoires')); await p.waitForSelector('[data-st]');
  console.log('histoires listées :', await p.locator('[data-st]').count());
  await p.click('[data-st]'); await p.waitForSelector('#sq .opt');
  console.log('ouverte :', (await p.textContent('#sh')).trim(), '·', await p.locator('.lyric').count(), 'phrases ·', await p.locator('.vocab .vchip').count(), 'mots');
  const hidden = await p.locator('.lyric .fr[hidden]').count(); await p.click('#st');
  console.log('traductions : masquées', hidden, '→ visibles', await p.locator('.lyric .fr:not([hidden])').count());
  await p.click('#sr'); await p.waitForTimeout(600); console.log('bouton après lecture :', (await p.textContent('#sr')).trim());
  const data = await p.evaluate(() => loadStories());
  const st = data[1][0];
  for (let k = 0; k < st.q.length; k++) { await p.click(`#sq .opt[data-o="${st.q[k][1][0]}"]`); await p.waitForTimeout(1000); }
  console.log('résultat :', (await p.textContent('#sq p')).trim(), '· marquée', await p.evaluate(id => !!S.stories[id], st.id));
  await p.click('.vocab .vchip'); await p.waitForTimeout(300); console.log('fiche de mot ouverte :', await p.evaluate(() => document.getElementById('wsheet').open));
  console.log(errs.length ? 'ERREURS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close(); if (errs.length) process.exit(1);
})();
