# Grille de triage feedback beta — PLI

**Owner** : PM · **Cadence** : 3× / semaine (lundi, mercredi, vendredi, 20 min chacun)
**Sources** : Discord `#bugs` + `#feedback` + `#feature-requests`, widget NPS, formulaire in-app, 1-to-1 founder.

---

## 1. Matrice frequency × severity

On scorise chaque item de 1 à 5 sur deux axes.

### Severity

| Score | Signification |
|---|---|
| 5 — Bloquant | L'utilisateur ne peut pas utiliser PLI ou perd des données |
| 4 — Majeur | Parcours clé cassé ou très dégradé, workaround pénible |
| 3 — Modéré | Friction notable sur un parcours secondaire |
| 2 — Mineur | Gêne cosmétique, sensibilité de swipe, copy |
| 1 — Trivial | Préférence personnelle, nice-to-have |

### Frequency

| Score | Signification |
|---|---|
| 5 | > 50 % des beta users remontent |
| 4 | 20-50 % |
| 3 | 10-20 % |
| 2 | 3-10 % |
| 1 | < 3 % (1-2 users seulement) |

### Priorité calculée

**Priorité = Severity × Frequency**

| Score | Action |
|---|---|
| ≥ 16 | Hot-fix immédiat (release patch dans la semaine) |
| 10-15 | Inclus dans le sprint en cours |
| 5-9 | Inclus dans le prochain sprint ou M5 |
| 1-4 | Backlog post-launch, re-scoré périodiquement |

---

## 2. Catégories de feedback

| Code | Catégorie | Exemples |
|---|---|---|
| BUG | Défaut fonctionnel | crash composer, sync qui boucle |
| UX | Friction ergonomie | swipe trop sensible, icône illisible |
| PERF | Lenteur perçue | liste qui saccade, recherche lente |
| FEAT | Demande de feature | raccourcis clavier, rules d'archivage |
| DOC | KB manquante / confuse | "où changer signature ?" |
| BILL | Question facturation | "qu'est-ce qui est inclus en trial ?" |
| SEC | Préoccupation sécurité | "où sont stockés mes mails ?" |
| OTHER | Autre | |

---

## 3. Workflow triage

```
Feedback entrant
   │
   ▼
[PM lecture < 24 h] ──► [Catégorisation + severity + frequency]
   │
   ▼
[Réponse initiale Discord / email] ◄── Template par catégorie
   │
   ▼
[Score priorité ≥ 16 ?] ─── oui ──► Hot-fix ticket créé, owner assigné J0
   │                                 │
   non                                ▼
   │                           Release patch cette semaine
   ▼
[Score 10-15 ?] ─── oui ──► Ticket sprint courant (si capacité) ou suivant
   │
   non
   ▼
[Score 5-9 ?] ─── oui ──► Backlog M4/M5
   │
   non
   ▼
[Score < 5] ──► Remerciement + "noté, on y pensera"
```

---

## 4. Règle anti-dérive scope

M4 est **fix + UX friction**. Toute demande FEAT (score ≥ 10) est :
1. Acceptée au backlog M5+ (pas M4)
2. Répondue publiquement : "On prend, mais ça attend M5 car on stabilise"
3. Candidate à l'étude de valeur (combien d'users la veulent, impact sur proposition de valeur)

Exception possible : FEAT avec priorité ≥ 20 **et** impact < 1 jour dev.

---

## 5. Templates de réponse Discord

### BUG

> Merci {user}, j'ai ouvert le ticket #{id}. Dans l'intervalle, un workaround : {workaround}. Mise à jour ici dès qu'on a un fix, cadence de release hebdo vendredi.

### UX

> Merci, bien noté — c'est le retour n°{count} sur ce point. On le priorise pour la release du {date}. Tu peux décrire ton parcours exact ? (étapes, ce que tu attendais, ce qui s'est passé)

### FEAT

> Super suggestion, merci. En M4 on ne fait que stabiliser, donc ça part au backlog M5+ (#{id}). Si plusieurs users la demandent on accélère. Compte-toi comme +1 automatique.

### DOC

> Bonne question, je la transforme en article KB. Lien ici dans 48 h : {placeholder}

---

## 6. Métriques de santé du triage

Publiées chaque vendredi dans `#annonces` :

- Nombre d'items reçus cette semaine
- Temps médian réponse initiale (cible < 24 h)
- Répartition par catégorie
- Top-5 items en cours de résolution
- Releases de la semaine (changelog)

---

## 7. Template NPS (widget in-app)

### Question principale

> Quelle est la probabilité que vous recommandiez PLI à un collègue ou à un proche ? (0 = très peu probable, 10 = très probable)

### Question suivante (conditionnelle)

- Score 0-6 (Détracteur) : « Qu'est-ce qui vous empêche de nous recommander aujourd'hui ? »
- Score 7-8 (Passif) : « Qu'est-ce qui vous ferait passer à 10 ? »
- Score 9-10 (Promoteur) : « Qu'est-ce qui vous plaît le plus ? »

### Bouton final

- « Envoyer »
- « Envoyer anonymement » (option secondaire, remplace user_id_hash par null)

### Méta capturée

- `score` (0-10)
- `comment` (0-500 car.)
- `user_id_hash` (sha256 salted) ou `null` si anonyme
- `app_version`
- `platform` (pwa-mobile, pwa-desktop)
- `days_since_signup`
- `created_at`

---

*Grille de triage approuvée par PM + Founder le 11 août 2026, veille Sprint 9.*
