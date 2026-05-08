# Tag logique — `rebaseline-base-2026-04-22`

**Type** : snapshot manifest (md5sum) — substitut au tag git
**Émis par** : direction Mail, 2026-04-22 fin de journée
**Portée** : baseline coordonnée M3 (sécurité) + M4 (UX/perf) + M5 (métriques J30/NPS/uptime)
**Status** : ACTIF — référence pour toute re-mesure jusqu'au prochain tag

---

## 1. Raison d'être

Ni la sandbox Mail (direction) ni les sandboxes M1-M5 (exécutifs) ne sont des
repos git initialisés. Le workspace OneDrive `pli-app/` n'a pas de `.git`.
La commande `git tag -a rebaseline-base-2026-04-22` n'est donc pas exécutable
en l'état.

Ce fichier sert de **point de référence reproductible** : la somme md5 de
chaque fichier Python critique + pyproject.toml + ADR fige l'état du code au
moment où :

- M1 ferme T1.6 avec 50/50 pytest dans les deux modes (PLI_ENABLE_M2 unset et =1).
- M2 a mergé le fix Sprint 1↔M2 (Fix C `plan="free"`) + extra `[project.optional-dependencies].m2`.
- ADR 0007 (feature-flag-m2) et 0008 (integration-freeze) sont signés.

M3 et M4 doivent vérifier ce manifeste (`md5sum -c`) avant chaque campagne
de mesure pour garantir la reproductibilité de leurs chiffres sécurité/UX/perf.

Ce fichier sera **remplacé par un vrai tag git** dès que le repo sera
initialisé (tâche optionnelle prévue sprint dédié, non-bloquante).

---

## 2. État du code à la date du snapshot

### 2.1 Comptage

- Fichiers Python `backend/pli/` : **72**
- Fichiers Python `backend/tests/` : **24**
- `backend/pyproject.toml` : **1**
- ADR `docs/adr/*.md` : **8** (0001-0008)

### 2.2 Empreintes de conformité

**Pytest Sprint 1, mode (a) `PLI_ENABLE_M2` unset** :
- 50/50 passed (test_accounts + test_messages + test_contacts + test_conversations + test_auth_oauth)
- OpenAPI : **17 paths** (0 M2)
- Log boot : `pli_m2_routers_disabled`

**Pytest Sprint 1, mode (b) `PLI_ENABLE_M2=1`** :
- 50/50 passed (mêmes suites)
- OpenAPI : **31 paths** (+14 M2)
- Log boot : `pli_m2_routers_enabled`

Ces deux empreintes sont les **pré-requis minimum** pour toute mesure
dérivée. Si la vérification md5 échoue OU si l'empreinte pytest diffère
de 50/50, la mesure doit être suspendue et un ticket ouvert.

### 2.3 Somme globale

```
md5(concat(backend_md5.txt, adr_md5.txt)) = 6a8d82bcbd292422f3ef87d0d6a30dce
```

Cette somme est l'empreinte unique de l'état `rebaseline-base-2026-04-22`.
Elle remplace fonctionnellement un SHA git. À utiliser comme ancre dans :
- Daily logs M3/M4/M5 (entrée "baseline = 6a8d82bc…")
- Rapport re-baseline M3 (REBASELINE-CHECKLIST.md)
- Rapport re-baseline M4 (perf/UX mesures)

---

## 3. Manifeste md5sum — backend/pli/

```
6fa24c4ca27c84c4d70c738ff57b1bc6  pli/__init__.py
0c98dfbe26932b166b4a1a08c56a8879  pli/accounts_repo.py
474d9a4c95aee886ee06cc8714572cf5  pli/adapters/__init__.py
7e7cf946107c81ee2be8ff0d3b25fe32  pli/adapters/base.py
a335d2cacea37f540ea630fc1683c5a4  pli/adapters/cloud.py
dfa5de1cfd7d35d5bd62ce0fe93e7b60  pli/adapters/container.py
89cb82be03cac84b347ec29270b975dd  pli/adapters/local.py
5a3d4eee4c80cbbbbee3fd8e65a56244  pli/api/__init__.py
eb8f0e825dd872a1e39f0b2ceca866d6  pli/api/accounts.py
6b5b32dbd5226ff6cd2cac9759d59ea0  pli/api/auth.py
694d679cf406d5cd9eb20c63c71c88e7  pli/api/auth_pli.py
5b4a8606240d3e315b62a3188e92133a  pli/api/billing.py
f388068373315ef28ac59aba0687857c  pli/api/contacts.py
6ba4791b0530b9725c95caeb3de5581d  pli/api/conversations.py
d914f1ab7fd81620367c1db079a2dc08  pli/api/feedback.py
9e7acae852e0755e4c42243978a67297  pli/api/invitations.py
5f622634f1a148c8a816f38c85e6a3d5  pli/api/licensing.py
5bcf5720066a43c986d85733dadd034f  pli/api/messages.py
6a170b39f57c60c9ab5d17100e0f519e  pli/api/search.py
f62185f44835b0f874324c875b6c7791  pli/api/waitlist.py
612b18a751cd34a05ed5df4a52582d69  pli/auth/__init__.py
5905e37d63d87f1282da91a44cdffb33  pli/auth/dependencies.py
2b81aaf50a691adcee8040837abf651d  pli/auth/deps.py
e045ea1281abd4792866444235d3c0a2  pli/auth/jwt.py
59b4a200cefe81e5c6fdef351973b309  pli/auth/login.py
98c6923ee678d8995fd7bf0451403a75  pli/auth/password_reset.py
8be967d74dcd2a8fb93fc5b4facc479b  pli/auth/passwords.py
92d800be1aec97078be941291f0c384e  pli/auth/signup.py
043a95e9c1c7d79aca8e6ce099482d37  pli/auth/tokens.py
8266b95ceef5a55da61da37934e68b73  pli/beta/__init__.py
edd4238eff01641c5c6df9f38d70fe12  pli/beta/activation.py
0b4db1d91f0f1e5029def9d5b4bc6f82  pli/beta/batches.py
e5bf8ec55b6c089d2d90a834e343430a  pli/beta/nps.py
6bc3825378e9db443cbcfa48893b66e8  pli/billing/__init__.py
628567689b0c1471c21432b44f3eecdd  pli/billing/licenses.py
54222c7a3a16bde6a7a1f997487630c9  pli/billing/plans.py
f5844138862bb8eb9e68fa43fa4898b6  pli/billing/stripe_client.py
ce4ada737c7ef20077f0ce2a7414518c  pli/billing/subscriptions.py
6ff9ecb037fb99059a08c6c90066531c  pli/billing/webhooks.py
2f0fd2551b084f3d758f1b34f83fdd8c  pli/config.py
74fb3337b5f5d959535af06f5739286f  pli/crypto.py
3d8965eae372fecedfa928c5769f76b3  pli/crypto/__init__.py
c0d8c7a831a6c2373dcca7d609d5c39b  pli/crypto/attachments.py
ef50f960c655a462cc950ea726b281ed  pli/crypto/backups.py
d1e1a3a1093937246b0506f5f6ec24a3  pli/crypto/oauth.py
b9a053154acf77125b1c73838e9d334b  pli/db.py
68d4150ddf636697f62fdf8cfd26c69a  pli/emails/__init__.py
90504d0469def5c7c6fab2e0cc2d0d28  pli/emails/provider.py
255650f118b6da25a23f412ad1e48aa1  pli/emails/sender.py
dbb81d35ad9066c595f32c3f32176bd9  pli/gdpr/__init__.py
b8111c8b1f3ec66cf80a04bfb0744b93  pli/gdpr/api.py
abc1cb990c0989a3e4fad612da59b164  pli/gdpr/deletion.py
f4ef9c3328cf4e4ad8c2b9067f2b4a05  pli/gdpr/export.py
20ad21956b15a4e1b87363749fb99c24  pli/licensing/__init__.py
0e7457492ed732db6b1818a6d40d2cbd  pli/licensing/local_key.py
8b837ff84cf2e486812f9fc1a6bcb3d4  pli/logging_config.py
07d0a729404b3724cceb6b192e2dfa48  pli/main.py
0816a289b6b7185737a2a71dc7dce8ad  pli/models.py
e599d91d34125bb33c8fed0ccd54f354  pli/ocr/__init__.py
84f44e2d545c3d05cc18d13f3edef760  pli/ocr/api.py
c487905e035bb6f59e13a22dd7d842ee  pli/ocr/worker.py
f451c0439696d23d067c70a558a5870b  pli/providers/__init__.py
ac22f17a79b6f6ebccae8c5cfd49e6e2  pli/providers/base.py
0ae0bec5035bcc2fd763b8e2b7ba9948  pli/providers/gmail.py
f87509489a046cd767bbf3108618125c  pli/providers/microsoft.py
1d7f81aeb843a19b2e8703237d2efd0e  pli/security/hashing.py
a8d3e5769c174170bf96011e83e30f99  pli/sync/__init__.py
566c4bfc1195d98394a0c0289e30e39b  pli/sync/parser.py
c60adfacf629acb1a91527a68f5fabcc  pli/sync/service.py
1de27b3e4018232c9cf08fa0f6f93257  pli/tenancy/__init__.py
98794d4ac29de1dc8c1f1cc619f3b6a8  pli/tenancy/context.py
1362175541b699da6db862b7f2bdea21  pli/tenancy/repository.py
```

## 4. Manifeste md5sum — backend/tests/

```
d41d8cd98f00b204e9800998ecf8427e  tests/__init__.py
587619bce46b64f605fde77af5ac66f8  tests/conftest.py
ce8616a0b32a51e41bd9b8797c3610bc  tests/integration/ocr/test_api.py
51257eb763ade1c0d1a466a3beaca1ce  tests/test_accounts.py
e46879015e5e2fd189614946df0a4da2  tests/test_api_feedback.py
ce9ee65742e4109aba42a47c3e055378  tests/test_auth_flow.py
175c94dc6e693d0d6ab1b36faa446c27  tests/test_auth_oauth.py
cfc87b45e22f60ea42222e1bd43476b4  tests/test_beta_activation.py
4371a4ea047d423f74bebe01dc0e83fe  tests/test_beta_batches.py
65b1ba12469b1ea355eac1880806754c  tests/test_beta_nps.py
dee87b243fb0fe80d134fb1e227d79c1  tests/test_contacts.py
962c1797668bb9455f5012b20f538473  tests/test_conversations.py
869c8f5a91debb3e461144c4f20a520e  tests/test_db_schema.py
3c60a50ff63c73ccd1284fa24b15f189  tests/test_emails.py
3a3d3271279dff8f633f69eb7bc9d12a  tests/test_gdpr.py
c65b77de02d62cf4b52b36c366e8d1cc  tests/test_health_logging.py
99f100c45f3e721475a3589a3293fa8b  tests/test_licensing.py
5ee12da2d55c56565eb5f387266f872b  tests/test_messages.py
2542607a223abb6d82c5dbe6d2d81c39  tests/test_parser.py
02888e1ce63f09804cc2c58510d6e004  tests/test_storage_adapters.py
1f36630e9b7dfb682dbd22a90be6fb5d  tests/test_stripe_webhooks.py
aee86fab6e5884829abc783412f5fdcc  tests/test_sync_gmail.py
a545360a27af47a9cea66ddc12d6255f  tests/test_tenancy_isolation.py
f954008af14f576a521fab54ce6befe2  tests/unit/ocr/test_worker.py
```

## 5. Manifeste md5sum — backend/pyproject.toml

```
771b5e924ca8d31cea5da07aec3665dd  pyproject.toml
```

## 6. Manifeste md5sum — docs/adr/

```
76a5f55904aff0018ac6b5c4a2ce577d  docs/adr/0001-adapters-local-cloud.md
d2781cf72103f145b88ffc30841d95cd  docs/adr/0002-multi-tenancy.md
02e07a686d87b989df97e7634268638f  docs/adr/0003-jwt-sessions.md
f1c86d0614aa9ab2517c9ea9dfa0c1c9  docs/adr/0004-stripe-integration.md
d3735d6c8767c0e78753903517280c99  docs/adr/0005-emails-transactionnels.md
b2e6699f9daea073f0114fbcc81826d3  docs/adr/0006-licences-offline-ed25519.md
d989324099769a1dfb642412de5ee585  docs/adr/0007-feature-flag-m2.md
d808f52226014961fc58a5b5b387580d  docs/adr/0008-integration-freeze.md
```

---

## 7. Procédure de vérification (M3, M4)

Avant chaque campagne de mesure (sécurité M3 ou perf/UX M4) :

```bash
cd <pli-app>/backend

# Étape 1 — reconstituer les manifestes localement
{
  find pli -name "*.py" -not -path "*/__pycache__/*" | sort
  find tests -name "*.py" -not -path "*/__pycache__/*" | sort
  echo pyproject.toml
} | xargs md5sum > /tmp/backend_md5_local.txt

cd .. && find docs/adr -name "*.md" | sort | xargs md5sum > /tmp/adr_md5_local.txt

# Étape 2 — comparer avec ce manifeste
diff <(grep -A200 '^```$' docs/governance/tags/rebaseline-base-2026-04-22.md | \
        grep -E '^[0-9a-f]{32}  (pli|tests|pyproject|docs)') \
     <(cat /tmp/backend_md5_local.txt /tmp/adr_md5_local.txt)

# Étape 3 — vérifier l'empreinte pytest (doit être 50/50 dans les 2 modes)
cd backend
PYTHONPATH=. pytest tests/test_{accounts,messages,contacts,conversations,auth_oauth}.py \
    -p no:cacheprovider --no-cov -q
PYTHONPATH=. PLI_ENABLE_M2=1 pytest <mêmes suites> -p no:cacheprovider --no-cov -q
```

Si **un seul** hash diffère OU si pytest dévie de 50/50, la baseline n'est
plus valable : ne pas publier de métriques dérivées, ouvrir un ticket
`P0-rebaseline-drift-<date>` dans `docs/governance/tickets/`.

## 8. Dépendances et versions

Pour reproduire le boot mode (b) (M2 wire-up actif) :

```bash
pip install -e .[m2]
# Ou explicite : pyjwt stripe python-ulid argon2-cffi asyncpg jinja2 tomli_w
```

Pour reproduire le boot mode (a) (Sprint 1 pur) :

```bash
pip install -e .
# Aucun extra nécessaire. Ne PAS installer les deps M2 en mode (a) pour
# garantir que la baseline locale ne dépend pas de Postgres.
```

## 9. Migration vers tag git (différé)

Quand le repo sera initialisé (sprint dédié, non-bloquant) :

```bash
git init
git add -A
git commit -m "Baseline Sprint 1 + M2 wired — snapshot 2026-04-22"
git tag -a rebaseline-base-2026-04-22 \
    -m "Baseline coordonnée M3/M4/M5 — 50/50 pytest (a)+(b), 17→31 paths openapi, md5_global=6a8d82bcbd292422f3ef87d0d6a30dce"
```

Le tag git devra préserver l'empreinte md5 globale `6a8d82bcbd292422f3ef87d0d6a30dce`
dans son message pour assurer la continuité avec ce manifeste.

---

## Journal

### 2026-04-22 — Ouverture (direction Mail)

Manifeste créé suite à découverte que le workspace OneDrive n'est pas git.
M1 a attesté T1.6 CLOSED (50/50 deux modes, critères #1-4 validés, mode b
17→31 paths openapi, ticket M1-regression-m2.md RÉSOLU).

Empreinte globale : `6a8d82bcbd292422f3ef87d0d6a30dce`.

Notification envoyée à M3 + M4 + M5 pour débloquer la chaîne de
re-baseline (deadline D+21 = 2026-05-14 cohérente avec M3 CLOSEOUT).
