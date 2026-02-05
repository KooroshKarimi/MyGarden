#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker-compose pull hugo

build_audience() {
  local audience=$1
  local group=${2:-}
  local srcdir=".build/site-${audience}${group:+-${group}}"
  local outdir="out/${audience}"

  if [[ "${audience}" == "group" ]]; then
    outdir="out/groups/${group}"
  fi

  mkdir -p "${outdir}" "${srcdir}"
  rm -rf "${outdir}"/*

  python3 scripts/build/filter_site.py \
    --source site \
    --dest "${srcdir}" \
    --audience "${audience}" \
    --group "${group}"

  docker-compose run --rm \
    hugo \
    --source "/workspace/${srcdir}" \
    --destination "/workspace/${outdir}" \
    --cleanDestinationDir \
    --minify
}

build_audience public
build_audience group friends
build_audience group family
build_audience private

./scripts/checks/leak-check.sh
./scripts/checks/verify-public-tree.sh

echo "Builds written to out/public, out/groups/friends, out/groups/family, out/private"
