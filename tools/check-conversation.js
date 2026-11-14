// Vérifie l'écran Conversation : sans Claude (message d'explication), avec un Claude simulé (ouverture,
// réponse, correction affichée sous le message), et en cas d'erreur (le message revient dans la zone de saisie).
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
(async () => {
  const b = await chromium.launch(); let bad = 0;
  for (const mode of ['sans', 'avec', 'erreur']) {
    const p = await b.newPage({viewport: {width: 390, height: 844}}); const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
    await p.addInitScript(m => {
      localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}, level: 1}));
      if (m === 'sans') return;
      let n = 0;
      const sm = async () => ({text: ''}); sm.json = async (prompt, opts) => {
        window.__prompts = (window.__prompts || []).concat(prompt);
        n++; if (m === 'erreur' && n > 1) throw {code: 'rate_limited'};
        return n === 1 ? {zh: '你好！你叫什么名字？', pinyin: 'Nǐ hǎo! Nǐ jiào shénme míngzi?', fr: 'Bonjour ! Comment tu t\'appelles ?', correction: null}
          : {zh: '安娜，你好！', pinyin: 'Ānnà, nǐ hǎo!', fr: 'Bonjour Anna !', correction: {corrige: '我叫安娜。', explication: 'Avec 叫, pas besoin de 是.'}};
      };
      window.claude = {use: async name => name === 'sample' ? sm : null};
    }, mode);
    await p.goto(await urlFor('index.html'));
    await p.evaluate(() => go('conversation')); await p.waitForTimeout(500);
    if (mode === 'sans') {
      const t = await p.textContent('#cb'); console.log('[sans Claude]', t.includes('version claude.ai') ? 'message affiché' : 'MANQUE le message');
      if (!t.includes('version claude.ai')) bad++;
    } else {
      await p.click('#cgo'); await p.waitForSelector('#ci');
      await p.fill('#ci', '我是叫安娜。'); await p.click('#csend'); await p.waitForTimeout(400);
      if (mode === 'avec') {
        const r = await p.evaluate(() => [document.querySelectorAll('#cm .card').length, document.querySelector('.fixzh')?.textContent, window.__prompts.at(-1).includes('我是叫安娜')]);
        console.log(`[avec Claude] ${r[0]} bulles · correction : ${r[1]} · historique transmis : ${r[2]}`);
        if (r[0] !== 3 || r[1] !== '我叫安娜。' || !r[2]) bad++;
      } else {
        const r = await p.evaluate(() => [document.querySelectorAll('#cm .card').length, document.querySelector('#ci').value, document.querySelector('#cm').textContent.includes('réessaie dans une minute')]);
        console.log(`[erreur] ${r[0]} bulle · saisie conservée : « ${r[1]} » · message : ${r[2]}`);
        if (r[0] !== 1 || r[1] !== '我是叫安娜。' || !r[2]) bad++;
      }
    }
    if (errs.length) { console.log('ERREURS :', errs.join(' | ')); bad++; }
    await p.close();
  }
  await b.close(); console.log(bad ? `${bad} problème(s)` : 'aucune erreur JS'); if (bad) process.exit(1);
})();
