#!/bin/bash
CWD="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

VENV="${CWD}/.venv"

if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"

python -m pip install -r requirements.txt