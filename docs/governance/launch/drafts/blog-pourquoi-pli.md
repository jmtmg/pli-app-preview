---
title: "Pourquoi PLI — et pourquoi maintenant"
slug: pourquoi-pli
author: Jean-Marie Simeoni
published: TBD — bascule `public_signup_enabled` en Sprint 11 (cible J6 = 2026-09-16, sous réserve Checkpoint 4 M5)
updated: 2026-04-22
tags: [pli, email, product, local-first, beta]
excerpt: "J'ouvre PLI en beta publique. Voici ce que c'est, pourquoi je l'ai construit, et ce que ça fait vraiment (et ne fait pas)."
ogImage: /og/pourquoi-pli.png
status: draft
review_status: en attente feu vert direction (cf. règle §7 ordre de mission 2026-04-22)
reviewers: [direction (Mail), TL, SEC, Founder]
---

> **🚫 NE PAS PUBLIER.**
> Ce texte est un **draft** sous le freeze communication externe fixé par l'ordre de mission du 2026-04-22 (§7).
> Aucune publication blog / social / email externe n'est autorisée avant :
> 1. Fermeture de l'integration sprint (D2 + D3 + D5 validées)
> 2. Validation Checkpoint 4 M5 (cf. `M5-KICKOFF.md §8`)
> 3. Feu vert direction écrit dans `docs/governance/launch/publications-log.md`
> Les chiffres ci-dessous sont **provisoires / simulés** tant que M3 + M4 n'ont pas rebaseliné sur binaire intégré (D5 — deadline 2026-05-14). Ne pas citer en externe.

---

# Pourquoi PLI — et pourquoi maintenant

*Aujourd'hui j'ouvre PLI en beta publique.*

La beta privée a tourné plusieurs semaines sur un périmètre restreint, des testeurs triés, beaucoup de feedback, quelques sueurs froides. À partir de maintenant, n'importe qui peut créer un compte, connecter sa boîte mail et tester 14 jours gratuitement — sans carte bancaire.

Avant de vous donner le lien, je voudrais vous dire pourquoi j'ai construit ça.

## Le problème que je n'arrivais plus à accepter

Je lis mon email au moins 30 fois par jour. Vous aussi, sans doute. Et depuis 15 ans, je vis avec la même frustration : **mon client email me parle en "threads", alors que je pense en "personnes"**.

Quand je cherche l'échange que j'ai eu avec Marie la semaine dernière, je ne me souviens pas du sujet. Je me souviens de Marie. Mais Gmail me force à retrouver le bon thread dans la bonne arborescence, avec le bon objet, parmi 40 000 mails.

J'ai essayé Superhuman, Hey, Spike, Thunderbird. Chacun résolvait une partie du problème, aucun les deux.

Et puis surtout, tous ces outils ont un point commun que je n'arrive plus à ignorer : **ils voient mes emails.** Au minimum pour les stocker, souvent pour les indexer, parfois pour entraîner des modèles.

Mes emails, c'est mon CV, mes factures, mes relations perso, mon avocat, mon médecin. Ce n'est pas une donnée fonctionnelle. C'est une mémoire.

## Le pari PLI

PLI fait deux choses simples, qu'aucun produit que j'ai essayé ne fait bien ensemble :

**1. Rassembler les emails par contact, pas par thread.**
Vous ouvrez PLI. À gauche, une liste de personnes. Vous cliquez sur Marie. Vous voyez toute l'histoire de votre échange avec Marie — pro, perso, newsletter à laquelle elle vous a abonné·e, peu importe. Comme dans WhatsApp ou iMessage, mais pour l'email.

**2. Vous décidez où vivent vos données.**

- **Mode Local** : votre base d'emails reste sur votre machine, chiffrée. PLI ne voit jamais vos messages. Jamais. (35 €/an, clé de licence hors-ligne vérifiée par signature Ed25519, c'est tout.)
- **Mode Cloud** : si vous voulez accéder à vos emails depuis plusieurs appareils sans gérer de sync vous-même, on héberge pour vous — en France, chiffré au repos, exportable en 1 clic. (7 €/mois après 14 j d'essai, paiement Stripe.)

Le mode Local, c'est ce qui m'a pris le plus de temps à faire marcher. Une PWA qui tourne en local, SQLite chiffré, FTS5 pour la recherche, sync directe avec Gmail ou Microsoft sans passer par nos serveurs. Techniquement pas trivial. Économiquement inconfortable (on vend moins de récurrent). Mais c'est non négociable pour moi.

## Ce que PLI fait à l'ouverture de la Beta publique

> **À valider avant publication** : ce périmètre reflète l'état du **binaire intégré** (branche `release-v1` post integration-sprint). Le blog ne doit citer que ce qui fonctionne réellement dans le binaire testé, pas la somme théorique des modules M1-M5. À relire après re-baseline M3 + M4 (deadline 2026-05-14) et après smoke tests synthétiques validés (Sprint 11 US-11.9).

Concrètement, à l'ouverture de la beta publique :

- **Connexion Gmail et Microsoft 365** en OAuth, 1 ou plusieurs comptes par utilisateur
- **Fil par contact** avec filtres Humains / Notifs / Non lus / Avec PJ
- **Composer + signature + brouillons** auto-sauvegardés
- **Recherche plein texte** sous 300 ms *(cible — à confirmer par re-baseline M3)*
- **Swipe bilatéral** mobile (archive, muter, non lu, suppression) avec seuils configurables
- **Épinglage** de 3 contacts max, avec réordonnement drag-and-drop
- **Pièces jointes** : sélecteur + preview + OCR des PDF (Tesseract en Local, côté serveur en Cloud)
- **Export complet** (ZIP EML + vCard + JSON) — aucune captivité
- **Suppression de compte** avec effacement sous 30 jours — RGPD conforme
- **FR + EN**, dark / light, accessible WCAG AA, Lighthouse > 90 *(cible — à re-mesurer sur binaire intégré)*

Ce que PLI **ne fait pas** à l'ouverture de la Beta publique :

- Pas d'IA assistant pour rédiger à votre place. *Prévu V2.*
- Pas d'app native iOS/Android à ce jour. PWA performante sur mobile. *Natif prévu V1.2.*
- Pas de calendrier intégré. *Peut-être V2.*
- Pas de boîte partagée / team features. *V3.*
- Pas de support chat 24/7. Un founder, une équipe d'agents, un Discord actif.

## Pourquoi maintenant

La beta privée a duré plusieurs semaines. Une centaine d'utilisateurs, quelques milliers de messages synchronisés cumulés, bugs corrigés, itérations majeures sur l'onboarding.

> **À compléter avant publication** : les métriques beta privée (NPS, rétention J30, conversion intent payant) doivent être **celles mesurées sur le binaire intégré**, pas les chiffres isolés des modules M3/M4. La re-baseline est due pour le 2026-05-14 (D5 ordre de mission). Tant qu'elle n'est pas faite : pas de chiffre dans ce blog. On publie sans chiffre ou on ne publie pas.

Ce sont des chiffres modestes. Mais c'est assez pour avoir la conviction que le produit fait quelque chose d'utile pour une partie des gens — peut-être pas tout le monde, et c'est bien.

Alors j'ouvre à 500-1000 personnes de plus. Je ne lance pas officiellement (Launch prévu 2026-10-07). J'ouvre la beta **publique** : pas d'invitation, pas de waitlist, inscription directe. Je prends le risque que l'infra tienne. Je prends le risque qu'on m'écrive pour dire que c'est moche ou que ça manque.

## Ce que je vous demande

**Si PLI résout un problème que vous avez** : essayez 14 jours. Dites-moi ce qui ne va pas. Utilisez le petit widget en bas à droite dans l'app, ou passez sur notre Discord, ou répondez à cet email si vous êtes sur la newsletter.

**Si PLI ne vous intéresse pas** : c'est complètement ok, et vous avez aidé sans le savoir juste en lisant jusqu'ici.

**Si vous bossez dans la tech et que vous avez des idées** : envoyez-les-moi. Je réponds.

## Les risques que je vois

Je ne vais pas faire semblant. Pendant la Beta publique :

- Il peut y avoir des ralentissements. L'infra a été validée à 3× notre capacité en tests de charge k6 (Sprint 11 US-11.8). Si on explose, la status page dira la vérité en temps réel.
- Il peut y avoir des bugs. On corrigera vite. Je publierai un changelog public toutes les 48 h.
- Certains parcours ne sont pas parfaits. Les empty states ne sont pas tous jolis. Il manque des raccourcis clavier évidents. C'est en cours.
- Les paiements sont en mode live Stripe, donc si vous passez à l'offre payante et qu'on casse quelque chose, on rembourse. Sans discussion.

## Pour essayer

[→ Créer un compte PLI (14 j gratuits, pas de CB)](https://pli.app/signup)

Si vous préférez voir avant : une démo interactive courte sur la page d'accueil.

Merci d'être arrivé jusqu'ici. On se retrouve dans l'app, sur Discord, ou en réponse à ce billet.

— Jean-Marie

---

*PLI est construit à Paris par une seule personne et une équipe d'agents. Code source du moteur de sync : open source, licence AGPL-3.0. Mentions légales et CGU : pli.app/legal. Contact direct : jm@pli.app.*

---

## Meta-draft — à retirer avant publication

**Checklist publication (CONT + direction)** :

- [ ] Re-baseline M3 + M4 faite (2026-05-14 max) → remplir ou retirer les chiffres
- [ ] Smoke tests US-11.9 verts depuis 48 h
- [ ] Checkpoint 4 M5 validé
- [ ] Feu vert direction écrit dans `docs/governance/launch/publications-log.md`
- [ ] Date de publication posée en clair (pas "TBD")
- [ ] Lien `https://pli.app/signup` testé, flag `public_signup_enabled` actif
- [ ] OG image `/og/pourquoi-pli.png` générée et accessible en < 1 s
- [ ] Version EN du blog créée en parallèle
- [ ] Retirer ce bloc "Meta-draft" avant publication

**Historique** :

- 2026-04-22 : déplacement depuis `blog/blog-pourquoi-pli.md` vers drafts governance + ajout règle no-publish + retrait chiffres durs non vérifiés sur binaire intégré (session M5, T5.2).
