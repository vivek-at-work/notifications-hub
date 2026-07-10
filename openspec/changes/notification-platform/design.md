## Context

`notifications-hub` is a greenfield Nx monorepo with OpenSpec tooling and platform conventions (GraphQL → Service → Repository → Model, Temporal orchestration, structured logging) but no application code yet. Multiple client applications need a shared notification platform to send email, SMS, and push notifications without reimplementing channel adapters, retry logic, templates, or delivery tracking.

Stakeholders: client application teams (S2S integrators), tenant administrators (template/channel config), end users (preference management), and platform operators (monitoring, retention).

## Goals / Non-Goals

**Goals:**

- Centralized multi-tenant notification platform supporting Email (SES), SMS (SNS), Push Android (FCM), Push iOS (direct APNs).
- GraphQL API for synchronous notification submission and querying; SQS for async bulk ingestion.
- Temporal-based async processing with scheduling, retries, preference gating, and status lifecycle.
- Admin web UI for template authoring, channel configuration, and notification history.
- Standalone end-user portal with Google OIDC for preferences and history.
- Structured logging, OpenTelemetry tracing, and Prometheus metrics.
- 90-day default retention with scheduled purge.
- Production deployment on Kubernetes with Docker Compose for local dev.

**Non-Goals (v1):**

- Transactional outbox pattern (use direct Temporal start + 5-minute reconciler instead).
- Multi-locale template support.
- Client-facing GraphQL template CRUD (admin UI only).
- Shell JWT passthrough / multizone hosting.
- WhatsApp, Slack, Microsoft Teams channels.
- Cross-region disaster recovery.
- Magic link or non-Google OIDC providers.
- Tenant daily quota enforcement (deferred; per-message limits only).

## Decisions

### D1: Monorepo layout

**Decision:** Nx monorepo with `apps/api` (Python FastAPI + Strawberry), `apps/web` (Next.js 15), `libs/py/common`, `libs/js/design-system`, `libs/js/notifications-ui`.

**Rationale:** Matches existing technology-stack conventions. Shared libraries avoid duplication between API domain logic and web types.

**Alternatives considered:** Separate repos per service — rejected due to coordination overhead for a greenfield platform.

### D2: Tenant model

**Decision:** Tenant = `Application`. Every database row scoped by `application_id`. Auth binding determines tenant — never trust client-supplied tenant IDs.

**Rationale:** Simple mental model; each client app registers as an Application with isolated templates, credentials, and quotas.

### D3: Layered architecture

**Decision:** Strict dependency chain: GraphQL → Service → Repository → Model (API); Workflow → Activity → Service → Repository → Model (Temporal).

**Rationale:** Platform convention. Enables independent testing and prevents business logic in resolvers/workflows.

### D4: Orchestration engine

**Decision:** Temporal for all notification processing (send, schedule, retention purge, orphan reconciler).

**Rationale:** Native support for scheduling (`workflow.sleep`), per-activity retry policies, fan-out/fan-in, and durable workflow history. Celery rejected — no built-in scheduling or saga patterns.

### D5: Ingestion paths

**Decision:** Two ingestion paths converging on the same `NotificationService`:

| Path | Limit | Use case |
|------|-------|----------|
| GraphQL `sendNotification` | 1 recipient | Single notification |
| GraphQL `sendBulkNotifications` | Max 10 recipients | Small bulk, sync response |
| SQS message | Max 100 recipients | Large bulk, async |

**Rationale:** GraphQL provides sync feedback for small sends; SQS buffers burst traffic without blocking API.

### D6: No transactional outbox

**Decision:** DB commit → direct `temporal.start_workflow` with 3× retry. Orphan reconciler cron (every 5 min) heals stuck `Queued` rows.

**Rationale:** Simpler v1. Accepted tradeoff: rare orphan notifications for up to 5 minutes before healing.

**Alternatives considered:** Transactional outbox table — deferred to v2 if stronger guarantees needed.

### D7: Channel adapter pattern

**Decision:** Hexagonal ports & adapters. `ChannelDeliveryPort` interface with `SesEmailAdapter`, `SnsSmsAdapter`, `FcmPushAdapter`, `ApnsPushAdapter`.

**Rationale:** Extensible to future channels (WhatsApp, Slack) without changing orchestration logic.

### D8: iOS push via direct APNs

**Decision:** `ApnsPushAdapter` using HTTP/2 + JWT auth with `.p8` key stored in Secrets Manager. No FCM relay for iOS.

**Rationale:** Lower latency, simpler debugging, no Google dependency for iOS delivery.

### D9: Template authoring

**Decision:** Admin UI only in v1. No GraphQL mutations for template CRUD. Client apps reference templates by `templateKey` at send time. No locale support — single default per template key + channel.

**Rationale:** Templates are operator-managed assets; client apps should not create or modify them.

### D10: Authentication

**Decision:** Three auth mechanisms:

| Actor | Method |
|-------|--------|
| Client app (S2S) | API key (hashed, scoped) |
| Tenant admin | Google OIDC → JWT |
| End user | Google OIDC → JWT (standalone hub login) |

**Rationale:** API keys for machine-to-machine; Google OIDC for human users. Single IdP simplifies v1.

### D11: Credential storage

**Decision:** Per-tenant channel credentials in AWS Secrets Manager. Database stores `secret_ref` (ARN) only.

**Rationale:** Secrets never in DB, logs, or traces. KMS encryption at rest.

### D12: Delivery callbacks

**Decision:** AWS EventBridge routes provider events (SES bounce/delivery, SNS receipts) to a callback handler that matches `provider_message_id` → updates attempt → aggregates parent status.

**Rationale:** Decouples provider integrations from core processing; EventBridge is native for SES.

### D13: Retention

**Decision:** Default 90-day retention per tenant (`applications.retention_policy` JSONB). Daily `RetentionPurgeWorkflow` deletes expired notifications, attempts, events, and recipients.

**Rationale:** Compliance and storage cost management. Per-tenant override via admin UI.

### D14: Database

**Decision:** PostgreSQL 16 with SQLAlchemy async ORM and Alembic migrations. ~15 tables (see proposal impact).

**Rationale:** JSONB for placeholders/config, strong consistency for idempotency, mature ecosystem.

### D15: Observability

**Decision:** Structured logging via `app.logging` emitters only. OpenTelemetry traces from GraphQL through repository. Prometheus metrics for submission/delivery counts and processing duration. `x-request-id` propagated end-to-end as `correlation_id`.

**Rationale:** Platform convention. Enables debugging across sync and async paths.

### D16: Deployment

**Decision:** Docker Compose locally (Postgres, API, web, Temporal dev server, optional LocalStack). Kubernetes/EKS in production with HPA on API, SQS consumer, and Temporal worker pods. Alembic migrations as K8s Job.

**Rationale:** Standard cloud-native pattern. Phase 1 single-region, no DR.

## Architecture

```
Client Apps ──GraphQL──▶ API Service ──▶ NotificationService ──▶ DB + Temporal
              SQS ──▶ Consumer Service ──┘                              │
                                                                        ▼
                                                              Temporal Workers
                                                                        │
                                                    ┌───────────────────┼───────────┐
                                                    ▼                   ▼           ▼
                                                 SES (email)        SNS (SMS)    FCM/APNs (push)
                                                    │                   │           │
                                                    └───────────────────┴───────────┘
                                                                        │
                                                              EventBridge callbacks
                                                                        ▼
                                                              Callback Handler → DB
```

### Key workflows

1. **SendNotificationWorkflow**: validate → preference gate → render template → parallel channel fan-out → record attempts → aggregate status → audit event.
2. **ScheduledNotificationWorkflow**: `workflow.sleep(until scheduled_at)` → child SendNotificationWorkflow.
3. **OrphanNotificationReconciler**: every 5 min, find `Queued` rows with no `workflow_id` → retry start or mark Failed.
4. **RetentionPurgeWorkflow**: daily, delete records older than tenant retention policy.

### Status lifecycle

`Scheduled → Queued → Processing → Sent → Delivered | Failed | Cancelled | Skipped`

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Orphan `Queued` notifications after DB commit but failed Temporal start | 3× immediate retry + 5-minute reconciler cron |
| SQS poison messages | DLQ after max receive count; alert + manual replay |
| Provider outage (SES/SNS down) | Temporal retry with exponential backoff; circuit breaker in adapters |
| Credential leak | Secrets Manager only; `secret_ref` in DB; redact in logs/traces |
| Tenant data leak | Mandatory `application_id` filter in every repository query; tenant-safe DataLoaders |
| Large SQS messages rejected | Per-message 100-recipient limit; client splits into multiple messages |
| No daily quotas in v1 | Per-message limits only; add tenant quotas in v2 if abuse occurs |

## Migration Plan

Greenfield — no migration from existing systems.

**Deployment sequence:**

1. Scaffold monorepo (§1).
2. Deploy Postgres + run Alembic migrations (§3).
3. Deploy API + Temporal workers (§4–§10).
4. Deploy SQS consumer + callback handler (§8, §11).
5. Deploy admin web (§12).
6. Onboard first tenant: create Application, API key, channel configs, templates.
7. Enable retention purge cron.

**Rollback:** Standard K8s rolling deploy rollback. DB migrations are forward-only (Alembic downgrade scripts maintained but not auto-run).

## Open Questions

- **Tenant daily quotas**: Defer to v2 unless abuse observed during pilot.
- **SQS per-message cap**: Confirmed at 100 recipients; env-configurable via `MAX_SQS_RECIPIENTS_PER_MESSAGE`.
