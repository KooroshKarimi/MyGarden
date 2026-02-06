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

  docker-compose run --rm -T \
    hugo \
    --source "/workspace/${srcdir}" \
    --destination "/workspace/${outdir}" \
    --cleanDestinationDir \
    --buildFuture \
    --minify
}

build_audience public
build_audience group friends
build_audience group family
build_audience private

./scripts/checks/leak-check.sh
./scripts/checks/verify-public-tree.sh
./scripts/checks/frontmatter-lint.sh
./scripts/checks/link-check.sh

echo "Builds written to out/public, out/groups/friends, out/groups/family, out/private"
