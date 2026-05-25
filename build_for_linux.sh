#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo "[1/4] Using existing virtual environment: $VIRTUAL_ENV"
elif [ -d .venv ]; then
    echo "[1/4] Activating existing virtual environment ..."
    source .venv/bin/activate
else
    echo "[1/4] Creating Python virtual environment ..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

echo "[2/4] Installing Python dependencies ..."
pip install -q -r requirements.txt
pip install -q pyinstaller

echo "[3/4] Building standalone executable (onefile) ..."
pyinstaller --noconfirm CheckitoutWeather.spec

echo "[4/4] Done!  dist/CheckitoutWeather"
ls -lh dist/CheckitoutWeather
