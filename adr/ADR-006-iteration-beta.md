# ADR-006 — Stratégie d'itération en beta privée (M4)

**Statut** : Accepté
**Date** : 12 août 2026
**Auteur** : Tech Lead
**Contexte** : Phase M4 (Beta privée, 100 invités)

---

## 1. Contexte

M4 marque la bascule du dogfooding interne au produit mis entre des mains extérieures. Le risque majeur est la **dérive de scope** : tout beta user a des suggestions, le founder est enthousiaste, l'équipe d'agents est rapide. Sans règle, on sort de M4 avec un produit moins stable que celui qu'on y fait entrer.

Par ailleurs, l'équipe est petite (0.8 FTE humain + agents) et M4 ne dure que 4 semaines. Chaque arbitrage de priorité coûte cher.

---

## 2. Décision

Pendant M4, nous adoptons les règles suivantes, non négociables :

### 2.1 Gel du backlog features

Aucune nouvelle fonctionnalité n'est développée pendant M4. Seuls sont admis :

- **Fix** de bugs (tout niveau de severity)
- **Polish UX** sur frictions remontées par ≥ 3 beta users
- **Performance** si p95 dégrade au-delà des cibles ADR-005

Exception unique : FEAT priorité ≥ 20 (severity 5 × frequency 4+) **et** effort < 1 jour dev **et** validation TL + PM + founder.

### 2.2 Cadence de release

- Release main production **chaque vendredi matin** (10h CET)
- Soak staging 24 h minimum avant prod
- Patch intermédiaire autorisé pour bug bloquant (severity 5, ouvert < 24 h)
- Pas de release en fin de journée, pas le weekend, pas le lundi (démarrage semaine propre)

### 2.3 Discipline batches d'invitation

4 batches de 25 users, invités à cadence fixe :

- Batch 1 : J1 (12 août)
- Batch 2 : J15 (27 août) — après itération #1
- Batch 3 : J19 (31 août)
- Batch 4 : J24 (05 septembre)

Si un batch révèle un bug bloquant avant J+3, **on retarde le batch suivant** de 3 jours minimum. La santé du produit prime sur le calendrier.

### 2.4 Règle de l'échantillon diversifié

Chaque batch est composé de :

- 6-7 users Gmail-only
- 6-7 users Microsoft-only
- 6-7 users multi-comptes
- 5-6 users « non-tech » (via réseau JMJ Consulting)

Objectif : éviter le biais « early adopters techno » qui donnerait un NPS surévalué.

### 2.5 Décision en cas de désaccord

Le triage feedback est tranché **par le PM**, sauf :

- Décision architecture : TL
- Décision sécurité / conformité : SEC + founder
- Décision commerciale / pricing : founder
- Arbitrage scope vs qualité : founder en dernier ressort

---

## 3. Alternatives considérées

### 3.1 Scope ouvert, feature-drive

**Rejeté** : risque fort de régressions sur des fonctions déjà livrées, NPS faible malgré nouvelles features (les users demandent stabilité avant nouveauté), dépassement calendrier M5.

### 3.2 Release continue (multi-fois / jour)

**Rejeté** : équipe trop petite pour opérer un vrai continuous deployment fiable en beta, risque d'instabilité perçue, pas de fenêtre claire de monitoring.

### 3.3 Beta rolling sans batches

**Rejeté** : impossible de corréler feedback à une version, biais temporel (les plus matures ont plus de recul).

---

## 4. Conséquences

### Positives

- Scope maîtrisé, effort concentré sur qualité observable
- Cadence prédictible, oncall gérable par 1 personne
- Corrélation claire feedback ↔ version ↔ batch
- Base solide pour ouvrir en M5 sans surprise

### Négatives

- Frustration possible des beta users demandant des features (mitigée par réponse publique "M5+")
- Rythme de release perçu lent par rapport à la cadence d'agents possible (hebdo plutôt que daily)
- Pas d'A/B testing, pas de champ d'expérimentation (accepté vu taille échantillon 100)

---

## 5. Métriques de suivi de cette décision

- Nb de releases / semaine (cible : exactement 1, tolérance 0-2)
- % fix vs feature dans les PR mergées (cible : ≥ 90 % fix/polish)
- Durée médiane ouverture → fermeture ticket bloquant (cible : < 48 h)
- NPS trend par batch (cible : stable ou en hausse de batch 1 à 4)

---

## 6. Révision

Ré-évaluation à la fin de M4 (09 septembre 2026), avant signature Go M5. Si la décision s'avère trop rigide, ajuster pour M5 (ouverture publique = besoin de feature velocity retrouvée).

---

*Signé TL, validé PM + Founder le 11 août 2026.*
