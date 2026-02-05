#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${BASE_URL:-http://localhost:1234}

check_200() {
  local path=$1
  local code
  code=$(curl -fsS -o /dev/null -w "%{http_code}" "${BASE_URL}${path}")
  if [[ "${code}" != "200" ]]; then
    echo "[FAIL] ${path} -> ${code}" >&2
    exit 1
  fi
  echo "[OK] ${path} -> ${code}"
}

check_200 "/"
check_200 "/healthz"
