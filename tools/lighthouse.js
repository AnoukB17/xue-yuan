// Mesure Lighthouse (mobile, réseau 4G lent simulé) d'une version de l'appli servie en local.
// Usage : node tools/lighthouse.js [dossier contenant index.html] [nom du rapport]
// Limite : dans cet environnement, jsdelivr.net est bloqué (l'outil d'écriture ne se charge pas pendant la mesure).
const { spawn } = require('child_process'); const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(process.argv[2] || path.join(__dirname, '..')), NAME = process.argv[3] || 'mesure';
const OUT = path.join(__dirname, '..', 'out', 'lighthouse'); fs.mkdirSync(OUT, { recursive: true });
const TYPES = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.js': 'application/javascript', '.webmanifest': 'application/manifest+json', '.png': 'image/png', '.svg': 'image/svg+xml' };
const server = http.createServer((req, res) => {
  let p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0])); if (p.endsWith('/')) p += 'index.html';
  if (!p.startsWith(ROOT) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  const body = fs.readFileSync(p);
  // Comme GitHub Pages : compression gzip et cache court
  const zlib = require('zlib'); const gz = zlib.gzipSync(body);
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream', 'Content-Encoding': 'gzip', 'Cache-Control': 'max-age=600' }); res.end(gz);
});
server.listen(0, '127.0.0.1', () => {
  const url = `http://127.0.0.1:${server.address().port}/`;
  const bin = path.join(__dirname, 'node_modules/.bin/lighthouse');
  // spawn (et non execFileSync) : le serveur ci-dessus doit pouvoir répondre pendant la mesure
  const lh = spawn(bin, [url, '--quiet', '--output=json', `--output-path=${path.join(OUT, NAME + '.json')}`, '--only-categories=performance,accessibility,best-practices',
    '--chrome-flags=--headless=new --no-sandbox', '--form-factor=mobile'], { env: { ...process.env, CHROME_PATH: require('playwright').chromium.executablePath() }, stdio: 'inherit' });
  lh.on('close', () => { server.close(); report(); });
});
function report() {
  const f = path.join(OUT, NAME + '.json'); if (!fs.existsSync(f)) return;
  const r = JSON.parse(fs.readFileSync(f, 'utf8')), a = r.audits, c = r.categories;
  const ms = id => a[id]?.numericValue != null ? (a[id].numericValue / 1000).toFixed(2) + ' s' : '—';
  console.log(`\n${NAME} — Performance ${Math.round(c.performance.score * 100)} · Accessibilité ${Math.round(c.accessibility.score * 100)} · Bonnes pratiques ${Math.round(c['best-practices'].score * 100)}`);
  console.log(`  FCP ${ms('first-contentful-paint')} · LCP ${ms('largest-contentful-paint')} · TBT ${Math.round(a['total-blocking-time'].numericValue)} ms · CLS ${a['cumulative-layout-shift'].numericValue.toFixed(3)} · Speed Index ${ms('speed-index')}`);
  console.log(`  Poids total ${(a['total-byte-weight'].numericValue / 1024).toFixed(0)} Ko · ${a['network-requests'].details.items.length} requêtes`);
  const fails = Object.values(a).filter(x => x.score !== null && x.score < 0.9 && x.scoreDisplayMode !== 'informative' && x.scoreDisplayMode !== 'manual' && x.scoreDisplayMode !== 'notApplicable').map(x => `${x.id} (${x.displayValue || x.score})`);
  console.log('  À améliorer :', fails.slice(0, 14).join(' · ') || 'rien');
}
