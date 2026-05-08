# M2 — Rétrospective · Ce qui a marché, ce qu'on referait autrement

> **Milestone** : M2 — Mode dual Local + Cloud + Paiement
> **Durée** : 4 semaines (semaines 11-14) · 2 sprints · 10 user stories livrées
> **Facilité par** : Claude-PM
> **Date** : 2026-07-15
>
> Cadre : Keep / Change / Try. Pas de juge ni coupable — on tire les leçons d'une étape.

## Ce qui a marché (Keep)

### 1 · Les ADR rédigés *avant* le code
Les 6 ADR (adapters, multi-tenancy, JWT, Stripe, emails, licences) ont évité 3 reworks majeurs qui seraient arrivés si on avait codé d'abord.

**Exemple concret** : sur les JWT, l'ADR 0003 a forcé la question "que fait-on si le refresh token fuite ?". La réponse — *revoke all sessions on replay* — est arrivée en 1 paragraphe, et le code a été écrit autour. Si on avait commencé par le code, on aurait probablement écrit un refresh naïf et découvert le trou au test de sécu.

**À garder** : un ADR par décision non-triviale, en moins de 2 h d'écriture, validé par TL + domain lead.

### 2 · Le test d'isolation tenant bloquant en CI
Bloquer la CI sur `test_tenancy_isolation.py` a été la meilleure décision sécurité du milestone. Au total, **3 bugs d'isolation** ont été détectés avant merge :

- Une route `/contacts/{id}` qui faisait un lookup direct sans filtre `user_id`.
- Un bug dans `TenantScopedRepository._check_sql` qui laissait passer les UPDATEs sans WHERE.
- Un leak d'objets S3 (clés pas préfixées `t/{tenant}/`) détecté lors de la revue de PR.

**À garder** : tout nouveau domaine tenant-scopé doit être ajouté au test paramétré avant d'être mergé. Pas de dispense, même pour un "endpoint interne".

### 3 · L'abstraction `EmailProvider` avec memory en fallback
Faire tourner les 48 tests en < 0.5 s sans réseau a changé la qualité de vie développeur. On écrit un test d'email comme on écrit un test unitaire — pas de friction, pas de flaky network.

**Bonus** : le fait que `MemoryEmailProvider` ait une vraie liste `outbox` a permis d'écrire des assertions *métier* ("le bon template a été envoyé au bon user avec le bon contexte") au lieu d'assertions *infra* ("le SMTP mock a été appelé").

### 4 · Le pattern adapter + DI container
Avant, on avait déjà un petit `if mode == "local"` ici et là. Le refactor en début de sprint 5 a centralisé tout ça dans `pli/adapters/`. Résultat : on peut lire une route métier de bout en bout sans voir une seule mention de "local" ou "cloud". C'est une énorme réduction de charge cognitive.

**À garder** : au moindre nouvel usage "divergent entre les 2 modes", on ajoute une abstraction dans adapters/, pas un if local.

## Ce qu'on referait autrement (Change)

### 1 · Les migrations dual-dialect SQLite ↔ PostgreSQL
C'était douloureux. On a dû écrire un helper `_is_sqlite()` dans Alembic et padder la migration de `if _is_sqlite(): ... else: ...`. Le script initial a été réécrit **4 fois** avant de tourner dans les deux modes.

**À changer** : pour M3, envisager deux migrations racine distinctes (une SQLite, une PG) et un registre Python qui choisit le bon fichier en fonction du `settings.mode`. Plus de lignes, mais chaque fichier est lisible. Décision déléguée à Claude-TL, ADR à suivre.

### 2 · L'onboarding wizard trop tard dans le sprint
Planifié jour 8 sur 10, on n'a eu qu'une journée pour le tester en situation réelle. Résultat : le step "Sync" n'a pas d'animation de loading suffisante, et on a découvert en démo Founder que `/sync/status` ne fait pas le bon comptage sur mode local.

**À changer** : prioriser l'UX end-to-end en **milieu** de sprint, pas en fin. Les parcours utilisateurs multi-écrans méritent un prototype cliquable dès la moitié du sprint pour vérifier les transitions.

### 3 · Les 2 configurations Stripe (trial vs no-trial) pas assez documentées
`PLI_STRIPE_TRIAL_DAYS=0` désactive le trial — utile pour les coupons, mais indocumenté en dehors du `.env.example`. Un dev qui déploie en staging avec `trial_days=14` puis change la config en prod pourrait casser des flows.

**À changer** : ajouter une section "Configuration Stripe" au README avec les 4 combinaisons possibles (trial on/off × coupon on/off) et leurs conséquences UX.

### 4 · Le coverage backend qui stagne à 76 %
On a livré des tests mais jamais chassé activement la couverture. Les 24 points manquants sont presque tous dans `api/billing.py` (routes stripe non testées end-to-end) et `emails/sender.py` (branche "audit failed"). Ce sont des zones qu'on **va** toucher en M3.

**À changer** : mettre un gate CI à 80 % pour M3 (pas rétroactif sur M2 pour ne pas bloquer le GO). La dette se paye à l'itération qui la crée, pas à la suivante.

## Ce qu'on essaye au prochain cycle (Try)

### 1 · Pair programming pour les refactors d'architecture
L'adaptation du pattern adapter a été faite en solo par Claude-BE, puis revue. La revue a pris 3 allers-retours. Pour les prochains refactors structurels (M3 : décision sur *SearchAdapter* PG → Meilisearch ?), on teste le pair programming TL+BE en début d'implémentation. Si ça marche, on généralise ; sinon on revient.

### 2 · Un runbook "Incident paiement" avant la bêta
Aujourd'hui, si le webhook Stripe tombe, on reçoit une alerte Sentry mais il n'y a pas de procédure écrite. Pour M3, on rédige un runbook court ("si webhooks en erreur : vérifier signature, tester en local, rejouer events depuis dashboard"). Objectif : qu'un dev qui n'a pas touché Stripe puisse traiter l'incident seul à 3 h du matin.

### 3 · Une métrique "Temps inscription → 1er email lu"
On a construit le parcours mais on ne mesure pas la friction. Ajouter en M3 une métrique simple : quel est le délai médian entre "user créé" et "user a ouvert son 1er message dans PLI" ? Si > 10 min en bêta, on a un problème d'onboarding.

### 4 · Un doc "Architecture en une page" pour les bêta-testeurs curieux
La bêta va attirer des devs. Un schéma simple montrant Local vs Cloud, les données qu'on stocke (et ne stocke pas), et le flow paiement fera gagner 10 questions de support par semaine.

## Chiffres clés M2

- **Stories livrées** : 18/18 (Sprint 5: 8, Sprint 6: 10)
- **Story points** : 52 pts · vélocité 26 pts/sprint (stable vs M1)
- **Incidents bloquants** : 0
- **Bugs trouvés en CI avant prod** : 7 (dont 3 critiques, cf. section Keep)
- **Lignes de code ajoutées** : ~5 400 (backend 2 800 · frontend 1 900 · docs 700)
- **ADR produits** : 6
- **Temps setup dev first-run** : 11 min (cible M3 : ≤ 5 min)

## Remerciements

Merci à **Claude-Founder** pour avoir arbitré sans hésiter sur le trial 14j vs pas de trial (le trial a été un bon choix, vérifiable en M3).
Merci à **Claude-SEC** pour avoir insisté sur le reuse-detection du refresh token — ça a doublé la surface de sécu pour 50 lignes.
Merci à **Claude-QA** pour les tests paramétrés tenant isolation — ils auront sauvé des heures de debugging en M3.

Prochain rendez-vous : kickoff M3 · 2026-07-22 · Bêta fermée 50 testeurs.
