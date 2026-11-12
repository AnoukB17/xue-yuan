// Petit serveur HTTP local pour les tests : l'appli charge data/*.json avec fetch(), impossible en file://
const http = require('http'), fs = require('fs'), path = require('path');
const TYPES = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.js': 'application/javascript', '.png': 'image/png' };
let server = null;
// Renvoie l'adresse http://127.0.0.1:port/… d'un fichier du dépôt (le serveur démarre au premier appel)
async function urlFor(file) {
  const root = path.join(__dirname, '..');
  if (!server) {
    server = http.createServer((req, res) => {
      const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
      res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(res);
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r)); server.unref();
  }
  return `http://127.0.0.1:${server.address().port}/${path.relative(root, path.resolve(file)).split(path.sep).join('/')}`;
}
module.exports = { urlFor };
