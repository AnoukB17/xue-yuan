// Application installable et hors ligne : manifeste et icônes, service worker, réouverture sans réseau,
// leçon et écriture hors ligne, téléchargement de tous les tracés. Usage : node tools/check-offline.js
// jsdelivr.net étant bloqué dans cet environnement (et les requêtes du service worker n'étant pas interceptables),
// le test tourne sur une copie (out/pwa-test/) où l'outil d'écriture est servi depuis le même site.
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const ROOT = path.join(__dirname, '..'), T = path.join(ROOT, 'out', 'pwa-test');
const CDN = 'https://cdn.jsdelivr.net/npm/hanzi-writer@3.7.2/dist/hanzi-writer.min.js';
fs.rmSync(T, { recursive: true, force: true }); fs.mkdirSync(path.join(T, 'vendor'), { recursive: true });
for (const d of ['data', 'icons']) fs.cpSync(path.join(ROOT, d), path.join(T, d), { recursive: true });
fs.copyFileSync(path.join(ROOT, 'manifest.webmanifest'), path.join(T, 'manifest.webmanifest'));
fs.copyFileSync(path.join(__dirname, 'node_modules/hanzi-writer/dist/hanzi-writer.min.js'), path.join(T, 'vendor/hanzi-writer.min.js'));
for (const f of ['index.html', 'sw.js']) { const s = fs.readFileSync(path.join(ROOT, f), 'utf8'); if (!s.includes(CDN)) throw new Error(`${f} : adresse de l'outil d'écriture introuvable`); fs.writeFileSync(path.join(T, f), s.split(CDN).join('vendor/hanzi-writer.min.js')); }
const drawn = p => p.evaluate(() => !!document.querySelector('#pad svg path') && !document.querySelector('#pad .muted'));
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 390, height: 844 } }); const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  await p.addInitScript(() => { if (!localStorage.getItem('hsk-jardin-v1')) localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1 })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [{ lang: 'zh-CN', name: 'Test', voiceURI: 't' }] } }); window.SpeechSynthesisUtterance = function () {}; });
  const root = (await urlFor(path.join(T, 'index.html'))).replace(/index\.html$/, '');
  await p.goto(root);
  const m = await p.evaluate(async () => { const r = await fetch(document.querySelector('link[rel=manifest]').href); const j = await r.json(); const icons = await Promise.all(j.icons.map(async i => (await fetch(i.src)).status)); return { nom: j.short_name, affichage: j.display, icones: icons.join(' '), iphone: (await fetch(document.querySelector('link[rel=apple-touch-icon]').href)).status }; });
  console.log('Manifeste :', JSON.stringify(m));
  await p.evaluate(() => navigator.serviceWorker.ready); await p.reload(); await p.waitForTimeout(500);
  console.log('Service worker : page contrôlée', await p.evaluate(() => !!navigator.serviceWorker.controller));
  await p.evaluate(() => { writeCurrent = '你'; go('ecriture'); }); await p.waitForTimeout(900);
  console.log('En ligne, écriture HSK 1 :', await drawn(p) ? 'OK' : 'ÉCHEC');
  await ctx.setOffline(true); await p.reload(); await p.waitForTimeout(700);
  console.log('Hors ligne : l\'appli s\'ouvre', !!(await p.$('#app .view')));
  await p.evaluate(() => { current = 'lecons'; render('lecons', '2a#0'); }); await p.waitForTimeout(500);
  console.log('  leçon HSK 2 avec phrase d\'exemple :', !!(await p.$('.ex')));
  await p.evaluate(() => { writeCurrent = '好'; go('ecriture'); }); await p.waitForTimeout(900);
  console.log('  écriture HSK 1 (niveau déjà utilisé) :', await drawn(p) ? 'OK' : 'ÉCHEC');
  await p.evaluate(() => { writeCurrent = '鼓'; render('ecriture'); }); await p.waitForTimeout(900);
  console.log('  écriture HSK 4 (jamais ouvert) :', await drawn(p) ? 'OK' : `message « ${await p.textContent('#toast')} »`);
  await ctx.setOffline(false);
  await p.evaluate(() => go('objectifs')); await p.waitForTimeout(200);
  await p.click('#offline-all'); await p.waitForFunction(() => S.offlineAll === true, null, { timeout: 30000 }).catch(() => {});
  console.log('« Télécharger les tracés » :', await p.evaluate(() => S.offlineAll) ? 'terminé' : 'ÉCHEC', '· bouton :', await p.textContent('#offline-all'));
  await ctx.setOffline(true); await p.reload(); await p.waitForTimeout(600);
  await p.evaluate(() => { writeCurrent = '鼓'; go('ecriture'); }); await p.waitForTimeout(900);
  console.log('Hors ligne après téléchargement, écriture HSK 4 :', await drawn(p) ? 'OK' : 'ÉCHEC');
  console.log(errs.length ? 'ERREURS JS : ' + [...new Set(errs)].join(' | ') : 'aucune erreur JS');
  await b.close();
})();
