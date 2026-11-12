// Sonde : position du bouton « Continuer » après l'écriture en séance, sur mobile
const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
const HW = fs.readFileSync(path.join(__dirname, 'node_modules/hanzi-writer/dist/hanzi-writer.min.js'), 'utf8');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 360, height: 780 }, hasTouch: true }); const p = await ctx.newPage();
  await p.route('**/*', r => r.request().url().includes('hanzi-writer@') ? r.fulfill({ body: HW, contentType: 'application/javascript' }) : /fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.goto('file://' + path.resolve(process.argv[2] || 'index.html'));
  await p.evaluate(() => { S.onboarded = true; closeOnboarding(); seance = { steps: [{ k: 'write', t: 'Écriture', d: '', c: '人' }], back: false, i: 0, res: [] }; go('seance'); });
  await p.waitForTimeout(300);
  await p.evaluate(() => { const fb = document.querySelector('#wf'); fb.innerHTML = 'Parfait ! <button class="btn inkbtn small" id="cont">Continuer →</button>'; });
  const r = await p.evaluate(() => { const c = document.querySelector('#cont').getBoundingClientRect(); const nav = document.querySelector('#bottomnav').getBoundingClientRect(); return { contTop: c.top, contBottom: c.bottom, navTop: nav.top, docH: document.documentElement.scrollHeight, vh: innerHeight, scrollMax: document.documentElement.scrollHeight - innerHeight }; });
  console.log(r);
  await p.evaluate(() => scrollTo(0, 99999)); await p.waitForTimeout(100);
  console.log(await p.evaluate(() => { const c = document.querySelector('#cont').getBoundingClientRect(); return { contTopAfterScroll: c.top, contBottom: c.bottom, navTop: document.querySelector('#bottomnav').getBoundingClientRect().top, hit: document.elementFromPoint(c.left + 5, c.top + 5)?.id || document.elementFromPoint(c.left + 5, c.top + 5)?.className }; }));
  await b.close();
})();
