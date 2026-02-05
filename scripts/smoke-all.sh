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

check_noindex() {
  local path=$1
  local header
  header=$(curl -fsSI "${BASE_URL}${path}" | tr -d '\r' | awk 'tolower($1)=="x-robots-tag:" {print tolower($0)}')
  if [[ "${header}" != *"noindex"* ]]; then
    echo "[FAIL] ${path} missing X-Robots-Tag noindex" >&2
    exit 1
  fi
  echo "[OK] ${path} has X-Robots-Tag noindex"
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

check_200 "/private/"
check_200 "/g/friends/"
check_200 "/g/family/"

check_noindex "/private/"
check_noindex "/g/friends/"
check_noindex "/g/family/"

check_contains "/" "Willkommen im digitalen Garten"
check_contains "/politik/" "Map of Content für Politik"
check_contains "/technik/" "Map of Content für Technik"
check_contains "/reisen/" "Map of Content für Reisen"
