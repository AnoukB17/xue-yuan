// Audit d'accessibilité automatique (axe-core, règles WCAG 2.0 / 2.1 / 2.2 A et AA), écran par écran,
// en mobile (360 px, tactile). Le contraste est contrôlé à part par check-contrast.js (plus précis sur nos fonds teintés).
// Usage : node tools/check-a11y.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const FILE = path.resolve(process.argv[2] || 'index.html');
const AXE = fs.readFileSync(path.join(__dirname, 'node_modules/axe-core/axe.min.js'), 'utf8');
const HW = fs.readFileSync(path.join(__dirname, 'node_modules/hanzi-writer/dist/hanzi-writer.min.js'), 'utf8');
const STATES = {
  'accueil': p => p.evaluate(() => go('accueil')),
  'questionnaire': p => p.evaluate(() => onboarding(1)),
  'leçon (liste)': p => p.evaluate(() => { closeOnboarding(); lessonLevel = 2; go('lecons'); }),
  'leçon 2e': async p => { await p.evaluate(() => { current = 'lecons'; render('lecons', '2e'); }); await p.click('details summary'); },
  'leçon : découvrir': p => p.evaluate(() => { current = 'lecons'; render('lecons', '2e#0'); }),
  'quiz': p => p.evaluate(() => { current = 'quiz'; app.innerHTML = ''; runQuiz(WORDS.filter(w => w.l === 1), { title: 'Quiz', n: 5 }); }),
  'écriture': p => p.evaluate(() => go('ecriture')),
  'origines': p => p.evaluate(() => go('origines')),
  'mémo': p => p.evaluate(() => go('memo')),
  'chansons': p => p.evaluate(() => go('chansons')),
  'devinettes': p => p.evaluate(() => go('devinettes')),
  'détective': p => p.evaluate(() => go('detective')),
  'test de niveau': p => p.evaluate(() => go('test')),
  'objectifs': p => p.evaluate(() => go('objectifs')),
  'actus': p => p.evaluate(() => go('actus')),
  'dictionnaire': async p => { await p.evaluate(() => go('dico')); await p.fill('#dq', 'gare'); },
  'listes (A à Z)': async p => { await p.evaluate(() => { listMode = 'az'; go('listes'); }); await p.waitForSelector('.lgrid'); },
  'listes (thèmes)': async p => { await p.evaluate(() => { listMode = 'theme'; go('listes'); }); await p.waitForSelector('.lth'); },
  'grammaire (liste)': async p => { await p.evaluate(() => go('grammaire')); await p.waitForSelector('[data-g]'); },
  'grammaire (fiche)': async p => { await p.evaluate(() => go('grammaire', '1-le2')); await p.waitForSelector('#gq .opt'); },
  'histoires (liste)': async p => { await p.evaluate(() => go('histoires')); await p.waitForSelector('[data-st]'); },
  'histoires (lecture)': async p => { await p.evaluate(() => go('histoires', '1-journee')); await p.waitForSelector('#sq .opt'); await p.click('#st'); },
  'examen (accueil)': async p => { await p.evaluate(() => go('examen')); await p.waitForSelector('[data-run]'); },
  'examen (question)': async p => { await p.evaluate(() => go('examen', '2:court')); await p.click('#xs'); await p.waitForSelector('#xb .opt'); },
  'examen (ordre des mots)': async p => { await p.evaluate(() => go('examen', '2:court')); for (let k = 0; k < 2; k++) { await p.click('#xs'); for (let n = 0; n < 8; n++) await p.click('#xn'); } await p.click('#xs'); await p.waitForSelector('[data-i]'); },
};
(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 360, height: 780 }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' })).newPage();
  await p.route('**/*', r => r.request().url().includes('hanzi-writer@') ? r.fulfill({ body: HW, contentType: 'application/javascript' }) : /fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1 })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [] } }); window.SpeechSynthesisUtterance = function () {}; });
  await p.goto(await urlFor(FILE)); await p.addScriptTag({ content: AXE });
  const all = new Map();
  for (const [name, fn] of Object.entries(STATES)) {
    await fn(p); await p.waitForTimeout(250);
    const res = await p.evaluate(async () => (await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] }, rules: { 'color-contrast': { enabled: false } } })).violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.map(n => n.target.join(' ')).slice(0, 3), n: v.nodes.length })));
    for (const v of res) { const k = v.id; if (!all.has(k)) all.set(k, { ...v, where: new Set(), total: 0 }); const x = all.get(k); x.where.add(name); x.total += v.n; }
  }
  if (!all.size) console.log('Aucune violation WCAG A/AA détectée par axe-core.');
  for (const v of all.values()) console.log(`[${v.impact}] ${v.id} — ${v.help}\n   ${v.total} élément(s) · écrans : ${[...v.where].join(', ')}\n   ex. : ${v.nodes.join(' | ')}`);
  await b.close();
})();
