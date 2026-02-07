#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_DIR="backups"
BACKUP_FILE="${BACKUP_DIR}/${TIMESTAMP}.tar.gz"

mkdir -p "${BACKUP_DIR}"

TARGETS=()

# Authelia
[ -f infra/authelia/db.sqlite3 ] && TARGETS+=("infra/authelia/db.sqlite3")
[ -f infra/authelia/users_database.yml ] && TARGETS+=("infra/authelia/users_database.yml")

# Remark42 (public + private)
[ -d infra/remark42 ] && TARGETS+=("infra/remark42")
[ -d infra/remark42-private ] && TARGETS+=("infra/remark42-private")

# FreshRSS
[ -d infra/freshrss ] && TARGETS+=("infra/freshrss")

if [ ${#TARGETS[@]} -eq 0 ]; then
  echo "[WARN] No backup targets found." >&2
  exit 1
fi

tar czf "${BACKUP_FILE}" "${TARGETS[@]}"

SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "[OK] Backup created: ${BACKUP_FILE} (${SIZE})"
