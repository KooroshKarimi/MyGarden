#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

DB_PATH="infra/authelia/db.sqlite3"
BACKUP_PATH="infra/authelia/db.sqlite3.bak.$(date +%Y%m%d-%H%M%S)"

echo "[authelia] stopping container"
docker-compose stop authelia >/dev/null 2>&1 || true

if [[ -f "${DB_PATH}" ]]; then
  cp "${DB_PATH}" "${BACKUP_PATH}"
  echo "[authelia] backup created: ${BACKUP_PATH}"
  rm -f "${DB_PATH}"
  echo "[authelia] removed stale database: ${DB_PATH}"
else
  echo "[authelia] no existing database at ${DB_PATH}"
fi

echo "[authelia] recreating container"
docker-compose up -d --force-recreate authelia

echo "[authelia] status"
docker-compose ps authelia

echo "[authelia] recent logs"
docker-compose logs --tail=50 authelia
