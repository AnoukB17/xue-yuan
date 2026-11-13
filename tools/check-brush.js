// La police pinceau (Ma Shan Zheng) n'est chargée que pour une liste de caractères (paramètre text= dans <head>).
// Ce test parcourt tous les écrans et vérifie que chaque caractère affiché en pinceau est dans la liste.
// S'il en manque, ajouter les caractères au paramètre text= du lien id="brush-font" (encodés pour une URL).
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
(async () => {
  const b = await chromium.launch(), p = await b.newPage({viewport: {width: 1280, height: 900}});
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {reasons: ['voyage'], goal: 'hsk3'}})));
  await p.goto(await urlFor('index.html')); await p.evaluate(() => advReady);
  const allowed = await p.evaluate(() => new Set(decodeURIComponent(new URL(document.getElementById('brush-font').href).searchParams.get('text'))).size);
  const grab = () => p.evaluate(() => {
    const out = new Set(), han = /[㐀-鿿]/g, txt = decodeURIComponent(new URL(document.getElementById('brush-font').href).searchParams.get('text'));
    for (const el of document.querySelectorAll('body *')) for (const pseudo of [null, '::after', '::before']) {
      const cs = getComputedStyle(el, pseudo); if (!/Ma Shan/.test(cs.fontFamily)) continue;
      const t = pseudo ? (cs.content !== 'none' ? cs.content : '') : el.textContent;
      (t.match(han) || []).forEach(c => { if (!txt.includes(c)) out.add(c); });
    }
    return [...out];
  });
  const missing = new Set();
  for (const v of await p.evaluate(() => Object.keys(VIEWS))) { await p.evaluate(v => go(v), v); await p.waitForTimeout(200); (await grab()).forEach(c => missing.add(c)); }
  for (let st = 0; st < 6; st++) { await p.evaluate(st => onboarding(st), st); await p.waitForTimeout(100); (await grab()).forEach(c => missing.add(c)); }
  const data = await p.evaluate(() => { const txt = decodeURIComponent(new URL(document.getElementById('brush-font').href).searchParams.get('text'));
    const src = JSON.stringify(RIDDLES) + JSON.stringify(CULTURE.map(c => c.h)) + SONGS.map(s => s.t[0]).join('') + Object.values(SECTION).map(x => x[1]).join('') + '早上好下午好晚上好好！';
    return [...new Set(src.match(/[㐀-鿿]/g))].filter(c => !txt.includes(c)); });
  data.forEach(c => missing.add(c));
  console.log(`${allowed} caractères dans la police pinceau réduite`);
  console.log(missing.size ? `MANQUANTS : ${[...missing].join('')}` : 'aucun caractère pinceau manquant');
  await b.close(); if (missing.size) process.exit(1);
})();
