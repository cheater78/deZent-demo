PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

VENV_DIR="${PROJECT_DIR}/.venv"
if [[ ! -d "${VENV_DIR}" ]]; then
    echo "Creating virtual environment at ${VENV_DIR}"
    python3 -m venv "$VENV_DIR"
fi
source "${VENV_DIR}/bin/activate"

PACKAGE_NAME="deZent_demo"
if ! python -m pip show "${PACKAGE_NAME}" >/dev/null 2>&1; then
    echo "Installing ${PACKAGE_NAME}..."
    python -m pip install -e "${PROJECT_DIR}"
fi
python -m "${PACKAGE_NAME}"