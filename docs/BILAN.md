# Xué Yuán 学园 : bilan final (14/11/2026)

Audit du 12/11/2026, puis sept lots de travaux. 105 commits sur GitHub (AnoukB17/xue-yuan), appli publiée sur
https://anoukb17.github.io/xue-yuan/ et dans l'artifact claude.ai.

## 1. Récapitulatif des lots

| Lot | Contenu | État |
|---|---|---|
| 1. Contenu prioritaire | Corrections (离…), un identifiant par sens (花, 只, 长, 得, 还), balisage `lang="zh-CN"` | ✓ |
| 2. Améliorations rapides | Phrases d'exemple et unités thématiques HSK 2, tracés chargés à la demande, contrastes | ✓ |
| 3. Mobile et accessibilité | Boutons de 44 px, couleur des erreurs distincte, aucune violation WCAG A/AA (axe-core) | ✓ |
| 4. Performance | Polices non bloquantes, appli installable, hors ligne, choix de la voix | ✓ |
| 5. UX / UI | Navigation niveau → leçon, dictionnaire, écran Listes, FSRS et plafond quotidien | ✓ |
| 6. Couverture HSK 1 à 6 | Programme officiel 2025 : 5 334 mots (5 389 sens), 395 leçons, 238 fiches de grammaire, test de niveau, examen blanc, validation de niveau | ✓ |
| 7. Fonctionnalités | 18 histoires graduées, écran Oral (enregistrement, comparaison, vérification), conversation avec Claude | ✓ |

## 2. Recommandations de l'audit

| Recommandation (priorité) | État | Détail |
|---|---|---|
| Corrections de contenu et identifiants par sens (P1) | ✓ fait | |
| `lang="zh"`, boutons de 44 px, couleur des erreurs (P1) | ✓ fait | Contrôlé à chaque modification par 3 tests |
| Tracés à la demande, polices allégées (P1) | ✓ fait | Police pinceau réduite à 177 caractères (68 Ko au lieu de ~390 Ko) |
| Données sorties du code, étiquetées 3.0 / 2.0 / fréquence (P1) | ✓ fait | `data/vocab.json` (source), bloc généré ; HSK 5-6 chargés après l'affichage |
| Réaligner sur le HSK 3.0 (P1) | ✓ fait | Programme officiel 2025, niveaux 1 à 6 complets |
| Phrases et grammaire par unité (P1) | ✓ fait | Fiches par niveau ; phrases pour le HSK 2 et dans les fiches et histoires |
| FSRS et plafond quotidien (P2) | ✓ fait | |
| Audio de qualité pré-généré et relu (P2) | ✗ non fait | Voix de l'appareil, au choix de l'utilisateur ; demande une source audio |
| Oral noté (P2) | ◐ partiel | Enregistrement et comparaison ; vérification des caractères par reconnaissance vocale, pas des tons |
| Navigation niveau → unité → leçon, dictionnaire (P2) | ✓ fait | |
| Test de niveau adaptatif, tests de fin de niveau (P2) | ✓ fait | |
| Examens blancs par niveau (P2) | ◐ partiel | Format et minutage officiels ; écrit simplifié (ordre des mots), oral non simulé |
| Histoires graduées (P2) | ✓ fait | 18 histoires, HSK 1 à 6 |
| Appli installable, hors ligne (P2) | ✓ fait | |
| HSK 5-6 : vocabulaire, textes, chengyu, rédaction (P3) | ◐ partiel | Vocabulaire, grammaire et histoires faits ; pas de module chengyu ni de correction de rédaction |
| Conversation IA (P3) | ◐ partiel | 8 situations par niveau (claude.ai uniquement), pas encore par unité |

## 3. Performance (Lighthouse, mobile, 4G lente simulée)

| | Avant (23/10) | Fin du lot 4 | Maintenant |
|---|---|---|---|
| Score Performance | 57 | 97 à 99 | 97 |
| Premier affichage (FCP) | 7,9 s | 1,07 s | 1,56 à 1,59 s |
| Affichage principal (LCP, objectif < 2,5 s) | 9,5 s | ~1,9 s | 2,32 à 2,35 s |
| Temps de blocage (TBT) | 0 ms | 94 à 147 ms | 70 à 120 ms |
| Décalage visuel (CLS) | 0,044 | 0,011 | 0 à 0,012 |
| Accessibilité / Bonnes pratiques | 95 / – | 100 / 96 | 100 / 100 |
| Poids de la première visite | ~3 Mo | – | 436 Ko |
| Hors ligne | non | oui | oui |

Le contenu a été multiplié par plus de quatre depuis le lot 4 (vocabulaire, grammaire, histoires) : le LCP était
remonté à 2,9 s. Il est repassé sous 2,5 s (2,32 à 2,35 s, 4 mesures) quand l'outil d'écriture, chargé depuis un
CDN, a cessé de bloquer l'affichage (attribut `defer` ; les écrans d'écriture attendent son arrivée). L'appli
installée se charge depuis la mémoire du téléphone et n'est pas concernée par ces chiffres de première visite.

## 4. Nouvelle grille (notes sur 10)

| Domaine | Audit | Maintenant | Pourquoi |
|---|---|---|---|
| Contenu chinois | 6,5 | 7 | Bien plus riche et contrôlé automatiquement (niveau, pinyin) ; validé par la propriétaire mais pas encore relu par un natif |
| Couverture HSK | 3 | 9 | HSK 1 à 6 du programme 2025 complets (vocabulaire et grammaire) ; HSK 7-9 absents |
| Pédagogie | 5,5 | 8 | Unités thématiques, FSRS, grammaire, histoires, examens, oral |
| UX | 6,5 | 8 | Navigation par niveau, dictionnaire, listes, tests ; beaucoup d'écrans désormais |
| UI | 7,5 | 8 | Identité conservée, couleurs d'erreur séparées, rendu vérifié sur 8 tailles d'écran |
| Mobile et responsive | 7 | 9 | Appli installable, hors ligne, aucun débordement testé |
| Accessibilité | 5 | 9 | Chinois balisé partout, 0 violation axe-core, contrastes AA contrôlés |
| Performance | 4 | 9 | 97, hors ligne, LCP sous 2,5 s |
| Positionnement marché | 4,5 | 6 | Seule appli francophone alignée sur le HSK 2025 du 1 au 6 ; manquent audio natif et synchronisation |

## 5. Points ouverts

- Relecture par un natif de tout le contenu chinois : liste des points prioritaires dans `A-RELIRE.md`.
- ~~Bouton « Passer » absent dans l'étape d'écriture~~ : l'appli était correcte ; c'est le test qui laissait le service worker charger les tracés. Test corrigé.
- Progression séparée entre l'appli du téléphone et l'artifact claude.ai.

## 6. Les 5 prochaines priorités

1. **Relecture native** du contenu (`A-RELIRE.md`), en commençant par les HSK 1 à 3 et les points ⚠ : c'est le principal risque restant.
2. **Audio de qualité** : enregistrements natifs ou voix de synthèse haut de gamme pré-générées pour les mots et phrases des HSK 1 à 3, puis notation des tons à l'oral.
3. **Synchroniser la progression** entre appareils (compte en ligne ou export / import), avant tout lancement public.
4. ~~Revenir sous 2,5 s de LCP~~ (fait : 2,3 s). Prochaine marge : découper le code par écran pour garder ce niveau quand le contenu grandira.
5. **Compléter le HSK 5-6** selon l'objectif : correction de rédaction par Claude et module chengyu, ou bien les niveaux 7 à 9.
