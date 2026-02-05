#!/usr/bin/env bash
set -euo pipefail

HOST=${HOST:-localhost}
PORT=${PORT:-1234}
BASE_URL="http://${HOST}:${PORT}"

# Start only gateway to avoid requiring TLS env vars for local/domain-through-proxy tests.
docker-compose up -d gateway

check_200() {
  local path=$1
  local code
  code=$(curl -fsS -o /dev/null -w "%{http_code}" "${BASE_URL}${path}")
  if [[ "${code}" != "200" ]]; then
    echo "[FAIL] ${BASE_URL}${path} -> ${code}" >&2
    exit 1
  fi
  echo "[OK] ${BASE_URL}${path} -> ${code}"
}

check_200 "/"
check_200 "/healthz"

echo
echo "Gateway is up."
echo "Next DSM Reverse Proxy target: http://${HOST}:${PORT}"
