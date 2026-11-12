// Vérifie que les mots d'un paquet ne reviennent pas dans le même ordre entre « Découvrir », « Reconnaître » et « Retrouver »
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext()).newPage();
  await p.route('**/*', r => /hanzi-writer@|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true })); window.__said = []; Object.defineProperty(window, 'speechSynthesis', { value: { speak: u => window.__said.push(u.text), cancel() {}, getVoices: () => [] } }); window.SpeechSynthesisUtterance = function (t) { this.text = t; }; });
  await p.goto('file://' + path.resolve('index.html'));
  let same = 0, runs = 20;
  for (let r = 0; r < runs; r++) {
    const res = await p.evaluate(() => new Promise(done => {
      const box = document.createElement('div'); document.body.append(box);
      const words = WORDS.filter(w => w.l === 1).slice(0, 5), seen = { intro: [], listen: [], produce: [] };
      const orig = window.speak; window.speak = t => {}; // pas de son
      learnFlow(box, words, { title: 't', onDone: () => { window.speak = orig; box.remove(); done(seen); } });
      const tick = () => {
        const lab = box.querySelector('.label:last-child')?.textContent || '';
        const ph = lab.startsWith('Découvrir') ? 'intro' : lab.startsWith('Reconnaître') ? 'listen' : 'produce';
        if (ph === 'intro') { seen.intro.push(box.querySelector('.prompt .h').textContent); box.querySelector('#nx').click(); }
        else if (ph === 'listen') { const w = box.querySelector('[data-say]').dataset.say; seen.listen.push(w); box.querySelector(`.opt[data-o="${w}"]`).click(); }
        else { const h = box.querySelector('.prompt .h').textContent; seen.produce.push(h); box.querySelector('#ti').value = 'x'; box.querySelector('#tf').requestSubmit(); setTimeout(() => box.querySelector('#cont')?.click(), 10); }
        if (box.isConnected) setTimeout(tick, 30);
      };
      tick();
    }));
    for (const k in res) res[k] = res[k].filter((x, j, a) => x !== a[j - 1]);
    if (res.intro.join() === res.listen.join() || res.listen.join() === res.produce.join()) same++;
    if (r < 3) console.log('exemple :', JSON.stringify(res));
  }
  console.log(`${same} série(s) sur ${runs} avec deux phases dans le même ordre`);
  await b.close();
})();
