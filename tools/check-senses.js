// Vérifie que chaque sens d'un mot à plusieurs lectures a sa propre fiche de révision,
// et qu'une progression enregistrée avec l'ancien format (clé = caractères) est conservée.
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext(); const p = await ctx.newPage();
  await p.route('**/*', r => /hanzi-writer@|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, srs: { '花': { b: 3, due: 0 }, '长': { b: 2, due: 0 } } })));
  await p.goto('file://' + path.resolve(process.argv[2] || 'index.html'));
  const r = await p.evaluate(() => {
    const multi = WORDS.filter(w => w.id.includes('#')).map(w => `${w.id} ${w.p} « ${w.f} » (HSK ${w.l})`);
    const before = dueWords().map(w => `${w.id}=${w.f}`);
    grade('花#2', true); grade('长#2', true);
    return { multi, ancienneProgressionConservee: before, apres: learned(), reviews: [W['花'].f, W['花#2'].f, W['长'].p, W['长#2'].p], caracteres: knownChars() };
  });
  console.log(JSON.stringify(r, null, 1)); await b.close();
})();
