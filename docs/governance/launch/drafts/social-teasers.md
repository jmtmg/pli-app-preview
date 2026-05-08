# Social teasers M5 — Beta publique PLI (drafts)

**Statut** : 🚫 DRAFT — NE PAS PUBLIER
**Période cible** : Sprint 11, J-3 à J10 (calendrier à verrouiller à la sortie de l'integration sprint)
**Plateformes** : LinkedIn (primaire), X/Twitter, Bluesky, Threads
**Ton** : sobre, factuel, 1re personne, pas de hype
**Source** : déplacé depuis `marketing/social-teasers.md` le 2026-04-22 (T5.2 ticket `M5-freeze.md`).

---

## ⚠️ Règle freeze communication externe

> Aucune publication sur ces plateformes avant :
> 1. Fermeture de l'integration sprint (cf. `docs/governance/2026-04-22-ordre-mission.md` §7)
> 2. Validation du Checkpoint 11a (Go/No-Go ouverture, Sprint 11 J5)
> 3. Feu vert direction écrit dans `docs/governance/launch/publications-log.md` pour chaque post
>
> **Tout chiffre dans un post doit être mesuré sur le binaire intégré (branche `release-v1`)**, pas sur les métriques isolées des modules M3/M4 d'avant-audit. La re-baseline est due pour le 2026-05-14 (D5).

**Règles rédactionnelles** (inchangées) :
- 1 idée par post
- Aucun emoji décoratif (sauf 👍/👎 factuels)
- Pas de "BREAKING" / "INCROYABLE" / "JE VOUS DÉVOILE"
- Lien en commentaire sur LinkedIn, inline sur X/Bluesky/Threads
- Chaque claim chiffré est vérifiable dans `publications-log.md`

---

## 1. Calendrier récapitulatif (cible à confirmer post integration-sprint)

| ID | Jour Sprint 11 | Date cible (2026) | Heure CET | Plateforme | Owner | Statut |
|---|---|---|---|---|---|---|
| S-01 | J-3 | Ven 4 sept | 11h00 | LinkedIn | Founder | Draft prêt, en attente FV |
| S-02 | J6 | Mer 16 sept | 09h00 | LinkedIn | Founder | Draft prêt, en attente FV + chiffres |
| S-03 | J7 | Jeu 17 sept | 17h00 | LinkedIn | Founder | Template J+1 |
| S-04 | J8 | Ven 18 sept | 14h00 | LinkedIn | Founder | Template itération |
| S-05 | J9 | Lun 21 sept | 10h00 | X / Bluesky / Threads | Founder | Thread draft prêt |
| S-06 | J9 | Lun 21 sept | 14h00 | LinkedIn | Founder | Draft prêt, en attente FV + chiffres |
| S-07 | J10 | Mar 22 sept | 11h00 | LinkedIn | Founder | Template clôture |

---

## 2. Posts LinkedIn (ordre chronologique)

### S-01 · LinkedIn J-3 — Post réflexif pré-ouverture

> Ça fait plusieurs mois que je construis un client email.
>
> Pas par ambition — par frustration. Je lisais mes mails 30 fois par jour et mon client me parlait en threads quand je pensais en personnes.
>
> J'ai essayé Superhuman, Hey, Spike, Thunderbird. Chacun résolvait une moitié du problème, aucun les deux.
>
> Alors j'ai fait le mien. PLI. Avec deux règles non négociables :
>
> 1. Fils regroupés par contact, pas par thread.
> 2. Mode Local possible — vos emails restent chez vous, chiffrés, jamais chez nous.
>
> La beta privée a tourné plusieurs semaines avec une centaine de testeurs. Assez pour savoir qu'il y a un usage.
>
> Le 16 septembre, j'ouvre la beta publique. Sans invitation. 500 à 1000 personnes bienvenues.
>
> Lien en commentaire le jour J.

**Caractères** : ~800 · **Hashtags** : aucun · **Pas de lien encore (teasing)**
**Pré-publication** : FV direction + date confirmée + chiffres si présents mesurés sur binaire intégré (ici volontairement pas de chiffre dur).

---

### S-02 · LinkedIn J6 — Annonce ouverture

> La beta publique de PLI est ouverte depuis 8h ce matin.
>
> Pas de Launch officiel — ça viendra en octobre. Aujourd'hui c'est juste l'ouverture.
>
> Concrètement, ce que vous pouvez faire :
>
> • Créer un compte en 30 secondes, 14 jours gratuits, sans CB
> • Connecter Gmail ou Microsoft 365
> • Tester le mode Local (vos emails restent chez vous) ou le mode Cloud (hébergé en France)
> • Me dire ce qui ne va pas, directement dans l'app ou sur notre Discord
>
> J'ai écrit un article plus long pour expliquer pourquoi j'ai construit ça et ce que ça fait vraiment (et ne fait pas). Lien en commentaire.
>
> Je réponds à tout. Même "c'est moche".

**Caractères** : ~710 · **CTA** : article blog en 1er commentaire
**Pré-publication** : flag `public_signup_enabled` bien passé à `true` à 08h00 CET ; blog en ligne ; smoke tests verts à J5 ; dashboards Grafana verts.

---

### S-03 · LinkedIn J7 — Métriques J+1 (transparence)

> 24h après l'ouverture de la beta publique de PLI.
>
> Chiffres bruts (sources : widget in-app + dashboards Grafana M5 sur binaire intégré) :
>
> • `{signups}` signups
> • `{connected_accounts}` comptes mail connectés
> • Latence p95 : `{p95_ms}` ms (cible < 500)
> • Incidents : `{incident_count}` (`{incident_minutes}` min cumulées)
> • Thumbs up / down : `{thumbs_up}` / `{thumbs_down}`
> • Membres Discord : `{discord_members}`
>
> Ce qu'on corrige tout de suite :
> • `{top_issue_1}`
> • `{top_issue_2}`
>
> Ce que je n'avais pas anticipé :
> • `{surprise_observation}`
>
> Si vous voulez suivre en temps réel, tout est sur notre status page publique.
>
> Merci aux premiers 24h.

**Caractères** : ~650 (template à remplir J7) · **Source chiffres** : exclusivement les dashboards Grafana M5 et le widget feedback in-app — pas de chiffre issu de branches dev ou de simulations.
**Note** : si chiffres décevants, ne pas publier ou ajuster le ton. Si très bons, ne pas en faire trop.

---

### S-04 · LinkedIn J8 — Itération #1

> Ce qu'on a changé dans PLI en 48h grâce à vos retours :
>
> 1. `{fix_1}`
> 2. `{fix_2}`
> 3. `{fix_3_ux}`
>
> Détail complet dans notre changelog public (lien en commentaire).
>
> Le point qui revient le plus : `{dominant_theme}`. On y travaille pour la fin de semaine.
>
> Continuer à nous dire ce qui ne va pas — c'est plus utile qu'un like.

**Caractères** : ~470 (template) · **Contrainte freeze** : chaque `fix_N` doit pointer vers un commit cherry-pick vers `release-v1` labellisé `hotfix-p1` ou `hotfix-p0`. Pas de "nouvelle feature" déguisée.

---

### S-05 · Thread X / Bluesky / Threads — J9 (10h00)

**Tweet 1/5**

> Il y a 5 jours, j'ai ouvert la beta publique d'un client email que je construis depuis avril.
>
> Pas de Launch officiel encore. Juste une ouverture progressive pour valider 3 choses sur le produit.
>
> Voici ce que j'ai appris.

**Tweet 2/5**

> Hypothèse 1 : "les gens veulent un email groupé par contact, pas par thread"
>
> Résultat : `{onboarding_passed_pct}` % des testeurs passent le stade onboarding, `{d1_return_pct}` % reviennent le lendemain.
>
> → `{valide_ou_non}`, `{nuance_profil_user}`.

**Tweet 3/5**

> Hypothèse 2 : "le mode Local a une vraie demande, malgré le setup"
>
> Résultat : `{local_share_pct}` % des signups ont choisi Local au choix. Corrélation `{profil_type}`.
>
> → `{conclusion_courte}`.

**Tweet 4/5**

> Hypothèse 3 : "un solo founder + agents peut maintenir un SaaS sous charge"
>
> Résultat : 7 jours, `{signups_total}` signups, `{downtime_min}` min de downtime cumulées, `{bugs_reported}` bugs remontés, `{bugs_fixed}` corrigés.
>
> → À confirmer au Launch.

**Tweet 5/5**

> Si vous voulez tester avant le Launch officiel (2026-10-07) : beta ouverte → https://pli.app
>
> 14 j gratuits sans CB. Mode Local ou Cloud. Dites-moi ce qui ne va pas, je réponds à tout.

**Contrainte freeze** : les cinq tweets partent **ensemble** ou pas du tout (feu vert unique). Chaque chiffre est vérifié sur dashboards Grafana M5 + widget feedback.

---

### S-06 · LinkedIn J9 — Bilan 5 jours

> 5 jours de beta publique PLI. Quelques leçons honnêtes.
>
> Ce qui marche :
> • `{working_aspect}`
> • Le mode Local est testé par `{local_share_pct}` % des users
> • La recherche tient sous 300 ms sur la plupart des comptes
>
> Ce qui cloche :
> • `{friction_1}`
> • Onboarding encore trop long pour les comptes > 10k messages
> • L'empty state du composer n'est pas clair
>
> Ce qu'on va faire avant Launch (2026-10-07) :
> • Traiter ces 3 points
> • Préparer mieux les signalements de bug depuis l'app
> • Améliorer la page d'accueil pour ceux qui arrivent "à froid"
>
> Merci aux `{signups_total}` personnes qui ont pris le temps d'essayer.

**Caractères** : ~830 (template)

---

### S-07 · LinkedIn J10 — Rapport clôture

> Rapport complet : 7 jours de beta publique PLI.
>
> Objectif initial : 500-1000 signups, 0 incident majeur, feedback positif majoritaire.
>
> Résultats :
>
> • Signups : `{signups_total}`
> • Incidents : `{incident_count}`
> • Feedback ratio thumbs : `{thumbs_ratio}`
> • NPS : `{nps_score}` (n=`{nps_n}`)
> • Conversion trial → intent payant : `{intent_pay_pct}` %
>
> Décision : `{Go_Launch_7_octobre}` / `{Décalage_N_semaines}`
>
> Article complet avec tous les chiffres et l'analyse : lien en commentaire.
>
> Prochaine étape : Launch officiel. ProductHunt, Hacker News, presse. On y va avec ce qu'on a appris.

**Caractères** : ~650 · **Pré-publication** : rapport clôture `closures/M5.md` signé ; tous les chiffres proviennent de `publications-log.md`.

---

## 3. Autres contenus courts

### Annonce Discord Welcome (J6)

> Bienvenue sur le Discord PLI 👋
>
> La beta publique est ouverte depuis ce matin. Ici on peut :
> • Signaler un bug (#bugs)
> • Partager un usage (#feedback)
> • Demander une feature (#feature-requests)
> • Discuter librement (#off-topic)
>
> Je suis connecté à peu près en continu en heures ouvrées. Hors heures : je réponds sous 12h.
>
> Règles : soyez factuels et respectueux. Les attaques personnelles entraînent un mute, pas une discussion.
>
> — JM (founder)

### Tweet incident court (si besoin)

> Incident en cours sur PLI : `{endpoint_affecté}`. Suivi en temps réel sur https://status.pli.app. On corrige, ETA < `{eta_min}` min.

**Contrainte** : toute communication incident passe par le même template. Aucune spéculation sur la cause avant post-mortem.

### Tweet résolution

> Incident `{endpoint_affecté}` résolu à `{heure_resolution}`. Durée totale : `{duree_min}` min. Cause : `{ligne_factuelle}`. Post-mortem public sous 48h. Merci de votre patience.

---

## 4. Messages à NE PAS publier en M5

- ❌ "We're launching today!" — on n'est pas en Launch, on est en beta
- ❌ Comparatifs frontaux ("meilleur que Gmail") — pas le moment
- ❌ Témoignages utilisateurs non sollicités / non validés (attendre consentement écrit)
- ❌ Screenshots montrant des données utilisateur même floutées (on demande l'accord)
- ❌ Promesses sur V2/V3 dans un post public (risque attente > livraison)
- ❌ Critiques publiques de concurrents (dans article blog c'est différent, factuel)
- ❌ **Aucun chiffre non re-baseliné sur binaire intégré** (ex. NPS +42 beta privée issu de branche M4 isolée : retiré de tout post)
- ❌ Toute revendication de feature M2-M5 qui n'a pas été vue fonctionner dans le binaire en CI avec `PLI_ENABLE_M2=1`

---

## 5. Politique de réponse aux commentaires

- **Réponses positives** : accuser réception, 1 ligne, ne pas sur-remercier
- **Questions techniques** : répondre factuellement, rediriger Discord si débordé
- **Plaintes / frustrations** : remercier pour le retour, proposer Discord ou DM, ne jamais justifier
- **Trolls** : ignorer ou répondre 1 fois calmement puis stop
- **Demandes de démo / freelance** : "on n'est pas dispo pour des démos M5, mais un compte gratuit 14 j est ouvert à tous, vous pouvez tester vous-même"

**Règle founder** : ne pas rester > 30 min sur les réponses réseaux en 1 session. Pomodoro 25 min max pour ne pas déraper.

---

## 6. Checklist pré-publication (à cocher ligne par ligne, par post)

Avant chaque post, vérifier :

- [ ] **FV direction écrit** dans `docs/governance/launch/publications-log.md` (ID, plateforme, horodatage, signataire)
- [ ] Tous les `{placeholders}` remplacés — aucun `{...}` ne part en live
- [ ] Chiffres cités : corrects, **mesurés sur binaire intégré**, non sensibles (pas d'identifiants users)
- [ ] Orthographe : 2 relectures (CONT)
- [ ] Longueur conforme (LinkedIn < 1 500 car., X < 280, Bluesky < 300)
- [ ] Pas d'emoji décoratif superflu
- [ ] Lien testé (redirige bien, tracking ok)
- [ ] Image OG / preview ok sur l'aperçu plateforme
- [ ] Publication programmée à l'heure définie (pas en live)
- [ ] Post précédent : analytics notés dans le tableau PM
- [ ] Entrée `publications-log.md` mise à jour `statut=published, url=...`

---

## 7. Historique draft

- 2026-04-22 : déplacé depuis `marketing/social-teasers.md` vers drafts governance. Chiffres durs (NPS 46, rétention 58 %, conversion 24 %) remplacés par `{placeholders}` car non re-baselinés sur binaire intégré. Ajout règle freeze communication externe. (Session M5, T5.2.)

---

*Rédigé par PM en coordination avec founder. Relecture finale founder + direction + CONT avant chaque publication.*
