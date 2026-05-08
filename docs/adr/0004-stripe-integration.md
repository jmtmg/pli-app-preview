# ADR 0004 — Intégration paiement Stripe Checkout + webhooks idempotents

- **Statut** : Accepté · 2026-07-08
- **Décideurs** : Claude-Founder (prix), Claude-TL (archi), Claude-BE, Claude-SEC
- **Remplacé par** : —
- **Lien Sprint** : Sprint 6, US-6.1 & US-6.2

## Contexte

PLI Cloud doit encaisser des abonnements récurrents (mensuel 9 €, annuel 96 €), avec un essai gratuit de 14 jours sans carte pour Plus. Les contraintes :

- **Pas de PCI-DSS** — on ne stocke **aucune** donnée de carte côté PLI.
- **Résilience** aux double-envois de webhook (Stripe retry jusqu'à 3 jours).
- **Mode local** — PLI Local n'a pas de paiement ; le code Stripe doit être 100 % inerte dans ce mode (pas un simple `if` noyé dans la logique métier).
- **Traçabilité** — tous les events reçus doivent être auditables individuellement.

## Options envisagées

### Option A — Stripe Checkout (hosted) + Webhooks

Checkout héberge la page de paiement. PLI ne voit jamais le numéro de carte.

**Pour** :
- Conformité PCI-DSS SAQ-A automatique (la plus légère).
- UI responsive, localisée, testée par des millions de transactions.
- Trial period natif (`trial_period_days`) — 1 ligne de config.
- Coupon codes, taxes EU, SCA/3DS gérés par Stripe.
- Portail client inclus (Billing Portal) — update carte, télécharger factures.

**Contre** :
- UX moins cohérente (page Stripe au milieu du parcours PLI).
- Dépendance forte à un fournisseur.

### Option B — Stripe Elements (embedded)

Champs carte dans notre UI, tokenisation côté Stripe.JS.

**Pour** : UX plus native, branding PLI conservé.

**Contre** : PCI-DSS SAQ-A-EP (plus d'exigences), plus de code à maintenir, pas de gain métier significatif au stade M2.

### Option C — Paddle / LemonSqueezy (merchant of record)

**Pour** : gestion TVA EU + compliance hors-UE clés en main.

**Contre** : reversements différés (J+30), moins d'outillage développeur, surface plus grande sur la marge.

## Décision

**Option A — Stripe Checkout + webhooks** pour toute la fenêtre M2→M5. Réévaluation post-lancement (> 1 000 abonnés) pour considérer Paddle uniquement si la complexité TVA devient critique.

## Implémentation retenue

### Flow checkout

```
FE /pricing → POST /billing/checkout { plan: "monthly" | "yearly" }
  → StripeClient.create_checkout_session(
       price_id,
       metadata: { pli_user_id, pli_tenant_id },
       subscription_data: { trial_period_days: 14, metadata: {...} },
       idempotency_key: f"checkout:{user_id}:{plan}",
     )
  → return { url }
FE redirige vers session.url (checkout.stripe.com/…)
Après paiement → session.success_url → /settings/billing?status=success
Stripe webhook → POST /billing/webhook → handle_event(event)
```

### Idempotence webhooks

1. **Insertion d'abord** dans `webhook_events (event_id UNIQUE)`.
2. Si `UniqueViolation` → event déjà vu → return.
3. Sinon dispatch au handler dédié.

```python
async def handle_event(event):
    first_time = await _record_event(event["id"], event["type"])
    if not first_time:
        return
    handler = _HANDLERS.get(event["type"])
    if handler:
        await handler(event)
```

Le handler métier peut lui-même être idempotent via `ON CONFLICT` sur
`subscriptions.stripe_subscription_id` — double protection.

### Table `webhook_events`

```sql
CREATE TABLE webhook_events (
    event_id    TEXT PRIMARY KEY,  -- evt_XXXX
    event_type  TEXT NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Pas de tenant_id** — la table est globale, consultée avant authentification
(webhook entrant de Stripe non lié à un tenant PLI tant qu'on n'a pas lu les metadata).

### Dérivation du plan

```python
def plan_from_subscription_status(status, price_id):
    if status == "trialing":         return Plan.PLUS_TRIAL
    if status in ("active", "past_due"):
        return get_plan_from_price_id(price_id)   # past_due = grace period
    return Plan.FREE
```

**Past_due** = grace period : on conserve les privilèges Plus pendant que
Stripe Smart Retries retente le paiement (3 jours par défaut). Si toujours
`unpaid` à la fin, Stripe envoie `customer.subscription.deleted` → bascule free.

### Sécurité

- Signature vérifiée via `stripe.Webhook.construct_event()` + `PLI_STRIPE_WEBHOOK_SECRET`.
- `PLI_STRIPE_WEBHOOK_SECRET` stocké dans secrets Fly.io — jamais dans git.
- Route `/billing/webhook` hors du middleware d'auth PLI (public, signature = auth).
- Endpoint 404 en mode local via `_require_cloud()`.

## Conséquences

**Positives** :
- Intégration testable sans compte Stripe grâce au fake event store dans `test_stripe_webhooks.py`.
- Pas de PCI audit à subir.
- Portail Stripe natif → 0 ligne de code pour "update carte" / "télécharger facture".

**Négatives / contraintes à surveiller** :
- En cas de rotation du webhook secret, bien redéployer avant de régénérer.
- Si on ajoute un 3e price (ex: lifetime), `get_plan_from_price_id` doit être étendu.
- Le retry Stripe ne "réveille" pas d'event custom — si un handler rate silencieusement, il faut le rejouer depuis le dashboard Stripe. Runbook SRE à écrire.

## Plan de rollback

Si bug critique post-M2 :
1. Désactiver route `/billing/checkout` (404) — les abonnés existants restent servis.
2. Stripe retry les webhooks manqués pendant 3 jours → pas de perte de data.
3. Fix + redeploy sans perte d'état (idempotence garantit).
