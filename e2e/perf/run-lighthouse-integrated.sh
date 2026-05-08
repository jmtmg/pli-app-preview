#!/usr/bin/env bash
#
# Runner Lighthouse re-baseline M3 sur binaire intégré.
#
# Ce script est volontairement verbeux : il refuse de démarrer tant que
# le binaire cible n'a pas les routers M2 montés. C'est le garde-fou
# direction pour éviter de re-mesurer sur un binaire Sprint-1-only et
# d'encore se planter comme avant audit 2026-04-22.
#
# Usage :
#   PLI_ENABLE_M2=1 ./run-lighthouse-integrated.sh
#
# Sortie : docs/governance/metrics/lighthouse-integrated/<timestamp>-*.html
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

# -----------------------------------------------------------------------------
# Garde-fous — refuser de tourner sans binaire intégré
# -----------------------------------------------------------------------------

if [[ "${PLI_ENABLE_M2:-}" != "1" ]]; then
  cat >&2 <<EOF
[lighthouse-integrated] ABORT : PLI_ENABLE_M2 != 1

Ce runner est réservé au binaire intégré (M2 wire-up). Si tu relances
sur le binaire Sprint 1 seul, tu reproduis l'erreur pointée par l'audit
2026-04-22 et la mesure n'a aucune valeur de re-baseline.

Attendre la livraison T2.2 de M2 (deadline 2026-05-07).
EOF
  exit 1
fi

# Garde-fou coordination M3/M4 : workspace OneDrive non git-init → le tag
# git est remplacé par un manifeste md5 logique (cf. REBASELINE-CHECKLIST.md §2
# et docs/governance/tags/rebaseline-base-2026-04-22.md). Même contrat :
# refuse de tourner si un seul hash diffère. M3 et M4 doivent mesurer sur la
# même empreinte globale pour que leurs chiffres soient comparables dans la
# décision GO M4. Override dry-run via PLI_REBASELINE_ALLOW_UNTAGGED=1.
echo "[lighthouse-integrated] vérification baseline md5…"
"${REPO_ROOT}/scripts/rebaseline/check-baseline-md5.sh" || {
  cat >&2 <<EOF
[lighthouse-integrated] ABORT : baseline md5 invalidée ou manquante.

Protocole : REBASELINE-CHECKLIST.md §2 + manifeste
  docs/governance/tags/rebaseline-base-2026-04-22.md

Pour dry-run local sans rapport officiel :
  PLI_REBASELINE_ALLOW_UNTAGGED=1 $0
EOF
  exit 1
}
CURRENT_TAG="${PLI_REBASELINE_TAG:-rebaseline-base-2026-04-22}"
echo "[lighthouse-integrated] baseline de mesure : ${CURRENT_TAG}"

# Vérifie que /api/billing répond (proxy : si le router n'est pas wire-up, 404).
BASE_API="${PLI_API_URL:-http://localhost:8000}"
if ! curl -fsS --max-time 3 "${BASE_API}/api/billing/ping" >/dev/null 2>&1; then
  cat >&2 <<EOF
[lighthouse-integrated] ABORT : /api/billing/ping KO sur ${BASE_API}

Le backend ne semble pas exposer le router billing. Vérifier que :
  1. uvicorn pli.main:app tourne avec PLI_ENABLE_M2=1
  2. app.include_router(billing.router, prefix="/api/billing") est actif
  3. Aucune erreur d'import au démarrage (ex. pli.auth)

Tant que ces 3 points ne sont pas verts, ne pas re-baseliner.
EOF
  exit 1
fi

# -----------------------------------------------------------------------------
# Vérifications secondaires
# -----------------------------------------------------------------------------

# npx lhci doit être disponible
if ! command -v npx >/dev/null 2>&1; then
  echo "[lighthouse-integrated] ABORT : npx introuvable" >&2
  exit 1
fi

# Dossier de sortie
OUT_DIR="${REPO_ROOT}/docs/governance/metrics/lighthouse-integrated"
mkdir -p "${OUT_DIR}"

# -----------------------------------------------------------------------------
# Exécution
# -----------------------------------------------------------------------------

echo "[lighthouse-integrated] baseline sur ${PLI_BASE_URL:-http://localhost:5173}"
echo "[lighthouse-integrated] sortie   : ${OUT_DIR}"

# NB : on utilise la config .cjs (CommonJS) pour éviter les soucis ESM avec lhci.
npx --yes @lhci/cli@0.13.x autorun \
  --config="${SCRIPT_DIR}/lighthouserc.integrated.cjs" \
  --collect.numberOfRuns=3

echo "[lighthouse-integrated] OK — rapports dans ${OUT_DIR}"
