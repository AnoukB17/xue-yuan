# Activer les comptes Xué Yuán (Firebase)

L'écran **Moi › Mon compte** permet de créer un compte (adresse e-mail vérifiée) et de synchroniser la progression
entre appareils. Tant que la configuration ci-dessous n'est pas faite, l'écran affiche « Bientôt disponible » et
l'appli fonctionne comme avant (progression sur l'appareil).

Le service est gratuit à cette échelle (offre Spark de Firebase : 50 000 lectures par jour).

## 1. Créer le projet

1. Aller sur https://console.firebase.google.com et se connecter avec un compte Google.
2. **Créer un projet**, nom : `xue-yuan`. Google Analytics : non (inutile).
3. Sur la page du projet, cliquer l'icône **Web** `</>`, surnom `Xué Yuán`, sans Firebase Hosting, puis **Enregistrer**.
4. Firebase affiche un bloc `const firebaseConfig = { apiKey: …, authDomain: …, projectId: …, … }`.
   **Copier ce bloc** : c'est lui qu'il faut me transmettre. Ces valeurs sont publiques par conception (elles
   identifient le projet, elles ne donnent aucun droit) ; la protection repose sur les règles de l'étape 3.

## 2. Activer la connexion par e-mail

1. Menu **Créer › Authentication › Commencer**.
2. Onglet **Mode de connexion** › **Adresse e-mail/Mot de passe** › activer le premier interrupteur (pas « Lien par
   e-mail ») › **Enregistrer**.
3. Onglet **Paramètres › Domaines autorisés** › **Ajouter un domaine** : `anoukb17.github.io`.
4. Facultatif : onglet **Modèles** › « Validation de l'adresse e-mail » : la langue est déjà choisie par l'appli
   (français) ; on peut y changer le nom de l'expéditeur, par exemple « Xué Yuán ».

## 3. Créer la base et ses règles

1. Menu **Créer › Firestore Database › Créer une base de données**.
2. Emplacement : `eur3 (europe)` (données en Europe). Mode : **production**.
3. Onglet **Règles**, remplacer tout le contenu par :

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{uid} {
      allow read, write: if request.auth != null
                         && request.auth.uid == uid
                         && request.auth.token.email_verified == true;
    }
  }
}
```

   puis **Publier**. Chaque personne ne peut lire et écrire que sa propre progression, et seulement après avoir
   confirmé son adresse.

## 4. Me transmettre la configuration

Coller le bloc `firebaseConfig` de l'étape 1 dans la conversation. Je le place dans `index.html`
(`const FIREBASE_CONFIG = …`), je teste et je publie.

## Fonctionnement

- **Création** : e-mail + mot de passe (8 caractères au moins), puis e-mail de confirmation en français. Tant que
  l'adresse n'est pas confirmée, rien n'est envoyé en ligne.
- **Synchronisation** : à la connexion, la progression de l'appareil et celle du compte sont **fusionnées**, sans
  rien perdre (pour chaque mot, la révision la plus récente ; pour l'XP, le maximum ; leçons, tracés, histoires,
  examens réunis). Ensuite, chaque sauvegarde part en ligne 4 secondes après la dernière activité, et aussi quand on
  quitte l'appli.
- **Mot de passe oublié**, **déconnexion** (la progression reste sur l'appareil), **suppression du compte** (efface le
  compte et la copie en ligne).
- **« Tout remettre à zéro »** l'emporte sur la copie en ligne.
- **Artifact claude.ai** : pas d'écran Compte, la progression y suit déjà le compte Claude.
- Le code Firebase (≈ 250 Ko) n'est chargé que sur l'écran Compte ou quand une session est ouverte : la première
  visite reste aussi rapide.
- Test : `node tools/check-compte.js` (Firebase simulé, 20 vérifications).
