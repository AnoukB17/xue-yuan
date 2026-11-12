// Mesure les zones tactiles sur un téléphone (écran tactile, 360 px) : tout bouton, lien ou champ
// doit faire au moins 44 × 44 px (recommandation iOS ; Android : 48 dp). Usage : node tools/check-targets.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const FILE = path.resolve(process.argv[2] || 'index.html'), MIN = 44;
const HW = fs.readFileSync(path.join(__dirname, 'node_modules/hanzi-writer/dist/hanzi-writer.min.js'), 'utf8');
const VIEWS = ['accueil', 'apprendre', 'pratiquer', 'lecons', 'quiz', 'ecriture', 'origines', 'memo', 'actus', 'chansons', 'devinettes', 'detective', 'confusions', 'test', 'objectifs'];
(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 360, height: 780 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 })).newPage();
  await p.route('**/*', r => r.request().url().includes('hanzi-writer@') ? r.fulfill({ body: HW, contentType: 'application/javascript' }) : /fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1, conf: { '买|卖': 2 } })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [] } }); window.SpeechSynthesisUtterance = function () {}; });
  await p.goto(await urlFor(FILE));
  console.log('pointeur grossier (tactile) :', await p.evaluate(() => matchMedia('(pointer: coarse)').matches));
  const small = new Map();
  const scan = async name => {
    const r = await p.evaluate(MIN => [...document.querySelectorAll('button, a[href], input:not([type=hidden]), select, summary, [role="button"]')].filter(e => {
      const cs = getComputedStyle(e); if (cs.visibility === 'hidden' || cs.display === 'none' || e.closest('[hidden]')) return false;
      if (e.tagName === 'A' && e.closest('p') && cs.display === 'inline') return false; // lien dans une phrase : exception WCAG
      const r = e.getBoundingClientRect(); return r.width > 0 && (r.width < MIN - .5 || r.height < MIN - .5);
    }).map(e => { const r = e.getBoundingClientRect(); return { k: (e.className || e.tagName).toString().split(' ').slice(0, 2).join('.') || e.tagName, s: `${Math.round(r.width)}×${Math.round(r.height)}`, t: (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 18) }; }), MIN);
    r.forEach(x => { const key = x.k; if (!small.has(key)) small.set(key, { ...x, where: new Set() }); small.get(key).where.add(name); });
  };
  for (const v of VIEWS) { await p.evaluate(v => go(v), v); await p.waitForTimeout(100); await scan(v); }
  await p.evaluate(() => { current = 'lecons'; render('lecons', '1a'); }); await scan('leçon');
  await p.evaluate(() => { current = 'lecons'; render('lecons', '1a#0'); }); await scan('leçon : paquet');
  await p.evaluate(() => onboarding(1)); await scan('questionnaire'); await p.evaluate(() => closeOnboarding());
  if (!small.size) console.log('Aucune zone tactile sous 44 px.');
  else { console.log(`${small.size} type(s) d'élément sous ${MIN} px :`); for (const [k, x] of small) console.log(`  ${x.s.padEnd(8)} ${k.padEnd(26)} « ${x.t} » — ${[...x.where].slice(0, 4).join(', ')}`); }
  await b.close();
})();
