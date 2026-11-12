// Dictionnaire et fiche d'un mot : recherches (caractères, pinyin avec ou sans tons, français), fiche, ajout aux révisions
// Usage : node tools/check-dico.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const OUT = path.join(__dirname, '..', 'out', 'dico'); fs.mkdirSync(OUT, { recursive: true });
const AXE = fs.readFileSync(path.join(__dirname, 'node_modules/axe-core/axe.min.js'), 'utf8');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, reducedMotion: 'reduce' })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 2 })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [{ lang: 'zh-CN', name: 'T', voiceURI: 't' }] } }); window.SpeechSynthesisUtterance = function () {}; });
  await p.goto(await urlFor(path.resolve(process.argv[2] || 'index.html'))); await p.waitForTimeout(400);
  await p.click('.mtop [data-nav="dico"]'); await p.waitForTimeout(200);
  console.log('Loupe de l\'en-tête → écran', await p.evaluate(() => current));
  for (const q of ['路', '你好', 'nihao', 'ni hao', 'nǐ hǎo', 'lu', 'gare', 'ecole', 'xyz']) {
    await p.fill('#dq', q); await p.waitForTimeout(80);
    const r = await p.evaluate(() => [...document.querySelectorAll('#dr .word')].slice(0, 4).map(w => w.querySelector('.h').textContent + ' ' + w.querySelector('.f').textContent.split(/[;,]/)[0]));
    console.log(`  « ${q} » → ${await p.textContent('#dn')} ${r.length ? '· ' + r.join(' | ') : ''}`);
  }
  await p.fill('#dq', 'gare'); await p.waitForTimeout(80);
  await p.screenshot({ path: path.join(OUT, 'recherche.png') });
  await p.click('#dr .word .h'); await p.waitForTimeout(200);
  console.log('Fiche ouverte :', await p.evaluate(() => document.querySelector('#wsheet').open), '·', (await p.textContent('#wsheet .tipline')).trim());
  await p.screenshot({ path: path.join(OUT, 'fiche.png') });
  const ax = await p.evaluate(async c => { eval(c); return (await axe.run(document.querySelector('#wsheet'), { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'] }, rules: { 'color-contrast': { enabled: false } } })).violations.map(v => v.id); }, AXE);
  console.log('  axe-core sur la fiche :', ax.length ? ax.join(', ') : '0 violation');
  await p.click('#ws-add'); await p.waitForTimeout(150);
  console.log('  « Ajouter à mes révisions » →', (await p.textContent('#wsheet .tipline')).trim(), '· à réviser aujourd\'hui :', await p.evaluate(() => dueWords().length));
  const other = await p.$('#wsheet .ws-others [data-word]'); if (other) { await other.click(); await p.waitForTimeout(150); console.log('  mot lié → fiche de', await p.textContent('#ws-title')); }
  await p.keyboard.press('Escape'); console.log('  Échap → fiche fermée :', !(await p.evaluate(() => document.querySelector('#wsheet').open)));
  await p.evaluate(() => { current = 'lecons'; render('lecons', '2e'); }); await p.click('details summary'); await p.click('.wordlist .word .h');
  console.log('Liste des mots d\'une leçon → fiche :', await p.textContent('#ws-title'));
  await p.keyboard.press('Escape');
  await p.evaluate(() => go('accueil')); await p.click('.b-word .big'); console.log('Mot du jour → fiche :', await p.textContent('#ws-title'));
  console.log(errs.length ? 'ERREURS JS : ' + errs.join(' | ') : 'aucune erreur JS'); await b.close();
})();
