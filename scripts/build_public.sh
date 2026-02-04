#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

mkdir -p "${ROOT_DIR}/out/public"

if command -v hugo >/dev/null 2>&1; then
  hugo --source "${ROOT_DIR}/site" --destination "${ROOT_DIR}/out/public"
  exit 0
fi

docker run --rm \
  -v "${ROOT_DIR}/site:/src" \
  -v "${ROOT_DIR}/out/public:/out" \
  klakegg/hugo:0.121.2 \
  hugo --source /src --destination /out
