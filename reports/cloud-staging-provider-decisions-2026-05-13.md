# PLI cloud-staging — recommandations fournisseurs réversibles

Date : 2026-05-13
Statut : recherche / cadrage décisionnel. Aucun compte, ressource cloud, DNS, certificat, OAuth consent, import de secret ou déploiement n'a été créé ou modifié.

## Résumé exécutif

Bundle recommandé pour un premier `cloud-staging` simple, réversible et EU/Paris-compatible :

1. API/runtime : conserver Fly app `pli-staging` en région `cdg` avec le `fly.toml` actuel.
2. Frontend : privilégier la même origine `https://staging.pli.app` sur Fly, plutôt qu'un domaine frontend séparé, pour minimiser CORS et redirects OAuth.
3. PostgreSQL managé : Scaleway Managed Database PostgreSQL en région Paris `fr-par`, avec backup/restore staging testé.
4. Stockage objet : Scaleway Object Storage Standard Multi-AZ en région Paris `fr-par`, bucket `pli-staging-attachments`, credentials least-privilege.
5. Email transactionnel : Brevo SMTP en staging via `PLI_EMAIL_PROVIDER=smtp`, avec domaine sender vérifié SPF/DKIM/DMARC.
6. Domaine/certificat : `staging.pli.app` attaché à Fly et certificat géré via Fly, après confirmation DNS humaine.

Alternative rapide si la priorité devient la réinitialisation staging/CI plutôt que Paris/CDG : Neon Postgres Europe Frankfurt + Cloudflare R2 ou AWS S3 Paris + Postmark/SendGrid + frontend Cloudflare Pages/Vercel séparé. Cette alternative est plus flexible pour branches de données, mais augmente le nombre d'origines et la configuration CORS/OAuth.

Fly Postgres n'est pas recommandé comme choix principal faible-maintenance : la documentation publique actuelle l'intitule `Fly Postgres (Unmanaged)`. Il reste utile pour un staging jetable très co-localisé, pas pour réduire l'exploitation.

## Recommandations par composant

### 1. PostgreSQL managé

Recommandation : Scaleway Managed Database PostgreSQL, région `fr-par`.

Pourquoi :
- aligne la donnée principale avec l'objectif Europe/Paris ;
- service managé avec sauvegardes automatiques, réplication/HA selon plan, et moins d'exploitation qu'un Postgres autogéré ;
- distance raisonnable avec Fly `cdg` et cohérence avec un stockage objet Scaleway `fr-par`.

Variables/gates côté PLI :
- `PLI_DATABASE_URL` doit rester secret et être injecté via GitHub environment / Fly secrets / secret manager ;
- exécuter migrations Alembic en staging avec snapshot préalable ;
- preflight attendu : `make cloud-staging-preflight` doit passer `ready` avant tout déploiement ;
- restore PostgreSQL staging à tester avant de considérer le fournisseur validé.

Alternative principale : Neon Postgres en région Europe Frankfurt (`aws-eu-central-1`). À choisir si les branches/reset de données staging et CI priment sur Paris. La région est fixe par projet, donc la décision doit être prise avant création.

Alternative non prioritaire : Fly Postgres en `cdg`. Avantage : co-localisation réseau. Inconvénient : docs publiques `Fly Postgres (Unmanaged)`, donc responsabilité exploitation/backup plus forte.

Décision humaine requise : choisir Scaleway vs Neon vs Fly Postgres ; confirmer région, plan, propriétaire backup/restore, politique d'accès réseau et lieu de stockage des secrets.

### 2. S3 / Object storage

Recommandation : Scaleway Object Storage Standard Multi-AZ, région Paris `fr-par`.

Configuration proposée :
- bucket : `pli-staging-attachments` ;
- endpoint : `https://s3.fr-par.scw.cloud/` ;
- région : `fr-par` ;
- credentials : clé IAM/API dédiée least-privilege, scoped au bucket et stockée uniquement via secret manager.

Pourquoi :
- S3-compatible, donc compatible avec le `CloudStorageAdapter` boto3 actuel ;
- région Paris documentée ;
- Standard Multi-AZ disponible en Paris/Amsterdam/Warsaw ;
- bundle cohérent si PostgreSQL est aussi chez Scaleway.

Attention technique : `.env.staging.example` met aujourd'hui `PLI_S3_REGION=eu-west-3`, ce qui correspond plutôt à AWS Paris. Si Scaleway est choisi, prévoir `PLI_S3_REGION=fr-par`. Le code `backend/pli/adapters/cloud.py` instancie actuellement `CloudStorageAdapter(region="auto")` et ne lit pas explicitement `settings.s3_region`; le smoke storage devra valider que le provider accepte cette signature ou qu'un petit correctif branche `settings.s3_region` avant GO staging.

Alternative : AWS S3 `eu-west-3` si l'on veut rester sur un S3 très standard et garder le template `eu-west-3` tel quel. Autre alternative : Cloudflare R2 si Cloudflare est déjà le DNS/CDN retenu ; vérifier alors la juridiction EU et les limites S3 utiles au smoke.

Décision humaine requise : choisir fournisseur/région, confirmer bucket, politique IAM, lifecycle/rétention, chiffrement, et propriétaire du test upload/download/delete + restore/backup objet.

### 3. Email transactionnel

Recommandation : Brevo SMTP pour staging, via le backend existant `PLI_EMAIL_PROVIDER=smtp`.

Configuration proposée sans valeurs secrètes :
- `PLI_EMAIL_PROVIDER=smtp` ;
- `PLI_EMAIL_SMTP_HOST=<host SMTP Brevo>` ;
- `PLI_EMAIL_SMTP_PORT=587` ;
- `PLI_EMAIL_SMTP_USER` / `PLI_EMAIL_SMTP_PASSWORD` via secrets ;
- `PLI_EMAIL_FROM=noreply@pli.app` seulement après vérification du sender/domaine, sinon utiliser un sous-domaine staging validé.

Pourquoi :
- provider européen/français pertinent pour staging ;
- aucun changement backend requis si SMTP est validé ;
- le code PLI active STARTTLS sur les ports autres que 25/1025 ;
- Brevo exige un sender enregistré/vérifié pour l'envoi transactionnel.

Alternative : Postmark via `PLI_EMAIL_PROVIDER=postmark` et `PLI_EMAIL_API_KEY`. Avantage : chemin API déjà codé explicitement et bonne ergonomie transactionnelle ; vérifier l'adéquation RGPD/localisation et la validation DKIM/SPF du domaine. SendGrid reste possible mais pas préféré pour ce staging si l'objectif est simplicité + Europe.

Décision humaine requise : choisir Brevo SMTP vs Postmark/SendGrid ; confirmer domaine sender, DNS SPF/DKIM/DMARC, adresse de réception test, limites de volume et propriétaire du smoke email.

### 4. Frontend hosting / same-origin

Recommandation : même origine `https://staging.pli.app` sur Fly.

Pourquoi :
- garde `PLI_BASE_URL`, `PLI_APP_URL`, `VITE_API_URL` et `PLI_CORS_ORIGINS` cohérents avec les templates actuels ;
- évite une deuxième origine HTTPS et donc réduit les risques CORS/cookies/OAuth ;
- les redirects OAuth déjà documentés restent exacts :
  - `https://staging.pli.app/auth/gmail/callback` ;
  - `https://staging.pli.app/auth/microsoft/callback`.

Implication repo : le workflow `deploy-staging.yml` déploie aujourd'hui le backend Fly et ne build/sert pas encore le frontend staging. Avant tout déploiement réel, il faut choisir l'implémentation same-origin :
- soit build Vite dans l'image et servir `frontend/dist` depuis FastAPI avec fallback SPA ;
- soit ajouter un reverse proxy/multi-process Fly qui sert frontend statique + API sur la même app/domaine.

Alternative : Cloudflare Pages/Vercel/Fly static sur un domaine séparé, par exemple `https://staging-web.pli.app`, API `https://staging-api.pli.app`. Dans ce cas, mettre à jour `VITE_API_URL`, `PLI_APP_URL`, `PLI_CORS_ORIGINS`, redirects OAuth, et smoke navigateur CORS.

Décision humaine requise : valider même origine Fly vs frontend séparé ; autoriser l'éventuel petit changement repo nécessaire pour servir le frontend ; confirmer les URLs finales avant création OAuth.

### 5. Domaine et certificat

Recommandation : utiliser `staging.pli.app` comme domaine staging unique et attacher le certificat à Fly `pli-staging`.

Pourquoi :
- déjà cohérent avec `.env.staging.example`, `fly.toml`, `docs/runbooks/cloud-staging.md` et `deploy-staging.yml` ;
- Fly documente l'ajout de domaine/certificat via `fly certs add` ou dashboard, puis configuration DNS chez le provider ;
- garde les redirects OAuth et CORS simples.

Alternative : premier smoke sur `https://pli-staging.fly.dev` si DNS n'est pas encore disponible. À ne pas considérer comme cible finale si OAuth staging officiel doit déjà être configuré sur `staging.pli.app`.

Décision humaine requise : confirmer propriété de `pli.app`, provider DNS, mode Cloudflare proxy/non-proxy si applicable, autorisation d'ajouter les enregistrements DNS, et autorisation de demander le certificat Fly.

### 6. Fly app `pli-staging`

Recommandation : garder `app="pli-staging"`, région primaire `cdg`, `PLI_ENABLE_M2=false`, `PLI_MODE=cloud`, min 1 machine active comme dans `fly.toml`.

Pourquoi :
- le repo contient déjà `fly.toml` et un workflow manuel `Deploy staging` avec confirmation `deploy-staging` ;
- `cdg` est une région Fly publique Paris ;
- une machine toujours active réduit le risque de latence de cold start sur callbacks OAuth/smoke staging.

Alternative : déplacer API vers Scaleway Containers/Render/Railway uniquement si l'utilisateur veut réduire le nombre de fournisseurs. Cela demande de réécrire `fly.toml`, le workflow GitHub et le runbook ; non recommandé pour cette tranche.

Décision humaine requise : confirmer Fly comme plateforme staging, organisation/billing Fly, création app si absente, import des secrets, environnement GitHub `staging`, et autorisation explicite de lancer `Deploy staging`.

## Bundle de décision proposé

Choix par défaut recommandé :

- Fly `pli-staging` en `cdg` pour runtime API + frontend same-origin.
- Scaleway Managed PostgreSQL `fr-par`.
- Scaleway Object Storage Standard Multi-AZ `fr-par`.
- Brevo SMTP transactionnel.
- Domaine unique `staging.pli.app` avec certificat Fly.
- OAuth Gmail/Microsoft staging configurés seulement après confirmation domaine/certificat.

Ce bundle minimise les origines, garde les données principales en Europe/Paris, reste réversible pour staging, et évite un Postgres autogéré.

## Actions après décision humaine, sans secrets affichés

1. Créer les ressources approuvées dans les consoles officielles.
2. Importer uniquement les noms/valeurs via secret manager, GitHub environment protected variables/secrets et/ou Fly secrets ; ne jamais afficher les valeurs.
3. Adapter `.env.staging` privé et GitHub/Fly env selon le bundle retenu.
4. Si same-origin : implémenter/valider la façon de servir le frontend sur Fly avant deploy.
5. Exécuter `make cloud-staging-preflight` ; gate attendu `ready`.
6. Lancer le workflow staging uniquement après confirmation humaine explicite.
7. Smoke : `/health`, navigateur sans erreur CORS, stockage upload/download/delete, email de test reçu, OAuth Gmail/Microsoft staging avec comptes de test, backup/restore DB + objet.

## Sources repo lues

- `PLI_FINAL_FUNCTIONAL_STATUS.md`
- `reports/cloud-staging-readiness-2026-05-13.md`
- `reports/cloud-production-go-no-go-2026-05-13.md`
- `docs/runbooks/cloud-staging.md`
- `docs/runbooks/production-readiness.md`
- `.env.staging.example`
- `.github/workflows/ci.yml`
- `.github/workflows/deploy-staging.yml`
- `fly.toml`
- `backend/pli/prod_readiness.py`
- `backend/pli/emails/provider.py`
- `backend/pli/adapters/cloud.py`

## Sources publiques consultées

- Fly regions : `https://fly.io/docs/reference/regions/` — `cdg` correspond à Paris, France.
- Fly custom domains : `https://fly.io/docs/networking/custom-domain/` — domaine attaché à l'app, génération certificat TLS, configuration DNS.
- Fly Postgres : `https://fly.io/docs/postgres/` — page intitulée `Fly Postgres (Unmanaged)`.
- Scaleway Managed Database concepts : `https://www.scaleway.com/en/docs/managed-databases-for-postgresql-and-mysql/concepts/` — régions dont France/Paris `fr-par`, service managé avec backups automatiques selon docs.
- Scaleway Managed PostgreSQL/MySQL product : `https://www.scaleway.com/en/managed-postgresql-mysql/` — régions européennes Paris/Amsterdam/Warsaw et backups automatisés.
- Scaleway Object Storage concepts : `https://www.scaleway.com/en/docs/object-storage/concepts/` — S3-compatible, endpoint Paris `https://s3.fr-par.scw.cloud/`, Standard Multi-AZ disponible à Paris.
- Scaleway Object Storage quickstart : `https://www.scaleway.com/en/docs/object-storage/quickstart/` — service basé sur le protocole Amazon S3.
- Neon regions : `https://neon.com/docs/introduction/regions` — projets dans plusieurs régions AWS/Azure, choisir la région proche de l'app, région fixe à la création.
- Neon branching : `https://neon.com/docs/introduction/branching` — branches de données pour développement/test/CI.
- Cloudflare R2 S3 API compatibility : `https://developers.cloudflare.com/r2/api/s3/api/`.
- Cloudflare R2 data location : `https://developers.cloudflare.com/r2/buckets/data-location/` — juridictions dont `eu` selon docs.
- Brevo transactional email : `https://developers.brevo.com/docs/send-a-transactional-email` — sender email/name doit être enregistré et vérifié.
- Postmark send email API : `https://postmarkapp.com/developer/user-guide/send-email-with-api` — API avec `X-Postmark-Server-Token`, domaines/sender signatures, DKIM/SPF.
