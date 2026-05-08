#!/usr/bin/env bash
# Pipeline de backup chiffré PostgreSQL pour PLI.
# Usage : cron quotidien 03:00 UTC.
#
# Pré-requis :
#   - age installé (https://github.com/FiloSottile/age)
#   - pg_dump disponible (postgresql-client)
#   - awscli ou s5cmd pour upload S3-compat
#   - variables d'env :
#       DATABASE_URL              -> chaîne postgres://…
#       BACKUP_AGE_RECIPIENT      -> age1… (clé publique)
#       BACKUP_S3_BUCKET          -> nom du bucket (provider séparé du DB hébergeur)
#       BACKUP_S3_ENDPOINT        -> URL endpoint S3-compat
#       BACKUP_S3_REGION          -> région
#       AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
#
# Ne stocke jamais la clé privée age à côté des backups.

set -euo pipefail

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
NAME="pli-${TIMESTAMP}.sql.gz.age"
TMPDIR="$(mktemp -d -t pli-backup-XXXXXX)"
trap 'rm -rf "${TMPDIR}"' EXIT

OUT="${TMPDIR}/${NAME}"

: "${DATABASE_URL:?must be set}"
: "${BACKUP_AGE_RECIPIENT:?must be set}"
: "${BACKUP_S3_BUCKET:?must be set}"
: "${BACKUP_S3_ENDPOINT:?must be set}"

log() { printf '[%s] %s\n' "$(date -u '+%F %T')" "$*" >&2; }

log "starting backup ${NAME}"
START="$(date +%s)"

# pg_dump custom format (-Fc) + niveau de compression max (-Z 9) → pipe age.
pg_dump -Fc -Z 9 "${DATABASE_URL}" \
  | age -r "${BACKUP_AGE_RECIPIENT}" -o "${OUT}"

SIZE="$(stat -c%s "${OUT}")"
SHA="$(sha256sum "${OUT}" | awk '{print $1}')"
log "dump+encrypt ok size=${SIZE} sha256=${SHA}"

if (( SIZE < 1024 )); then
  log "ERROR: backup suspiciously small, aborting upload"
  exit 2
fi

# Upload vers S3-compat, storage-class standard, activation object lock si possible.
aws --endpoint-url "${BACKUP_S3_ENDPOINT}" \
    s3 cp "${OUT}" "s3://${BACKUP_S3_BUCKET}/backups/postgres/${NAME}" \
    --only-show-errors

DURATION="$(( $(date +%s) - START ))"
log "upload ok duration=${DURATION}s → s3://${BACKUP_S3_BUCKET}/backups/postgres/${NAME}"

# Notification Slack (optionnel — webhook URL si défini).
if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
  payload=$(printf '{"text":"pli backup ok `%s` size=%s duration=%ss sha=%s..."}' \
              "${NAME}" "${SIZE}" "${DURATION}" "${SHA:0:12}")
  curl -fsS -X POST -H 'Content-Type: application/json' -d "${payload}" \
       "${SLACK_WEBHOOK_URL}" >/dev/null 2>&1 || true
fi

# Metric Prometheus/Loki (via stdout pour collecte cron wrapper).
printf 'pli_backup_success 1\npli_backup_size_bytes %s\npli_backup_duration_s %s\n' \
  "${SIZE}" "${DURATION}"
