#!/usr/bin/env bash
# Pre-flight check pour la demo E2E M1 Sprint 1 closeout (T1.3).
# Usage : ./preflight.sh
# Sortie 0 = pret a lancer la demo. Sortie != 0 = corriger avant.

set -u

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
ENV_FILE="$ROOT/.env"
ERRORS=0
WARNINGS=0

color_red()   { printf '\033[31m%s\033[0m\n' "$1"; }
color_green() { printf '\033[32m%s\033[0m\n' "$1"; }
color_yellow(){ printf '\033[33m%s\033[0m\n' "$1"; }

check_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    color_red "[KO] python3 introuvable"
    ERRORS=$((ERRORS+1))
    return
  fi
  ver=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  if [ "$(printf '%s\n3.11' "$ver" | sort -V | head -1)" != "3.11" ]; then
    color_red "[KO] Python $ver < 3.11 requis (le code utilise from datetime import UTC)"
    ERRORS=$((ERRORS+1))
  else
    color_green "[OK] Python $ver"
  fi
}

check_node() {
  if ! command -v node >/dev/null 2>&1; then
    color_red "[KO] node introuvable"
    ERRORS=$((ERRORS+1))
    return
  fi
  ver=$(node --version | sed 's/v//')
  major=$(echo "$ver" | cut -d. -f1)
  if [ "$major" -lt 20 ]; then
    color_yellow "[WARN] Node $ver — recommande v20+ pour Vite 5"
    WARNINGS=$((WARNINGS+1))
  else
    color_green "[OK] Node $ver"
  fi
}

check_port() {
  port="$1"
  label="$2"
  if command -v lsof >/dev/null 2>&1; then
    if lsof -i ":$port" >/dev/null 2>&1; then
      color_red "[KO] Port $port deja utilise ($label)"
      lsof -i ":$port" | tail -n +2
      ERRORS=$((ERRORS+1))
    else
      color_green "[OK] Port $port libre ($label)"
    fi
  else
    color_yellow "[WARN] lsof absent — verifie manuellement que $port est libre"
    WARNINGS=$((WARNINGS+1))
  fi
}

check_env() {
  if [ ! -f "$ENV_FILE" ]; then
    color_red "[KO] $ENV_FILE absent — copier depuis .env.example et remplir PLI_GMAIL_*"
    ERRORS=$((ERRORS+1))
    return
  fi
  cid=$(grep -E '^PLI_GMAIL_CLIENT_ID=' "$ENV_FILE" | cut -d= -f2-)
  if [ -z "$cid" ]; then
    color_red "[KO] PLI_GMAIL_CLIENT_ID vide dans $ENV_FILE"
    color_yellow "     -> suivre docs/runbooks/oauth-gmail-setup.md"
    ERRORS=$((ERRORS+1))
  else
    color_green "[OK] PLI_GMAIL_CLIENT_ID renseigne (${cid:0:20}...)"
  fi
  csec=$(grep -E '^PLI_GMAIL_CLIENT_SECRET=' "$ENV_FILE" | cut -d= -f2-)
  if [ -z "$csec" ]; then
    color_red "[KO] PLI_GMAIL_CLIENT_SECRET vide"
    ERRORS=$((ERRORS+1))
  else
    color_green "[OK] PLI_GMAIL_CLIENT_SECRET renseigne"
  fi
  ruri=$(grep -E '^PLI_GMAIL_REDIRECT_URI=' "$ENV_FILE" | cut -d= -f2-)
  expected="http://localhost:8000/auth/gmail/callback"
  if [ "$ruri" != "$expected" ]; then
    color_yellow "[WARN] PLI_GMAIL_REDIRECT_URI = '$ruri' (attendu '$expected')"
    WARNINGS=$((WARNINGS+1))
  else
    color_green "[OK] PLI_GMAIL_REDIRECT_URI correct"
  fi
}

check_db() {
  db="${HOME}/.pli/db.sqlite"
  if [ -f "$db" ]; then
    if command -v sqlite3 >/dev/null 2>&1; then
      n=$(sqlite3 "$db" "SELECT COUNT(*) FROM accounts;" 2>/dev/null || echo "?")
      if [ "$n" = "0" ]; then
        color_green "[OK] DB existe et est vide ($db)"
      else
        color_yellow "[WARN] DB contient $n compte(s) — pour demo from-scratch : 'rm $db'"
        WARNINGS=$((WARNINGS+1))
      fi
    else
      color_yellow "[WARN] sqlite3 absent — impossible de verifier le contenu DB"
      WARNINGS=$((WARNINGS+1))
    fi
  else
    color_green "[OK] Pas de DB existante (premier run = demo propre)"
  fi
}

check_backend_deps() {
  if [ ! -d "$ROOT/backend/.venv" ] && ! python3 -c 'import fastapi' 2>/dev/null; then
    color_yellow "[WARN] FastAPI pas installe globalement — 'cd backend && pip install -e .' avant la demo"
    WARNINGS=$((WARNINGS+1))
  else
    color_green "[OK] Dependencies backend disponibles"
  fi
}

check_frontend_deps() {
  if [ ! -d "$ROOT/frontend/node_modules" ]; then
    color_yellow "[WARN] node_modules absent — 'cd frontend && npm install' avant la demo"
    WARNINGS=$((WARNINGS+1))
  else
    color_green "[OK] node_modules present"
  fi
}

echo "=== Pre-flight T1.3 (M1 Sprint 1 closeout) ==="
echo
echo "-- Tooling --"
check_python
check_node
echo
echo "-- Ports --"
check_port 8000 "uvicorn backend"
check_port 5173 "vite frontend"
echo
echo "-- Configuration --"
check_env
echo
echo "-- DB --"
check_db
echo
echo "-- Dependencies --"
check_backend_deps
check_frontend_deps
echo
echo "=== Resume ==="
if [ "$ERRORS" -gt 0 ]; then
  color_red "$ERRORS erreur(s), $WARNINGS warning(s) — corriger avant la demo"
  exit 1
fi
if [ "$WARNINGS" -gt 0 ]; then
  color_yellow "$WARNINGS warning(s) — demo lancable mais verifier ce qui est signale"
  exit 0
fi
color_green "Tout OK — pret pour la demo E2E"
exit 0
