#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[%s] [DEPLOY] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

fail() {
  printf '[%s] [DEPLOY][ERROR] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
  exit 1
}

WORKDIR="$(cd "$(dirname "$0")" && pwd)"
BRANCH="${DEPLOY_BRANCH:-main}"
COMPOSE_FILE="${DEPLOY_COMPOSE_FILE:-docker-compose.yml}"

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
docker version --format '{{.Server.Version}}' || true
log "Docker compose version:"
docker-compose version || true

log "Git status:"
git status --short || true

log "Fetching latest from origin…"
git fetch --all --prune

git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"

log "Bringing stack up"
docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans

log "Deploy finished successfully"
