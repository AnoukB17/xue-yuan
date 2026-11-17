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
        signInWithEmailAndPassword: async (a, e, pw) => { const r = M.users[e]; if (!r) throw {code: 'auth/user-not-found'}; if (r.pw !== pw) throw {code: 'auth/wrong-password'}; set(user(e, r.uid, r.v)); },
        reload: async u => { const r = M.users[u.email]; if (r) u.emailVerified = r.v; },
        signOut: async () => set(null),
        sendPasswordResetEmail: async (a, e) => M.log.push(['reset', e]),
        deleteUser: async u => { delete M.users[u.email]; set(null); },
      },
      firestore: {
        getFirestore: () => ({}), doc: (db, ...p) => p.join('/'), collection: (db, ...p) => p.join('/'),
        getDoc: async k => ({exists: () => k in M.docs, data: () => M.docs[k]}),
        setDoc: async (k, v) => { M.docs[k] = v; M.log.push(['set', k]); const cb = (M.subs || {})[k]; if (cb) setTimeout(() => cb({metadata: {hasPendingWrites: false}, exists: () => true, data: () => M.docs[k]}), 0); },
        deleteDoc: async k => { delete M.docs[k]; },
        getDocs: async c => ({docs: Object.keys(M.docs).filter(k => k.startsWith(c + '/') && !k.slice(c.length + 1).includes('/')).map(k => ({id: k.slice(c.length + 1), data: () => M.docs[k]}))}),
        onSnapshot: (k, cb) => { (M.subs = M.subs || {})[k] = cb; return () => { delete M.subs[k]; }; },
      },
    });
  });
  await p.goto(await urlFor('index.html') + '#objectifs');

  // Écran d'accueil : se connecter ou créer un compte avant d'entrer
  await p.waitForSelector('#onb #gab #af');
  check(await p.locator('#onb h1').textContent() === 'Bienvenue !', 'à l\'ouverture : écran de connexion / création de compte');
  await p.fill('#aem', 'personne@exemple.fr'); await p.fill('#apw', 'motdepasse99'); await p.click('#ago');
  await p.waitForFunction(() => document.querySelector('#as').textContent.trim());
  check(/Aucun compte/.test(await p.textContent('#as')), 'adresse sans compte : « Aucun compte n\'existe avec cette adresse »');
  await p.click('text=Créer un compte avec cette adresse'); await p.waitForSelector('#apw2');
  check(await p.inputValue('#aem') === 'personne@exemple.fr', 'bascule vers la création, adresse conservée');
  check(await p.getAttribute('#apw', 'type') === 'password', 'mot de passe masqué par défaut');
  await p.click('[data-eye="apw"]');
  check(await p.getAttribute('#apw', 'type') === 'text' && await p.getAttribute('[data-eye="apw"]', 'aria-label') === 'Masquer le mot de passe', 'œil : affiche le mot de passe');
  await p.click('[data-eye="apw"]');
  check(await p.getAttribute('#apw', 'type') === 'password', 'œil barré : masque à nouveau');
  const lv = async pw => { await p.fill('#apw', pw); return (await p.textContent('#apm .pwlab')).replace('Robustesse : ', '') + ' (' + await p.locator('#apm .pwbar i.on').count() + '/4)'; };
  const levels = [await lv('abc'), await lv('azerty123'), await lv('chatnoir'), await lv('Chatnoir42'), await lv('Chat-noir-2026'), await lv('Le chat noir dort, 42 !')];
  console.log('  jauge :', levels.join(' · '));
  check(/Trop court/.test(levels[0]) && /Faible/.test(levels[1]) && /Robuste/.test(levels[5]) && levels.map(x => +x.match(/\((\d)/)[1]).every((n, i, a) => !i || n >= a[i - 1] || i === 2), 'jauge de robustesse : de « Trop court » à « Robuste »');
  await p.click('#gskip'); await p.waitForSelector('text=Mon compte');
  check(await p.evaluate(() => localStorage.getItem('xy-no-account')) === '1' && await p.locator('#onb').isHidden(), '« Continuer sans compte » : l\'appli s\'ouvre, choix mémorisé');
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
  await p.click('#aok'); await p.waitForSelector('text=synchronisée en direct');
  const st = await p.evaluate(() => ({xp: S.xp, srs: Object.keys(S.srs).sort().join(''), one: S.srs['一'].b, doc: JSON.parse(__fb.docs['users/u-old'].s)}));
  check(st.xp === 40 && st.srs === '一二' && st.one === 1, `fusion : xp max (${st.xp}), mots des deux côtés (${st.srs}), carte la plus récente gardée`);
  check(Object.keys(st.doc.srs).length === 2, 'progression fusionnée renvoyée en ligne');

  // Point de restauration du jour : la progression en ligne d'avant la fusion
  const bk = await p.evaluate(() => Object.keys(__fb.docs).filter(k => k.startsWith('users/u-old/backups/')));
  check(bk.length === 1 && await p.evaluate(k => JSON.parse(__fb.docs[k].s).xp, bk[0]) === 40, 'point de restauration du jour créé (progression en ligne d\'avant)');

  // Synchronisation en direct : un autre appareil sauvegarde, la progression arrive ici sans rien toucher
  await p.evaluate(() => { const k = 'users/u-old', st = JSON.parse(__fb.docs[k].s); st.srs['四'] = {b: 1, s: 1, d: 5, last: 999999, due: 999999}; st.xp = 55; st.updated = Date.now() + 1000; __fb.docs[k] = {s: JSON.stringify(st), updated: st.updated}; __fb.subs[k]({metadata: {hasPendingWrites: false}, exists: () => true, data: () => __fb.docs[k]}); });
  await p.waitForFunction(() => !!S.srs['四'], null, {timeout: 3000}).catch(() => {});
  check(await p.evaluate(() => !!S.srs['四'] && S.xp === 55 && !!S.srs['二']), 'en direct : révisions de l\'autre appareil reçues et fusionnées');
  const nSet = await p.evaluate(() => __fb.log.filter(x => x[0] === 'set' && x[1] === 'users/u-old').length);
  await p.waitForTimeout(5000);
  check(await p.evaluate(n => __fb.log.filter(x => x[0] === 'set' && x[1] === 'users/u-old').length - n, nSet) <= 1, 'pas de boucle de sauvegardes entre appareils');

  // Sauvegarde automatique après une activité
  const n0 = await p.evaluate(() => __fb.log.filter(x => x[0] === 'set').length);
  await p.evaluate(() => { S.xp += 3; save(); });
  await p.waitForFunction(n => __fb.log.filter(x => x[0] === 'set').length > n, n0, {timeout: 8000});
  check(await p.evaluate(() => JSON.parse(__fb.docs['users/u-old'].s).xp === S.xp), 'chaque sauvegarde part en ligne (après 4 s)');

  check(await p.evaluate(() => localStorage.getItem('xy-cloud') === '1'), 'session mémorisée : Firebase se recharge tout seul au prochain lancement');

  // Restaurer un point de restauration (et l'état actuel est gardé avant)
  await p.evaluate(() => go('compte')); await p.waitForSelector('#arest');
  await p.click('#arest summary'); await p.waitForSelector('[data-rb]');
  p.once('dialog', d => d.accept()); await p.click('[data-rb="0"]');
  await p.waitForFunction(() => S.xp === 40, null, {timeout: 5000}).catch(() => {});
  const rs = await p.evaluate(() => ({xp: S.xp, four: !!S.srs['四'], cloud: JSON.parse(__fb.docs['users/u-old'].s).xp, kept: Object.keys(__fb.docs).filter(k => k.includes('/backups/') && k.includes('~')).length}));
  check(rs.xp === 40 && !rs.four && rs.cloud === 40 && rs.kept === 1, `restauration : progression d'avant remise (xp ${rs.xp}), envoyée en ligne, état précédent gardé (${rs.kept})`);
  await p.evaluate(() => { S.xp = 43; save(); }); await p.waitForTimeout(4500);

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

  // Nouvel appareil : connexion depuis l'écran d'accueil, qui se ferme et ouvre l'appli avec la progression du compte
  const ctx3 = await b.newContext({viewport: {width: 390, height: 844}, serviceWorkers: 'block'});
  await ctx3.addInitScript(() => { if (!sessionStorage.getItem('seeded')) { sessionStorage.setItem('seeded', 1); localStorage.clear(); } });
  const p3 = await ctx3.newPage(); p3.on('pageerror', e => errs.push(e.message));
  await p3.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  await p3.addInitScript(() => {
    window.__fbConfig = {apiKey: 'test'};
    const M = window.__fb = {docs: {'users/u9': {s: JSON.stringify({updated: 9, onboarded: true, profile: {}, level: 2, xp: 77, srs: {'三': {b: 2, s: 3, d: 5, last: 90, due: 95}}}), updated: 9}}, cb: null, auth: {currentUser: null}};
    const set = u => { M.auth.currentUser = u; M.cb && M.cb(u); };
    window.__fbLoader = async () => ({app: {initializeApp: () => ({})},
      auth: {getAuth: () => M.auth, onAuthStateChanged: (a, cb) => { M.cb = cb; setTimeout(() => cb(M.auth.currentUser), 0); }, reload: async () => {},
        signInWithEmailAndPassword: async (a, e, pw) => { if (pw !== 'bonmotdepasse') throw {code: 'auth/wrong-password'}; set({email: e, uid: 'u9', emailVerified: true, getIdToken: async () => 't'}); }},
      firestore: {getFirestore: () => ({}), doc: (d, c, id) => c + '/' + id, getDoc: async k => ({exists: () => k in M.docs, data: () => M.docs[k]}), setDoc: async (k, v) => { M.docs[k] = v; }}});
  });
  await p3.goto(await urlFor('index.html')); await p3.waitForSelector('#onb #af');
  await p3.fill('#aem', 'moi@exemple.fr'); await p3.fill('#apw', 'mauvais'); await p3.click('#ago');
  await p3.waitForFunction(() => document.querySelector('#as').textContent.trim());
  check(/Mot de passe incorrect/.test(await p3.textContent('#as')), 'mauvais mot de passe (compte existant) : « Mot de passe incorrect »');
  await p3.fill('#apw', 'bonmotdepasse'); await p3.click('#ago');
  await p3.waitForFunction(() => document.querySelector('#onb').hidden && current === 'accueil', null, {timeout: 8000});
  check(await p3.evaluate(() => S.xp === 77 && !!S.srs['三']), 'connexion depuis l\'accueil : écran fermé, progression du compte récupérée, pas de questionnaire');
  await ctx3.close();

  // Liens des e-mails : page d'action de l'appli (confirmation d'adresse, nouveau mot de passe)
  const ctx4 = await b.newContext({viewport: {width: 390, height: 844}, serviceWorkers: 'block'});
  await ctx4.addInitScript(() => {
    window.__fbConfig = {apiKey: 'test'};
    const M = window.__fb = {log: []};
    window.__fbLoader = async () => ({app: {initializeApp: () => ({})},
      auth: {getAuth: () => ({currentUser: null}), onAuthStateChanged: (a, cb) => setTimeout(() => cb(null), 0),
        applyActionCode: async (a, c) => { if (c !== 'bon') throw {code: 'auth/invalid-action-code'}; M.log.push(['apply', c]); },
        verifyPasswordResetCode: async (a, c) => { if (c !== 'bon') throw {code: 'auth/expired-action-code'}; return 'moi@exemple.fr'; },
        confirmPasswordReset: async (a, c, pw) => M.log.push(['reset', pw])},
      firestore: {getFirestore: () => ({})}});
  });
  const p4 = await ctx4.newPage(); p4.on('pageerror', e => errs.push(e.message));
  await p4.route('**/*', r => /hanzi|fonts/.test(r.request().url()) ? r.abort() : r.continue());
  const base = await urlFor('index.html');
  await p4.goto(base + '?mode=verifyEmail&oobCode=bon&lang=fr'); await p4.waitForSelector('.act h1');
  check(await p4.textContent('.act h1') === 'Adresse confirmée !' && await p4.evaluate(() => __fb.log.some(x => x[0] === 'apply')) && !/oobCode/.test(await p4.evaluate(() => location.href)), 'lien de confirmation : page Xué Yuán « Adresse confirmée ! », code retiré de l\'adresse');
  await p4.click('#acont'); await p4.waitForSelector('#onb #af');
  check(true, '« Ouvrir Xué Yuán » : on arrive sur la connexion');
  await p4.goto(base + '?mode=verifyEmail&oobCode=vieux'); await p4.waitForSelector('.act h1');
  check(await p4.textContent('.act h1') === 'Ce lien ne fonctionne plus', 'lien déjà utilisé : message clair');
  await p4.goto(base + '?mode=resetPassword&oobCode=bon'); await p4.waitForSelector('#arf');
  check(await p4.textContent('#aem2') === 'moi@exemple.fr', 'lien « mot de passe oublié » : formulaire pour le compte concerné');
  await p4.fill('#apw', 'Le chat noir dort, 42 !');
  check(/Robuste/.test(await p4.textContent('#apm .pwlab')), 'nouveau mot de passe : jauge de robustesse');
  await p4.fill('#apw2', 'Le chat noir dort, 42 !'); await p4.click('#ago'); await p4.waitForSelector('.act h1');
  check(await p4.textContent('.act h1') === 'Mot de passe changé' && await p4.evaluate(() => __fb.log.some(x => x[0] === 'reset')), 'nouveau mot de passe enregistré');
  await ctx4.close();

  // Dans l'artifact claude.ai, pas de compte Xué Yuán
  const p2 = await ctx.newPage();
  await p2.addInitScript(() => { localStorage.setItem('hsk-jardin-v1', JSON.stringify({onboarded: true, profile: {}, level: 1})); window.claude = {use: async () => null}; });
  await p2.goto(await urlFor('index.html') + '#objectifs'); await p2.waitForSelector('text=Ma progression');
  check(await p2.locator('[data-go="compte"]').count() === 0, 'artifact claude.ai : pas de bouton Compte');

  check(!errs.length, errs.length ? 'ERREURS : ' + errs.join(' | ') : 'aucune erreur JS');
  await b.close(); if (fails.length) process.exit(1);
})();
