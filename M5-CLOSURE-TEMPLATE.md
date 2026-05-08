# M5 — Rapport de clôture (template)

**Phase** : M5 — Beta publique (9 → 23 sept 2026)
**Date de clôture** : 22 septembre 2026 (J10)
**Auteurs** : PM agent (lead rédaction) + Founder (décision)
**Approbateurs** : PM + TL + SRE + SEC + Founder (signatures §10)
**Archive** : `pli-app/closures/M5.md`
**Jalon** : Go/No-Go Launch (S25)

> **Note** : ce fichier est un template à remplir le 22 septembre 2026. Les `[___]` sont à renseigner. Les sections marquées "À compléter" sont rédigées à chaud ce jour-là.

---

## 1. Résumé exécutif (TL;DR)

> **Décision proposée** : [ ] Go Launch S25 · [ ] Décalage Launch de [X] semaines · [ ] No-Go — pivot
>
> **Justification en 3 lignes** : [à compléter — les 3 faits principaux qui dictent la décision]

Exemple attendu si Go :
> Go Launch proposé pour la semaine 25 (30 sept – 6 oct 2026). M5 a livré [X] signups en 7 jours, 0 incident majeur, NPS [X], feedback ratio [X:1]. Les itérations #1 et #2 ont été déployées sans régression. Aucun critère du Checkpoint 4 n'est en rouge.

---

## 2. Métriques atteintes vs cibles

| Métrique | Cible M5 | Atteint | Status |
|---|---|---|---|
| Signups publics cumulés | 500 - 1000 | [___] | [ ] OK [ ] KO |
| Incidents P1 | 0 | [___] | [ ] OK [ ] KO |
| Downtime cumulé | < 30 min | [___] min | [ ] OK [ ] KO |
| Latence p95 API (moyenne M5) | < 500 ms | [___] ms | [ ] OK [ ] KO |
| Taux d'erreur 5xx (moyenne M5) | < 0.5 % | [___] % | [ ] OK [ ] KO |
| NPS | > 30 (cible 40) | [___] | [ ] OK [ ] KO |
| Ratio thumbs up/down | > 4:1 | [___] | [ ] OK [ ] KO |
| Intent payant (survey) | ≥ 15 % | [___] % | [ ] OK [ ] KO |
| Taux activation (1er compte mail connecté) | ≥ 60 % | [___] % | [ ] OK [ ] KO |
| Rétention J7 | > 40 % | [___] % | [ ] OK [ ] KO |
| IP email — taux inbox | > 95 % | [___] % | [ ] OK [ ] KO |
| Capacity validée (load test 3× trafic réel) | Oui | [ ] Oui [ ] Non | [ ] OK [ ] KO |
| 0 vulnérabilité SEC haute/critique ouverte | 0 | [___] | [ ] OK [ ] KO |
| Status page verte 95 % du temps | ≥ 95 % | [___] % | [ ] OK [ ] KO |

**Synthèse** : [X] critères OK sur 14, [Y] critères en vigilance, [Z] en rouge.

---

## 3. Trafic et funnel

### 3.1 Trafic landing
- Visiteurs uniques M5 : [___]
- Sources principales : [ex. blog founder 45 %, LinkedIn organique 25 %, direct 18 %, …]
- Pics de trafic : [dates/heures, cause]

### 3.2 Funnel signup
```
Visite landing       → [___] (100 %)
  ↓ [___] %
Clic "Essayer"       → [___]
  ↓ [___] %
Formulaire signup    → [___]
  ↓ [___] %
Compte créé          → [___]
  ↓ [___] %
Email vérifié        → [___]
  ↓ [___] %
1er compte connecté  → [___]   ← activation
  ↓ [___] %
Trial actif 48h+     → [___]
```

### 3.3 Conversion
- Taux global visite → signup : [___] % (cible ≥ 5 %)
- Taux signup → activation : [___] % (cible ≥ 60 %)
- Taux activation → intent payant : [___] % (cible ≥ 15 %)

---

## 4. Incidents et post-mortems

### 4.1 Incidents déclarés M5

| Date | Heure début | Durée | Gravité | Cause | Post-mortem |
|---|---|---|---|---|---|
| [date] | [HH:MM] | [X min] | [P1/P2/P3] | [1 ligne] | [lien] |
| ... | | | | | |

### 4.2 Bilan

- Total incidents : [___] ([P1] + [P2] + [P3])
- Downtime cumulé : [___] min
- MTTR (Mean Time To Resolution) : [___] min
- MTTA (Mean Time To Acknowledge) : [___] min
- Post-mortems publiés sur `status.pli.app/incidents` : [___] / [___]

### 4.3 Leçons principales

1. [Leçon 1 en 1 ligne]
2. [Leçon 2]
3. [Leçon 3]

---

## 5. Feedback utilisateurs

### 5.1 Volumes collectés
- Widget feedback : [X] thumbs up + [Y] thumbs down + [Z] entrées texte
- NPS répondants : [X] / [Y] users J+7 (taux [Z] %)
- Discord membres fin M5 : [X]
- Emails support traités : [X] (SLA < 4h respecté [Y] %)
- Interviews qualitatives : [X] / 5 (cf. annexe)

### 5.2 Top 5 points positifs

1. [Thème — N mentions]
2. ...
3. ...
4. ...
5. ...

### 5.3 Top 5 frictions / bugs

| # | Description | Fréquence | Sévérité | Status |
|---|---|---|---|---|
| 1 | [...] | [N] | [H/M/B] | [ ] Fixé M5 [ ] Ticket ouvert [ ] Reporté |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### 5.4 Top 5 features demandées

| # | Description | Fréquence | Décision |
|---|---|---|---|
| 1 | [...] | [N] | [ ] V1.0 [ ] V1.1 [ ] V1.2 [ ] V2 [ ] No |
| 2 | | | |
| ... | | | |

### 5.5 Exit survey (désinscription/désactivation)

| Raison principale | Nombre | % |
|---|---|---|
| Ça ne correspondait pas | [___] | [___] % |
| Trop de bugs | [___] | [___] % |
| Trop cher | [___] | [___] % |
| Pas pris le temps | [___] | [___] % |
| Continue avec autre client ([liste]) | [___] | [___] % |
| Autre | [___] | [___] % |

### 5.6 Citations représentatives

> _"[extrait]"_
> — [anonyme / pseudo avec accord]

> _"[extrait]"_
> — [anonyme / pseudo avec accord]

---

## 6. Itérations produit déployées en M5

### Itération #1 (J8 — 18 sept 2026)
- [Fix 1] — [lien PR]
- [Fix 2] — [lien PR]
- [Fix 3] — [lien PR]
- Changelog public : [lien]
- Régression constatée : [ ] Non [ ] Oui — [détails]

### Itération #2 (J10 — 22 sept 2026)
- [Fix 1]
- [Fix 2]
- Changelog public : [lien]
- Régression constatée : [ ] Non [ ] Oui

---

## 7. Bugs ouverts (snapshot J10)

| Priorité | Nombre | Plan |
|---|---|---|
| P0 | [___] | [À traiter en hotfix avant Launch si > 0] |
| P1 | [___] | [À traiter avant Launch] |
| P2 | [___] | [Traitement V1.0 ou V1.1] |
| P3 | [___] | [Backlog post-Launch] |

**Seuils Go Launch** : P0 = 0, P1 ≤ 2 (avec plan de résolution semaine Launch).

---

## 8. Capacity & performance

### 8.1 Charge observée
- Pic signups/heure : [___] (vs 500-2000 testé en k6)
- Pic connexions simultanées : [___]
- Pic DB connexions : [___]
- Marge capacity vs prod actuelle : [___] ×

### 8.2 Comparatif load test vs réel

| Métrique | k6 test | Réel M5 |
|---|---|---|
| Signups/heure pic | 2000 | [___] |
| p95 API sous charge | [X] ms | [___] ms |
| Queue sync drain time | [X] s | [___] s |

### 8.3 Provisionning Launch S25

- Recommandation : [ ] Statu quo [ ] Scaling additionnel nécessaire
- Détail : [si scaling : combien de replicas, quelles DB, etc.]

---

## 9. Communication & activation

### 9.1 Résultats canaux

| Canal | Impressions | Engagement | Signups attribués |
|---|---|---|---|
| Article blog founder | [___] views | [___] comments | [___] |
| LinkedIn posts founder | [___] impr. | [___] reactions | [___] |
| Thread X/Bluesky/Threads | [___] impr. | [___] reshares | [___] |
| Newsletter waitlist | [___] envoyés, [___] ouverts | [___] clicks | [___] |
| Discord | [___] membres | — | [___] |

### 9.2 Kit Launch — État d'avancement

- [ ] Vidéo démo 90s
- [ ] Page ProductHunt (tagline, gallery, 1er commentaire)
- [ ] Draft "Show HN"
- [ ] Press kit ZIP
- [ ] Communiqué de presse FR+EN
- [ ] Vidéo founder "pourquoi PLI" 3 min

---

## 10. Décision Go/No-Go Launch

### 10.1 Analyse des critères (Checkpoint 4 — cf. M5-KICKOFF §8)

| Critère | Status | Commentaire |
|---|---|---|
| 500-1000 signups | [ ] OK [ ] KO | [...] |
| 0 P1 non résolu | [ ] OK [ ] KO | |
| Downtime cumulé < 30 min | [ ] OK [ ] KO | |
| Funnel conforme | [ ] OK [ ] KO | |
| Feedback ratio > 4:1 | [ ] OK [ ] KO | |
| NPS > 30 | [ ] OK [ ] KO | |
| 0 vuln SEC H/C | [ ] OK [ ] KO | |
| 0 bug P1/P2 bloquant | [ ] OK [ ] KO | |
| Status verte > 95 % M5 | [ ] OK [ ] KO | |
| Taux inbox > 95 % | [ ] OK [ ] KO | |
| Capacity 3× validée | [ ] OK [ ] KO | |
| Assets Launch prêts | [ ] OK [ ] KO | |

### 10.2 Décision finale

- [ ] **Go Launch S25** (30 sept – 6 oct 2026)
- [ ] **Décalage Launch de 1 semaine** (raison : ___________)
- [ ] **Décalage Launch de 2 semaines** (raison : ___________)
- [ ] **No-Go — pivot nécessaire** (raison : ___________)

### 10.3 Actions avant Launch (si Go)

- [ ] Finaliser kit Launch (si incomplet)
- [ ] Fix dernier P1 / P2 critique : [ticket]
- [ ] Brief final presse 2 jours avant J-Launch
- [ ] Configuration Stripe live vérifiée sur transactions réelles M5 ([X] facturations OK)
- [ ] Status page : message "Launch officiel — bienvenue aux nouveaux users"
- [ ] Founder : 3 jours de repos (23-25 sept) avant reprise Launch

### 10.4 Signatures

| Rôle | Nom / Agent | Avis | Signature | Date |
|---|---|---|---|---|
| PM | [___] | [ ] Go [ ] No-Go [ ] Décalage | | 22/09/2026 |
| TL | [___] | [ ] Go [ ] No-Go [ ] Décalage | | 22/09/2026 |
| SRE | [___] | [ ] Go [ ] No-Go [ ] Décalage | | 22/09/2026 |
| SEC | [___] | [ ] Go [ ] No-Go [ ] Décalage | | 22/09/2026 |
| **Founder** | Jean-Marie Simeoni | **[ ] Go [ ] No-Go [ ] Décalage** | | 22/09/2026 |

---

## 11. Leçons apprises M5

### 11.1 Ce qui a bien marché

1. [...]
2. [...]
3. [...]

### 11.2 Ce qui a moins bien marché

1. [...]
2. [...]
3. [...]

### 11.3 À reproduire pour le Launch

1. [...]
2. [...]

### 11.4 À éviter pour le Launch

1. [...]
2. [...]

---

## 12. Backlog priorisé post-Launch (V1.0 → V1.1)

### V1.0 (Launch S25 — fixes bloquants uniquement)
- [ ] [issue] — [description]
- [ ] [issue] — [description]

### V1.1 (1-3 mois post-Launch)
- [ ] [feature / fix prioritaire]
- [ ] [...]

### Décisions reportées
- [ ] [feature] — décision : V1.2 / V2 / jamais

---

## 13. Annexes

- [Annexe A] : Export feedbacks CSV — `closures/M5-feedbacks.csv`
- [Annexe B] : Post-mortems individuels — `post-mortems/M5/`
- [Annexe C] : Interviews utilisateurs (anonymisées) — `interviews/M5/`
- [Annexe D] : Screenshots dashboards J10 — `closures/M5-dashboards/`
- [Annexe E] : Rapports load tests k6 — `ops/loadtest/reports/M5/`

---

*Template rédigé par PM + Founder. À remplir le 22 septembre 2026 (J10 M5) en séance de clôture, signé par tous les rôles de l'équipe d'agents + founder.*
