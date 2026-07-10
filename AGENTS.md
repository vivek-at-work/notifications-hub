# Agent Guide

## Quick Rules

- Run commands from the repo root
- Use `make` targets (not raw `pnpm exec nx`) when a Make target exists
- Use `python3` in the API workspace (via `.venv` / `scripts/with-venv.sh`)
- Never commit secrets
- Prefer existing patterns over new abstractions

## Stack

Nx monorepo for the **notifications-hub** multi-tenant notification platform:

- **API** — FastAPI + Strawberry GraphQL (`apps/api`)
- **Web** — Next.js 15 admin and end-user UI (`apps/web`)
- **Shared Python** — `libs/py/common`
- **Shared UI** — `libs/js/design-system`, `libs/js/notifications-ui`

## Requirements

- Python 3.12.13 (`.python-version`, pyenv → `.venv`)
- Node 24 (`.nvmrc`, nvm via `scripts/make-shell.sh` / `make`)
- Docker (optional, for `make docker-up`)

## Quick Start

```bash
cp .env.example .env
make install
make docker-up   # Postgres only until api/web bootstrap
# After api-bootstrap and web-bootstrap:
make dev
make api-dev     # http://localhost:8000
make web-dev     # http://localhost:3000
```

## Before PR

```bash
make test
make lint
make typecheck
```

## Task Routing

| Task area | Path |
|-----------|------|
| API app | `apps/api/` |
| Web app | `apps/web/` |
| Shared Python lib | `libs/py/common/` |
| Design system | `libs/js/design-system/` |
| Notifications UI | `libs/js/notifications-ui/` |
| Architecture decisions | `docs/adr/` |
| Root config / scripts | `Makefile`, `scripts/` |
| OpenSpec changes | `openspec/changes/` |

## Documentation

- [README.md](README.md) — project overview and quick start
- [ARCHITECTURE.md](ARCHITECTURE.md) — stack, layout, and ADR index
- [docs/adr/README.md](docs/adr/README.md) — ADR format and conventions
