# PLI NEXT 4/6 — synthèse autorisation cloud-staging

Statut de la note : décisionnel / secret-safe.
Verdict court : NO-GO pour tout déploiement staging réel aujourd’hui ; GO conditionnel uniquement pour préparer et durcir le repo avant preflight staging.

Aucun secret réel n’a été lu, affiché, copié ou inventé dans cette synthèse. Aucun déploiement, DNS, OAuth consent, import de secret, création cloud, migration ou action destructive n’est autorisé par ce document.

## Sources vérifiées

Sources repo lues :

- `PLI_FINAL_FUNCTIONAL_STATUS.md`
- `reports/cloud-staging-readiness-2026-05-13.md`
- `reports/cloud-production-go-no-go-2026-05-13.md`
- `reports/cloud-staging-provider-decisions-2026-05-13.md`
- `docs/runbooks/cloud-staging.md`
- `docs/runbooks/cloud-staging-secrets-oauth-matrix.md`
- `docs/runbooks/production-readiness.md`
- `.env.staging.example`
- `.github/workflows/ci.yml`
- `.github/workflows/deploy-staging.yml`
- `fly.toml`
- `backend/pli/prod_readiness.py`
- `backend/pli/adapters/cloud.py`
- `backend/pli/emails/provider.py`

Handoffs parents intégrés : audit PR/readiness, recommandations providers, matrice secrets/OAuth.

## 1. Décision recommandée

Recommandation : ne pas autoriser le deploy cloud-staging maintenant.

Autoriser seulement une phase intermédiaire `staging-hardening` sans cloud, sans secret et sans provider réel, pour corriger les garde-fous qui peuvent actuellement donner un faux GO ou exposer inutilement des secrets dans le workflow.

Décision cible proposée après confirmations Jm :

- Runtime/API : Fly app `pli-staging`, région `cdg`, `PLI_MODE=cloud`, `PLI_ENABLE_M2=false`.
- Domaine staging : origine unique `https://staging.pli.app`, certificat Fly, DNS confirmé par Jm.
- Frontend : même origine `https://staging.pli.app` si Jm accepte le petit chantier repo pour servir le frontend sur Fly ; sinon domaine séparé avec CORS/OAuth à recalibrer.
- PostgreSQL : Scaleway Managed PostgreSQL `fr-par`, sauf préférence explicite Neon pour reset/branching staging.
- Object storage : Scaleway Object Storage `fr-par`, bucket proposé `pli-staging-attachments`, credentials least-privilege.
- Email : Brevo SMTP (`PLI_EMAIL_PROVIDER=smtp`) avec sender/domain SPF-DKIM-DMARC validé ; Postmark reste alternative acceptable.
- OAuth : apps staging Gmail/Microsoft dédiées ou isolées, redirects exacts :
  - `https://staging.pli.app/auth/gmail/callback`
  - `https://staging.pli.app/auth/microsoft/callback`
- Production cloud : reste NO-GO tant que staging réel n’a pas prouvé preflight, deploy, smoke et restore.

## 2. Vérifié maintenant

État repo/documentation :

- `local-v1` reste le seul état ready recommandé à court terme.
- `cloud-staging` dispose d’un template secret-safe, d’un runbook, d’une matrice secrets/OAuth et d’une cible `make cloud-staging-preflight`.
- `.env.staging.example` est volontairement incomplet ; le résultat attendu avec le template est `blocked`.
- `fly.toml` cible déjà `pli-staging` en `cdg`, `PLI_MODE=cloud`, `PLI_ENABLE_M2=false`, `PLI_BASE_URL/PLI_APP_URL/PLI_CORS_ORIGINS=https://staging.pli.app`.
- Le workflow `deploy-staging.yml` est manuel et exige l’input `deploy-staging`.
- Le backend email supporte `smtp`, `sendgrid`, `postmark` et `memory`; `memory`/MailHog ne convient pas pour staging exposé.
- Le storage cloud actuel utilise boto3 S3-compatible avec `region="auto"` par défaut dans `CloudStorageAdapter`.

État incertain ou bloquant remonté par l’audit parent :

- CI/PR GitHub non vérifiable par l’auditeur sans authentification GitHub ; le statut vert doit être confirmé avec accès autorisé et SHA exact.
- Workspace partagé déjà dirty pendant les audits : changements docs non suivis/modifiés doivent être stabilisés avant toute décision ready/merge.
- Le preflight staging précédent était trop permissif : pour `cloud-v1 --env staging`, il ne forçait pas encore HTTPS public, redirects OAuth HTTPS, ni absence de localhost/hostname interne/notation IPv4 abrégée/wildcard CORS comme le runbook l’exigeait ; ce repo-only hardening ajoute désormais ces garde-fous dans `prod_readiness.py`.
- Le preflight production/S3 précédent vérifiait surtout présence/dummy markers ; ce repo-only hardening refuse maintenant les endpoints S3 locaux, internes, IPv4 abrégés ou non-HTTPS pour `cloud-v1` staging/prod.
- Le workflow staging est manuel et a été durci côté repo : action Fly référencée par commit immuable avec version `flyctl` explicite, secrets runtime limités à l’étape preflight, `FLY_API_TOKEN` limité au deploy, mappings `PLI_S3_REGION`, `PLI_EMAIL_FROM` et SMTP ajoutés.
- Le workflow staging déploie toujours le backend Fly, mais ne définit pas encore clairement le frontend staging same-origin.
- Les providers, DNS, OAuth apps, secrets, backups et smoke réel restent non provisionnés/non validés par Jm ; les mappings ne valent pas autorisation de déploiement.

## 3. Points à confirmer par Jm

P0 — décision providers / architecture :

1. Confirmer ou remplacer le bundle recommandé : Fly `pli-staging` + même origine `staging.pli.app` + Scaleway PostgreSQL `fr-par` + Scaleway Object Storage `fr-par` + Brevo SMTP.
2. Confirmer si le frontend staging doit être servi en même origine sur Fly, ou hébergé séparément.
3. Confirmer le domaine `staging.pli.app`, le provider DNS, le mode proxy éventuel, et l’autorisation d’ajouter DNS/certificat Fly plus tard.
4. Confirmer la création/configuration des apps OAuth Gmail et Microsoft staging avec les redirects exacts.
5. Confirmer le propriétaire du backup/restore staging PostgreSQL + objet, et le test restore attendu.

P0 — autorisations opérationnelles :

6. Autoriser explicitement seulement le durcissement repo no-cloud/no-secret : preflight, workflow, frontend strategy, tests/docs.
7. Plus tard seulement : autoriser création providers, DNS/cert, import secrets, migrations staging, deploy workflow et smoke réel.

P1 — détails de configuration :

8. Si Scaleway Object Storage est retenu, utiliser `PLI_S3_REGION=fr-par` et valider/patcher le passage de région dans l’adapter S3 si le smoke provider l’exige.
9. Si Brevo SMTP est retenu, définir `PLI_EMAIL_FROM`, SMTP host/port/user/password via secrets/vars protégés, jamais en clair.
10. Garder `PLI_ENABLE_M2=false` tant que Stripe/billing/auth cloud avancés ne sont pas validés.

## 4. Durcissement repo-only appliqué et reste sans cloud

Actions réalisées sans secrets ni providers :

1. `backend/pli/prod_readiness.py` durci pour `cloud-v1` staging/prod exposé :
   - exige `https://` public pour `PLI_BASE_URL`, `PLI_APP_URL` et redirects OAuth ;
   - refuse localhost/hostname interne/notation IPv4 abrégée/wildcard/non-HTTPS CORS en staging/prod ;
   - refuse endpoints S3 locaux, internes, IPv4 abrégés ou non-HTTPS pour staging/prod cloud ;
   - ajoute des tests de régression couvrant les faux GO signalés.
2. `.github/workflows/deploy-staging.yml` durci côté repo :
   - `setup-flyctl@master` remplacé par un commit immuable du tag v1 avec version `flyctl` explicite ;
   - secrets runtime limités à l’étape preflight, `FLY_API_TOKEN` limité au deploy ;
   - mappings `PLI_S3_REGION`, `PLI_EMAIL_FROM` et SMTP port/user/password ajoutés ; Stripe reste non mappé tant que `PLI_ENABLE_M2=false`.
3. Documentation clarifiée : providers recommandés non provisionnés/non validés ; staging réel toujours bloqué.
4. Reste à trancher hors repo-only : stratégie frontend staging même origine vs séparée, confirmations providers, secrets, DNS/OAuth et backups.
5. Gates locaux/secret-safe à relancer avant tout reviewer/merge : tests, lint, typecheck, `git diff --check`, scan diff secrets, preflight template expected-blocked.

## 5. Ce qui exige confirmation humaine explicite

Ne pas exécuter sans feu vert explicite et ciblé :

- créer ou modifier app Fly, org, billing, machine, DNS, certificat ;
- créer PostgreSQL, bucket S3/object storage, email provider, Sentry, OAuth apps ;
- importer, lister en détail, lire ou manipuler des valeurs de secrets réels ;
- créer `.env.staging` rempli avec des secrets réels hors procédure privée approuvée ;
- lancer le workflow GitHub `Deploy staging` ou `flyctl deploy` ;
- lancer migrations sur DB distante ;
- effectuer smoke OAuth/email/storage avec comptes réels ;
- ouvrir le chemin production.

## 6. Critères GO / NO-GO

### GO pour continuer vers `staging-hardening` no-cloud

GO si Jm confirme :

- le bundle providers ou ses remplacements ;
- la stratégie frontend ;
- l’autorisation de modifier uniquement le repo, sans cloud ni secret ;
- l’objectif de corriger les blockers preflight/workflow avant tout deploy.

### GO pour exécuter `make cloud-staging-preflight` contre une vraie config privée

GO seulement si :

- le repo est stabilisé : branche propre ou changements explicitement attendus, PR/SHA identifié, CI vérifiée avec accès autorisé ;
- les garde-fous preflight staging sont durcis et testés ;
- le workflow deploy est durci ou au minimum non utilisé tant qu’il reste mutable/job-level secrets ;
- providers staging choisis et créés par Jm ou sous autorisation explicite ;
- `.env.staging` privé ou GitHub/Fly env est rempli via secret manager, `chmod 600`, sans impression de valeur ;
- `make cloud-staging-preflight` sort `ready` sans `--show-env-keys` ;
- tests/lint/typecheck/build/diff/scan secrets sont verts.

### GO pour déployer staging

GO seulement si tous les critères précédents sont vrais, puis confirmation humaine explicite du type : “autorisé à déployer staging”, avec périmètre clair.

Checklist minimale avant deploy :

- snapshot/backup PostgreSQL staging ou preuve que la DB est jetable ;
- bucket objet créé, policy least-privilege, lifecycle/rétention décidés ;
- secrets runtime importés via Fly/GitHub secret manager ;
- DNS/certificat prêts si `staging.pli.app` est la cible ;
- OAuth apps staging configurées avec redirects exacts ;
- smoke plan prêt : `/health`, frontend HTTPS, CORS navigateur, storage upload/download/delete, email test, OAuth Gmail/Microsoft test, logs sans secret.

### NO-GO immédiat

NO-GO si un seul point ci-dessous est vrai :

- une confirmation Jm P0 manque ;
- `make cloud-staging-preflight` est `blocked` ;
- preflight staging peut encore accepter HTTP/localhost/wildcard CORS/redirects non HTTPS ;
- workflow deploy utilise encore un outil mutable avec secrets trop larges et doit être lancé ;
- CI/PR/SHA ne sont pas vérifiés ;
- workspace non stabilisé ;
- frontend staging n’a pas de stratégie cohérente avec CORS/OAuth ;
- DNS/OAuth/provider/secrets/backups ne sont pas créés/importés/testés ;
- un secret réel apparaît dans logs, tickets, docs, shell history ou diff ;
- production cloud est demandée avant staging réel vert.

## 7. Carte de dépendances

Ordre sûr :

1. Décisions Jm : providers, frontend, domaine, OAuth, backup owner, autorisation repo-only.
2. Durcissement repo no-cloud : preflight, tests, workflow, frontend staging strategy.
3. Stabilisation PR : branch clean, commit/SHA, CI vérifiée.
4. Provisioning humain ou explicitement autorisé : Fly, DB, S3, email, OAuth, DNS/cert.
5. Import secrets via gestionnaires officiels uniquement.
6. Preflight cloud-staging : doit sortir `ready` sans valeurs affichées.
7. Deploy staging seulement sur confirmation explicite.
8. Smoke staging complet + rapport horodaté.
9. Réévaluation production ; production reste NO-GO avant cette preuve.

## 8. Registre de risques

| Risque | Niveau | État | Mitigation recommandée |
|---|---:|---|---|
| Faux GO preflight staging | P0 | Corrigé côté repo-only, à vérifier en vraie config | Garde-fous HTTPS/CORS/OAuth staging + tests ajoutés, incluant hostnames internes/single-label et IPv4 abrégées ; staging réel reste NO-GO sans providers/secrets. |
| Endpoint S3 local/non-HTTPS accepté | P0 | Corrigé côté repo-only, à vérifier en vraie config | Refus local/interne/IPv4 abrégée/non-HTTPS en prod/staging exposé ; cible smoke locale séparée requise si besoin. |
| Exfiltration secrets GitHub Actions | P0 | Réduit côté repo-only | Action Fly pin immuable + version flyctl explicite ; secrets limités à preflight/deploy nécessaires ; ne pas lancer sans confirmation. |
| Frontend staging non servi | P0 | Non tranché | Choisir same-origin ou domaine séparé avant OAuth/CORS. |
| Provider/région S3 incohérent | P1 | Scaleway implique `fr-par`; template a `eu-west-3` | Adapter env + tester/patcher `CloudStorageAdapter` si nécessaire. |
| OAuth redirects incorrects | P0 | À configurer | Créer apps staging avec redirects exacts après domaine final. |
| Backup/restore non prouvé | P0 | À confirmer | Nommer owner + test restore avant GO deploy. |
| Production prématurée | P0 | Production NO-GO | Exiger staging réel vert et rapport smoke avant toute prod. |

## 9. Message d’autorisation proposé à Jm

À valider ou modifier par Jm :

> J’autorise uniquement une phase repo-only sans cloud et sans secrets pour durcir cloud-staging. Bundle cible par défaut : Fly `pli-staging` en `cdg`, même origine `https://staging.pli.app`, Scaleway PostgreSQL `fr-par`, Scaleway Object Storage `fr-par`, Brevo SMTP, OAuth Gmail/Microsoft staging avec redirects exacts, `PLI_ENABLE_M2=false`. Je n’autorise pas encore création cloud, DNS, OAuth consent, import secret, migration ou déploiement.

Sans cette confirmation, le prochain état doit rester bloqué.
