// Mises à jour avec le service worker : après publication d'une nouvelle version, la réouverture (en ligne)
// doit afficher la nouvelle version tout de suite. À lancer après check-offline.js (utilise out/pwa-test/).
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const T = path.join(__dirname, '..', 'out', 'pwa-test'), F = path.join(T, 'index.html');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext(); const p = await ctx.newPage();
  await ctx.route(/fonts\./, r => r.abort());
  await p.addInitScript(() => localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1 })));
  const root = (await urlFor(F)).replace(/index\.html$/, '');
  await p.goto(root); await p.evaluate(() => navigator.serviceWorker.ready); await p.reload(); await p.waitForTimeout(300);
  console.log('Version 1 affichée :', await p.evaluate(() => document.title));
  const html = fs.readFileSync(F, 'utf8');
  fs.writeFileSync(F, html.replace('<title>Xué Yuán 学园</title>', '<title>Xué Yuán 学园 (v2)</title>'));
  await p.reload(); await p.waitForTimeout(300);
  console.log('Après publication, réouverture en ligne :', await p.evaluate(() => document.title));
  await ctx.setOffline(true); await p.reload(); await p.waitForTimeout(300);
  console.log('Puis hors ligne (copie locale mise à jour) :', await p.evaluate(() => document.title));
  fs.writeFileSync(F, html);
  await b.close();
})();
