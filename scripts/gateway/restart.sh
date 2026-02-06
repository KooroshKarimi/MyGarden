#!/usr/bin/env bash
set -euo pipefail

PORT=${PORT:-1234}
HOST=${HOST:-localhost}
BASE_URL="http://${HOST}:${PORT}"

# Start only gateway to avoid requiring TLS env vars for local/domain-through-proxy tests.
docker-compose up -d gateway

check_200() {
  local base=$1
  local path=$2
  local code
  code=$(curl -fsS -o /dev/null -w "%{http_code}" "${base}${path}" || true)
  if [[ "${code}" != "200" ]]; then
    return 1
  fi
  echo "[OK] ${base}${path} -> ${code}"
}

if ! check_200 "${BASE_URL}" "/" || ! check_200 "${BASE_URL}" "/healthz"; then
  # Synology can expose published ports on LAN-IP while localhost loopback fails.
  LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
  if [[ -n "${LAN_IP}" ]]; then
    ALT_BASE="http://${LAN_IP}:${PORT}"
    echo "[WARN] ${BASE_URL} not reachable, trying ${ALT_BASE}" >&2
    check_200 "${ALT_BASE}" "/"
    check_200 "${ALT_BASE}" "/healthz"
    BASE_URL="${ALT_BASE}"
  else
    echo "[FAIL] gateway is not reachable on ${BASE_URL}" >&2
    exit 1
  fi
fi

echo
echo "Gateway is up."
echo "Detected health endpoint: ${BASE_URL}"
echo "Next DSM Reverse Proxy target: http://<NAS-LAN-IP>:${PORT}"
