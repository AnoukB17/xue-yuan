// Mesure le contraste de chaque texte visible avec son fond réel, écran par écran, en clair et en sombre.
// Seuils WCAG AA : 4,5:1 pour le texte normal, 3:1 pour le grand texte (≥ 24 px, ou ≥ 18,66 px en gras).
// Usage : node tools/check-contrast.js [fichier.html]
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const FILE = path.resolve(process.argv[2] || 'index.html');
const HW = fs.readFileSync(path.join(__dirname, 'node_modules/hanzi-writer/dist/hanzi-writer.min.js'), 'utf8');

const SCAN = () => {
  const parse = c => {
    let m = c.match(/^rgba?\(([^)]+)\)/); if (m) { const [r, g, b, a = 1] = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return { r, g, b, a }; }
    m = c.match(/^color\(srgb ([^)]+)\)/); if (m) { const [r, g, b, a = 1] = m[1].split(/[ /]+/).filter(Boolean).map(Number); return { r: r * 255, g: g * 255, b: b * 255, a }; }
    m = c.match(/^oklab\(([^)]+)\)/); if (m) { const [L, A, B, al = 1] = m[1].split(/[ /]+/).filter(Boolean).map(Number); const l = (L + .3963377774 * A + .2158037573 * B) ** 3, mm = (L - .1055613458 * A - .0638541728 * B) ** 3, s = (L - .0894841775 * A - 1.291485548 * B) ** 3; const g = v => 255 * (v <= .0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - .055); return { r: g(4.0767416621 * l - 3.3077115913 * mm + .2309699292 * s), g: g(-1.2684380046 * l + 2.6097574011 * mm - .3413193965 * s), b: g(-.0041960863 * l - .7034186147 * mm + 1.707614701 * s), a: al }; }
    return null;
  };
  const lum = ({ r, g, b }) => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
  const blend = (top, bot) => ({ r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1 });
  const bgOf = el => { const layers = []; for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; } } let bg = { r: 255, g: 255, b: 255, a: 1 }; for (let i = layers.length - 1; i >= 0; i--) bg = blend(layers[i], bg); return bg; };
  const out = [];
  const walker = document.createTreeWalker(document.querySelector('#app') || document.body, NodeFilter.SHOW_TEXT);
  const onb = document.querySelector('#onb:not([hidden])'); const roots = onb ? [onb] : [document.querySelector('#app')];
  for (const root of roots) {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) {
      const t = w.currentNode; if (!t.textContent.trim()) continue;
      const el = t.parentElement, cs = getComputedStyle(el), r = el.getBoundingClientRect();
      if (el.closest('[aria-hidden="true"]') || !r.width || cs.visibility === 'hidden' || +cs.opacity === 0 || el.closest('[hidden]') || cs.webkitTextStroke?.startsWith('1')) continue;
      let op = 1; for (let e = el; e; e = e.parentElement) op *= +getComputedStyle(e).opacity;
      const fg0 = parse(cs.color), bg = bgOf(el); if (!fg0) continue; const fg = blend({ ...fg0, a: fg0.a * op }, bg);
      const L1 = lum(fg), L2 = lum(bg), ratio = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
      const size = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700, large = size >= 24 || (size >= 18.66 && bold);
      const min = large ? 3 : 4.5;
      if (ratio < min) out.push({ txt: t.textContent.trim().slice(0, 24), cls: (el.className || el.tagName) + ' < ' + (el.parentElement?.className || ''), ratio: +ratio.toFixed(2), min, color: cs.color, bg: `rgb(${bg.r | 0},${bg.g | 0},${bg.b | 0})` });
    }
  }
  return out;
};

const STATES = {
  'accueil': p => p.evaluate(() => go('accueil')),
  'leçon : découvrir': p => p.evaluate(() => { current = 'lecons'; render('lecons', '1a#0'); }),
  'leçon : erreur de pinyin': async p => { await p.evaluate(() => { current = 'lecons'; render('lecons', '1h#0'); }); for (let k = 0; k < 5; k++) await p.click('#nx'); for (let k = 0; k < 5; k++) { const w = await p.$eval('[data-say]', b => b.dataset.say); await p.click(`.opt[data-o="${w}"]`); await p.waitForTimeout(950); } await p.fill('#ti', 'zzz'); await p.press('#ti', 'Enter'); await p.waitForSelector('.errcard'); },
  'quiz : pinyin': p => p.evaluate(() => { current = 'quiz'; app.innerHTML = ''; runQuiz(WORDS.filter(w => w.l === 1), { title: 'Quiz', n: 5, kinds: ['pinyin'] }); }),
  'quiz : ton': p => p.evaluate(() => { current = 'quiz'; app.innerHTML = ''; runQuiz(WORDS.filter(w => w.l === 1 && w.h.length === 1 && toneOf(w.p) === 3), { title: 'Tons', n: 5, kinds: ['tone'] }); }),
  'séance : écriture': p => p.evaluate(() => { seance = { steps: [{ k: 'write', t: 'Écriture', d: '', c: '中' }], back: false, i: 0, res: [] }; go('seance'); }),
  'écriture': p => p.evaluate(() => { writeCurrent = '妈'; go('ecriture'); }),
  'test de niveau': p => p.evaluate(() => go('test')),
  'mémo': p => p.evaluate(() => go('memo')),
  'origines': p => p.evaluate(() => go('origines')),
  'détective': async p => { await p.evaluate(() => go('detective')); await p.click('#o1 .opt'); },
  'chansons': async p => { await p.evaluate(() => { songLevel = 3; go('chansons'); }); await p.evaluate(() => { document.querySelector('.kc').classList.add('on'); document.querySelector('.lyric').classList.add('on'); }); },
  'devinettes': p => p.evaluate(() => go('devinettes')),
  'confusions (duel)': p => p.evaluate(() => { S.conf['他|她'] = 0; S.conf['买|卖'] = 3; current = 'confusions'; render('confusions', '买|卖'); }),
  'objectifs': p => p.evaluate(() => go('objectifs')),
  'actus': p => p.evaluate(() => go('actus')),
  'leçons HSK 3': p => p.evaluate(() => { lessonLevel = 3; go('lecons'); }),
  'questionnaire': p => p.evaluate(() => { onboarding(0); document.querySelectorAll('#onb .ch').forEach((b, i) => i % 2 && b.click()); }),
};

(async () => {
  const b = await chromium.launch(); let total = 0;
  for (const scheme of ['light', 'dark']) {
    for (const [width, label] of [[1280, 'desktop']]) {
      const ctx = await b.newContext({ viewport: { width, height: 900 }, colorScheme: scheme, reducedMotion: 'reduce' }); const p = await ctx.newPage();
      await p.route('**/*', r => r.request().url().includes('hanzi-writer@') ? r.fulfill({ body: HW, contentType: 'application/javascript' }) : /fonts/.test(r.request().url()) ? r.abort() : r.continue());
      await p.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({ onboarded: true, level: 1, profile: { reasons: ['voyage'], goal: 'hsk2', horizon: 'libre', start: 'zero' }, srs: { '你好': { b: 2, due: 0 }, '妈妈': { b: 1, due: 0 } } })); Object.defineProperty(window, 'speechSynthesis', { value: { speak() {}, cancel() {}, getVoices: () => [] } }); window.SpeechSynthesisUtterance = function (t) { this.text = t; }; });
      await p.goto('file://' + FILE);
      for (const [name, fn] of Object.entries(STATES)) {
        try { await fn(p); await p.waitForTimeout(150); } catch (e) { console.log(`[${scheme}] ${name} : état non atteint (${e.message.split('\n')[0]})`); continue; }
        const bad = await p.evaluate(SCAN);
        const uniq = [...new Map(bad.map(x => [x.cls + x.color + x.bg, x])).values()];
        total += uniq.length;
        if (uniq.length) { console.log(`\n[${scheme}] ${name} : ${uniq.length} problème(s)`); uniq.slice(0, 12).forEach(x => console.log(`   ${x.ratio}:1 (min ${x.min}) « ${x.txt} » ${x.cls} — texte ${x.color} sur ${x.bg}`)); }
        await p.evaluate(() => { try { closeOnboarding(); } catch {} });
      }
      await ctx.close();
    }
  }
  console.log(`\nTotal : ${total} combinaison(s) texte / fond sous le seuil WCAG AA`);
  await b.close();
})();
