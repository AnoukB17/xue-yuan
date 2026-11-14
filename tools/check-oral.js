// Vérifie l'écran Oral : phrases du niveau, écoute du modèle, enregistrement (micro simulé), réécoute,
// et vérification par une reconnaissance vocale simulée (score et caractères colorés).
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
(async () => {
  const b = await chromium.launch({args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream']});
  const ctx = await b.newContext({viewport: {width: 390, height: 844}, permissions: ['microphone']});
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => {
    localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}, level: 2}));
    window.SpeechRecognition = window.webkitSpeechRecognition = class { start() { setTimeout(() => { const t = document.querySelector('.prompt .han').textContent; this.onresult({results: [[{transcript: t.slice(0, -2) + '好'}]]}); this.onend(); }, 50); } };
  });
  await p.goto(await urlFor('index.html'));
  await p.evaluate(() => go('oral')); await p.waitForSelector('#om');
  console.log('phrase :', (await p.textContent('.prompt .han')).trim(), '· niveaux', await p.locator('.lvl-tabs .chip').count());
  await p.click('#or'); await p.waitForTimeout(1200); console.log('pendant :', (await p.textContent('#or')).trim());
  await p.click('#or'); await p.waitForFunction(() => !document.querySelector('#op').disabled, null, {timeout: 5000});
  console.log('après :', (await p.textContent('#os')).trim(), '· compteur', await p.evaluate(() => S.oral.n));
  await p.click('#ov'); await p.waitForSelector('#ovr p'); console.log('vérification :', (await p.textContent('#ovr .muted')).trim().slice(0, 80));
  await p.click('#on'); await p.waitForSelector('#om'); console.log('phrase suivante :', (await p.textContent('.prompt .han')).trim());
  const counts = await p.evaluate(async () => { const r = {}; for (const l of LEVELS) r[l] = (await oralSentences(l)).length; return r; });
  console.log('phrases par niveau :', JSON.stringify(counts));
  console.log(errs.length ? 'ERREURS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close(); if (errs.length || Object.values(counts).some(n => n < 10)) process.exit(1);
})();
