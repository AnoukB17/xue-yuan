// Vérifie « Tout remettre à zéro » : progression effacée, puis retour au tout début (questionnaire de bienvenue,
// test de niveau, objectifs), y compris après réouverture de l'appli.
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
const fails = [];
const check = (ok, msg) => { console.log((ok ? '✓ ' : '✗ ') + msg); if (!ok) fails.push(msg); };
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 390, height: 844}}); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { if (!sessionStorage.getItem('s')) { sessionStorage.setItem('s', 1); localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {reasons: ['voyage']}, level: 3, xp: 120, srs: {'一': {b: 3, s: 7, d: 5, last: 1, due: 2}}})); } });
  await p.goto(await urlFor('index.html') + '#objectifs'); await p.waitForSelector('#reset');
  await p.click('#reset'); await p.click('#resety');
  await p.waitForSelector('#onb:not([hidden]) .choices', {timeout: 5000}).catch(() => {});
  const st = await p.evaluate(() => ({onb: !document.querySelector('#onb').hidden, step: document.querySelector('#onb h1')?.textContent, xp: S.xp, words: Object.keys(S.srs).length, level: S.level, profile: S.profile?.reasons?.length || 0}));
  check(st.onb && /Pourquoi/.test(st.step || ''), `après la remise à zéro : questionnaire de bienvenue, première étape (« ${st.step} »)`);
  check(st.xp === 0 && st.words === 0 && st.level === null && st.profile === 0, 'progression, niveau et profil effacés');
  await p.reload(); await p.waitForSelector('#onb:not([hidden]) .choices', {timeout: 5000}).catch(() => {});
  check(await p.evaluate(() => !document.querySelector('#onb').hidden), 'à la réouverture : toujours le questionnaire, tant qu\'il n\'est pas terminé');
  check(!errs.length, errs.length ? 'ERREURS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close(); if (fails.length) process.exit(1);
})();
