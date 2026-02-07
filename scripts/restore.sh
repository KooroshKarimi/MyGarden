#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ $# -lt 1 ]; then
  echo "Usage: $0 <backup-tarball>" >&2
  exit 1
fi

BACKUP="$1"

if [ ! -f "${BACKUP}" ]; then
  echo "[FAIL] Backup file not found: ${BACKUP}" >&2
  exit 1
fi

echo "[INFO] Stopping services..."
docker-compose stop authelia remark42 remark42-private freshrss

echo "[INFO] Extracting ${BACKUP}..."
tar xzf "${BACKUP}"

echo "[INFO] Starting services..."
docker-compose start authelia remark42 remark42-private freshrss

echo "[INFO] Waiting for services to start..."
sleep 5

# Healthcheck
BASE_URL=${BASE_URL:-http://localhost:1234}
FAILED=0

for path in /healthz; do
  CODE=$(curl -sS -o /dev/null -w "%{http_code}" "${BASE_URL}${path}" || true)
  if [ "${CODE}" = "200" ]; then
    echo "[OK] ${path} -> ${CODE}"
  else
    echo "[WARN] ${path} -> ${CODE}"
    FAILED=1
  fi
done

if [ "${FAILED}" -eq 0 ]; then
  echo "[OK] Restore complete and verified."
else
  echo "[WARN] Restore complete but some health checks failed. Please verify manually."
fi
