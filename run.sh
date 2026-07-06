SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

PACKAGE_NAME="dezent_demo"

if ! python -m pip show "$PACKAGE_NAME" >/dev/null 2>&1; then
    echo "Installing $PACKAGE_NAME..."
    python -m pip install -e .
fi

# sudo -E $SCRIPT_DIR/.venv/bin/python -m deZent_demo --virtual
python -m deZent_demo