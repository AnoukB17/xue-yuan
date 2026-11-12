// Vérifie que tout le texte chinois visible est dans un élément lang="zh-CN", écran par écran.
// Usage : node tools/check-lang.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const HW = fs.readFileSync(path.join(__dirname, 'node_modules/hanzi-writer/dist/hanzi-writer.min.js'), 'utf8');
const FILE = path.resolve(process.argv[2] || 'index.html');
const VIEWS = ['accueil', 'apprendre', 'pratiquer', 'lecons', 'quiz', 'ecriture', 'origines', 'memo', 'actus', 'chansons', 'devinettes', 'detective', 'confusions', 'test', 'objectifs'];
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext()).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => r.request().url().includes('hanzi-writer@') ? r.fulfill({ body: HW, contentType: 'application/javascript' }) : /fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1 })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [] } }); window.SpeechSynthesisUtterance = function () {}; });
  await p.goto(await urlFor(FILE));
  console.log('langue de la page :', await p.evaluate(() => document.documentElement.lang));
  let total = 0;
  const check = async name => {
    const r = await p.evaluate(() => {
      const bad = [], w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (w.nextNode()) { const n = w.currentNode, el = n.parentElement; if (!/[㐀-鿿]/.test(n.data) || el.closest('script,style,svg,select,textarea,[hidden]')) continue; if (el.closest('[lang]')?.lang !== 'zh-CN') bad.push(n.data.trim().slice(0, 30)); }
      return { bad, zh: document.querySelectorAll('[lang="zh-CN"]').length };
    });
    total += r.bad.length;
    console.log(`${name.padEnd(22)} ${String(r.zh).padStart(4)} passages en chinois balisés${r.bad.length ? ` · ${r.bad.length} SANS BALISE : ${r.bad.slice(0, 4).join(' | ')}` : ''}`);
  };
  for (const v of VIEWS) { await p.evaluate(v => go(v), v); await p.waitForTimeout(120); await check(v); }
  await p.evaluate(() => { current = 'lecons'; render('lecons', '1a'); }); await check('leçon 1a');
  await p.evaluate(() => { current = 'lecons'; render('lecons', '1a#0'); }); await check('leçon 1a : découvrir');
  await p.evaluate(() => toast('Bienvenue dans Xué Yuán ! 欢迎！')); await p.waitForTimeout(50); await check('notification');
  await p.evaluate(() => onboarding(0)); await check('questionnaire');
  console.log(`\nTotal : ${total} texte(s) chinois sans lang="zh-CN"`, errs.length ? '\nERREURS JS : ' + errs.join(' | ') : '· aucune erreur JS');
  await b.close();
})();
