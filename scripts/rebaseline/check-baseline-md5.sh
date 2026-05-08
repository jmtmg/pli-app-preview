#!/usr/bin/env bash
#
# Garde-fou "baseline md5" — substitut au tag git pour workspace OneDrive.
#
# Origine : direction Mail a émis `docs/governance/tags/rebaseline-base-2026-04-22.md`
# (empreinte globale `6a8d82bcbd292422f3ef87d0d6a30dce`) en remplacement d'un
# tag git non-posable (le workspace n'est pas git-init). Cf. §1 du manifeste.
#
# Tout runner de mesure officielle (perf, vulns, E2E) doit appeler ce script
# AVANT de démarrer. Si un seul hash diffère OU si l'empreinte globale dévie,
# le runner doit refuser de tourner : §7 du manifeste dit explicitement
# "ouvrir un ticket P0-rebaseline-drift-<date> et ne pas publier de métriques".
#
# Override : PLI_REBASELINE_ALLOW_UNTAGGED=1 (dry-run local, jamais rapport).
#
# Usage :
#   ./scripts/rebaseline/check-baseline-md5.sh
#   → exit 0  si baseline OK
#   → exit 1  si drift détecté
#   → exit 2  si fichiers de référence introuvables
#
# Variable de sortie : PLI_REBASELINE_TAG = "rebaseline-base-2026-04-22"
# (utilisée par les runners pour nommer leurs répertoires de sortie de
# façon comparable au protocole git-tag initial).
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

MANIFEST="${REPO_ROOT}/docs/governance/tags/rebaseline-base-2026-04-22.md"
EXPECTED_GLOBAL_MD5="6a8d82bcbd292422f3ef87d0d6a30dce"
BASELINE_NAME="rebaseline-base-2026-04-22"

# -----------------------------------------------------------------------------
# Override dry-run
# -----------------------------------------------------------------------------

if [[ "${PLI_REBASELINE_ALLOW_UNTAGGED:-0}" == "1" ]]; then
  echo "[check-baseline-md5] OVERRIDE PLI_REBASELINE_ALLOW_UNTAGGED=1" >&2
  echo "[check-baseline-md5] dry-run local accepté — NE PAS publier de rapport officiel" >&2
  exit 0
fi

# -----------------------------------------------------------------------------
# Fichier de référence présent ?
# -----------------------------------------------------------------------------

if [[ ! -f "${MANIFEST}" ]]; then
  cat >&2 <<EOF
[check-baseline-md5] ABORT : manifeste introuvable
  attendu : ${MANIFEST}

Le manifeste est émis par direction et sert de référence à toute campagne
de mesure. Si absent, récupérer la version à jour auprès de direction Mail
avant de relancer la mesure.
EOF
  exit 2
fi

# -----------------------------------------------------------------------------
# Étape 1 — reconstituer les manifestes locaux
# -----------------------------------------------------------------------------

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

cd "${REPO_ROOT}/backend"
{
  find pli -name "*.py" -not -path "*/__pycache__/*" | sort
  find tests -name "*.py" -not -path "*/__pycache__/*" | sort
  echo pyproject.toml
} | xargs md5sum > "${WORK_DIR}/backend_local.txt"

cd "${REPO_ROOT}"
find docs/adr -name "*.md" | sort | xargs md5sum > "${WORK_DIR}/adr_local.txt"

# -----------------------------------------------------------------------------
# Étape 2 — extraire la référence depuis le manifeste markdown
# -----------------------------------------------------------------------------

grep -E '^[0-9a-f]{32}  (pli|tests|pyproject|docs)' "${MANIFEST}" \
  > "${WORK_DIR}/ref_all.txt"

REF_LINES="$(wc -l < "${WORK_DIR}/ref_all.txt" | tr -d ' ')"
if [[ "${REF_LINES}" -ne 105 ]]; then
  cat >&2 <<EOF
[check-baseline-md5] ABORT : manifeste corrompu
  attendu : 105 lignes de hash (72 pli + 24 tests + 1 pyproject + 8 adr)
  trouvé  : ${REF_LINES} lignes

Le manifeste ${MANIFEST##*/} semble altéré. Vérifier l'intégrité du fichier
avec direction avant de relancer.
EOF
  exit 2
fi

# Split ref en backend (pli+tests+pyproject) vs adr
grep -E '^[0-9a-f]{32}  (pli|tests|pyproject)' "${WORK_DIR}/ref_all.txt" \
  | sort > "${WORK_DIR}/ref_backend.txt"
grep -E '^[0-9a-f]{32}  docs/adr' "${WORK_DIR}/ref_all.txt" \
  | sort > "${WORK_DIR}/ref_adr.txt"

sort "${WORK_DIR}/backend_local.txt" > "${WORK_DIR}/backend_local_sorted.txt"
sort "${WORK_DIR}/adr_local.txt" > "${WORK_DIR}/adr_local_sorted.txt"

# -----------------------------------------------------------------------------
# Étape 3 — diff backend
# -----------------------------------------------------------------------------

if ! diff -q "${WORK_DIR}/ref_backend.txt" "${WORK_DIR}/backend_local_sorted.txt" >/dev/null; then
  echo "[check-baseline-md5] DRIFT détecté backend/ :" >&2
  diff "${WORK_DIR}/ref_backend.txt" "${WORK_DIR}/backend_local_sorted.txt" >&2 || true
  cat >&2 <<EOF

[check-baseline-md5] ABORT : baseline ${BASELINE_NAME} invalidée (backend).

Action requise (§7 manifeste) :
  1. NE PAS publier de métriques sur cette mesure.
  2. Ouvrir ticket P0-rebaseline-drift-\$(date -u +%Y-%m-%d) dans
     docs/governance/tickets/.
  3. Remonter à direction Mail pour ré-émettre une baseline à jour.
EOF
  exit 1
fi

# -----------------------------------------------------------------------------
# Étape 4 — diff ADR
# -----------------------------------------------------------------------------

if ! diff -q "${WORK_DIR}/ref_adr.txt" "${WORK_DIR}/adr_local_sorted.txt" >/dev/null; then
  echo "[check-baseline-md5] DRIFT détecté docs/adr/ :" >&2
  diff "${WORK_DIR}/ref_adr.txt" "${WORK_DIR}/adr_local_sorted.txt" >&2 || true
  cat >&2 <<EOF

[check-baseline-md5] ABORT : baseline ${BASELINE_NAME} invalidée (ADR).

Action requise : idem §7 manifeste — ne pas publier, ouvrir ticket
P0-rebaseline-drift-\$(date -u +%Y-%m-%d).
EOF
  exit 1
fi

# -----------------------------------------------------------------------------
# Étape 5 — empreinte globale
# -----------------------------------------------------------------------------

# §2.3 : md5(concat(backend_md5.txt, adr_md5.txt))
# Ordre AFFICHÉ (non-trié) — cf. §3 puis §6 du manifeste.
GLOBAL_MD5="$(cat "${WORK_DIR}/backend_local.txt" "${WORK_DIR}/adr_local.txt" | md5sum | awk '{print $1}')"

if [[ "${GLOBAL_MD5}" != "${EXPECTED_GLOBAL_MD5}" ]]; then
  cat >&2 <<EOF
[check-baseline-md5] ABORT : empreinte globale divergente
  attendue : ${EXPECTED_GLOBAL_MD5}
  calculée : ${GLOBAL_MD5}

Les hashes unitaires correspondent mais l'empreinte globale non, ce qui
signifie que l'ordre de concaténation ou un fichier caché diffère. Ouvrir
ticket P0-rebaseline-drift-\$(date -u +%Y-%m-%d).
EOF
  exit 1
fi

# -----------------------------------------------------------------------------
# OK
# -----------------------------------------------------------------------------

echo "[check-baseline-md5] OK — baseline ${BASELINE_NAME} vérifiée"
echo "[check-baseline-md5]   105/105 hashes identiques"
echo "[check-baseline-md5]   empreinte globale : ${GLOBAL_MD5}"

# Export pour runners appelants (source-able si besoin)
export PLI_REBASELINE_TAG="${BASELINE_NAME}"
export PLI_REBASELINE_GLOBAL_MD5="${GLOBAL_MD5}"
