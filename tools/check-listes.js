// Écran « Listes HSK » : niveaux, ordre de A à Z (officiel), classement par thème, entraînement par thème, fiches
// Usage : node tools/check-listes.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const OUT = path.join(__dirname, '..', 'out', 'listes'); fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, reducedMotion: 'reduce' })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1 })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [{ lang: 'zh-CN', name: 'T', voiceURI: 't' }] } }); window.SpeechSynthesisUtterance = function () {}; });
  await p.goto(await urlFor(path.resolve(process.argv[2] || 'index.html')));
  await p.evaluate(() => go('listes')); await p.waitForSelector('.lgrid');
  for (const lv of [1, 2, 4, 6]) {
    await p.click(`.lvl-tabs [data-l="${lv}"]`); await p.waitForSelector('.lgrid');
    const r = await p.evaluate(() => ({ titre: document.querySelector('#lsb .ttl').textContent, compte: document.querySelector('#lsb .muted').textContent, premiers: [...document.querySelectorAll('.lgrid .lrow')].slice(0, 5).map(x => x.querySelector('.lh').textContent).join(' ') }));
    console.log(`HSK ${lv} : ${r.titre} — ${r.compte} — premiers : ${r.premiers}`);
  }
  await p.click('.lvl-tabs [data-l="1"]'); await p.waitForSelector('.lgrid'); await p.screenshot({ path: path.join(OUT, 'a-z.png') });
  await p.click('[data-m="theme"]'); await p.waitForSelector('.lth');
  console.log('Par thème (HSK 1) :', await p.evaluate(() => [...document.querySelectorAll('.lth h2')].map(h => h.textContent.replace(/\s+/g, ' ').trim()).join(' · ')));
  await p.screenshot({ path: path.join(OUT, 'themes.png') });
  await p.click('[data-jump="nourriture"]'); await p.waitForTimeout(300); await p.screenshot({ path: path.join(OUT, 'theme-nourriture.png') });
  await p.click('#th-nourriture [data-train]'); await p.waitForSelector('.prompt');
  console.log('« S\'entraîner » (nourriture) →', await p.textContent('.quiz .label'), '· bouton Quitter', !!(await p.$('#qq')));
  await p.click('#qq'); await p.waitForSelector('.lgrid'); console.log('Quitter → retour aux listes :', await p.evaluate(() => current));
  await p.click('.lgrid .lrow .wbtn'); console.log('Mot → fiche :', await p.textContent('#ws-title'));
  console.log(errs.length ? 'ERREURS JS : ' + errs.join(' | ') : 'aucune erreur JS'); await b.close();
})();
