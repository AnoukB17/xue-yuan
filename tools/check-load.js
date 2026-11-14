// Mesure ce que la page télécharge (au démarrage, puis à l'ouverture de l'atelier d'écriture),
// et vérifie le comportement quand l'outil d'écriture (CDN) ou les tracés sont inaccessibles.
// Usage : node tools/check-load.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const FILE = path.resolve(process.argv[2] || 'index.html');
const HW = fs.readFileSync(path.join(__dirname, 'node_modules/hanzi-writer/dist/hanzi-writer.min.js'), 'utf8');
const ko = n => (n / 1024).toFixed(0) + ' Ko';
async function open(b, { cdn = true, data = true } = {}) {
  // Service worker bloqué : ses requêtes échappent à page.route, il récupérerait les fichiers que le test veut rendre inaccessibles
  const p = await (await b.newContext({ serviceWorkers: 'block' })).newPage(); const got = []; const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('response', async r => { try { const u = r.url(); if (/fonts/.test(u)) return; got.push({ u: u.split('/').pop(), n: (await r.body()).length }); } catch {} });
  await p.route('**/*', r => { const u = r.request().url();
    if (u.includes('hanzi-writer@')) return cdn ? r.fulfill({ body: HW, contentType: 'application/javascript' }) : r.abort();
    if (/fonts\./.test(u)) return r.abort();
    if (!data && /strokes-/.test(u)) return r.abort();
    return r.continue(); });
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1 })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [] } }); window.SpeechSynthesisUtterance = function () {}; });
  return { p, got, errs };
}
(async () => {
  const b = await chromium.launch();
  { const { p, got, errs } = await open(b);
    await p.goto(await urlFor(FILE)); await p.waitForTimeout(500);
    const start = got.reduce((s, x) => s + x.n, 0);
    console.log('Au démarrage :', got.map(x => `${x.u} ${ko(x.n)}`).join(', '), '→ total', ko(start));
    await p.waitForTimeout(2600); const idle = got.slice(); console.log('Après 3 s (préchargement du niveau) :', idle.filter(x => /strokes/.test(x.u)).map(x => `${x.u} ${ko(x.n)}`).join(', ') || 'rien');
    await p.evaluate(() => { writeCurrent = '学'; go('ecriture'); }); await p.waitForTimeout(800);
    const n = got.length; await p.evaluate(() => { writeCurrent = '鼓'; render('ecriture'); }); await p.waitForTimeout(800);
    console.log('Atelier : caractère HSK 4 (鼓) →', got.slice(n).map(x => `${x.u} ${ko(x.n)}`).join(', ') || 'rien de plus');
    console.log('  conseil de tracé :', await p.textContent('#wc-mn'), '| erreurs JS :', errs.length);
  }
  { const { p, errs } = await open(b, { cdn: false });
    await p.goto(await urlFor(FILE)); await p.evaluate(() => go('ecriture')); await p.waitForTimeout(300);
    console.log('\nSans l\'outil d\'écriture (CDN bloqué) : écriture →', (await p.textContent('#pad')).trim().slice(0, 60), '| erreurs JS :', errs.length);
    await p.evaluate(() => { seance = { steps: [{ k: 'write', t: 'Écriture', d: '', c: '人' }], back: false, i: 0, res: [] }; go('seance'); }); await p.waitForTimeout(200);
    await p.click('#wskip'); await p.waitForTimeout(200);
    console.log('  séance, étape d\'écriture → bouton « Passer » puis :', (await p.textContent('#wf')).trim(), '| erreurs JS :', errs.length);
  }
  { const { p, errs } = await open(b, { data: false });
    await p.goto(await urlFor(FILE)); await p.evaluate(() => go('ecriture')); await p.waitForTimeout(700);
    console.log('Sans les fichiers de tracés : message →', await p.textContent('#toast'), '| erreurs JS :', errs.length, errs.join(' | '));
    await p.evaluate(() => { seance = { steps: [{ k: 'write', t: 'Écriture', d: '', c: '人' }], back: false, i: 0, res: [] }; go('seance'); }); await p.waitForTimeout(700);
    const skip = !!(await p.$('#wskip')); if (skip) { await p.click('#wskip'); await p.waitForTimeout(200); }
    console.log('  séance, étape d\'écriture → bouton « Passer » :', skip, skip ? '→ ' + (await p.textContent('#wf')).trim() : '', '| erreurs JS :', errs.length, errs.join(' | '));
    if (!skip) process.exitCode = 1;
  }
  await b.close();
})();
