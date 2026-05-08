# ADR 0005 — Emails transactionnels : abstraction provider + fallbacks

- **Statut** : Accepté · 2026-07-09
- **Décideurs** : Claude-BE, Claude-UX, Claude-SRE
- **Lien Sprint** : Sprint 6, US-6.3

## Contexte

PLI doit envoyer 4 emails transactionnels en M2 :

1. **Vérification email** (signup) — critique pour activation compte.
2. **Réinitialisation mot de passe** — critique pour support.
3. **Rappel fin d'essai** (trial_will_end) — critique pour conversion.
4. **Facture** (invoice.paid) — obligation légale.

Contraintes :
- En dev / CI → pas de dépendance externe (tests ne doivent pas envoyer de vrais emails).
- En dev local → inspection visuelle via MailHog.
- En prod → SLA livrabilité ≥ 99 %, délivrabilité inbox (pas de dossier spam).
- Futur : multi-lingue, newsletters, ESP-spécifiques (templates SendGrid).

## Options envisagées

### Option A — SMTP uniquement (Postfix self-hosted)
**Pour** : indépendance totale, pas de coût variable.
**Contre** : réputation IP à construire, compliance anti-spam (DKIM/SPF/DMARC) à gérer, probable relégation spam dans les premiers mois.

### Option B — Un seul ESP (SendGrid)
**Pour** : réputation IP mutualisée, dashboards, templates.
**Contre** : lock-in si incident ou tarification change.

### Option C — Abstraction `EmailProvider` + pluggable (Memory / SMTP / SendGrid / Postmark)
**Pour** : changement ESP en 1 variable d'env, tests sans réseau via memory, dev local avec MailHog.
**Contre** : légère surface à maintenir (4 implémentations, mais toutes < 50 lignes).

## Décision

**Option C**. Interface `EmailProvider` avec méthode unique `async send(msg: EmailMessage) -> str | None`. Quatre implémentations live :

- **MemoryEmailProvider** — outbox in-process. Utilisé dans tous les tests unitaires et E2E. Expose `.outbox: list[SentEmail]` pour assertions.
- **SmtpEmailProvider** — `aiosmtplib`. Dev local via MailHog (localhost:1025, UI :8025).
- **SendGridEmailProvider** — API HTTPS. Prod par défaut.
- **PostmarkEmailProvider** — API HTTPS. Fallback / alternative (Postmark a meilleure réputation pour le transactionnel pur).

Sélection via `PLI_EMAIL_PROVIDER` ∈ {`memory`, `smtp`, `sendgrid`, `postmark`}. Singleton initialisé lazy.

## Templating

Jinja2 avec arborescence `pli/emails/templates/<name>.{html,txt}` + layout `base.html` pour l'HTML uniquement (le texte reste brut pour compatibilité max).

Context commun injecté automatiquement :
- `app_url` — pour tous les liens et le footer.
- `subject` — pour le `<title>` HTML.

Chaque sender expose une fonction typée : `send_verification_email(to, token)`, etc.

## Audit

Table `outbound_emails` :
```sql
CREATE TABLE outbound_emails (
  id SERIAL,
  user_id UUID,       -- cloud : scopé tenant via RLS
  template TEXT,
  to_address TEXT,
  subject TEXT,
  provider_msg_id TEXT,
  status TEXT,        -- 'sent' | 'failed'
  error TEXT,
  sent_at TIMESTAMPTZ
);
```

Audit **best-effort** : une exception du audit log ne doit **jamais** bloquer l'envoi (ex: DB momentanément indisponible → le user doit quand même recevoir son lien de reset).

## Conséquences

**Positives** :
- Test `test_emails.py` capture les 4 flows sans réseau (0.3 s total).
- Dev local sans compte SendGrid (MailHog dans docker-compose).
- Bascule provider = 1 variable d'env + redémarrage.

**Risques / contraintes** :
- Pas de fallback automatique ESP en cas d'incident provider. **Décision post-M2** : ajouter `PLI_EMAIL_PROVIDER_FALLBACK` si retry failed.
- SMTP non sécurisé sur port 1025 (dev) vs START_TLS automatique sur autres ports — ne pas utiliser le port 1025 en prod.
- Templates HTML non responsive-testés sur Outlook older — acceptable pour essentiellement B2C début.

## Plan de rollback

Si ESP principal tombe :
1. Changer `PLI_EMAIL_PROVIDER=postmark` dans les secrets Fly.io.
2. Redéployer (1 min).
3. Les emails déjà en queue chez l'ancien ESP partent quand même (pas dépendants de PLI).
