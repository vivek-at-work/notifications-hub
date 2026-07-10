# notifications-hub

Multi-tenant notification platform for email, SMS, and push — GraphQL ingestion, Temporal processing, and admin web UI.

## Features

- **API** — FastAPI + Strawberry GraphQL (`apps/api`)
- **Web** — Next.js frontend (`apps/web`)
- **Monorepo** — Nx workspace with pnpm, shared Python and JavaScript libraries
- **Orchestration** — Temporal workflows for send, schedule, and retention (wired in later milestones)

## Quick Start

### Docker Compose

```bash
cp .env.example .env
make docker-up
make docker-logs
make docker-down
```

Local Postgres listens on **localhost:5433** (container port 5432).

### Local Development

```bash
make install
```

| Service | URL (after app bootstrap) |
|---------|---------------------------|
| API | http://localhost:8000 |
| API health | http://localhost:8000/health |
| API GraphQL | http://localhost:8000/graphql |
| Web | http://localhost:3000 |

## Workspace layout

```
apps/api/                    # Python API (api-bootstrap)
apps/web/                    # Next.js UI (web-bootstrap)
libs/py/common/              # Shared domain types and utilities
libs/js/design-system/       # MUI design system
libs/js/notifications-ui/    # Notification-specific UI components
docs/adr/                    # Architecture decision records
scripts/                     # venv and Make shell helpers
```

## Documentation

- [AGENTS.md](AGENTS.md) — agent and developer runbook
- [ARCHITECTURE.md](ARCHITECTURE.md) — architecture overview
- [docs/adr/](docs/adr/) — architecture decision records

## License

Proprietary — add license terms when published.
