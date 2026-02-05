#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${1:-karimi.me}

echo "== TLS handshake test for ${DOMAIN} =="
if command -v openssl >/dev/null 2>&1; then
  openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" </dev/null 2>/tmp/${DOMAIN}.ssl.err | sed -n '1,20p' || true
  if [[ -s "/tmp/${DOMAIN}.ssl.err" ]]; then
    echo "-- openssl stderr --"
    sed -n '1,40p' "/tmp/${DOMAIN}.ssl.err"
  fi
else
  echo "openssl not found; skipping handshake details"
fi

echo
echo "== HTTP head checks =="
curl -kI "https://${DOMAIN}/" || true
curl -kI "https://${DOMAIN}/healthz" || true
