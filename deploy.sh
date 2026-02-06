#!/usr/bin/env bash
set -Eeuo pipefail

log() {
  printf '[%s] [DEPLOY] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

err() {
  printf '[%s] [DEPLOY][ERROR] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

on_error() {
  local ec=$?
  err "Deploy failed (exit code: $ec)"
  err "Last command: ${BASH_COMMAND}"
  exit "$ec"
}
trap on_error ERR

WORKDIR="$(cd "$(dirname "$0")" && pwd)"
BRANCH="${DEPLOY_BRANCH:-main}"
COMPOSE_FILE="${DEPLOY_COMPOSE_FILE:-docker-compose.yml}"

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

cd "$WORKDIR"

log "PATH=$PATH"
log "docker=$(command -v docker || echo 'not-found')"
log "Starting deploy on host: $(hostname)"
log "Working directory: $WORKDIR"
log "Deploy mode: git"
log "Branch: $BRANCH"
log "Compose file: $COMPOSE_FILE"

# Avoid fatal git error on NAS after ownership changes.
if ! git config --global --get-all safe.directory 2>/dev/null | grep -Fxq "$WORKDIR"; then
  git config --global --add safe.directory "$WORKDIR"
  log "Added git safe.directory: $WORKDIR"
fi

log "Docker version:"
docker --version || true
log "Docker compose version:"
docker-compose version || true

log "Git status:"
git status --short || true

log "Fetching latest from origin…"
git fetch --all --prune

# Reset any local changes (including unresolved merge conflicts) before checkout.
git reset --hard
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"

log "Submodules (if any)…"
git submodule update --init --recursive || true

log "Current commit:"
git rev-parse --short HEAD || true

# Ensure compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
  err "Compose file not found: $WORKDIR/$COMPOSE_FILE"
  ls -la
  exit 3
fi

log "Building all audience outputs (public, friends, family, private)…"
bash scripts/build-all.sh 2>&1
log "All builds complete"

log "Starting/updating containers…"
docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans 2>&1

log "Containers status:"
docker-compose -f "$COMPOSE_FILE" ps || true

log "Deploy finished successfully"
