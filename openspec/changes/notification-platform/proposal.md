## Why

Client applications currently reimplement notification delivery (email, SMS, push), retry logic, template rendering, and delivery tracking independently. A centralized Notification Hub eliminates this duplication, provides consistent multi-tenant isolation, and gives operators a single platform for auditing, monitoring, and managing notification channels across all applications.

## What Changes

- Bootstrap an Nx monorepo with Python API (`apps/api`), Next.js admin portal (`apps/web`), and shared libraries (`libs/py/common`, `libs/js/*`).
- Introduce a multi-tenant notification platform where each **Application** is an isolated tenant with its own templates, channel credentials, and quotas.
- Expose GraphQL APIs for client applications to send, query, schedule, and cancel notifications.
- Support three delivery channels in v1: **Email** (AWS SES), **SMS** (AWS SNS), **Push** (FCM for Android, direct APNs for iOS).
- Process notifications asynchronously via **Temporal** workflows with configurable retry policies and status lifecycle tracking.
- Provide an **SQS ingestion path** for bulk/low-priority notification requests.
- Build an **admin web UI** for tenant configuration, template authoring, channel setup, and notification history.
- Build a **standalone end-user portal** with Google OIDC login for preference management and notification history.
- Implement provider callback handling (EventBridge/webhooks) for delivery status updates.
- Add structured logging, OpenTelemetry tracing, and Prometheus metrics across all components.
- Deploy via Docker Compose (local) and Kubernetes (production).

## Capabilities

### New Capabilities

- `notification-ingestion`: GraphQL mutations and queries for submitting, scheduling, cancelling, and querying notifications; idempotency key deduplication; bulk send (max 10 recipients).
- `multi-tenancy`: Application-scoped tenant isolation, API key authentication for S2S clients, Google OIDC for admin and end-user roles, authorization enforcement at every layer.
- `template-management`: Versioned templates per application and channel; placeholder schema validation; admin UI authoring only (no client-facing template CRUD in v1); no multi-locale support in v1.
- `notification-processing`: Temporal workflow orchestration for send pipeline, scheduling, preference gating, status aggregation, and orphan reconciler (5-minute interval).
- `channel-delivery`: Hexagonal channel adapters for SES (email), SNS (SMS), FCM (Android push), and direct APNs (iOS push); per-tenant credentials via AWS Secrets Manager.
- `delivery-tracking`: Provider webhook/callback handling, per-channel attempt records, status lifecycle (Queued → Processing → Sent → Delivered/Failed), and notification event audit trail.
- `event-ingestion`: SQS consumer for async notification ingestion with per-message recipient limit (100); shared queue with tenant routing via `applicationId` message attribute.
- `observability`: Structured logging (`app.logging`), OpenTelemetry instrumentation (GraphQL → Service → Repository → DB), Prometheus metrics, and request correlation via `x-request-id`.
- `admin-dashboard`: Next.js web application for tenant admin (templates, channel config, metrics, history) and end-user self-service (preferences, history) with standalone Google OIDC login.

### Modified Capabilities

<!-- No existing capabilities in openspec/specs/ — all are new. -->

## Impact

- **New monorepo**: `apps/api`, `apps/web`, `libs/py/common`, `libs/js/design-system`, `libs/js/notifications-ui`.
- **New infrastructure dependencies**: PostgreSQL 16, Temporal, AWS SQS, SES, SNS, EventBridge, Secrets Manager, KMS.
- **New database schema**: ~15 tables covering applications, templates, notifications, attempts, events, preferences, device tokens, and end users.
- **New deployment targets**: Docker Compose (local dev), Kubernetes/EKS (production) with HPA-scaled API, worker, and consumer pods.
- **New CI/CD pipelines**: Nx build, pytest, lint, Docker image build, Alembic migrations.
- **Retention policy**: 90-day default notification history with scheduled purge workflow.
- **Out of scope for v1**: Transactional outbox, multi-locale templates, shell JWT passthrough, WhatsApp/Slack/Teams channels, cross-region DR, client-facing template GraphQL CRUD.
