# notifications-hub — Architecture

Centralized multi-tenant notification platform: client apps submit notifications via GraphQL or SQS; Temporal processes delivery across email (SES), SMS (SNS), and push (FCM/APNs); tenant admins configure templates and channels in the web UI.

## Architecture Decision Records

Decisions live in [docs/adr/README.md](docs/adr/README.md).

| Area | Path |
|------|------|
| Backend ADRs | `docs/adr/backend/` |
| Web ADRs | `docs/adr/web/` |

Add new ADRs as work progresses. Bootstrap does not require pre-filled ADR files beyond the index.

## Repository Layout

```
apps/
  api/                       # FastAPI + Strawberry GraphQL backend
  web/                       # Next.js frontend
libs/
  py/common/                 # shared Python library
  js/design-system/          # shared MUI design system
  js/notifications-ui/       # notification UI components
docs/
  adr/                       # architecture decision records
scripts/                     # repo automation (venv, make shell)
openspec/                    # OpenSpec change proposals and specs
```

## Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Strawberry, SQLAlchemy (async), Alembic |
| Web | Next.js 15, React 18, MUI, Redux Toolkit, Apollo Client |
| Monorepo | Nx, pnpm, uv |
| Workflows | Temporal |
| Database | PostgreSQL 16 |
| Messaging | AWS SQS, EventBridge (production) |
| Containers | Docker Compose (local), Kubernetes (production) |
| Observability | Structured logging (`app.logging`), OpenTelemetry, Prometheus |

## Request flow (API)

```
GraphQL API → Service → Repository → Model
```

Temporal:

```
Workflow → Activity → Service → Repository → Model
```

## Cross-References

- Agent runbook: [AGENTS.md](AGENTS.md)
- Setup and commands: [README.md](README.md)
- Platform GraphQL conventions: `.cursor/rules/graphql.mdc`
