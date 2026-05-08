# A4 — Build image `pli/backend:prod` (turnkey)

**Source arbitrage** : `docs/governance/arbitrages/2026-04-23-baseline-infra.md` §A4
**Propriétaire** : session M4 (build), session M3 (scan)
**Deadline** : 2026-04-27 fin de journée

---

## Contexte

Le sandbox de toutes les sessions (Mail direction + M1 + M2 + M3 + M4) n'a pas Docker. Seul un build depuis la machine hôte est réaliste. Ce script encapsule la commande `docker build --target runtime -t pli/backend:prod .` avec vérifications amont + attestation post-build.

## Pré-requis (JM, machine hôte Windows)

1. **Docker Desktop installé et démarré** : https://www.docker.com/products/docker-desktop/
   - Vérifier l'icône dans la system tray en bas à droite — doit être vert/stable.
   - Sur Windows, Docker Desktop nécessite WSL2 (déjà en place d'après la liste d'apps) ou Hyper-V (également présent).
2. **PowerShell** (Windows PowerShell 5.1 ou PowerShell 7, peu importe).
3. **~8 Go d'espace disque libre** (pour l'image python:3.11-slim + deps pli).

## Exécution

### Option 1 — double-clic

1. Aller dans `pli-app/backend/` avec l'Explorateur.
2. Clic droit sur `build-prod-image.ps1` → **Exécuter avec PowerShell**.
3. Si une alerte "fichier non signé" apparaît, autoriser (sinon voir §Troubleshooting).
4. Le script affiche en direct les étapes du build. Laisser tourner ~5-8 min au premier run.
5. À la fin : image ID + taille + digest affichés.
6. Appuyer sur Entrée pour fermer.

### Option 2 — terminal PowerShell

```powershell
cd "C:\Users\GESTIONJMJCONSULTING\OneDrive - JMJ CONSULTING\Bureau\PLI\PLI-Documentation\Mail\pli-app\backend"
.\build-prod-image.ps1
```

### Retour attendu

À coller dans le chat direction :
- **Image ID** (sha256 court)
- **Taille** (MB)
- **Durée** du build

Exemple :
```
Image ID    : sha256:abc123…
Taille      : 185.4 MB
Duree       : 5m42s
```

## Vérification post-build (optionnel côté JM)

```powershell
docker images pli/backend:prod
docker run --rm pli/backend:prod python -c "from pli import __version__; print(__version__)"
```

La seconde commande doit afficher la version actuelle (ex. `0.1.0-m1`) sans erreur — preuve que l'image est bootable.

## Puis côté M3

Une fois l'image buildée sur la machine hôte, M3 peut scanner depuis le même host :

```powershell
trivy image --severity CRITICAL,HIGH --ignore-unfixed pli/backend:prod
```

(Trivy s'installe via `scoop install trivy` ou `winget install Aqua.trivy`.)

## Troubleshooting

**"L'exécution de scripts est désactivée sur ce système"** :
```powershell
powershell -ExecutionPolicy Bypass -File .\build-prod-image.ps1
```
(Ou, une fois et pour tout l'utilisateur : `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.)

**"Cannot connect to the Docker daemon"** :
Docker Desktop n'est pas démarré. Ouvrir l'app, attendre l'icône verte, relancer le script.

**"Error response from daemon: dockerfile parse error"** :
Ne devrait pas arriver — Dockerfile vérifié par direction. Si ça arrive, ping direction.

**Build très lent (>15 min)** :
Probablement download python:3.11-slim depuis registry. Deuxième build = layers en cache, beaucoup plus rapide.

## Notes

- Le `.dockerignore` (ajouté 2026-04-24 par M4) exclut les caches, venv, tests, docs du context de build — image plus propre et plus rapide à scanner.
- Le Dockerfile existant est déjà multi-stage (`builder` → `runtime`), aligné arbitrage A4. Pas de `Dockerfile.prod` séparé nécessaire.
- L'image n'inclut **pas** de Postgres ni de Redis — c'est une image applicative pure, alembic + uvicorn au démarrage.

---

_Rédigé par session M4 le 2026-04-24, suite à "prend docker" direction._
_Réf. arbitrage A4 : `docs/governance/arbitrages/2026-04-23-baseline-infra.md`._
