#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "[authelia-runtime] container status"
status_line=$(docker-compose ps authelia | awk 'NR==3{print}')
if [[ -z "${status_line}" ]]; then
  echo "[FAIL] authelia container not found in docker-compose ps output" >&2
  exit 1
fi
echo "${status_line}"

if ! grep -qi "Up" <<<"${status_line}"; then
  echo "[FAIL] authelia container is not running" >&2
  exit 1
fi

echo "[authelia-runtime] check startup path in logs"
recent_logs=$(docker-compose logs --tail=120 authelia || true)
if [[ "${recent_logs}" != *"Startup complete"* ]]; then
  echo "[FAIL] authelia did not report startup complete" >&2
  echo "${recent_logs}" >&2
  exit 1
fi

if [[ "${recent_logs}" != *"path '/auth'"* ]]; then
  echo "[FAIL] authelia is running with path '/' (or unknown), expected '/auth'." >&2
  echo "       You likely run an older config revision. Run: git pull, then recreate authelia." >&2
  exit 1
fi

echo "[authelia-runtime] OK (startup complete and path '/auth')"
