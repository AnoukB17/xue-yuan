// Vérifie l'affichage de 320 à 1440 px, en portrait et en paysage : défilement horizontal,
// éléments qui débordent de l'écran, et captures dans out/responsive/.
// Usage : node tools/check-responsive.js [fichier.html] [--shots]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const FILE = path.resolve(process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : 'index.html');
const SHOTS = process.argv.includes('--shots'), OUT = path.join(__dirname, '..', 'out', 'responsive'); fs.mkdirSync(OUT, { recursive: true });
const HW = fs.readFileSync(path.join(__dirname, 'node_modules/hanzi-writer/dist/hanzi-writer.min.js'), 'utf8');
const SIZES = [['320 petit téléphone', 320, 640, true], ['360 téléphone', 360, 780, true], ['414 grand téléphone', 414, 896, true], ['téléphone paysage', 780, 360, true],
  ['768 tablette', 768, 1024, true], ['1024 tablette paysage', 1024, 768, true], ['1280 ordinateur', 1280, 800, false], ['1440 grand écran', 1440, 900, false]];
const STATES = {
  accueil: p => p.evaluate(() => go('accueil')),
  decouvrir: p => p.evaluate(() => { current = 'lecons'; render('lecons', '2e#0'); }),
  quiz: p => p.evaluate(() => { current = 'quiz'; app.innerHTML = ''; runQuiz(WORDS.filter(w => w.l === 2), { title: 'Quiz', n: 5, kinds: ['mean'] }); }),
  ecriture: p => p.evaluate(() => { writeCurrent = '路'; go('ecriture'); }),
  origines: p => p.evaluate(() => go('origines')),
  objectifs: p => p.evaluate(() => go('objectifs')),
};
(async () => {
  const b = await chromium.launch(); let problems = 0;
  for (const [label, w, h, touch] of SIZES) {
    for (const scale of [1, 1.3]) {
      if (scale !== 1 && w > 414) continue; // texte agrandi : vérifié sur téléphone
      const p = await (await b.newContext({ viewport: { width: w, height: h }, isMobile: touch && w < 900, hasTouch: touch, deviceScaleFactor: SHOTS ? 2 : 1, reducedMotion: 'reduce' })).newPage();
      const errs = []; p.on('pageerror', e => errs.push(e.message));
      await p.route('**/*', r => r.request().url().includes('hanzi-writer@') ? r.fulfill({ body: HW, contentType: 'application/javascript' }) : /fonts/.test(r.request().url()) ? r.abort() : r.continue());
      await p.addInitScript(sc => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 2, textScale: sc })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [{ lang: 'zh-CN' }] } }); window.SpeechSynthesisUtterance = function () {}; }, scale);
      await p.goto(await urlFor(FILE)); await p.waitForTimeout(400);
      for (const [name, fn] of Object.entries(STATES)) {
        await fn(p); await p.waitForTimeout(300);
        const r = await p.evaluate(() => {
          const W = document.documentElement.clientWidth, out = [];
          for (const el of document.querySelectorAll('#app *, .mtop *, .bottom *')) {
            const rc = el.getBoundingClientRect(); if (!rc.width || getComputedStyle(el).position === 'fixed') continue;
            if (rc.right > W + 1 || rc.left < -1) out.push(`${(el.className || el.tagName).toString().split(' ')[0]} (${Math.round(rc.left)}→${Math.round(rc.right)})`);
          }
          return { scroll: document.documentElement.scrollWidth > W + 1, out: [...new Set(out)].slice(0, 4) };
        });
        if (r.scroll || r.out.length) { problems++; console.log(`${label}${scale !== 1 ? ' · texte ×1,3' : ''} · ${name} : ${r.scroll ? 'DÉFILEMENT HORIZONTAL · ' : ''}${r.out.join(', ')}`); }
        if (SHOTS) await p.screenshot({ path: path.join(OUT, `${w}x${h}${scale !== 1 ? '-grand' : ''}-${name}.png`) });
      }
      if (errs.length) { problems++; console.log(`${label} : erreurs JS : ${errs.join(' | ')}`); }
      await p.close();
    }
  }
  console.log(problems ? `\n${problems} problème(s)` : 'Aucun débordement, aucun défilement horizontal, sur les 8 tailles et les 6 écrans.');
  await b.close();
})();
