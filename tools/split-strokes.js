// Migration (lot 2) : sort les tracés des caractères (STROKES, 2,75 Mo) de index.html
// et les range dans data/strokes-hsk1.json … strokes-hsk4.json + strokes-autres.json.
// Un caractère va dans le fichier du premier niveau HSK où il apparaît ; « autres » = caractères
// utilisés ailleurs (origines, devinettes, chansons). index.html garde seulement l'index (STROKE_INDEX).
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..'), FILE = path.join(ROOT, 'index.html');
const lines = fs.readFileSync(FILE, 'utf8').split('\n');
const i = lines.findIndex(l => l.startsWith('const STROKES = '));
if (i < 0) { console.log('Déjà fait : plus de STROKES dans index.html'); process.exit(0); }
const strokes = JSON.parse(lines[i].slice(lines[i].indexOf('{'), lines[i].lastIndexOf('}') + 1));
// Niveau de chaque caractère, d'après les listes de vocabulaire (RAW)
const start = lines.findIndex(l => l.startsWith('const RAW = {')), end = lines.findIndex(l => l.startsWith('const WORDS = []'));
const ctx = {}; vm.runInNewContext(lines.slice(start, end).join('\n').replace('const RAW', 'RAW') + '\nthis.RAW = RAW;', ctx);
const lvl = {};
for (const l of [1, 2, 3, 4]) for (const line of ctx.RAW[l].split('\n')) for (const c of line.split('|')[0]) if (!(c in lvl)) lvl[c] = l;
const packs = { 1: {}, 2: {}, 3: {}, 4: {}, autres: {} };
for (const [c, d] of Object.entries(strokes)) packs[lvl[c] || 'autres'][c] = d;
fs.mkdirSync(path.join(ROOT, 'data'), { recursive: true });
const index = {};
for (const [k, p] of Object.entries(packs)) {
  const name = k === 'autres' ? 'strokes-autres.json' : `strokes-hsk${k}.json`;
  fs.writeFileSync(path.join(ROOT, 'data', name), JSON.stringify(p));
  index[k] = Object.keys(p).join('');
  console.log(`${name.padEnd(22)} ${String(Object.keys(p).length).padStart(4)} caractères  ${(fs.statSync(path.join(ROOT, 'data', name)).size / 1024).toFixed(0)} Ko`);
}
lines[i] = `// Tracés des caractères : chargés à la demande depuis data/strokes-*.json (voir strokeData). Ici, seulement l'index.\nconst STROKE_INDEX = ${JSON.stringify(index)};`;
fs.writeFileSync(FILE, lines.join('\n'));
console.log(`index.html : ${(fs.statSync(FILE).size / 1024).toFixed(0)} Ko`);
