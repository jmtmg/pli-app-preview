#!/usr/bin/env bash
# Drill mensuel : télécharge un backup récent, déchiffre, restaure sur base
# jetable, vérifie quelques invariants, nettoie. Exit non-zéro = alerte.
#
# Variables d'env requises :
#   BACKUP_S3_BUCKET, BACKUP_S3_ENDPOINT, AWS_*
#   BACKUP_AGE_IDENTITY          -> chemin vers clé privée age (restreint 0600)
#   DRILL_DATABASE_URL_PREFIX    -> postgres://user:pass@host/  (sans dbname)
#
# Usage : cron mensuel le 1er à 04:00 UTC.

set -euo pipefail

: "${BACKUP_S3_BUCKET:?must be set}"
: "${BACKUP_S3_ENDPOINT:?must be set}"
: "${BACKUP_AGE_IDENTITY:?must be set}"
: "${DRILL_DATABASE_URL_PREFIX:?must be set}"

TMPDIR="$(mktemp -d -t pli-drill-XXXXXX)"
trap 'rm -rf "${TMPDIR}"; _cleanup_drill_db' EXIT

DRILL_DB="pli_drill_$(date -u +%Y%m%dT%H%M%SZ)"

log() { printf '[%s] %s\n' "$(date -u '+%F %T')" "$*" >&2; }

_cleanup_drill_db() {
  psql "${DRILL_DATABASE_URL_PREFIX}postgres" -c "DROP DATABASE IF EXISTS \"${DRILL_DB}\";" \
    >/dev/null 2>&1 || true
}

log "selecting latest backup"
LATEST="$(aws --endpoint-url "${BACKUP_S3_ENDPOINT}" \
          s3 ls "s3://${BACKUP_S3_BUCKET}/backups/postgres/" \
          | sort | tail -n 1 | awk '{print $4}')"

if [[ -z "${LATEST}" ]]; then
  log "ERROR: no backup found"
  exit 2
fi

log "drill target: ${LATEST}"
aws --endpoint-url "${BACKUP_S3_ENDPOINT}" \
    s3 cp "s3://${BACKUP_S3_BUCKET}/backups/postgres/${LATEST}" "${TMPDIR}/enc.age" \
    --only-show-errors

log "decrypting"
age -d -i "${BACKUP_AGE_IDENTITY}" -o "${TMPDIR}/dump.sql.gz" "${TMPDIR}/enc.age"

log "creating drill db ${DRILL_DB}"
createdb --maintenance-db="${DRILL_DATABASE_URL_PREFIX}postgres" "${DRILL_DB}"

log "restoring"
pg_restore --no-owner --no-privileges -j 2 \
           -d "${DRILL_DATABASE_URL_PREFIX}${DRILL_DB}" \
           "${TMPDIR}/dump.sql.gz"

log "running invariants"
PSQL() { psql -d "${DRILL_DATABASE_URL_PREFIX}${DRILL_DB}" -tAc "$1"; }

[[ "$(PSQL "SELECT to_regclass('public.users') IS NOT NULL;")" == "t" ]] \
  || { log "FAIL: users table missing"; exit 3; }

ROW_COUNT="$(PSQL "SELECT COUNT(*) FROM users;")"
[[ "${ROW_COUNT}" -ge 0 ]] || { log "FAIL: users count invalid"; exit 3; }

RLS="$(PSQL "SELECT relrowsecurity FROM pg_class WHERE relname='messages';")"
[[ "${RLS}" == "t" ]] || { log "FAIL: RLS not enabled on messages"; exit 3; }

log "DRILL OK — restored ${LATEST}, users=${ROW_COUNT}, rls=${RLS}"

# Optional Slack success notification.
if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
  payload=$(printf '{"text":"pli restore drill ok backup=`%s` users=%s"}' \
              "${LATEST}" "${ROW_COUNT}")
  curl -fsS -X POST -H 'Content-Type: application/json' -d "${payload}" \
       "${SLACK_WEBHOOK_URL}" >/dev/null 2>&1 || true
fi
