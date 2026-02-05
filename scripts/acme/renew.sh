#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${DOMAIN:-karimi.me}
ACME_SERVER=${ACME_SERVER:-letsencrypt}

cert_exists() {
  [[ -f "certs/${DOMAIN}_ecc/fullchain.cer" ]] || [[ -f "certs/${DOMAIN}/fullchain.cer" ]]
}

set +e
docker-compose run --rm acme \
  --renew \
  -d "${DOMAIN}" \
  --dns dns_ionos \
  --home /acme.sh \
  --cert-home /certs \
  --server "${ACME_SERVER}"
RENEW_EXIT=$?
set -e

if [[ ${RENEW_EXIT} -ne 0 ]]; then
  if cert_exists; then
    echo "Renew step returned ${RENEW_EXIT}; existing cert found, continuing with deploy." >&2
  else
    echo "Renew step failed and no existing certificate was found." >&2
    exit ${RENEW_EXIT}
  fi
fi

docker-compose run --rm acme \
  --deploy \
  -d "${DOMAIN}" \
  --deploy-hook synology_dsm \
  --home /acme.sh \
  --cert-home /certs
