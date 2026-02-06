#!/usr/bin/env bash
<<<<<<< HEAD
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
=======
set -Eeuo pipefail

ts() { date +"%Y-%m-%d %H:%M:%S"; }
log() { echo "[$(ts)] [DEPLOY] $*"; }
err() { echo "[$(ts)] [DEPLOY][ERROR] $*" >&2; }

on_error() {
  local ec=$?
  err "Deploy failed (exit code: $ec)"
  err "Last command: ${BASH_COMMAND}"
  exit "$ec"
}
trap on_error ERR

# ---- CONFIG (filled by setup script) ----
NAS_DEPLOY_PATH="/volume1/docker/MyGarden"
BRANCH="main"
DEPLOY_MODE="git"
COMPOSE_FILE="docker-compose.yml"

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
log "PATH=$PATH"
log "docker=$(command -v docker || echo NOT_FOUND)"


log "Starting deploy on host: $(hostname)"
log "Working directory: $NAS_DEPLOY_PATH"
log "Deploy mode: $DEPLOY_MODE"
log "Branch: $BRANCH"
log "Compose file: $COMPOSE_FILE"

if [[ ! -d "$NAS_DEPLOY_PATH" ]]; then
  err "Deploy path does not exist: $NAS_DEPLOY_PATH"
  err "Create it (and ensure permissions) or fix NAS_DEPLOY_PATH."
  exit 2
fi

cd "$NAS_DEPLOY_PATH"

# Diagnostic information
log "Docker version:"
docker --version || true
log "Docker compose version:"
docker compose version || true

# Ensure compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
  err "Compose file not found: $NAS_DEPLOY_PATH/$COMPOSE_FILE"
  err "Check your repo or set correct COMPOSE_FILE."
  ls -la
  exit 3
fi

# If deploy mode is 'git', update repo
if [[ "$DEPLOY_MODE" == "git" ]]; then
  if [[ ! -d ".git" ]]; then
    err "DEPLOY_MODE=git but no .git directory in $NAS_DEPLOY_PATH"
    err "You must 'git clone' the repo into this folder once."
    exit 4
  fi

  log "Git status:"
  git status -sb || true

  log "Fetching latest from origin…"
  git fetch --all --prune

  log "Resetting working tree to origin/$BRANCH…"
  git reset --hard "origin/$BRANCH"

  log "Submodules (if any)…"
  git submodule update --init --recursive || true

  log "Current commit:"
  git rev-parse --short HEAD || true
else
  log "DEPLOY_MODE=images -> skipping git operations."
fi

log "Pulling docker images…"
docker compose -f "$COMPOSE_FILE" pull

log "Starting/updating containers…"
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

log "Containers status:"
docker compose -f "$COMPOSE_FILE" ps

log "Recent logs (last 80 lines) for quick debugging:"
docker compose -f "$COMPOSE_FILE" logs --tail=80 || true

log "Deploy finished OK."
>>>>>>> origin/main
