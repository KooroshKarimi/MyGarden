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

  cert_subject=$(openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" </dev/null 2>/dev/null     | openssl x509 -noout -subject 2>/dev/null || true)
  cert_san=$(openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" </dev/null 2>/dev/null     | openssl x509 -noout -ext subjectAltName 2>/dev/null || true)

  if [[ -n "${cert_subject}" ]]; then
    echo
    echo "== Certificate identity =="
    echo "${cert_subject}"
    [[ -n "${cert_san}" ]] && echo "${cert_san}"
  fi

  if [[ "${cert_subject}${cert_san}" != *"${DOMAIN}"* ]]; then
    echo ""
    echo "WARNING: Certificate does not appear to include ${DOMAIN}." >&2
    echo "Likely DSM is still serving another cert (e.g. koorosh.synology.me)." >&2
    echo "Fix in DSM: Security -> Certificate -> Configure, assign karimi.me cert to reverse proxy host karimi.me:443." >&2
  fi
else
  echo "openssl not found; skipping handshake details"
fi

echo
echo "== HTTP head checks =="
curl -kI "https://${DOMAIN}/" || true
curl -kI "https://${DOMAIN}/healthz" || true
