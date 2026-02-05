#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p out/public

docker-compose pull hugo

docker-compose run --rm \
  hugo \
  --source /src \
  --destination /out \
  --cleanDestinationDir \
  --minify

echo "Public build written to out/public"
