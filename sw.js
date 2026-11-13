// Service worker de Xué Yuán : l'appli fonctionne hors ligne une fois ouverte une première fois.
// - La page (index.html) : réseau d'abord, copie locale si hors ligne → les mises à jour arrivent dès l'ouverture.
// - Phrases, manifeste, icônes, polices, outil d'écriture : copie locale, rafraîchie en arrière-plan.
// - Tracés des caractères (gros fichiers) : copie locale dès qu'un niveau a été utilisé, ou tout télécharger depuis « Moi ».
// Changer VERSION à chaque modification de ce fichier ou de la liste ci-dessous.
const VERSION = 'xy-2026-11-13-14';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'data/sentences-hsk2.json', 'data/hsk-officiel.json', 'data/grammaire.json',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png', 'icons/favicon-32.png',
  'https://cdn.jsdelivr.net/npm/hanzi-writer@3.7.2/dist/hanzi-writer.min.js'];
const STROKES = ['data/strokes-hsk1.json', 'data/strokes-hsk2.json', 'data/strokes-hsk3.json', 'data/strokes-hsk4.json', 'data/strokes-autres.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => Promise.allSettled(CORE.map(u => c.add(u)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
// « Moi » → « Télécharger pour le hors ligne » : met tous les tracés en cache
self.addEventListener('message', e => {
  if (e.data?.type !== 'offline-all') return;
  e.waitUntil(caches.open(VERSION).then(async c => {
    let ok = 0; for (const u of STROKES) { try { if (!(await c.match(u))) await c.add(u); ok++; } catch {} }
    e.source?.postMessage({type: 'offline-all-done', ok, total: STROKES.length});
  }));
});

const fromCache = req => caches.match(req, {ignoreSearch: true});
const store = (req, res) => { if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); } return res; };

self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const same = url.origin === location.origin;
  // Page : réseau d'abord (version la plus récente), sinon la copie locale
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => store(new Request('index.html'), r)).catch(() => fromCache('index.html')));
    return;
  }
  // Tracés : copie locale d'abord (fichiers lourds et stables)
  if (same && url.pathname.includes('/data/strokes-')) {
    e.respondWith(fromCache(req).then(c => c || fetch(req).then(r => store(req, r))));
    return;
  }
  // Le reste de l'appli, les polices Google et l'outil d'écriture : copie locale, mise à jour en arrière-plan
  if (same || /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname) || url.hostname === 'cdn.jsdelivr.net') {
    e.respondWith(fromCache(req).then(c => {
      const net = fetch(req).then(r => store(req, r)).catch(() => c);
      return c || net;
    }));
  }
});
