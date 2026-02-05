#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p out/public .build/site-public
rm -rf out/public/*

python3 scripts/build/filter_site.py \
  --source site \
  --dest .build/site-public \
  --audience public

docker-compose pull hugo

docker-compose run --rm \
  hugo \
  --source /workspace/.build/site-public \
  --destination /workspace/out/public \
  --cleanDestinationDir \
  --minify

./scripts/checks/leak-check.sh

echo "Public build written to out/public"
