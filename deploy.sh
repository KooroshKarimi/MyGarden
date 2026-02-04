#!/usr/bin/env bash
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
