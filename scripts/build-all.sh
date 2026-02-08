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

# Best-effort EXIF strip from JPEGs in content (privacy)
python3 -c "
import pathlib, sys
try:
    from PIL import Image
    count = 0
    for jpg in pathlib.Path('site/content').rglob('*.jpg'):
        img = Image.open(jpg)
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        clean.save(jpg, quality=95)
        count += 1
    for jpg in pathlib.Path('site/content').rglob('*.jpeg'):
        img = Image.open(jpg)
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        clean.save(jpg, quality=95)
        count += 1
    print(f'[INFO] Stripped EXIF from {count} JPEG(s)')
except ImportError:
    print('[WARN] Pillow not available — skipping EXIF strip', file=sys.stderr)
except Exception as e:
    print(f'[WARN] EXIF strip failed: {e}', file=sys.stderr)
" || true

build_audience() {
  local audience=$1
  local group=${2:-}
  local srcdir=".build/site-${audience}${group:+-${group}}"
  local outdir="out/${audience}"

  local baseurl="https://karimi.me/"

  if [[ "${audience}" == "group" ]]; then
    outdir="out/groups/${group}"
    baseurl="https://karimi.me/g/${group}/"
  elif [[ "${audience}" == "private" ]]; then
    baseurl="https://karimi.me/private/"
  fi

  mkdir -p "${outdir}" "${srcdir}"

  python3 scripts/build/filter_site.py \
    --source site \
    --dest "${srcdir}" \
    --audience "${audience}" \
    --group "${group}"

  docker-compose run --rm -T --user "$(id -u):$(id -g)" \
    hugo \
    --source "/workspace/${srcdir}" \
    --destination "/workspace/${outdir}" \
    --baseURL "${baseurl}" \
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
