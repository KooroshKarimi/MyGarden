#!/usr/bin/env bash
set -Eeuo pipefail

# =========================
# GitHub -> Synology Deploy Setup (Variante A: GitHub Actions via SSH)
# Runs locally inside your MyGarden folder.
# Creates:
#  - deploy.sh (to run on NAS)
#  - SSH keypair (for GitHub Actions)
#  - .github/workflows/deploy.yml (optional)
# Provides:
#  - exact GitHub Secrets to set
# =========================

# ---------- Pretty logging ----------
ts() { date +"%Y-%m-%d %H:%M:%S"; }
log() { echo "[$(ts)] [INFO ] $*"; }
warn(){ echo "[$(ts)] [WARN ] $*" >&2; }
err() { echo "[$(ts)] [ERROR] $*" >&2; }
die() { err "$*"; exit 1; }

on_error() {
  local exit_code=$?
  err "Script failed (exit code: $exit_code)."
  err "Last command: ${BASH_COMMAND}"
  err "Tip: Run with 'bash -x setup_github_deploy.sh' for even more trace."
  exit "$exit_code"
}
trap on_error ERR

# ---------- Helpers ----------
prompt() {
  local var_name="$1"
  local message="$2"
  local default="${3:-}"
  local secret="${4:-0}"

  if [[ "$secret" == "1" ]]; then
    # shellcheck disable=SC2162
    read -rsp "$message${default:+ [$default]}: " input
    echo
  else
    # shellcheck disable=SC2162
    read -rp "$message${default:+ [$default]}: " input
  fi

  if [[ -z "${input:-}" ]]; then
    input="$default"
  fi

  if [[ -z "${input:-}" ]]; then
    die "Missing required value for: $var_name"
  fi

  printf -v "$var_name" '%s' "$input"
}

confirm() {
  local message="$1"
  local default="${2:-y}"  # y/n
  local ans=""
  # shellcheck disable=SC2162
  read -rp "$message [y/n] (default: $default): " ans
  ans="${ans:-$default}"
  [[ "$ans" =~ ^[Yy]$ ]]
}

require_cmd() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
}

# ---------- Start ----------
log "Starting setup in folder: $(pwd)"
log "Assumption: You are running this script from inside your MyGarden directory."

# sanity checks
require_cmd git
require_cmd ssh
require_cmd ssh-keygen
require_cmd chmod
require_cmd sed
require_cmd awk

# ---------- Gather inputs ----------
log "Collecting configuration…"

# Repo setup
if [[ -d ".git" ]]; then
  log "Detected existing git repository in this folder."
  DEFAULT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
else
  DEFAULT_BRANCH="main"
fi

prompt REPO_URL "GitHub repo HTTPS or SSH URL (e.g. https://github.com/user/repo.git)" "${REPO_URL:-}"
prompt BRANCH  "Branch to deploy on push" "$DEFAULT_BRANCH"

# NAS connection
prompt NAS_HOST     "NAS public hostname/IP (reachable from GitHub Actions)" "${NAS_HOST:-}"
prompt NAS_SSH_PORT "NAS SSH port (forwarded from router)" "${NAS_SSH_PORT:-22}"
prompt NAS_USER     "NAS SSH username for deploy (e.g. deploy)" "${NAS_USER:-deploy}"
prompt NAS_DEPLOY_PATH "Absolute path on NAS to MyGarden folder" "${NAS_DEPLOY_PATH:-/volume1/docker/MyGarden}"

# Deploy mode
log "Deploy mode:"
log "  A) 'git'    -> NAS pulls your repo (git fetch/reset) then docker compose up"
log "  B) 'images' -> NAS only docker compose pull/up (assumes compose uses registry images)"
prompt DEPLOY_MODE "Choose deploy mode: git/images" "${DEPLOY_MODE:-git}"
if [[ "$DEPLOY_MODE" != "git" && "$DEPLOY_MODE" != "images" ]]; then
  die "DEPLOY_MODE must be 'git' or 'images'"
fi

# Compose filename
DEFAULT_COMPOSE="compose.yml"
[[ -f "docker-compose.yml" ]] && DEFAULT_COMPOSE="docker-compose.yml"
[[ -f "compose.yml" ]] && DEFAULT_COMPOSE="compose.yml"
[[ -f "docker-compose.yaml" ]] && DEFAULT_COMPOSE="docker-compose.yaml"
[[ -f "compose.yaml" ]] && DEFAULT_COMPOSE="compose.yaml"

prompt COMPOSE_FILE "Compose file name in repo" "$DEFAULT_COMPOSE"

# Optional: create workflow file?
CREATE_WORKFLOW=false
if confirm "Create/overwrite GitHub Actions workflow file in this repo (.github/workflows/deploy.yml)?" "y"; then
  CREATE_WORKFLOW=true
fi

# Optional: test SSH from local machine now?
TEST_SSH=false
if confirm "Test SSH connectivity from THIS machine to your NAS now (recommended)?" "y"; then
  TEST_SSH=true
fi

# ---------- Ensure repo ----------
if [[ ! -d ".git" ]]; then
  log "No git repo detected here."
  if confirm "Do you want me to initialize git here and add remote '$REPO_URL'?" "y"; then
    git init
    git remote add origin "$REPO_URL"
    log "Git initialized and remote 'origin' added."
  else
    warn "Proceeding without initializing git. Workflow creation still possible."
  fi
else
  log "Git repo OK."
fi

# ---------- Create deploy.sh (to run on NAS) ----------
log "Creating deploy script (deploy.sh) with detailed debug output…"

cat > deploy.sh <<'EOF'
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
NAS_DEPLOY_PATH="__NAS_DEPLOY_PATH__"
BRANCH="__BRANCH__"
DEPLOY_MODE="__DEPLOY_MODE__"
COMPOSE_FILE="__COMPOSE_FILE__"

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
EOF

# Replace placeholders
sed -i \
  -e "s|__NAS_DEPLOY_PATH__|$NAS_DEPLOY_PATH|g" \
  -e "s|__BRANCH__|$BRANCH|g" \
  -e "s|__DEPLOY_MODE__|$DEPLOY_MODE|g" \
  -e "s|__COMPOSE_FILE__|$COMPOSE_FILE|g" \
  deploy.sh

chmod +x deploy.sh
log "Created: $(pwd)/deploy.sh"

# ---------- SSH key generation ----------
KEY_DIR=".deploy_keys"
KEY_PATH="$KEY_DIR/github_deploy_key"
PUB_PATH="$KEY_PATH.pub"

mkdir -p "$KEY_DIR"

if [[ -f "$KEY_PATH" ]]; then
  warn "SSH key already exists at $KEY_PATH"
  if confirm "Overwrite existing SSH deploy keypair?" "n"; then
    rm -f "$KEY_PATH" "$PUB_PATH"
  fi
fi

if [[ ! -f "$KEY_PATH" ]]; then
  log "Generating SSH keypair (ed25519) for GitHub Actions…"
  ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$KEY_PATH" -N ""
  log "Keypair created:"
  log "  Private: $KEY_PATH"
  log "  Public : $PUB_PATH"
fi

# ---------- Optional: SSH connectivity test ----------
if [[ "$TEST_SSH" = true ]]; then
  log "Testing SSH connectivity to NAS using your DEFAULT ssh agent/keys (not GitHub key)…"
  log "Command: ssh -p $NAS_SSH_PORT $NAS_USER@$NAS_HOST 'echo ok && uname -a'"
  if ssh -p "$NAS_SSH_PORT" -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new "$NAS_USER@$NAS_HOST" "echo ok && uname -a"; then
    log "SSH connectivity test OK."
  else
    warn "SSH connectivity test FAILED."
    warn "This must work for GitHub Actions too."
    warn "Common causes:"
    warn "  - Router port forward not set"
    warn "  - NAS firewall blocks SSH"
    warn "  - Wrong NAS_HOST / NAS_SSH_PORT"
    warn "  - User not allowed to SSH"
  fi
fi

# ---------- Create GitHub workflow ----------
if [[ "$CREATE_WORKFLOW" = true ]]; then
  log "Creating GitHub Actions workflow: .github/workflows/deploy.yml"

  mkdir -p .github/workflows
  cat > .github/workflows/deploy.yml <<EOF
name: Deploy to Synology (SSH)

on:
  push:
    branches: ["$BRANCH"]

concurrency:
  group: "deploy-synology"
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: \${{ secrets.NAS_HOST }}
          username: \${{ secrets.NAS_USER }}
          key: \${{ secrets.NAS_SSH_KEY }}
          port: \${{ secrets.NAS_SSH_PORT }}
          script_stop: true
          script: |
            set -e
            cd "$NAS_DEPLOY_PATH" || exit 2
            bash ./deploy.sh
EOF

  log "Workflow created. You still need to commit & push it."
fi

# ---------- Final instructions ----------
log "============================================================"
log "NEXT STEPS (manual, one-time):"
log ""
log "1) Add the PUBLIC key to NAS user '$NAS_USER' authorized_keys:"
log "   Public key file: $PUB_PATH"
log ""
log "   On NAS (as $NAS_USER):"
log "     mkdir -p ~/.ssh && chmod 700 ~/.ssh"
log "     # append this public key to ~/.ssh/authorized_keys"
log ""
log "2) Ensure the repo exists on NAS at: $NAS_DEPLOY_PATH"
if [[ "$DEPLOY_MODE" == "git" ]]; then
  log "   Since DEPLOY_MODE=git, NAS must have the repo cloned there once:"
  log "     cd $(dirname "$NAS_DEPLOY_PATH")"
  log "     git clone $REPO_URL $(basename "$NAS_DEPLOY_PATH")"
  log "   Then ensure deploy.sh exists there (copy it) and compose file is present."
else
  log "   Since DEPLOY_MODE=images, ensure compose file refers to registry images and exists at NAS path."
fi
log ""
log "3) Add these GitHub Secrets (Repo Settings -> Secrets and variables -> Actions):"
log "   NAS_HOST     = $NAS_HOST"
log "   NAS_SSH_PORT = $NAS_SSH_PORT"
log "   NAS_USER     = $NAS_USER"
log "   NAS_SSH_KEY  = (paste the PRIVATE key from: $KEY_PATH)"
log ""
log "4) Copy deploy.sh to NAS folder (if it's not already there):"
log "   scp -P $NAS_SSH_PORT ./deploy.sh $NAS_USER@$NAS_HOST:$NAS_DEPLOY_PATH/deploy.sh"
log ""
log "5) If you created the workflow file, commit & push:"
log "   git add .github/workflows/deploy.yml"
log "   git commit -m \"Add Synology deploy workflow\""
log "   git push origin $BRANCH"
log ""
log "DEBUG TIP:"
log " - When a deploy fails, open GitHub Actions logs and look for [DEPLOY] lines."
log " - On NAS, run: bash $NAS_DEPLOY_PATH/deploy.sh"
log "============================================================"

log "Setup script finished OK."

