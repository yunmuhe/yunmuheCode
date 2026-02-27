#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

# Stop
PID_FILE=".keyhub.pid"
if [[ -f "$PID_FILE" ]]; then
  PID="$(tr -d '[:space:]' < "$PID_FILE")"
  if [[ "$PID" =~ ^[0-9]+$ ]]; then
    echo "[INFO] Stopping KEYHUB (PID $PID)..."
    kill -9 "$PID" 2>/dev/null || true
  else
    echo "[WARN] Invalid PID in $PID_FILE: '$PID'"
  fi
  rm -f "$PID_FILE" || true
else
  echo "[INFO] $PID_FILE not found in $(pwd)"
  echo "       KEYHUB may not be running, or it was started elsewhere."
fi

sleep 1

# Start (inline from KEYHUB-Start-macOS.sh)
echo "============================================"
echo " KEYHUB Web UI - Startup Check (macOS/Linux)"
echo "============================================"
echo

have() { command -v "$1" >/dev/null 2>&1; }

confirm() {
  local prompt="$1"
  while true; do
    read -r -p "$prompt [y/n]: " yn
    case "${yn,,}" in
      y|yes) return 0 ;;
      n|no) return 1 ;;
      *) echo "Please answer y or n." ;;
    esac
  done
}

echo "[1/4] Checking Python..."
if ! have python3; then
  echo "  [MISSING] python3 not found."
  echo "  Please install Python 3.9+ and re-run."
  echo
  read -r -p "Press Enter to close..." _
  exit 1
fi
python3 --version | sed 's/^/  [OK] /'

echo

echo "[2/4] Checking pip..."
if ! python3 -m pip --version >/dev/null 2>&1; then
  echo "  [MISSING] pip not available for python3."
  echo "  Try: python3 -m ensurepip --upgrade"
  echo
  read -r -p "Press Enter to close..." _
  exit 1
fi
python3 -m pip --version | sed 's/^/  [OK] /'

echo

echo "[3/4] Checking Flask..."
if ! python3 -c "import flask" >/dev/null 2>&1; then
  echo "  [MISSING] Flask not installed."
  if confirm "Install Flask now?"; then
    python3 -m pip install flask
  else
    echo "  Aborted. Run: python3 -m pip install flask"
    echo
    read -r -p "Press Enter to close..." _
    exit 1
  fi
fi
python3 -c "import flask; print(flask.__version__)" | sed 's/^/  [OK] Flask /'

echo

echo "[4/4] Checking project files..."
if [[ ! -f "run_keyhub_web.py" ]]; then
  echo "  [ERROR] run_keyhub_web.py not found in $(pwd)"
  echo
  read -r -p "Press Enter to close..." _
  exit 1
fi
echo "  [OK] Project files found."

echo

echo "============================================"
echo " Starting KEYHUB Web UI..."
echo "============================================"
echo

python3 run_keyhub_web.py --no-debug >/dev/null 2>&1 &
PID=$!
echo "$PID" > .keyhub.pid

echo "  Waiting for server to start..."
sleep 1

URL="http://127.0.0.1:5000"
echo "  Opening $URL ..."
if [[ "$(uname -s)" == "Darwin" ]]; then
  open "$URL" || true
else
  xdg-open "$URL" >/dev/null 2>&1 || true
fi

echo "  Done. KEYHUB is running in background (PID $PID)."
echo "  Stop: KEYHUB-Stop-macOS.command"

echo
read -r -p "Press Enter to close..." _
