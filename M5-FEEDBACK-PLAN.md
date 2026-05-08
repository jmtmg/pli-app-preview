# M5 — Plan de collecte & traitement du feedback

**Phase** : M5 (9 → 23 sept 2026)
**Owners** : PM (lead) + UX (lead qualitatif) · **Supports** : Founder, TL
**Objectif** : transformer 500-1000 nouveaux users en insights actionnables → 2 itérations produit et 1 décision Go/No-Go Launch documentée.
**MàJ 2026-04-22 (T5.4)** : couverture explicite du **périmètre intégré M1-M5** (routers M2 derrière `PLI_ENABLE_M2`), pas uniquement Sprint 1.

---

## 1. Principes directeurs

1. **Mesurer avant d'interpréter** — toujours disposer de chiffres bruts avant de raisonner sur "ce que les users veulent".
2. **Prioriser par fréquence × sévérité** — pas le plus bruyant, pas le plus éloquent, le plus impactant.
3. **Ne pas rationaliser l'absence de feedback** — silence = désinscription probable, pas "ils sont contents".
4. **Clore la boucle** — chaque feedback actionné fait l'objet d'une mention publique (changelog, post Discord, réponse directe).
5. **Distinguer bug, friction, désir, malentendu** — chaque catégorie a un traitement différent.

---

## 2. Canaux de collecte

| Canal | Type | Volume attendu M5 | Owner |
|---|---|---|---|
| Widget feedback in-app (thumbs + texte) | Quant + qual libre | 300-800 entrées | PM + UX |
| NPS survey à J+7 post-signup (in-app) | Quant structuré | 200-500 réponses | PM |
| Discord `#feedback`, `#bugs`, `#feature-requests` | Qual discuté | 50-200 entrées | PM + Founder |
| Email direct (`support@pli.app`, `jm@pli.app`) | Qual ciblé | 20-80 entrées | Founder |
| Réponses LinkedIn / X sur posts founder | Qual visible | 30-150 commentaires | Founder |
| Interviews qualitatives (5 users ciblés) | Qual profond | 5 × 30 min | PM + UX |
| Événements analytics (Plausible + PostHog free) | Quant comportemental | continu | PM |
| Sessions replay (PostHog, opt-in) | Qual observation | 20-50 sessions analysées | UX |
| Exit survey à désabonnement / désinscription | Qual causes | tous les départs | PM |

---

## 2bis. Taxonomie de feedback — périmètre intégré (ajout T5.4)

Chaque feedback entrant est tagué par **module** pour que le triage distingue les bugs M1 (core Mail) des frictions M2 (paiement/auth/licensing), M3 (RGPD/OCR), M4 (onboarding/KB). Cette taxonomie garantit qu'aucun module n'est invisibilisé par le volume M1.

| Module | Étendue | Sous-thèmes attendus | Owner triage | Escalation |
|---|---|---|---|---|
| **M1 — Core Mail** | OAuth Gmail/MS, liste par contact, recherche, compose, swipe, épinglage | Sync lente, recherche vide, compose KO, shortcut cassé | PM | TL si bug, UX si friction |
| **M2 — Auth / Licensing / Tenancy** | Signup, login, refresh token, 2FA à venir, licence Local (Ed25519), mode Cloud | Login boucle, session perdue, licence expirée, clé invalide, voir données autre tenant | SEC + BE | **P1 immédiat** si tenancy leak, licence root, token vol |
| **M2 — Billing (Stripe live)** | Checkout trial, upgrade, downgrade, cancel, factures | Paiement refusé, double facturation, invoice manquante, webhook down | Founder + BE | SEC si signature ou fuite data |
| **M2 — Emails transactionnels** | Confirmation signup, reset, receipt, issuance licence, feedback ack | Email non reçu, faux spam, mauvais objet, liens cassés | PM + SRE | SEC si SPF/DKIM/DMARC drift |
| **M3 — RGPD / OCR / Sécu** | Export complet, suppression compte, OCR PJ, perms OAuth | Export KO, deletion incomplète, OCR erroné, scope OAuth surévalué | PM + SEC | Legal si RGPD non-compliant |
| **M4 — KB / Onboarding / Tour** | Pages KB FR/EN, product tour, plans, swipe mobile | Article introuvable, tour bloqué, traduction cassée | CONT + UX | PM si friction bloquante |
| **M5 — Infra Beta** | Status page, rate limits, landing, widget feedback lui-même | Page blanche, 429, widget plantage | SRE | Runbook §5/§6/§13 |
| **Autre / Non-classifiable** | Feedback philosophique, "j'aime", "je n'aime pas" sans détail | — | PM | — |

### Tagging pratique

- **Widget in-app** : le champ `context` émis par le widget inclut automatiquement le module dérivé de la route active (`/inbox` → M1 ; `/settings/billing` → M2-Billing ; `/settings/licence` → M2-Licensing ; `/settings/export` → M3 ; `/onboarding` → M4 ; etc.).
- **Discord** : convention de tags `[m1]`, `[m2-billing]`, `[m2-auth]`, `[m2-emails]`, `[m3]`, `[m4]`, `[m5-infra]`. CONT applique les tags rétroactivement à la relecture du salon chaque matin.
- **Email / support** : classification manuelle PM à l'arrivée.
- **Dashboard `m5-feedback`** : ajouter un breakdown par module dans Grafana — ratio thumbs par module, volume quotidien par module, top-3 issues par module.

### Règle d'équilibrage (anti-biais M1)

Si > 70 % des feedbacks portent sur M1 alors que M2-M4 sont entrés en production via flag, c'est un signal de sous-usage (users ne touchent pas aux endpoints M2-M4). **Action PM + UX** : inspecter funnel — est-ce que les users atteignent même les pages M2-M4 ? Si non, itération UX pour les rendre visibles. Ne pas conclure "M2-M4 OK parce que pas de plainte".

---

## 3. Métriques suivies

### 3.1 Métriques quantitatives temps réel (dashboard PM `m5-feedback`)

| Métrique | Fréquence | Cible M5 |
|---|---|---|
| Thumbs up / down ratio 24h | heure | > 4:1 |
| Thumbs up / down ratio cumulé M5 | heure | > 4:1 |
| Nombre feedbacks textuels 24h | heure | > 20 |
| NPS cumulé | jour | > 30 (cible 40) |
| Taux réponse NPS | jour | > 25 % des users J+7 |
| Retention J1 (retour J+1 post-signup) | jour | > 60 % |
| Retention J7 | jour | > 40 % |
| Taux activation (1er compte mail connecté) | jour | > 60 % |
| Taux trial → intent payant (survey) | jour | > 15 % |
| Taux désinscription | jour | < 5 % / semaine |
| Taux réponse support < 4h | jour | > 90 % |

### 3.2 Métriques qualitatives (synthèse J4, J7, J10)

- Tonalité dominante : enthousiaste / positive / mitigée / négative (répartition %)
- Top 5 thèmes positifs
- Top 5 frictions / bugs
- Top 5 features demandées
- Citations représentatives (anonymisées)
- Segments utilisateurs identifiés (freelance solo, ops B2B, journaliste, etc.)

---

## 4. Processus de triage

### 4.1 Classification d'un feedback entrant

Chaque entrée est classée en 1 des 4 catégories :

| Catégorie | Définition | Traitement |
|---|---|---|
| **BUG** | Comportement qui ne respecte pas l'intention produit | Issue GitHub, prioritisation technique |
| **FRICTION** | Fonctionne, mais cause de l'irritation ou du blocage mental | Backlog UX, à pondérer |
| **DÉSIR** | Fonctionnalité manquante | Backlog produit, report post-Launch probable |
| **MALENTENDU** | Attente incorrecte sur ce que PLI fait | Amélioration onboarding/doc/copy |

### 4.2 Priorisation BUG

Matrice fréquence × sévérité :

| | Sévérité basse | Sévérité moyenne | Sévérité haute |
|---|---|---|---|
| **Fréquence basse** (< 3 signalements) | P3 | P3 | P2 |
| **Fréquence moyenne** (3-10 signalements) | P3 | P2 | P1 |
| **Fréquence haute** (> 10 signalements) | P2 | P1 | **P0 — fix immédiat** |

**Bumps forcés par module (ajout T5.4 — périmètre intégré)** :

- Tout bug tagué `[m2-auth]` impliquant session perdue ou login boucle → **minimum P1** (risque attrition massive)
- Tout bug tagué `[m2-billing]` impliquant erreur de débit, double facturation ou refund nécessaire → **minimum P1** + escalation Founder
- Tout bug tagué `[m2-licensing]` impliquant licence root rejetée ou clé `kid` invalide → **P1 immédiat** + SEC (cf. runbook §13.5)
- Tout rapport cross-tenant suggéré (`[m2-tenancy]`) → **P0 automatique**, kill switch inscription, alerter SEC sous 5 min (runbook §13.6)
- Tout bug tagué `[m3]` impliquant export incomplet ou suppression non effective → **P1** (risque non-conformité RGPD)
- Tout bug tagué `[m2-emails]` impliquant un email de `password_reset` non délivré → **P1** (blocage récupération compte)

Ces bumps écrasent la matrice générique : on ne laisse pas un "fréquence basse" rester P3 sur ces catégories.

- **Sévérité haute** : bloque usage, perte de données potentielle, sécurité
- **Sévérité moyenne** : dégrade significativement l'expérience
- **Sévérité basse** : cosmétique, cas de bord rare

### 4.3 Priorisation FRICTION

Pareil, avec l'ajout d'une 3ᵉ dimension : **effort correctif estimé**.

- Si effort < 2 h : fix direct
- Si effort 2 h – 1 j : itération M5 (J8 ou J10)
- Si effort > 1 j : backlog post-Launch

### 4.4 Priorisation DÉSIR

Par défaut : **tout désir est reporté post-Launch**, avec une exception :

> Si un désir émerge > 20× et l'effort est < 1 jour, il peut entrer en M5 itération 2 (J10). PM décide.

### 4.5 Priorisation MALENTENDU

- Si le malentendu porte sur le **positionnement** (> 5 users confondent PLI avec un autre produit) → ajuster landing copy / blog → immédiat
- Si le malentendu porte sur une **feature spécifique** → ajuster tooltip / onboarding / doc

---

## 5. Cadence de traitement

### Daily

- **9h00** : PM revue entrées widget nuit + Discord nuit → catégorise, score, route vers issues GitHub
- **14h00** : PM mid-day → nouveaux feedbacks, arbitrages urgents
- **18h00** : PM debrief jour, Founder briefé top 3 items

### Hebdo (si M5 s'étendait)

Non applicable — M5 = 2 semaines, on reste en daily.

### Jalons synthèse

- **J4 (12 sept)** : 1re synthèse mini (soft, mode hardening) — tendances canaux de collecte
- **J7 (17 sept)** : 1re synthèse complète (post-ouverture 48 h) → input itération #1 (J8)
- **J9 (21 sept)** : 2e synthèse complète → input itération #2 (J10)
- **J10 (22 sept)** : synthèse finale M5 → input rapport de clôture

---

## 6. Itération produit — Protocole

### Cycle itération J8 / J10

1. **Input** : synthèse feedback (J7 pour itération #1, J9 pour itération #2)
2. **Priorisation** (PM, 1h) : matrice P0 top 3-5 → confirmer avec TL que l'effort est cadrable
3. **Exécution** (BE/FE/UX, 6-8 h) :
   - Branches `fix/` séparées
   - PR, review TL obligatoire
   - Smoke tests post-merge
4. **Déploiement** (SRE) : en heures ouvrées, jamais après 17h (hors hotfix P0)
5. **Communication** (PM + Founder) :
   - Changelog public mis à jour
   - Post Discord "ce qu'on a amélioré aujourd'hui"
   - Post LinkedIn si itération significative
   - Notification in-app discrète aux users ayant signalé

### Budget itération

| Itération | Items traités | Effort total | Deadline déploiement |
|---|---|---|---|
| #1 (J8) | 3 à 5 | 8 h | 18h00 CET J8 |
| #2 (J10) | 2 à 3 | 4 h (fin de M5, scope réduit) | 14h00 CET J10 |

---

## 7. Widget feedback — Spécifications produit

### 7.1 UX

- Bouton flottant, bas-droite, 48×48 px, icône `MessageSquare` neutre
- États : neutral (gris), hover (bleu), active (sheet ouvert)
- Ne s'affiche pas sur pages marketing publiques (`/`, `/pricing`, `/legal/*`)
- Ne s'affiche pas dans les 30 premières secondes après signup (onboarding prioritaire)

### 7.2 Sheet de saisie

1. Titre : "Qu'est-ce qu'on peut améliorer ?"
2. Row de 2 boutons : 👍 Ça va / 👎 Ça coince (obligatoire)
3. Textarea libre (max 500 car., placeholder "Raconte-moi en 1 phrase si tu veux")
4. Checkbox "Joindre une capture d'écran de cette page" (opt-in, html2canvas)
5. Bouton "Envoyer" → confirmation "Merci, reçu ✓" 2 s puis close
6. Link discret "Détails / bug report formel" → ouvre /feedback avec catégorisation plus fine

### 7.3 Backend

- Table `feedbacks` :
  - `id`, `user_id` (nullable si anonyme), `sentiment` (up/down), `text` (nullable)
  - `url`, `user_agent`, `viewport_w`, `viewport_h`
  - `screenshot_url` (nullable, S3), `created_at`
- Endpoint `POST /feedback` (authed), rate-limit 10/min/user
- Webhook interne → Slack `#feedback` pour streaming live
- Auto-tag par regex (ex. "lent", "plante", "sync", "composer") pour pré-classification

### 7.4 Dashboard admin `/admin/feedback`

- Stream temps réel (websocket ou polling 10s)
- Filtres : sentiment, période, tags auto, url
- Actions rapides : marquer "traité", créer issue GitHub, répondre à l'user par email
- Export CSV pour analyse pandas

---

## 8. NPS Survey — Spécifications

### 8.1 Timing

- Apparition : J+7 après signup, **1 seule fois**
- Déclenchement : 1re ouverture de l'app après J+7
- Snooze : possible 1 fois (réapparaît 24 h plus tard), puis plus jamais

### 8.2 Questions

1. **NPS** : "Recommanderais-tu PLI à un ami ou collègue ?" (0-10)
2. **Raison** (optionnel, conditionnelle au score) :
   - Score 9-10 (Promoteurs) : "Qu'est-ce qui t'a plu en particulier ?"
   - Score 7-8 (Passifs) : "Qu'est-ce qui t'empêche de mettre 10 ?"
   - Score 0-6 (Détracteurs) : "Qu'est-ce qui nous manque pour toi ?"
3. **Intent payant** (obligatoire) : "Envisages-tu de passer à l'offre payante ?" Oui / Peut-être / Non / Je ne sais pas

### 8.3 Analyse

- NPS classique = % Promoteurs - % Détracteurs
- **Intent payant agrégé** : objectif ≥ 15 % de "Oui" (métrique M5 critique)
- Corrélation score × segment utilisateur pour identifier le PMF

---

## 9. Interviews qualitatives — 5 users

### 9.1 Sélection (J5-J7)

- Identifier 5 users avec profils variés :
  - 1 freelance (ops / admin / juridique / compta)
  - 1 créateur de contenu / journaliste
  - 1 opérationnel B2B (équipe commerciale / support)
  - 1 technique (dev / produit / data)
  - 1 "profil surprise" (détracteur ou usage inattendu)
- Inviter par email personnalisé founder, compensation : 3 mois PLI Plus gratuits

### 9.2 Format

- 30 min en visio
- Template questions :
  1. Comment t'es-tu retrouvé·e sur PLI ?
  2. Raconte-moi ta 1re semaine d'usage.
  3. Moment le plus frustrant ?
  4. Moment le plus satisfaisant ?
  5. Qu'est-ce qui t'empêcherait de payer ?
  6. Qu'est-ce qui t'inciterait à parler de PLI autour de toi ?
  7. Sur quoi on devrait passer 0 temps en ce moment ?

### 9.3 Restitution

- Notes structurées, quotes signalées
- Synthèse croisée J8 matin → input itération #1 si pertinent
- Archive `interviews/M5/` (privée, consentement pour anonymisation confirmé)

---

## 10. Exit survey — Désinscription / désactivation

### 10.1 Trigger

- Endpoint `/settings/cancel` et `/settings/delete-account`
- Modal 1 question avant confirmation définitive

### 10.2 Question unique

> "Qu'est-ce qui fait que tu arrêtes PLI ?" (1 choix + champ libre optionnel)
> - Ça ne correspondait pas à ce que je cherchais
> - Trop de bugs / instable
> - Trop cher
> - Je n'ai pas pris le temps
> - Je vais continuer avec mon client actuel (lequel ?)
> - Autre : ____

### 10.3 Usage

- Taux par raison → dashboard PM
- Si > 20 % citent "bugs" → alarme immédiate priorisation
- Si > 30 % citent "ne correspondait pas" → signal positionnement à retravailler pour Launch

---

## 11. Synthèse hebdomadaire (template)

Remplie J7 et J10, 1 page max.

```markdown
# M5 — Synthèse feedback — [Date]

## Volumes
- Feedbacks widget : X (up) / Y (down) = ratio Z:1
- NPS : X (n = Y répondants)
- Intent payant : X %
- Membres Discord : X
- Interviews réalisées : X/5

## Tonalité dominante
[Enthousiaste / Positive / Mitigée / Négative] — [justification 2 lignes]

## Top 3 points positifs
1. [Thème] — [N mentions]
2. ...
3. ...

## Top 5 frictions / bugs
1. [Description] — [N mentions] — [Sévérité] — [Effort correctif]
2. ...

## Top 5 features demandées
1. [Description] — [N mentions] — [Décision : Launch / post-Launch / jamais]

## Segments utilisateurs identifiés
- [Segment] : [comportement observé, taux dans la beta]

## Actions proposées pour itération
- [ ] Fix immédiat : [...]
- [ ] Fix itération #1 / #2 : [...]
- [ ] Amélioration copy / onboarding : [...]
- [ ] Reporté post-Launch : [...]

## Signaux Launch
- Pro Launch : [points]
- Contre Launch : [points]
- Recommandation : [Go / Attendre X / No-Go]
```

---

## 12. Clôture M5 — Input pour rapport

Le 22 sept (J10), PM livre au founder :

1. Synthèse finale M5 (format §11 étendu)
2. Base de données feedback exportée (CSV)
3. Liste issues GitHub ouvertes/fermées M5 avec métriques
4. Courbes NPS / intent payant / rétention M5
5. Recommandation Go/No-Go Launch argumentée
6. Backlog priorisé V1.0 (post-Launch) pour clarté

Ces éléments alimentent `M5-CLOSURE-TEMPLATE.md`.

---

## 13. Ce qu'on **ne** fait **pas** en M5

- Pas de A/B testing complexe (données pas assez massives)
- Pas d'analyse cohorte long terme (trop tôt)
- Pas de roadmap publique (réservée post-Launch)
- Pas d'engagement sur features (on écoute, on ne promet pas)
- Pas de réponse "c'est dans la roadmap" aux users (formulation floue → préférer "c'est noté")

---

*Plan rédigé par PM agent en coordination avec UX agent et Founder. Revu J5 et J8 pour ajustements.*
