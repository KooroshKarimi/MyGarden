#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${DOMAIN:-karimi.me}

docker-compose run --rm acme \
  --renew \
  -d "${DOMAIN}" \
  --dns dns_ionos \
  --home /acme.sh \
  --cert-home /certs

docker-compose run --rm acme \
  --deploy \
  -d "${DOMAIN}" \
  --deploy-hook synology_dsm \
  --home /acme.sh \
  --cert-home /certs
