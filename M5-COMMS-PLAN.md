# M5 — Plan de communication · Beta publique PLI

**Phase** : M5 (9 → 23 sept 2026)
**Public cible** : prospects tech/freelances FR + early adopters, utilisateurs exigeants sur la vie privée email
**Tonalité** : confiant, humble, technique mais accessible, pas de hype, pas d'enchères émotionnelles
**Objectif communication** : 500-1000 signups, feedback ratio thumbs up/down > 4:1, posture "on construit avec vous"
**Auteurs** : PM + Founder · **Revue** : UX (cohérence voix) · **Relecture CONT + feu vert direction obligatoires**

> **⚠️ Freeze communication externe — 2026-04-22 → validation Checkpoint 4 M5**
> L'ordre de mission du 2026-04-22 (§7) interdit toute publication externe avant feu vert direction post-integration-sprint.
> Tous les drafts sont dans `docs/governance/launch/drafts/` et gouvernés par `docs/governance/launch/publications-log.md`.
> **Aucune ligne de ce plan comms ne déclenche d'envoi sans un `statut=approved` signé direction** dans le journal.
> Chiffres cités : exclusivement mesurés sur **binaire intégré** (branche `release-v1`).

---

## 1. Philosophie de communication M5

M5 n'est pas le Launch. **La communication doit être délibérément sobre** pour trois raisons :

1. **Éviter le pic non maîtrisé** — infra dimensionnée pour ramp-up progressif, pas pour un Show HN à 10k visites/jour.
2. **Réserver l'énergie Launch** — garder l'effet "nouveauté" pour S25 (ProductHunt + HN).
3. **Valider le funnel en vrai** — mesurer conversion sans biais d'effet d'annonce massif.

**Règle d'or** : en M5 on ne dit jamais "c'est lancé". On dit "la beta publique est ouverte".

---

## 2. Calendrier de publications

### Phase 0 — Pré-ouverture (J-7 → J-1, semaine M4 finale)

| Date | Canal | Contenu | Owner | État |
|---|---|---|---|---|
| J-7 (2 sept) | Newsletter PLI beta privée | "La beta publique arrive le 16 sept" — merci aux 100 early, invitation à partager | PM | Draft |
| J-3 (6 sept) | LinkedIn founder | Post réflexif "Ce que 4 mois de construction m'ont appris sur l'email" | Founder | Draft |
| J-1 (8 sept) | Mail beta privée | "Aperçu des changements, nouveauté du widget feedback, merci encore" | PM | Draft |

### Phase 1 — J6 : activation discrète (16 septembre 2026)

| Heure CET | Canal | Contenu | Owner |
|---|---|---|---|
| 08h00 | Flag prod on | Activation `public_signup_enabled=true` | SRE |
| 08h15 | Status page | Annonce "Beta publique ouverte" (info, pas incident) | SRE |
| 08h30 | Blog PLI | Publication article `docs/governance/launch/drafts/blog-pourquoi-pli.md` (après FV direction, ligne B-01 `publications-log.md`) | Founder |
| 09h00 | LinkedIn founder | Post annonce lien blog, ton mesuré | Founder |
| 10h00 | Newsletter publique | Email à liste waitlist (si > 200 inscrits) avec lien signup | PM |
| 12h00 | Discord PLI | Annonce #annonces + ouverture public | PM |
| — | Réseaux complémentaires | **Silence volontaire** X/Bluesky/Threads jusqu'à J4 | — |

### Phase 2 — J7-J8 : observation & amplification sobre

| Date | Canal | Contenu | Owner |
|---|---|---|---|
| J7 (17 sept) | LinkedIn founder | Partage métriques transparentes "J+1 : 120 signups, latence p95 430 ms, 0 incident" | Founder |
| J8 (18 sept) | Blog PLI | Changelog public "Ce qu'on a amélioré en 48h" (résultat itération #1) | PM |
| J8 | LinkedIn founder | Repartage changelog, ton "on écoute" | Founder |

### Phase 3 — J9 : amplification élargie (21 septembre 2026)

| Heure | Canal | Contenu | Owner |
|---|---|---|---|
| 10h00 | X / Twitter | Thread 5 tweets "Ce que PLI fait différemment (mode Local)" | Founder |
| 10h15 | Bluesky | Mirror thread X | Founder |
| 10h30 | Threads | Mirror thread X | Founder |
| 14h00 | LinkedIn founder | Post "5 jours de beta publique : retours utilisateurs + leçons" | Founder |
| — | Hacker News | **Pas de post HN en M5** — réservé Launch | — |
| — | ProductHunt | **Pas de post PH en M5** — réservé Launch | — |

### Phase 4 — J10 : préparation Launch

| Date | Canal | Contenu | Owner |
|---|---|---|---|
| J10 (22 sept) | Blog PLI | "5 jours de beta publique : le rapport complet" (métriques, décision Launch) | Founder |
| J10 | Discord | "On lance officiellement le [date Launch] — restez avec nous" | PM |
| J10 | LinkedIn | Partage rapport beta publique | Founder |

---

## 3. Messages clés (positioning pendant M5)

### Message principal
> **PLI rassemble tes emails par contact, comme une messagerie — et tourne en local si tu veux.**

### Messages secondaires (pour varier les angles)

- **Angle vie privée** : "Tes emails restent chez toi. Vraiment. Mode Local = jamais dans nos serveurs."
- **Angle usage** : "Plus de thread dispersés. Un contact = une conversation continue."
- **Angle beta** : "On ouvre à 1000 personnes. On écoute, on itère, on documente tout publiquement."
- **Angle technique** (pour X/HN plus tard) : "FastAPI + SQLite-FTS5 en Local, PostgreSQL en Cloud, architecture dual assumée."

### Phrases à éviter en M5

- ❌ "Révolutionnaire" / "game changer" / "réinventer l'email"
- ❌ "IA native" (faux en M5, prévu V2)
- ❌ "Meilleur client email" (pas de comparatif absolu en beta)
- ❌ "Gratuit" sans préciser "14 j d'essai"
- ❌ "Bientôt disponible" (on est disponible)

---

## 4. Briefs par canal

### Blog PLI — Article founder "Pourquoi PLI"

- **Format** : 1 200 à 1 800 mots, 6-7 min lecture
- **Structure** : pourquoi j'ai commencé → ce qui cloche dans l'email → le pari Local-first → ce que c'est aujourd'hui → ce que vous pouvez faire (CTA)
- **SEO** : titre H1 < 60 car., meta-desc < 155 car., 1 image OG 1200×630
- **CTA** : "Essayer PLI 14 jours, sans CB" → `/signup`
- **Contenu** : cf. [blog/blog-pourquoi-pli.md](blog/blog-pourquoi-pli.md)

### LinkedIn — Posts founder

- **Ton** : 1re personne, pas de jargon, 1 idée forte par post, 600-1200 car.
- **Structure** : hook (1 ligne) → contexte → point → conclusion humaine
- **Pas de CTA agressif** : une ligne neutre en fin "Lien en commentaire" ou "Beta publique ouverte — lien pinné"
- **Visuels** : 1 screenshot simple par post (pas de carrousel M5 — réservé Launch)
- **Cadence** : 3 posts sur 14 jours (J-3, J+1, J+5)

### X/Twitter / Bluesky / Threads — Threads J9

- **Format** : 5 tweets max, un seul thread mirroré sur les 3 plateformes
- **Ton** : factuel technique, 1 info par tweet
- **Pas de CTA dans tweet 1** : on pose le problème d'abord
- **CTA tweet 5** : lien signup + mention "beta, pas Launch officiel"

### Newsletter — Liste waitlist + beta privée

- **Outil** : Buttondown ou ConvertKit (configuré M3)
- **Objet** : courts, concrets — "La beta publique est ouverte" / "Ce qu'on a appris en 48h"
- **Préférer texte brut** aux templates HTML complexes en M5 (proximité > production value)
- **Désinscription** : un clic, sans interstitiel

### Discord PLI

- **Modération** : PM + founder connectés 2×/jour minimum
- **Réponse aux signalements** : < 4h en heures ouvrées, 12h week-end
- **Pinned messages** :
  - #annonces : règles + liens utiles
  - #bugs : template de bug report
  - #feedback : "on lit tout, on répond quand on peut, merci"
- **Pas d'événements live en M5** (AMA reportés post-Launch)

### Press (FR tech media) — **Pas en M5**

- Frandroid / Numerama / Usine Digitale / Journal du Net / Maddyness → **réservés Launch S25**
- En M5 : briefing préparatoire envoyé J5 à 2-3 journalistes identifiés, sous embargo Launch.

---

## 5. Mesure & KPIs communication

### Indicateurs suivis quotidiennement (dashboard PM)

| Métrique | Source | Cible M5 |
|---|---|---|
| Trafic landing `/` | Plausible / Umami | 5 000-15 000 visiteurs uniques |
| Taux visit → signup | Plausible + DB | ≥ 5 % |
| Signups totaux | DB | 500-1000 |
| Taux trial actif (1er compte mail connecté) | DB | ≥ 60 % des signups |
| Intent payant (survey J7) | Feedback widget | ≥ 15 % |
| NPS | Survey J7 in-app | ≥ 30, cible 40 |
| Ratio thumbs up/down | Widget feedback | ≥ 4:1 |
| Membres Discord | Discord | 100-300 |
| Mentions LinkedIn | Recherche manuelle / Mention | > 20 |
| Retweets/reshares thread J9 | X/Bluesky | Variable, non cible |
| Article blog — pageviews | Plausible | 3 000-8 000 |
| Temps moyen article blog | Plausible | > 3 min |

### Indicateurs qualitatifs (revus J8 et J10)

- Tonalité majoritaire du feedback (positif / mitigé / négatif)
- Thèmes récurrents (onboarding, perf, manque, bug)
- Champions identifiés (users qui parlent spontanément de PLI)
- Détracteurs à comprendre (pourquoi désinscription / thumbs down)

---

## 6. Kill switch communication

Si une de ces conditions est remplie, la communication externe est **suspendue** et le founder décide d'une stratégie de crise :

- Incident P1 non résolu > 30 min
- Bug visible côté utilisateur impactant > 20 % des users
- Fuite de données suspectée (même non confirmée)
- Vague de signalements négatifs > 30 thumbs down en 2h

**Action** : statut "maintenance" sur status page, post Discord neutre "on enquête", pas de tweet ni post LinkedIn tant que non résolu, post-mortem public dans les 48 h.

---

## 7. Kit assets Launch (préparé en M5, publié S25)

L'équipe prépare **en parallèle** les assets pour Launch S25, sans les diffuser en M5 :

- [ ] Vidéo démo 90 secondes (script + screen recording)
- [ ] Page ProductHunt (tagline, gallery 6 images, first comment draft)
- [ ] Draft "Show HN" (titre + 1er commentaire = l'histoire)
- [ ] Press kit ZIP : logo, screenshots HD, founder bio, elevator pitch FR+EN
- [ ] Communiqué de presse FR + EN (400 mots)
- [ ] Vidéo founder "pourquoi PLI" 3 min (format LinkedIn natif)

**Deadline kit Launch** : J8 (18 sept), revue J9, validation founder J10.

---

## 8. Contacts externes à briefer pour Launch (pas en M5)

| Contact | Canal | Angle | Action M5 |
|---|---|---|---|
| Journaliste Numerama tech | Email perso | Vie privée email + solo founder | Email de teasing J5, embargo Launch |
| Journaliste Frandroid | Email perso | PWA mobile + alternative | Email teasing J5 |
| Journaliste Usine Digitale | Email perso | SaaS français | Email teasing J8 |
| 3 influenceurs tech FR (1k-10k followers) | DM X/LinkedIn | Essai gratuit prioritaire | DM J3 avec accès prioritaire |
| Communauté IndieHackers FR | Forum | Solo dev journey | Post "Ask HN: I'm launching soon" S25 |

---

## 9. Ton de voix PLI — rappel pour toute prise de parole

- **Direct sans être brutal** : "c'est cassé, on corrige dans l'heure" > "un petit désagrément technique mineur"
- **Technique mais accessible** : donner les chiffres (p95 en ms) dans les posts tech ; dans les posts grand public, utiliser "rapide comme ton client actuel"
- **Humble assumé** : "on est 1 personne + des agents, on ne prétend pas tout couvrir"
- **Factuel > marketing** : chaque claim chiffré ou retirer
- **Vie privée comme valeur, pas comme argument** : ne pas dramatiser, juste expliquer

---

*Plan de communication rédigé par PM, validé par founder. Revu à J5 (mid-sprint) pour ajuster selon trafic observé.*
