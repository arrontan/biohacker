#!/usr/bin/env bash
set -euo pipefail

# restart-backend.sh
# Stops any running backend server, sources the project's .venv activate script
# so environment variables like STRANDS_TOOL_CONSOLE_MODE are applied, then
# starts the backend via npm start and writes a pidfile to backend/server.pid

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_ACTIVATE="$REPO_ROOT/.venv/bin/activate"
BACKEND_DIR="$REPO_ROOT/backend"
LOG_FILE="$BACKEND_DIR/server.log"
PID_FILE="$BACKEND_DIR/server.pid"

echo "Using repo root: $REPO_ROOT"

if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE" 2>/dev/null || true)
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Stopping old backend pid $OLD_PID"
    kill "$OLD_PID" || true
    sleep 1
  fi
fi

if [ -f "$PID_FILE" ]; then rm -f "$PID_FILE"; fi

if [ -f "$VENV_ACTIVATE" ]; then
  # shellcheck disable=SC1090
  source "$VENV_ACTIVATE"
  echo "Sourced venv: $VENV_ACTIVATE"
else
  echo "Warning: venv activate not found at $VENV_ACTIVATE -- continuing without venv"
fi

# If PYTHON_BIN isn't explicitly set, prefer the project's venv python so the
# backend spawns the same interpreter that has the project's packages.
if [ -z "${PYTHON_BIN:-}" ]; then
  if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
    export PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
    echo "Auto-set PYTHON_BIN=$PYTHON_BIN"
  fi
fi

cd "$BACKEND_DIR"
echo "Starting backend (logs -> $LOG_FILE)"
nohup npm start > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"
echo "Backend started with pid $NEW_PID"

echo "Tail logs with: tail -f $LOG_FILE"
