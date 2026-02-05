#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${DOMAIN:-karimi.me}
TARGET_HOSTNAME=${TARGET_HOSTNAME:-koorosh.synology.me}
# Safer default for first go-live attempts when IPv6 path is unknown.
INCLUDE_AAAA=${INCLUDE_AAAA:-false}

export DOMAIN TARGET_HOSTNAME INCLUDE_AAAA

echo "[1/5] Sync IONOS DNS for ${DOMAIN} (target: ${TARGET_HOSTNAME}, INCLUDE_AAAA=${INCLUDE_AAAA})"
./scripts/domain/sync-ionos-dns.py

echo
echo "[2/5] Start/verify gateway"
./scripts/gateway/restart.sh

echo
echo "[3/5] DNS + path diagnostics"
./scripts/domain/check-dns-path.sh "${DOMAIN}" "synology.${DOMAIN}"

echo
echo "[4/5] TLS diagnostics"
./scripts/domain/diagnose-ssl.sh "${DOMAIN}"

echo
echo "[5/5] Optional certificate issue/deploy"
if [[ -n "${EMAIL:-}" ]]; then
  EMAIL="${EMAIL}" ./scripts/acme/issue.sh
else
  echo "Skipping ACME issue: EMAIL not set."
  echo "Run with: EMAIL=you@example.com ./scripts/domain/go-live.sh"
fi

echo
echo "Done. If https://${DOMAIN}/ still fails, verify DSM Reverse Proxy + certificate assignment for ${DOMAIN}:443."
