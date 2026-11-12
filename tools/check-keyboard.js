// Accessibilité au clavier et pour les lecteurs d'écran : questionnaire (dialogue, focus, page inerte),
// pinyin masqué révélable au clavier, retours juste / faux annoncés (role="status").
// Usage : node tools/check-keyboard.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext()).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi-writer@|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [{ lang: 'zh-CN' }] } }); window.SpeechSynthesisUtterance = function () {}; });
  await p.goto(await urlFor(path.resolve(process.argv[2] || 'index.html')));
  await p.waitForSelector('#onb:not([hidden])');
  console.log('Questionnaire :', await p.evaluate(() => ({ role: onb.getAttribute('role'), modal: onb.getAttribute('aria-modal'), focus: document.activeElement.tagName + ' « ' + document.activeElement.textContent.slice(0, 30) + ' »', pageInerte: document.querySelector('.shell').inert })));
  // Tab ne doit jamais sortir du questionnaire
  let out = 0; for (let k = 0; k < 25; k++) { await p.keyboard.press('Tab'); if (!(await p.evaluate(() => onb.contains(document.activeElement) || document.activeElement === document.body))) out++; }
  console.log('  25 appuis sur Tab : focus sorti du questionnaire', out, 'fois');
  await p.evaluate(() => { S.onboarded = true; closeOnboarding(); S.pinyin = 'hide'; applyPrefs(); current = 'lecons'; render('lecons', '1a'); });
  console.log('Après fermeture : page inerte', await p.evaluate(() => document.querySelector('.shell').inert));
  await p.click('details summary');
  const py = await p.$('.wordlist .pyx'); await py.focus();
  console.log('Pinyin masqué : focusable', await p.evaluate(() => document.activeElement.classList.contains('pyx')), '· rôle', await py.getAttribute('role'), '· nom', `« ${await py.getAttribute('aria-label')} »`);
  await p.keyboard.press('Enter');
  console.log('  après Entrée : révélé', await py.evaluate(e => e.classList.contains('revealed')), '· nom', `« ${await py.getAttribute('aria-label')} »`);
  await p.evaluate(() => { current = 'quiz'; app.innerHTML = ''; runQuiz(WORDS.filter(w => w.l === 1), { title: 'Quiz', n: 3, kinds: ['mean'] }); });
  await p.click('.opt'); await p.waitForTimeout(100);
  console.log('Quiz : zone de retour annoncée', await p.evaluate(() => document.querySelector('#fbk').getAttribute('role')));
  console.log(errs.length ? 'ERREURS JS : ' + errs.join(' | ') : 'aucune erreur JS'); await b.close();
})();
