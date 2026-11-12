// La voix : choix parmi les voix mandarin de l'appareil, bandeau quand il n'y en a aucune, « Je n'entends rien »
// Usage : node tools/check-voice.js [fichier.html]
const { chromium } = require('playwright'); const { urlFor } = require('./serve'); const path = require('path'); const fs = require('fs');
const FILE = path.resolve(process.argv[2] || 'index.html'), OUT = path.join(__dirname, '..', 'out', 'voix'); fs.mkdirSync(OUT, { recursive: true });
const VOICES = [
  { name: 'Tingting', lang: 'zh-CN', voiceURI: 'com.apple.voice.compact.zh-CN.Tingting', localService: true },
  { name: 'Li-mu', lang: 'zh-CN', voiceURI: 'com.apple.voice.compact.zh-CN.Li-mu', localService: true },
  { name: 'Meijia', lang: 'zh-TW', voiceURI: 'com.apple.voice.compact.zh-TW.Meijia', localService: true },
  { name: 'Sinji', lang: 'zh-HK', voiceURI: 'com.apple.voice.compact.zh-HK.Sinji', localService: true },
  { name: 'Thomas', lang: 'fr-FR', voiceURI: 'com.apple.voice.compact.fr-FR.Thomas', localService: true },
];
async function open(b, voices, state) {
  const p = await (await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, reducedMotion: 'reduce' })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi-writer@|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(([vs, st]) => {
    window.__spoken = [];
    if (st) localStorage.setItem('hsk-jardin-v1', JSON.stringify(st));
    Object.defineProperty(window, 'speechSynthesis', { value: { speak: u => window.__spoken.push(u.voice?.name || '(aucune)'), cancel() {}, getVoices: () => vs, onvoiceschanged: null } });
    window.SpeechSynthesisUtterance = function (t) { this.text = t; };
  }, [voices, state]);
  await p.goto(await urlFor(FILE)); await p.waitForTimeout(1700);
  return { p, errs };
}
(async () => {
  const b = await chromium.launch();
  { const { p, errs } = await open(b, VOICES, { onboarded: true });
    console.log('Avec voix : bandeau « pas de voix » visible :', await p.isVisible('#novoice'));
    await p.evaluate(() => go('objectifs')); await p.waitForTimeout(200);
    console.log('  voix proposées :', await p.$$eval('#vsel option', o => o.map(x => x.textContent).join(' | ')));
    await p.selectOption('#vsel', 'com.apple.voice.compact.zh-CN.Li-mu'); await p.waitForTimeout(100);
    await p.evaluate(() => speak('你好'));
    console.log('  après choix de Li-mu : voix utilisée =', await p.evaluate(() => window.__spoken.at(-1)), '· enregistrée :', await p.evaluate(() => S.voice.split('.').pop()));
    await p.locator('#voix').screenshot({ path: path.join(OUT, 'choix-voix.png') });
    console.log('  erreurs JS :', errs.length);
  }
  { const { p, errs } = await open(b, [VOICES[4]], { onboarded: true });
    console.log('Sans voix chinoise : bandeau visible :', await p.isVisible('#novoice'));
    await p.locator('#novoice').screenshot({ path: path.join(OUT, 'bandeau-sans-voix.png') });
    await p.click('#novoice-go'); await p.waitForTimeout(200);
    console.log('  « Comment l\'installer » → écran', await p.evaluate(() => current), '· aide affichée :', !!(await p.$('#voix .vhelp')));
    console.log('  erreurs JS :', errs.length);
  }
  { const { p, errs } = await open(b, [], null);
    await p.click('#onb .ch'); await p.click('#onb-next'); await p.click('#onb-next'); await p.click('#onb .ch'); await p.click('#onb-next'); await p.click('#onb .ch[data-k="zero"]'); await p.click('#onb-next');
    await p.click('#nohear'); console.log('Questionnaire, « Je n\'entends rien » :', (await p.textContent('#wfb')).slice(0, 80) + '…');
    await p.click('#nohear-next'); console.log('  → étape suivante (écriture) :', !!(await p.$('#wpad')), '· erreurs JS :', errs.length);
  }
  await b.close();
})();
