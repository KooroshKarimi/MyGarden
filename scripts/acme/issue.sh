#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${DOMAIN:-karimi.me}
EMAIL=${EMAIL:-}

if [[ -z "${EMAIL}" ]]; then
  echo "EMAIL is required (export EMAIL=you@example.com)." >&2
  exit 1
fi

docker-compose run --rm acme \
  --register-account -m "${EMAIL}"

docker-compose run --rm acme \
  --issue \
  --dns dns_ionos \
  -d "${DOMAIN}" \
  --keylength ec-256 \
  --home /acme.sh \
  --cert-home /certs

docker-compose run --rm acme \
  --deploy \
  -d "${DOMAIN}" \
  --deploy-hook synology_dsm \
  --home /acme.sh \
  --cert-home /certs
