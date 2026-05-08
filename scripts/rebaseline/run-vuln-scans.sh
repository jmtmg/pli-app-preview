#!/usr/bin/env bash
#
# Re-baseline scan vulns M3 — ticket tickets/M3-rebaseline.md T3.2.
#
# Lance les trois scans (pip-audit, npm audit, trivy) sur le binaire
# intégré et archive les rapports JSON dans docs/governance/metrics/
# pour audit direction.
#
# Target direction : 0 Critical / 0 High. Si nouveau High apparaît,
# ne PAS masquer : documenter dans le rapport de synthèse T3.4 avec
# proposition de patch.
#
# Usage :
#   ./scripts/rebaseline/run-vuln-scans.sh [--image=pli/backend:prod]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

IMAGE="${1:-pli/backend:prod}"
IMAGE="${IMAGE#--image=}"

# Garde-fou coordination M3/M4 — cf. REBASELINE-CHECKLIST.md §2.
# Workspace OneDrive non git-init → substitut = manifeste md5 logique
# (`docs/governance/tags/rebaseline-base-2026-04-22.md`, empreinte globale
# `6a8d82bcbd292422f3ef87d0d6a30dce`). Même contrat que git describe :
# refuse de tourner si un seul hash diffère.
echo "[vuln-scans] vérification baseline md5…"
"${SCRIPT_DIR}/check-baseline-md5.sh" || {
  echo "[vuln-scans] ABORT : baseline md5 invalidée ou manquante." >&2
  echo "[vuln-scans] dry-run local : PLI_REBASELINE_ALLOW_UNTAGGED=1 $0" >&2
  exit 1
}
CURRENT_TAG="${PLI_REBASELINE_TAG:-rebaseline-base-2026-04-22}"
echo "[vuln-scans] baseline de mesure : ${CURRENT_TAG}"

TIMESTAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
OUT_DIR="${REPO_ROOT}/docs/governance/metrics/vuln-scans/${TIMESTAMP}"
mkdir -p "${OUT_DIR}"

echo "[vuln-scans] cible image : ${IMAGE}"
echo "[vuln-scans] sortie      : ${OUT_DIR}"

# -----------------------------------------------------------------------------
# T3.2a — pip-audit (Python)
# -----------------------------------------------------------------------------
# Runs sur le lockfile intégré (pas de venv éphémère sandbox — on veut ce qui
# sera vraiment déployé). On capture JSON pour diff programmatique ET texte
# pour lecture humaine.

echo "[vuln-scans] pip-audit…"
if ! command -v pip-audit >/dev/null 2>&1; then
  echo "[vuln-scans] pip-audit manquant : pip install --break-system-packages pip-audit" >&2
  exit 2
fi

pip-audit \
  --requirement "${REPO_ROOT}/backend/requirements.lock" \
  --format json \
  --output "${OUT_DIR}/pip-audit.json" \
  --strict \
  || echo "[vuln-scans] pip-audit a trouvé des vulns (voir JSON)"

pip-audit \
  --requirement "${REPO_ROOT}/backend/requirements.lock" \
  --format columns \
  --output "${OUT_DIR}/pip-audit.txt" \
  || true

# -----------------------------------------------------------------------------
# T3.2b — npm audit (Node)
# -----------------------------------------------------------------------------
# --production pour ignorer les devDeps (Vite, Playwright, etc.) qui n'iront
# pas en prod. --json pour diff, --audit-level=high pour exit 0 si rien de grave.

echo "[vuln-scans] npm audit…"
pushd "${REPO_ROOT}/frontend" >/dev/null

npm audit --production --json > "${OUT_DIR}/npm-audit.json" 2>&1 || true
npm audit --production --audit-level=high > "${OUT_DIR}/npm-audit.txt" 2>&1 || true

popd >/dev/null

# -----------------------------------------------------------------------------
# T3.2c — trivy fs (image Docker)
# -----------------------------------------------------------------------------
# On scanne l'image prod build (pas l'image dev qui contient Tesseract + debug
# tools). Severity CRITICAL,HIGH seulement — Medium + Low sont tracés dans le
# rapport complet mais n'entrent pas dans le gate.

echo "[vuln-scans] trivy…"
if ! command -v trivy >/dev/null 2>&1; then
  echo "[vuln-scans] trivy manquant : https://aquasecurity.github.io/trivy/latest/getting-started/installation/" >&2
  exit 2
fi

trivy image \
  --severity CRITICAL,HIGH \
  --format json \
  --output "${OUT_DIR}/trivy-image.json" \
  --ignore-unfixed \
  "${IMAGE}" \
  || echo "[vuln-scans] trivy a trouvé des vulns (voir JSON)"

trivy image \
  --severity CRITICAL,HIGH,MEDIUM \
  --format table \
  --output "${OUT_DIR}/trivy-image.txt" \
  "${IMAGE}" \
  || true

# -----------------------------------------------------------------------------
# Agrégation gate Critical/High
# -----------------------------------------------------------------------------

python3 "${SCRIPT_DIR}/summarize-scans.py" \
  --pip-audit "${OUT_DIR}/pip-audit.json" \
  --npm-audit "${OUT_DIR}/npm-audit.json" \
  --trivy "${OUT_DIR}/trivy-image.json" \
  --output "${OUT_DIR}/SUMMARY.md"

echo "[vuln-scans] synthèse : ${OUT_DIR}/SUMMARY.md"
cat "${OUT_DIR}/SUMMARY.md"
