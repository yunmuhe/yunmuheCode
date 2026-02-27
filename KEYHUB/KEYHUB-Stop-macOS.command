#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

PID_FILE=".keyhub.pid"
if [[ ! -f "$PID_FILE" ]]; then
  echo "[INFO] $PID_FILE not found in $(pwd)"
  echo "       KEYHUB may not be running, or it was started elsewhere."
  echo
  read -r -p "Press Enter to close..." _
  exit 0
fi

PID="$(tr -d '[:space:]' < "$PID_FILE")"
if [[ ! "$PID" =~ ^[0-9]+$ ]]; then
  echo "[ERROR] Invalid PID in $PID_FILE: '$PID'"
  echo
  read -r -p "Press Enter to close..." _
  exit 1
fi

echo "[INFO] Stopping KEYHUB (PID $PID)..."
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE" || true

echo "[INFO] Done."
echo
read -r -p "Press Enter to close..." _
