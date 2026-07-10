#!/usr/bin/env bash
# Make invokes this as SHELL: $(SHELL) $(.SHELLFLAGS) "recipe"
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [[ -s "$NVM_DIR/nvm.sh" ]]; then
  source "$NVM_DIR/nvm.sh"
  if [[ -f "$ROOT/.nvmrc" ]]; then
    nvm use --silent >/dev/null 2>&1 || nvm use || {
      echo "error: failed to switch to Node version in .nvmrc ($(cat "$ROOT/.nvmrc")). Run 'nvm install'." >&2
      exit 1
    }
  fi
elif [[ -f "$ROOT/.nvmrc" ]]; then
  echo "warning: nvm not found; using system Node ($(node -v 2>/dev/null || echo unknown))" >&2
fi

exec /bin/bash "$@"
