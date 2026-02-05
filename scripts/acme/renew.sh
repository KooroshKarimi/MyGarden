#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${DOMAIN:-karimi.me}
ACME_SERVER=${ACME_SERVER:-letsencrypt}

load_env_compat() {
  if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
  fi

  if [[ -z "${SYNO_HOSTNAME:-}" && -n "${SYNO_DSM_HOSTNAME:-}" ]]; then
    export SYNO_HOSTNAME="${SYNO_DSM_HOSTNAME}"
  fi

  if [[ -z "${SYNO_PORT:-}" && -n "${SYNO_DSM_PORT:-}" ]]; then
    export SYNO_PORT="${SYNO_DSM_PORT}"
  fi
}

require_var() {
  local name=$1
  if [[ -z "${!name:-}" ]]; then
    echo "${name} is required (set it in .env)." >&2
    exit 1
  fi
}

export_syno_compat_env() {
  export SYNO_Username="${SYNO_USERNAME:-}"
  export SYNO_Password="${SYNO_PASSWORD:-}"
  export SYNO_Certificate="${SYNO_CERTIFICATE:-}"
  export SYNO_Hostname="${SYNO_HOSTNAME:-}"
  export SYNO_Port="${SYNO_PORT:-5001}"
  export SYNO_Scheme="${SYNO_SCHEME:-https}"
  export SYNO_Device_ID="${SYNO_DEVICE_ID:-}"
  if [[ -n "${SYNO_DEVICE_ID:-}" ]]; then
    export SYNO_Device_Name="${SYNO_DEVICE_NAME:-CertRenewal}"
    export SYNO_DEVICE_NAME="${SYNO_DEVICE_NAME:-CertRenewal}"
  else
    export SYNO_Device_Name=""
    export SYNO_DEVICE_NAME=""
  fi
}

load_env_compat
require_var SYNO_HOSTNAME
require_var SYNO_USERNAME
require_var SYNO_PASSWORD
require_var SYNO_CERTIFICATE
export_syno_compat_env

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

docker-compose run --rm \
  -e "SYNO_HOSTNAME=${SYNO_HOSTNAME:-}" \
  -e "SYNO_PORT=${SYNO_PORT:-5001}" \
  -e "SYNO_SCHEME=${SYNO_SCHEME:-https}" \
  -e "SYNO_USERNAME=${SYNO_USERNAME:-}" \
  -e "SYNO_PASSWORD=${SYNO_PASSWORD:-}" \
  -e "SYNO_CERTIFICATE=${SYNO_CERTIFICATE:-}" \
  -e "SYNO_Username=${SYNO_Username:-}" \
  -e "SYNO_Password=${SYNO_Password:-}" \
  -e "SYNO_Certificate=${SYNO_Certificate:-}" \
  -e "SYNO_Hostname=${SYNO_Hostname:-}" \
  -e "SYNO_Port=${SYNO_Port:-5001}" \
  -e "SYNO_Scheme=${SYNO_Scheme:-https}" \
  -e "SYNO_Device_ID=${SYNO_Device_ID:-}" \
  -e "SYNO_Device_Name=${SYNO_Device_Name:-}" \
  acme \
  --deploy \
  -d "${DOMAIN}" \
  --deploy-hook synology_dsm \
  --home /acme.sh \
  --cert-home /certs
