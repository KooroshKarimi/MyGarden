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
check_200 "/index.xml"
check_200 "/politik/"
check_200 "/technik/"
check_200 "/reisen/"
check_200 "/politik/dossier-iran/"


check_contains() {
  local path=$1
  local needle=$2
  local body
  body=$(curl -fsS "${BASE_URL}${path}")
  if [[ "${body}" != *"${needle}"* ]]; then
    echo "[FAIL] ${path} missing expected marker: ${needle}" >&2
    exit 1
  fi
  echo "[OK] ${path} contains marker: ${needle}"
}



check_contains "/" "Willkommen im digitalen Garten"
check_contains "/politik/" "Map of Content für Politik"
check_contains "/technik/" "Map of Content für Technik"
check_contains "/reisen/" "Map of Content für Reisen"
