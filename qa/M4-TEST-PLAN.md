# M4 — Plan de tests beta

**Propriétaire** : QA · **Cycle** : smoke daily + E2E pré-release + reg. post-fix
**Cadre** : ce plan couvre les livrables M4 (waitlist, invitations, onboarding tour, NPS widget, feedback fab) et la non-régression des features M1-M3.

---

## 1. Inventaire des scénarios

### 1.1 E2E critiques (smoke daily)

Exécutés automatiquement chaque matin 06h CET sur staging. Échec = rollback immédiat.

| ID | Scénario | Durée cible |
|---|---|---|
| SMOKE-001 | Signup → email vérif → login → connecter Gmail → sync 10 msg → voir la liste | 90 s |
| SMOKE-002 | Ouvrir conversation → répondre → envoyer → vérif destination externe | 60 s |
| SMOKE-003 | Recherche "invoice" → résultats ≤ 300 ms → ouvrir 1er résultat | 30 s |
| SMOKE-004 | Épinglage d'une conv → drag reorder → persisté après refresh | 30 s |
| SMOKE-005 | Swipe gauche une conv → unread → swipe droit → archive | 30 s |
| SMOKE-006 | Stripe test : trial → upgrade → change plan → cancel (mode test) | 180 s |

### 1.2 E2E M4 (pré-release)

| ID | Scénario | Remarques |
|---|---|---|
| M4-E2E-001 | Waitlist signup → email confirm → lien confirm → status confirmed | Tester aussi lien expiré (7 j) |
| M4-E2E-002 | Admin issue batch #1 → 25 invitations → emails partis (MailHog check) | Vérifier quotas segment |
| M4-E2E-003 | User reçoit email → clique lien `/invited?code=...` → signup → redeem → user.plan=beta | Happy path |
| M4-E2E-004 | Code déjà consommé → message d'erreur clair + CTA waitlist | Error path |
| M4-E2E-005 | Code expiré (backdate DB 15 j) → message d'erreur clair | Error path |
| M4-E2E-006 | Premier lancement → tour 5 étapes apparaît → Skip → tour_completed_at renseigné | Happy skip |
| M4-E2E-007 | Tour complet 5 étapes → Finish → tour_completed_at renseigné | Happy complete |
| M4-E2E-008 | 2e lancement après tour → pas de tour | Idempotence |
| M4-E2E-009 | User J+7 d'usage → widget NPS s'affiche → submit score 9 → thanks | Happy path |
| M4-E2E-010 | Widget NPS dismiss → 30 jours plus tard re-apparition (simulation clock) | Cooldown |
| M4-E2E-011 | Feedback fab : bug → message → submit → 201 + admin voit la submission | Auth user |
| M4-E2E-012 | Feedback rate-limit : 4e submission dans l'heure → 429 | Rate-limit |
| M4-E2E-013 | Load test 100 users simultanés → p95 /conversations < 400 ms | Capacity |

### 1.3 Non-régression features M1-M3

Suite automatique Playwright ~40 scénarios. Exécutée à chaque PR + pré-release.

---

## 2. Stratégie de reproduction des bugs beta

Pour chaque ticket Discord catégorisé **BUG** :

1. **Capture de contexte** dans la réponse triage :
   - Version app, plateforme, navigateur, batch
   - Parcours précis (clics, URL, temps écoulé depuis signup)
   - Capture écran / vidéo si possible
2. **Reproduction locale** :
   - Script Playwright si parcours connu
   - Docker-compose + DB dump beta (anonymisé) si lié aux données
3. **Test de régression obligatoire** :
   - Ajouté à la suite E2E **avant** le merge du fix
   - Commenté avec le lien Discord + batch d'origine

---

## 3. Tests de charge (load)

### 3.1 Scénarios k6

```javascript
// infra/loadtest/k6-beta.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 20 },   // warm-up
    { duration: '5m', target: 100 },  // plateau beta
    { duration: '2m', target: 150 },  // surge check
    { duration: '3m', target: 0 },
  ],
  thresholds: {
    'http_req_duration{route:conversations}': ['p(95)<400'],
    'http_req_duration{route:search}': ['p(95)<300'],
    'http_req_failed': ['rate<0.01'],
  },
};

export default function () {
  const base = __ENV.STAGING_URL;
  const token = __ENV.BETA_USER_TOKEN;
  const headers = { Authorization: `Bearer ${token}` };

  const r1 = http.get(`${base}/conversations?limit=30`, { headers, tags: { route: 'conversations' } });
  check(r1, { '200': r => r.status === 200 });

  const r2 = http.get(`${base}/search?q=invoice`, { headers, tags: { route: 'search' } });
  check(r2, { '200': r => r.status === 200 });

  sleep(2 + Math.random() * 3);
}
```

### 3.2 Exécution

- Nightly CI sur staging (GitHub Actions scheduled)
- Avant chaque release hebdo
- Avant chaque batch (J-1 du batch)

---

## 4. Tests de sécurité

- **Burp community** : scan hebdomadaire sur staging
- **OWASP ZAP** : CI job mensuel
- **Revue manuelle** : endpoints nouveaux (cf. `security/M4-SECURITY-CHECKLIST.md` §4)

---

## 5. Critères de sortie (pré-release)

Release en prod autorisée si **tous** :

- [ ] Tous smoke E2E verts
- [ ] Tests unitaires 100 % green, coverage ≥ 70 % sur modules touchés
- [ ] Load test nightly vert (p95 < cible, 0% 5xx)
- [ ] Pas d'alerte P1/P2 ouverte en staging
- [ ] Changelog interne rédigé (pour comm Discord beta)
- [ ] Soak staging ≥ 24 h

---

## 6. Environnements

| Env | Usage | Reset | Données |
|---|---|---|---|
| **local** | dev | à la demande | seed minimal (3 users, 50 mails factices) |
| **CI** | PR validation | chaque run | seed full déterministe |
| **staging** | pré-prod | nightly clean-up > 30 j | seed + comptes beta fictifs |
| **prod** | users réels | jamais | données réelles (RGPD strict) |

---

## 7. Fixtures beta

Comptes de test dédiés (hors prod) :

- `beta-qa-gmail@pli.test` — compte Gmail factice, 200 msg
- `beta-qa-ms@pli.test` — compte Microsoft factice, 200 msg
- `beta-qa-mixed@pli.test` — 2 comptes connectés, 500 msg
- `beta-qa-fresh@pli.test` — compte sans historique (pour tour onboarding)

---

*Plan de test M4 publié par QA le 12 août 2026, revu à chaque sprint retro.*
