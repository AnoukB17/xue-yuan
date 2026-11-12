// Vérifie les unités du HSK 2 dans l'appli : liste des leçons, phrases d'exemple affichées,
// migration de l'ancienne progression (« Séries » 2-1 … 2-7) et captures mobile.
// Usage : node tools/check-hsk2.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const FILE = path.resolve(process.argv[2] || 'index.html'), OUT = path.join(__dirname, '..', 'out', 'hsk2'); fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 360, height: 780 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, reducedMotion: 'reduce' })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi-writer@|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  // Ancienne progression : la série 2-1 terminée, ses mots appris
  await p.addInitScript(() => {
    if (sessionStorage.getItem('init')) return; sessionStorage.setItem('init', 1);
    const old = '吧 白 百 帮助 报纸 比 别 宾馆 长 唱歌 出 穿 次 从 错 打篮球 大家 但是 到 得'.split(' ');
    localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 2, chunks: { '2-1': [0, 1, 2, 3] }, lessons: { '2-1': 15 }, srs: Object.fromEntries(old.map(h => [h, { b: 2, due: 99999 }])) }));
    Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [{ lang: 'zh-CN' }] } }); window.SpeechSynthesisUtterance = function () {};
  });
  await p.goto(await urlFor(FILE)); await p.waitForTimeout(600);
  const r = await p.evaluate(() => ({
    unites: LESSONS.filter(l => l.l === 2).map(l => `${l.id} ${l.t} (${l.w.split(' ').length})`),
    anciennes: Object.keys(S.chunks).filter(k => k.startsWith('2-')).length,
    paquetsFaits: Object.entries(S.chunks).filter(([k]) => /^2[a-j]$/.test(k)).map(([k, v]) => `${k}:${v.length}`).join(' '),
    revisionsConservees: Object.keys(S.srs).length,
    exemples: Object.keys(EXAMPLES).length,
  }));
  console.log('Unités HSK 2 :\n  ' + r.unites.join('\n  '));
  console.log(`Anciennes séries restantes : ${r.anciennes} · paquets comptés comme faits : ${r.paquetsFaits || 'aucun'} · mots en révision : ${r.revisionsConservees} · mots avec exemples : ${r.exemples}`);
  await p.evaluate(() => { lessonLevel = 2; go('lecons'); }); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(OUT, 'liste-hsk2.png') });
  await p.evaluate(() => { current = 'lecons'; render('lecons', '2e'); }); await p.waitForTimeout(300);
  await p.click('details summary'); await p.waitForTimeout(200);
  console.log('Leçon 2e : phrases affichées dans la liste des mots :', await p.$$eval('.wordlist .ex', e => e.length));
  await p.locator('.wordlist .word').nth(1).screenshot({ path: path.join(OUT, 'mot-avec-exemples.png') });
  await p.evaluate(() => { current = 'lecons'; render('lecons', '2e#0'); }); await p.waitForTimeout(300);
  console.log('Étape « Découvrir » : exemple affiché :', !!(await p.$('.ex mark')), '· mot surligné :', await p.$eval('.ex mark', m => m.textContent).catch(() => '—'));
  await p.screenshot({ path: path.join(OUT, 'decouvrir-exemple.png'), fullPage: true });
  console.log(errs.length ? 'ERREURS JS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close();
})();
