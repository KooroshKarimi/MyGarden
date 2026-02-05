#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "[1/7] Shell syntax checks"
bash -n \
  scripts/build-public.sh \
  scripts/build-all.sh \
  scripts/checks/leak-check.sh \
  scripts/checks/verify-public-tree.sh \
  scripts/checks/filter-site-check.sh \
  scripts/smoke.sh \
  scripts/smoke-all.sh \
  scripts/acme/issue.sh \
  scripts/acme/renew.sh \
  scripts/gateway/restart.sh \
  scripts/domain/check-dns-path.sh \
  scripts/domain/check-propagation.sh \
  scripts/domain/diagnose-ssl.sh \
  scripts/domain/go-live.sh

echo "[2/7] Compose env placeholders (grep fallback for NAS without rg)"
grep -nE "SYNO_HOSTNAME|IONOS_PREFIX|SYNO_USERNAME|HUGO_IMAGE" docker-compose.yml .env.example

echo "[3/7] Build pipeline references"
grep -nE "build-public|build-all|leak-check|verify-public-tree|HUGO_IMAGE|docker-compose pull hugo|politik|technik|reisen|index.xml|dossier-iran|timeline-entry|event_date|visibility" README.md scripts/build-public.sh docker-compose.yml scripts/smoke.sh

echo "[4/7] Authelia config references"
grep -nE "authelia|AUTHELIA_|/auth/|auth_unavailable|/private/|/g/" docker-compose.yml infra/nginx/conf.d/default.conf .env.example README.md

echo "[5/7] Nginx auth upstream mode"
# Must use runtime-resolved upstream to avoid nginx boot failure when authelia is absent
grep -n "resolver 127.0.0.11" infra/nginx/conf.d/default.conf
grep -nF 'set $authelia_upstream authelia:9091;' infra/nginx/conf.d/default.conf
grep -nF 'proxy_pass http://$authelia_upstream/' infra/nginx/conf.d/default.conf
grep -nF 'proxy_pass http://$authelia_upstream/api/authz/auth-request;' infra/nginx/conf.d/default.conf
if grep -nE "proxy_pass http://authelia:9091" infra/nginx/conf.d/default.conf; then
  echo "[FAIL] static authelia upstream found in nginx config; gateway may fail at boot" >&2
  exit 1
fi

echo "[6/7] Domain-routing references"
grep -nE "domain-routing|docker-compose up -d gateway" README.md scripts/gateway/restart.sh docs/domain-routing.md

echo "[7/7] filter-site checks"
./scripts/checks/filter-site-check.sh

echo "All NAS checks passed."
