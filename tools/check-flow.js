// Mode exercice sur mobile : barre du bas masquée, bouton Quitter, carte d'erreur visible en entier
// Usage : node tools/check-flow.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 360, height: 700 }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi-writer@|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1 })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [{ lang: 'zh-CN' }] } }); window.SpeechSynthesisUtterance = function () {}; });
  await p.goto(await urlFor(path.resolve(process.argv[2] || 'index.html')));
  const nav = () => p.evaluate(() => getComputedStyle(document.querySelector('#bottomnav')).display !== 'none');
  console.log('accueil : barre visible', await nav());
  await p.evaluate(() => { go('quiz'); }); await p.click('[data-m="level"]'); await p.waitForTimeout(200);
  console.log('quiz : barre visible', await nav(), '· bouton Quitter', !!(await p.$('#qq')));
  // mauvaises réponses jusqu'à la carte d'erreur ; « Continuer » doit être entièrement à l'écran et non masqué
  for (let k = 0; k < 6 && !(await p.$('#cont')); k++) {
    const ans = await p.evaluate(() => { const h = document.querySelector('.prompt .h')?.textContent; const w = h && WORDS.find(x => x.h === h); return w ? [w.f, w.p, w.h] : []; });
    const o = (await p.$$('.opt:not([disabled])')); let wrong = null;
    for (const x of o) { const d = await x.getAttribute('data-o'); if (!ans.includes(d)) { wrong = x; break; } }
    await (wrong || o[0]).click(); await p.waitForTimeout(1000);
  }
  await p.waitForTimeout(400);
  const r = await p.evaluate(() => { const c = document.querySelector('#cont').getBoundingClientRect(); const top = document.elementFromPoint(c.left + c.width / 2, c.top + c.height / 2); return { haut: Math.round(c.top), bas: Math.round(c.bottom), ecran: innerHeight, libre: top?.closest('#cont') != null }; });
  console.log('carte d\'erreur : « Continuer » de', r.haut, 'à', r.bas, 'px, écran', r.ecran, 'px →', r.bas <= r.ecran && r.haut >= 0 && r.libre ? 'VISIBLE ET TOUCHABLE' : 'MASQUÉ OU HORS ÉCRAN');
  const q = await p.$('#qq');
  if (q) { await q.click(); await p.waitForTimeout(200); console.log('Quitter → écran', await p.evaluate(() => current), '· barre visible', await nav()); }
  await p.evaluate(() => go('test')); await p.waitForTimeout(100);
  console.log('test de niveau : barre visible', await nav(), '· Quitter', !!(await p.$('.quit')));
  if (await p.$('.quit')) { await p.click('.quit'); console.log('Quitter le test → écran', await p.evaluate(() => current)); }
  console.log(errs.length ? 'ERREURS JS : ' + errs.join(' | ') : 'aucune erreur JS'); await b.close();
})();
