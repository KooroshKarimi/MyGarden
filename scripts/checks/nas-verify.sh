#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "[1/3] Shell syntax checks"
bash -n scripts/smoke.sh scripts/acme/issue.sh scripts/acme/renew.sh scripts/gateway/restart.sh

echo "[2/3] Compose env placeholders (grep fallback for NAS without rg)"
grep -nE "SYNO_HOSTNAME|IONOS_PREFIX|SYNO_USERNAME" docker-compose.yml

echo "[3/3] Domain-routing references"
grep -nE "domain-routing|docker-compose up -d gateway" README.md scripts/gateway/restart.sh docs/domain-routing.md

echo "All NAS checks passed."
