// Vérifie l'écran Compte avec un Firebase simulé : création de compte, e-mail de vérification, connexion refusée
// tant que l'adresse n'est pas confirmée, confirmation, fusion de la progression avec celle du compte,
// sauvegarde automatique, déconnexion, et absence de l'écran dans l'artifact claude.ai.
const { chromium } = require('playwright');
const { urlFor } = require('./serve');
const fails = [];
const check = (ok, msg) => { console.log((ok ? '✓ ' : '✗ ') + msg); if (!ok) fails.push(msg); };
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({viewport: {width: 390, height: 844}, serviceWorkers: 'block'});
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p.addInitScript(() => {
    if (!localStorage.getItem('hsk-jardin-v1')) localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}, level: 1, updated: 2, xp: 5, srs: {'一': {b: 1, s: 1, d: 5, last: 100, due: 101}}}));
    window.__fbConfig = {apiKey: 'test', projectId: 'test'};
    // Firebase simulé : un compte, un document par utilisateur, journal des appels
    const M = window.__fb = {log: [], users: {}, docs: {'users/u-old': {s: JSON.stringify({updated: 1, xp: 40, srs: {'二': {b: 2, s: 3, d: 5, last: 90, due: 95}, '一': {b: 3, s: 7, d: 5, last: 80, due: 90}}}), updated: 1}}, cb: null, auth: {currentUser: null, languageCode: null}};
    const set = u => { M.auth.currentUser = u; M.cb && M.cb(u); };
    const user = (email, uid, v) => ({email, uid, emailVerified: v, getIdToken: async () => 't'});
    window.__fbLoader = async () => ({
      app: {initializeApp: c => ({c})},
      auth: {
        getAuth: () => M.auth, onAuthStateChanged: (a, cb) => { M.cb = cb; setTimeout(() => cb(M.auth.currentUser), 0); },
        createUserWithEmailAndPassword: async (a, e, pw) => { if (M.users[e]) throw {code: 'auth/email-already-in-use'}; M.users[e] = {pw, uid: 'u-new', v: false}; const u = user(e, 'u-new', false); set(u); return {user: u}; },
        sendEmailVerification: async (u, opts) => { M.log.push(['verify', u.email, opts?.url, M.auth.languageCode]); },
        signInWithEmailAndPassword: async (a, e, pw) => { const r = M.users[e]; if (!r || r.pw !== pw) throw {code: 'auth/invalid-credential'}; set(user(e, r.uid, r.v)); },
        reload: async u => { const r = M.users[u.email]; if (r) u.emailVerified = r.v; },
        signOut: async () => set(null),
        sendPasswordResetEmail: async (a, e) => M.log.push(['reset', e]),
        deleteUser: async u => { delete M.users[u.email]; set(null); },
      },
      firestore: {
        getFirestore: () => ({}), doc: (db, c, id) => c + '/' + id,
        getDoc: async k => ({exists: () => k in M.docs, data: () => M.docs[k]}),
        setDoc: async (k, v) => { M.docs[k] = v; M.log.push(['set', k]); },
        deleteDoc: async k => { delete M.docs[k]; },
      },
    });
  });
  await p.goto(await urlFor('index.html') + '#objectifs');
  await p.waitForSelector('text=Mon compte');
  check(await p.locator('[data-go="compte"]').count() === 1, '« Moi » propose le compte');
  await p.click('[data-go="compte"]'); await p.waitForSelector('#af');
  check(await p.evaluate(() => current) === 'compte', 'écran Compte ouvert');

  // Création : contrôles du formulaire
  await p.click('[data-at="signup"]'); await p.waitForSelector('#apw2');
  await p.fill('#aem', 'moi@exemple.fr'); await p.fill('#apw', 'court'); await p.fill('#apw2', 'court'); await p.click('#ago');
  check(/8 caractères/.test(await p.textContent('#as')), 'mot de passe trop court refusé');
  await p.fill('#apw', 'motdepasse1'); await p.fill('#apw2', 'motdepasse2'); await p.click('#ago');
  check(/pas identiques/.test(await p.textContent('#as')), 'confirmation différente refusée');
  await p.fill('#apw2', 'motdepasse1'); await p.click('#ago');
  await p.waitForSelector('text=Vérifie ta boîte mail');
  const vlog = await p.evaluate(() => __fb.log.find(x => x[0] === 'verify'));
  check(vlog && vlog[3] === 'fr' && /#compte$/.test(vlog[2]), 'e-mail de vérification envoyé, en français, avec retour vers l\'appli');
  check(!(await p.evaluate(() => __fb.log.some(x => x[0] === 'set'))), 'rien n\'est envoyé en ligne avant la vérification');

  // Pas encore confirmé
  await p.click('#aok'); await p.waitForFunction(() => /Pas encore/.test(document.querySelector('#as').textContent));
  check(true, '« J\'ai confirmé » sans avoir cliqué le lien : message clair');
  await p.click('#aresend'); await p.waitForFunction(() => document.querySelector('#as').textContent.trim());
  check(/Patiente/.test(await p.textContent('#as')), 'renvoi limité à un par minute');

  // Confirmation par le lien, puis fusion avec la progression du compte existant (u-old)
  await p.evaluate(() => { __fb.users['moi@exemple.fr'].v = true; __fb.users['moi@exemple.fr'].uid = 'u-old'; __fb.auth.currentUser.uid = 'u-old'; });
  await p.click('#aok'); await p.waitForSelector('text=progression synchronisée');
  const st = await p.evaluate(() => ({xp: S.xp, srs: Object.keys(S.srs).sort().join(''), one: S.srs['一'].b, doc: JSON.parse(__fb.docs['users/u-old'].s)}));
  check(st.xp === 40 && st.srs === '一二' && st.one === 1, `fusion : xp max (${st.xp}), mots des deux côtés (${st.srs}), carte la plus récente gardée`);
  check(Object.keys(st.doc.srs).length === 2, 'progression fusionnée renvoyée en ligne');

  // Sauvegarde automatique après une activité
  const n0 = await p.evaluate(() => __fb.log.filter(x => x[0] === 'set').length);
  await p.evaluate(() => { S.xp += 3; save(); });
  await p.waitForFunction(n => __fb.log.filter(x => x[0] === 'set').length > n, n0, {timeout: 8000});
  check(await p.evaluate(() => JSON.parse(__fb.docs['users/u-old'].s).xp) === 43, 'chaque sauvegarde part en ligne (après 4 s)');

  check(await p.evaluate(() => localStorage.getItem('xy-cloud') === '1'), 'session mémorisée : Firebase se recharge tout seul au prochain lancement');

  // Déconnexion, mauvais mot de passe, mot de passe oublié
  await p.evaluate(() => go('compte')); await p.waitForSelector('#af, #aout');
  if (await p.locator('#aout').count()) { await p.click('#aout'); await p.waitForSelector('#af'); }
  check(await p.evaluate(() => localStorage.getItem('xy-cloud')) === null, 'déconnexion : session oubliée, progression gardée (' + await p.evaluate(() => S.xp) + ' xp)');
  await p.fill('#aem', 'moi@exemple.fr'); await p.fill('#apw', 'faux-mot-de-passe'); await p.click('#ago');
  await p.waitForFunction(() => document.querySelector('#as').textContent.trim());
  check(/incorrect/.test(await p.textContent('#as')), 'mauvais mot de passe : message en français');
  await p.click('#aforgot'); await p.waitForFunction(() => /nouveau mot de passe/.test(document.querySelector('#as').textContent));
  check(await p.evaluate(() => __fb.log.some(x => x[0] === 'reset')), 'mot de passe oublié : e-mail envoyé');
  await p.fill('#apw', 'motdepasse1'); await p.click('#ago'); await p.waitForSelector('#aout');
  check(true, 'connexion avec le bon mot de passe');

  // Remise à zéro : l'effacement l'emporte sur la copie en ligne
  await p.evaluate(() => { S = structuredClone(DEFAULT); S.wiped = Date.now(); save(); clearTimeout(cloud.timer); return cloudPush(); });
  await p.evaluate(() => cloudPull());
  check(await p.evaluate(() => Object.keys(S.srs).length) === 0, 'remise à zéro respectée par la synchronisation');

  // Dans l'artifact claude.ai, pas de compte Xué Yuán
  const p2 = await ctx.newPage();
  await p2.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}, level: 1})); window.claude = {use: async () => null}; });
  await p2.goto(await urlFor('index.html') + '#objectifs'); await p2.waitForSelector('text=Ma progression');
  check(await p2.locator('[data-go="compte"]').count() === 0, 'artifact claude.ai : pas de bouton Compte');

  check(!errs.length, errs.length ? 'ERREURS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close(); if (fails.length) process.exit(1);
})();
