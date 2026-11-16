// Vérifie le mode silence : bouton haut-parleur en haut de l'écran ; en mode silence, aucun mot n'est lu
// automatiquement (quiz « écoute », séance) ni aucun son de réponse joué, mais un toucher sur « Écouter » lit le mot.
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
const fails = [];
const check = (ok, msg) => { console.log((ok ? '✓ ' : '✗ ') + msg); if (!ok) fails.push(msg); };
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 360, height: 740}}); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => {
    if (!localStorage.getItem('hsk-jardin-v1')) localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}, level: 1}));
    window.__said = []; window.__beeps = 0;
    const fake = {speak: u => window.__said.push(u.text), cancel() {}, getVoices: () => [{lang: 'zh-CN', name: 'Test', voiceURI: 't'}], addEventListener() {}};
    Object.defineProperty(window, 'speechSynthesis', {value: fake});
    window.SpeechSynthesisUtterance = function (t) { this.text = t; };
    const AC = window.AudioContext; window.AudioContext = function () { const c = new AC(); const o = c.createOscillator.bind(c); c.createOscillator = () => { window.__beeps++; return o(); }; return c; };
  });
  await p.goto(await urlFor('index.html')); await p.waitForSelector('.mtop .st-snd');
  check(await p.getAttribute('.mtop .st-snd', 'aria-pressed') === 'false', 'bouton haut-parleur visible en haut, son activé par défaut');
  const quiz = () => p.evaluate(() => { current = 'quiz'; app.innerHTML = ''; runQuiz(WORDS.filter(w => w.l === 1), {title: 'Quiz', n: 5, kinds: ['listen']}); });

  await quiz(); await p.waitForTimeout(700);
  const n1 = await p.evaluate(() => __said.length);
  check(n1 > 0, `son activé : le mot est lu automatiquement (${n1})`);

  await p.click('.mtop .st-snd');
  check(await p.getAttribute('.mtop .st-snd', 'aria-pressed') === 'true' && await p.evaluate(() => S.quiet === true), 'un toucher active le mode silence (mémorisé)');
  await p.evaluate(() => { __said.length = 0; __beeps = 0; }); await quiz(); await p.waitForTimeout(700);
  check(await p.evaluate(() => __said.length) === 0, 'mode silence : rien n\'est lu automatiquement');
  await p.click('.opt'); await p.waitForTimeout(400);
  check(await p.evaluate(() => __beeps) === 0, 'mode silence : pas de son de bonne ou mauvaise réponse');
  await quiz(); await p.waitForTimeout(300); await p.click('[data-say]'); await p.waitForTimeout(200);
  check(await p.evaluate(() => __said.length) === 1, 'mode silence : toucher « Écouter » lit quand même le mot');

  await p.reload(); await p.waitForSelector('.mtop .st-snd');
  check(await p.getAttribute('.mtop .st-snd', 'aria-pressed') === 'true', 'le mode silence reste actif à la réouverture');
  await p.click('.mtop .st-snd');
  check(await p.evaluate(() => S.quiet === false), 'nouveau toucher : son réactivé');
  const box = await p.evaluate(() => { const r = document.querySelector('.mtop').getBoundingClientRect(); return [r.width, document.documentElement.scrollWidth]; });
  check(box[1] <= 360, `barre du haut sans débordement à 360 px (${box[1]} px)`);
  check(!errs.length, errs.length ? 'ERREURS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close(); if (fails.length) process.exit(1);
})();
