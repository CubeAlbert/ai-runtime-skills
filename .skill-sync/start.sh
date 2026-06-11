#!/usr/bin/env bash
# skill-sync launcher (Linux/macOS). Run `chmod +x start.sh` once before first use.
set -euo pipefail

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Prefer $PYTHON if set, then python3, then python.
PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
    PY="python"
fi
if ! command -v "$PY" >/dev/null 2>&1; then
    echo "[skill-sync] ERROR: Python not found on PATH (tried python3, python)." >&2
    echo "[skill-sync] Install Python 3, or set the PYTHON env var." >&2
    exit 1
fi

exec "$PY" "$SCRIPT_DIR/skill-sync.py" "$@"
