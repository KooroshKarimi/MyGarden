#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "[1/4] Shell syntax checks"
bash -n \
  scripts/build-public.sh \
  scripts/build-all.sh \
  scripts/checks/leak-check.sh \
  scripts/smoke.sh \
  scripts/acme/issue.sh \
  scripts/acme/renew.sh \
  scripts/gateway/restart.sh \
  scripts/domain/check-dns-path.sh \
  scripts/domain/check-propagation.sh \
  scripts/domain/diagnose-ssl.sh \
  scripts/domain/go-live.sh

echo "[2/4] Compose env placeholders (grep fallback for NAS without rg)"
grep -nE "SYNO_HOSTNAME|IONOS_PREFIX|SYNO_USERNAME|HUGO_IMAGE" docker-compose.yml .env.example

echo "[3/4] Build pipeline references"
grep -nE "build-public|build-all|leak-check|HUGO_IMAGE|docker-compose pull hugo|politik|technik|reisen|index.xml|dossier-iran|timeline-entry|event_date|visibility" README.md scripts/build-public.sh docker-compose.yml scripts/smoke.sh

echo "[4/4] Domain-routing references"
grep -nE "domain-routing|docker-compose up -d gateway" README.md scripts/gateway/restart.sh docs/domain-routing.md

echo "All NAS checks passed."
