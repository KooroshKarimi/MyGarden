#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

required=(
  out/public/index.html
  out/public/politik/index.html
  out/public/technik/index.html
  out/public/reisen/index.html
  out/public/politik/dossier-iran/index.html
)

for f in "${required[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "[FAIL] missing required public artifact: $f" >&2
    exit 1
  fi
  echo "[OK] found $f"
done
