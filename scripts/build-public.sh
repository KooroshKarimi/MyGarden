#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

require_docker_access() {
  if docker info >/dev/null 2>&1; then
    return 0
  fi

  echo "[FAIL] Docker daemon is not accessible for current user." >&2
  echo "       Re-run with sudo or add your user to the docker group on NAS." >&2
  exit 1
}

require_docker_access

mkdir -p out/public .build/site-public
rm -rf out/public/*

python3 scripts/build/filter_site.py \
  --source site \
  --dest .build/site-public \
  --audience public

docker-compose pull hugo

docker-compose run --rm -T \
  hugo \
  --source /workspace/.build/site-public \
  --destination /workspace/out/public \
  --cleanDestinationDir \
  --buildFuture \
  --minify

./scripts/checks/leak-check.sh
./scripts/checks/verify-public-tree.sh

echo "Public build written to out/public"
