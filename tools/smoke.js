// Parcours automatisés de Xué Yuán : questionnaire, séance, quiz, leçon, écriture, test de niveau.
// Usage : node tools/smoke.js [fichier.html] [dossier de sortie]
const { chromium } = require('playwright'); const { urlFor } = require('./serve');
const fs = require('fs');
const path = require('path');

const FILE = path.resolve(process.argv[2] || path.join(__dirname, '..', 'index.html'));
const OUT = path.resolve(process.argv[3] || path.join(__dirname, '..', 'out'));
fs.mkdirSync(OUT, { recursive: true });
const HW = fs.readFileSync(path.join(__dirname, 'node_modules/hanzi-writer/dist/hanzi-writer.min.js'), 'utf8');
const HWDATA = path.join(__dirname, 'node_modules/hanzi-writer-data');

async function newPage(browser, vp) {
  const ctx = await browser.newContext({ viewport: vp, hasTouch: vp.width < 600 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|ERR_/.test(m.text())) errors.push('console: ' + m.text()); });
  await page.route('**/*', route => {
    const u = route.request().url();
    if (u.includes('hanzi-writer@')) return route.fulfill({ status: 200, contentType: 'application/javascript', body: HW });
    const m = u.match(/hanzi-writer-data@[^/]+\/(.+)\.json$/);
    if (m) {
      const f = path.join(HWDATA, decodeURIComponent(m[1]) + '.json');
      return fs.existsSync(f) ? route.fulfill({ status: 200, contentType: 'application/json', body: fs.readFileSync(f) }) : route.fulfill({ status: 404, body: '' });
    }
    if (u.startsWith('file:') || u.startsWith('data:')) return route.continue();
    if (/fonts\.(googleapis|gstatic)\.com/.test(u)) return route.abort();
    return route.continue();
  });
  // Synthèse vocale factice : on note le dernier texte prononcé
  await page.addInitScript(() => {
    window.__said = [];
    const fake = { speak: u => { window.__said.push(u.text); setTimeout(() => u.onend && u.onend(), 5); }, cancel() {}, getVoices: () => [{ lang: 'zh-CN', name: 'Test' }], onvoiceschanged: null };
    Object.defineProperty(window, 'speechSynthesis', { value: fake, configurable: true });
    window.SpeechSynthesisUtterance = function (t) { this.text = t; };
  });
  return { ctx, page, errors };
}

// Trace un caractère dans le premier pad visible en suivant les médianes de ses traits
async function drawChar(page, ch) {
  const data = await page.evaluate(async c => {
    try { if (typeof STROKES !== 'undefined' && STROKES[c]) return STROKES[c]; } catch {}
    try { if (typeof strokeData === 'function') return await strokeData(c); } catch {}
    return null;
  }, ch);
  if (!data) return false;
  const svg = await page.$('.pad .target svg, .pad svg:not(.grid-bg)');
  if (!svg) return false;
  await svg.evaluate(e => e.scrollIntoView({ block: 'center' })); await page.waitForTimeout(100);
  const box = await svg.boundingBox();
  const size = box.width, pad = 14, scale = (size - 2 * pad) / 1024;
  for (const med of data.medians) {
    const pts = med.map(([x, y]) => [box.x + pad + x * scale, box.y + pad + (900 - y) * scale]);
    await page.mouse.move(pts[0][0], pts[0][1]);
    await page.mouse.down();
    for (let i = 1; i < pts.length; i++) {
      const [a, b] = [pts[i - 1], pts[i]];
      const n = Math.max(4, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / 4)); for (let k = 1; k <= n; k++) await page.mouse.move(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n);
    }
    await page.mouse.up();
    await page.waitForTimeout(120);
  }
  return true;
}

const click = async (page, sel) => { const el = await page.$(sel); if (!el) return false; await el.click(); return true; };
const visible = async (page, sel) => !!(await page.$(sel)) && await page.isVisible(sel);

async function onboarding(page, log) {
  await page.waitForSelector('#onb:not([hidden]) .ch');
  await page.click('#onb .ch'); await page.click('#onb-next');            // raisons
  await page.click('#onb-next');                                           // temps
  await page.click('#onb .ch'); await page.click('#onb-next');            // but
  await page.click('#onb .ch[data-k="zero"]'); await page.click('#onb-next'); // niveau
  await page.waitForSelector('#win .opt');
  await page.click('#win .opt[data-o="你好"]');
  await page.waitForSelector('#wpad .pad', { timeout: 4000 });
  await page.waitForTimeout(400);
  await drawChar(page, '人');
  await page.waitForSelector('#onb-next:not([disabled])', { timeout: 5000 });
  await page.click('#onb-next');                                           // plan
  await page.waitForTimeout(200);
  await page.click('#onb-next');                                           // c'est parti
  await page.waitForSelector('#onb', { state: 'hidden' });
  log.push('questionnaire : OK');
}

async function answerAny(page) {
  // Répond à l'écran affiché, quel qu'il soit. Renvoie false si rien à faire.
  if (await visible(page, '#cont')) { await page.click('#cont'); return true; }
  if (await visible(page, '#nx')) { await page.click('#nx'); return true; }
  if (await visible(page, '#ti:not([disabled])')) {
    const h = await page.textContent('.prompt .h');
    const p = await page.evaluate(h => { const w = WORDS.find(x => x.h === h.trim()); return w ? w.p : 'x'; }, h);
    await page.fill('#ti', p); await page.press('#ti', 'Enter'); await page.waitForTimeout(950); return true;
  }
  const opts = await page.$$('.opt:not([disabled])');
  if (opts.length) {
    const said = await page.evaluate(() => window.__said[window.__said.length - 1]);
    const right = said && await page.$(`.opt:not([disabled])[data-o="${said}"]`);
    await (right || opts[0]).click(); await page.waitForTimeout(950); return true;
  }
  if (await visible(page, '.pad')) { const c = await page.evaluate(() => (typeof seance !== 'undefined' && seance?.steps?.[seance.i]?.c) || null); if (c && await drawChar(page, c)) { await page.waitForTimeout(500); return true; } }
  if (await visible(page, '#dgo')) { await page.click('#dgo'); return true; }
  return false;
}

async function seanceRun(page, log) {
  await page.evaluate(() => go('seance'));
  for (let k = 0; k < 120; k++) {
    if (await page.$('text=Séance terminée')) { log.push(`séance : OK (${k} actions)`); return; }
    if (!(await answerAny(page))) { await page.waitForTimeout(300); if (!(await answerAny(page))) break; }
  }
  log.push('séance : NON TERMINÉE');
}

async function quizRun(page, log) {
  await page.evaluate(() => go('quiz'));
  await page.click('[data-m="level"]');
  for (let k = 0; k < 40; k++) { if (await page.$('text=terminé')) { log.push('quiz : OK'); return; } await answerAny(page) || await page.waitForTimeout(300); }
  log.push('quiz : NON TERMINÉ');
}

async function lessonRun(page, log, id) {
  await page.evaluate(id => { current = 'lecons'; render('lecons', id + '#0'); }, id);
  for (let k = 0; k < 40; k++) { if (await page.$('text=terminé')) { log.push(`leçon ${id} paquet 1 : OK`); return; } await answerAny(page) || await page.waitForTimeout(300); }
  log.push(`leçon ${id} : NON TERMINÉE`);
}

async function writeRun(page, log) {
  await page.evaluate(() => go('ecriture'));
  await page.waitForSelector('#pad svg');
  await page.click('#w-quiz');
  const c = await page.evaluate(() => writeCurrent);
  await drawChar(page, c); await page.waitForTimeout(600);
  const fb = await page.textContent('#w-fb');
  log.push(`écriture ${c} : ${/Parfait|Réussi|mémoire/.test(fb) ? 'OK' : 'ÉCHEC'} (« ${fb.trim()} »)`);
}

async function testRun(page, log) {
  await page.evaluate(() => go('test'));
  for (let k = 0; k < 30; k++) {
    if (await page.$('text=Résultat')) { log.push('test de niveau : OK'); return; }
    const o = await page.$('.opt:not([disabled])'); if (o) { await o.click(); await page.waitForTimeout(750); } else await page.waitForTimeout(300);
  }
  log.push('test de niveau : NON TERMINÉ');
}

(async () => {
  const browser = await chromium.launch();
  const report = {};
  for (const [name, vp] of [['mobile', { width: 360, height: 780 }], ['desktop', { width: 1280, height: 800 }]]) {
    const { ctx, page, errors } = await newPage(browser, vp);
    const log = [];
    const t0 = Date.now();
    await page.goto(await urlFor(FILE));
    log.push(`chargement : ${Date.now() - t0} ms`);
    try {
      await onboarding(page, log);
      await page.screenshot({ path: path.join(OUT, `${name}-accueil.png`), fullPage: true });
      await seanceRun(page, log);
      await quizRun(page, log);
      await lessonRun(page, log, await page.evaluate(() => LESSONS.find(l => l.l === 3).id));
      await writeRun(page, log);
      await page.screenshot({ path: path.join(OUT, `${name}-ecriture.png`) });
      await testRun(page, log);
      for (const v of ['apprendre', 'pratiquer', 'origines', 'memo', 'chansons', 'devinettes', 'confusions', 'detective', 'actus', 'objectifs', 'lecons']) {
        await page.evaluate(v => go(v), v); await page.waitForTimeout(80);
        const ok = await page.$('#app .view'); if (!ok) log.push(`vue ${v} : VIDE`);
      }
      log.push('toutes les vues : rendues');
      const st = await page.evaluate(() => ({ appris: learned().length, caracteres: knownChars() }));
      log.push(`progression : ${st.appris} mots, ${st.caracteres} caractères`);
    } catch (e) { log.push('ERREUR DU SCRIPT : ' + e.message.split('\n')[0]); await page.screenshot({ path: path.join(OUT, `${name}-erreur.png`) }); }
    report[name] = { log, errors };
    await ctx.close();
  }
  await browser.close();
  for (const [n, r] of Object.entries(report)) {
    console.log(`\n== ${n} ==`); r.log.forEach(l => console.log('  ' + l));
    console.log(r.errors.length ? '  ERREURS JS :\n    ' + [...new Set(r.errors)].join('\n    ') : '  aucune erreur JS');
  }
})();
