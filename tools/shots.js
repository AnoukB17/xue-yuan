// Captures d'écran de quelques états clés, en clair et en sombre (mobile 360 px)
// Usage : node tools/shots.js fichier.html dossier
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const FILE = path.resolve(process.argv[2] || 'index.html'), OUT = path.resolve(process.argv[3] || 'out/shots'); fs.mkdirSync(OUT, { recursive: true });
const STATES = {
  decouvrir: p => p.evaluate(() => { current = 'lecons'; render('lecons', '1a#0'); }),
  quiz: p => p.evaluate(() => { current = 'quiz'; app.innerHTML = ''; runQuiz(WORDS.filter(w => w.l === 1), { title: 'Quiz', n: 5, kinds: ['pinyin'] }); }),
  accueil: p => p.evaluate(() => go('accueil')),
};
(async () => {
  const b = await chromium.launch();
  for (const scheme of ['light', 'dark']) {
    const p = await (await b.newContext({ viewport: { width: 360, height: 740 }, deviceScaleFactor: 2, colorScheme: scheme, reducedMotion: 'reduce' })).newPage();
    await p.route('**/*', r => /hanzi-writer@/.test(r.request().url()) ? r.abort() : r.continue());
    await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1 })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [] } }); window.SpeechSynthesisUtterance = function () {}; Math.random = (() => { let x = 7; return () => (x = (x * 9301 + 49297) % 233280) / 233280; })(); });
    await p.goto('file://' + FILE); await p.waitForTimeout(800);
    for (const [n, fn] of Object.entries(STATES)) { await fn(p); await p.waitForTimeout(400); await p.screenshot({ path: path.join(OUT, `${n}-${scheme}.png`) }); }
  }
  await b.close();
})();
