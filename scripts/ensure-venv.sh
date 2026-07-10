#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="$ROOT/.venv"
PY_VER="$(tr -d '[:space:]' < .python-version 2>/dev/null || true)"
PY_VER="${PY_VER:-3.12}"

python_full_version() {
  "$1" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'
}

resolve_python_from_path() {
  local candidate ver
  for candidate in python3 python; do
    if ! command -v "$candidate" >/dev/null 2>&1; then
      continue
    fi
    ver="$(python_full_version "$(command -v "$candidate")" 2>/dev/null || true)"
    if [[ "$ver" == "$PY_VER" ]]; then
      PYTHON="$(command -v "$candidate")"
      return 0
    fi
  done
  return 1
}

ensure_pyenv_on_path() {
  if command -v pyenv >/dev/null 2>&1; then
    return 0
  fi

  export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
  if [[ -x "$PYENV_ROOT/bin/pyenv" ]]; then
    export PATH="$PYENV_ROOT/bin:$PATH"
    if command -v pyenv >/dev/null 2>&1; then
      eval "$(pyenv init - bash 2>/dev/null || pyenv init --path)"
      return 0
    fi
  fi

  return 1
}

install_pyenv_mac() {
  echo "Installing pyenv (macOS)..."
  if command -v brew >/dev/null 2>&1; then
    brew install pyenv
    return 0
  fi

  echo "Homebrew not found; using pyenv installer..."
  curl -fsSL https://pyenv.run | bash
}

install_pyenv_ubuntu() {
  echo "Installing pyenv (Ubuntu/Debian)..."

  if command -v apt-get >/dev/null 2>&1; then
    local deps=(
      make build-essential libssl-dev zlib1g-dev libbz2-dev
      libreadline-dev libsqlite3-dev curl git libncursesw5-dev
      xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
    )
    if command -v sudo >/dev/null 2>&1; then
      sudo apt-get update -qq
      sudo apt-get install -y --no-install-recommends "${deps[@]}"
    else
      echo "warning: sudo not available; skipping apt build dependencies." >&2
      echo "Install manually if pyenv install fails: ${deps[*]}" >&2
    fi
  fi

  curl -fsSL https://pyenv.run | bash
}

install_pyenv() {
  local os
  os="$(uname -s)"

  case "$os" in
    Darwin)
      install_pyenv_mac
      ;;
    Linux)
      if [[ -r /etc/os-release ]]; then
        source /etc/os-release
        case "${ID:-}${ID_LIKE:-}" in
          *ubuntu*|*debian*)
            install_pyenv_ubuntu
            ;;
          *)
            echo "Unsupported Linux distro (${ID:-unknown}); using pyenv installer..." >&2
            curl -fsSL https://pyenv.run | bash
            ;;
        esac
      else
        curl -fsSL https://pyenv.run | bash
      fi
      ;;
    *)
      echo "error: unsupported OS (${os}) for automatic pyenv install." >&2
      echo "Install pyenv manually: https://github.com/pyenv/pyenv#installation" >&2
      exit 1
      ;;
  esac
}

resolve_python_with_pyenv() {
  if ! ensure_pyenv_on_path; then
    install_pyenv
    ensure_pyenv_on_path || {
      echo "error: pyenv install completed but pyenv is not on PATH." >&2
      echo "Add to your shell profile:" >&2
      echo '  export PYENV_ROOT="$HOME/.pyenv"' >&2
      echo '  export PATH="$PYENV_ROOT/bin:$PATH"' >&2
      echo '  eval "$(pyenv init - bash)"' >&2
      exit 1
    }
  fi

  pyenv install -s "$PY_VER"

  PYTHON="$(pyenv root)/versions/${PY_VER}/bin/python"
  if [[ ! -x "$PYTHON" ]]; then
    echo "error: Python ${PY_VER} not found at ${PYTHON}" >&2
    exit 1
  fi
}

resolve_python() {
  if resolve_python_from_path; then
    return 0
  fi

  resolve_python_with_pyenv
}

resolve_python

if [[ -x "$VENV/bin/python3" ]]; then
  venv_py="$("$VENV/bin/python3" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  expected_py="$("$PYTHON" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  if [[ "$venv_py" != "$expected_py" ]]; then
    echo "Removing stale .venv (Python ${venv_py}, expected ${expected_py})"
    rm -rf "$VENV"
  fi
fi

if [[ ! -x "$VENV/bin/python3" ]]; then
  echo "Creating .venv with $("$PYTHON" -V) ($PYTHON)"
  "$PYTHON" -m venv "$VENV"
  "$VENV/bin/pip" install --upgrade pip
fi
