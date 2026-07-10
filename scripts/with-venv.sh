#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -x "$ROOT/.venv/bin/python3" ]]; then
  "$ROOT/scripts/ensure-venv.sh"
fi

export PATH="$ROOT/.venv/bin:$PATH"

if [[ $# -gt 0 ]] && ! command -v "$1" >/dev/null 2>&1; then
  echo "error: '$1' not found in .venv. Run 'make install' from repo root." >&2
  exit 1
fi

exec "$@"
