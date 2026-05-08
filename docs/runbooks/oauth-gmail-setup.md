# Runbook — OAuth Gmail réel (M1, T1.2)

**Audience** : opérateur humain (la session M1 ne peut pas exécuter ce runbook
en autonomie — il requiert un compte Google Cloud Console et une approbation
manuelle des écrans de consentement).

**Durée estimée** : 25 min première fois, 5 min sur un projet existant.

**Pré-requis** :
- Un compte Google personnel ou pro (si pro, les admins du domaine peuvent
  bloquer la création — basculer sur un compte perso pour la dev).
- Le repo PLI cloné, dépendances backend installées (`pip install -e .` dans
  `backend/`).

---

## 1. Création du projet Google Cloud

1. Aller sur https://console.cloud.google.com/projectcreate
2. Nommer le projet `PLI-dev` (ou autre — c'est cosmétique).
3. Sélectionner le projet créé en haut à gauche.

## 2. Activer l'API Gmail

1. https://console.cloud.google.com/apis/library/gmail.googleapis.com → **Activer**.
2. Vérifier également que **Google People API** est activée
   (https://console.cloud.google.com/apis/library/people.googleapis.com) — utile
   pour `userinfo.email`/`userinfo.profile` même si la première suffit en pratique.

## 3. Configurer l'écran de consentement OAuth

1. https://console.cloud.google.com/apis/credentials/consent
2. **User Type** : `External` (sauf si compte Google Workspace dédié — alors
   `Internal`).
3. **App information** :
   - App name : `PLI (dev)`
   - User support email : ton email
   - App logo : facultatif en dev
4. **App domain** : laisser vide en dev (sera requis pour la prod).
5. **Developer contact** : ton email.
6. **Scopes** — cliquer "Add or remove scopes" et ajouter :
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
7. **Test users** : ajouter ton email Gmail (en `External`/`Testing` mode, seuls
   les test users peuvent passer le consent — pas de "verified" requis).

> ⚠️ Tant que l'app reste en mode **Testing**, les refresh tokens expirent sous
> 7 jours. C'est OK pour la dev, mais documenter dans la doc J0 qu'il faudra
> passer en `Production` (review Google) avant le launch.

## 4. Créer les credentials OAuth client

1. https://console.cloud.google.com/apis/credentials → **Create Credentials** →
   **OAuth client ID**.
2. Application type : `Web application`.
3. Name : `PLI backend (local)`.
4. **Authorized redirect URIs** — ajouter exactement :
   ```
   http://localhost:8000/auth/gmail/callback
   ```
   (le slug est `gmail`, pas `google` — alignement avec `provider_name='gmail'`
   du schéma SQL.)
5. Cliquer **Create** → noter le **Client ID** et le **Client secret**.

## 5. Renseigner `.env` local

Copier `.env.example` en `.env` (gitignoré) et remplir :

```dotenv
PLI_GMAIL_CLIENT_ID=1234567890-xxxxxxxxxxxx.apps.googleusercontent.com
PLI_GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx
PLI_GMAIL_REDIRECT_URI=http://localhost:8000/auth/gmail/callback
```

**À ne PAS faire** :
- Ne jamais committer `.env`.
- Ne jamais coller le `client_secret` dans Slack/email/issue tracker.
- En cas de leak, **rotate immédiatement** depuis la même page Credentials
  ("Reset secret").

## 6. Valider le flow end-to-end

Terminal 1 — backend :
```bash
cd backend
uvicorn pli.main:app --reload --port 8000
```

Terminal 2 — frontend :
```bash
cd frontend
npm run dev   # → http://localhost:5173
```

Navigateur :
1. Ouvrir http://localhost:8000/auth/gmail/start
2. → redirige vers `accounts.google.com`
3. Se connecter avec le **test user** déclaré au §3.7
4. Accepter les scopes
5. → redirige vers `http://localhost:8000/auth/gmail/callback?code=...&state=...`
6. → backend échange le code, persiste le compte, kick-off sync initiale en BG
7. → redirect final vers `http://localhost:5173/?connected=<account_id>`

## 7. Vérifications post-flow

```bash
# Le compte est-il en DB ?
sqlite3 ~/.pli/db.sqlite \
  "SELECT id, provider, email, is_active, last_sync_at FROM accounts;"

# Les tokens sont-ils chiffrés ? (préfixe Fernet attendu : 'gAAAAA')
sqlite3 ~/.pli/db.sqlite \
  "SELECT substr(oauth_access, 1, 6) FROM accounts;"

# Compter les messages importés (sync initiale = newer_than:30d)
sqlite3 ~/.pli/db.sqlite "SELECT COUNT(*) FROM messages;"

# Vérifier que GET /accounts ne fuite aucun token
curl -s http://localhost:8000/accounts | python -m json.tool | grep -i token
# → doit retourner aucune ligne
```

## 8. Erreurs fréquentes

| Symptôme | Cause | Fix |
|----------|-------|-----|
| `redirect_uri_mismatch` | URI dans la console ≠ `PLI_GMAIL_REDIRECT_URI` | Recopier exactement (incluant `http://` et port) |
| `access_denied` | Test user pas déclaré dans le consent screen | Ajouter ton email dans Test users (§3.7) |
| `invalid_client` | Client ID/secret faux ou inversés | Re-vérifier `.env` |
| `invalid_grant` au callback | `code` réutilisé (lien rechargé) | Refaire `/auth/gmail/start` pour un nouveau `code` |
| Plus de messages que prévu | `PLI_INITIAL_SYNC_DAYS` (default 30j) | Réduire dans `.env` pour test rapide |
| `state inconnu` après attente | `_STATE_STORE` in-memory perdu si reload uvicorn | Refaire `/auth/gmail/start` |

## 9. Sortie attendue de cette tâche T1.2

À la fin du runbook :
- `.env` rempli localement (non commit)
- Au moins 1 compte Gmail réellement connecté visible dans `GET /accounts`
- `GET /accounts` ne renvoie aucun token en clair (vérifié au §7)
- Capture d'écran du parcours dans `docs/governance/demo/m1-e2e-2026-04-22/`
  (cf. ticket T1.3)

---

_Réf. ticket M1-sprint1-closeout T1.2, ordre de mission 2026-04-22 §3 P1._
