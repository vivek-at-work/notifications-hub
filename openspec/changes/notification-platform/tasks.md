## 1. Monorepo Scaffolding

- [ ] 1.1 Initialize git repository with main, development, and stage branches (repo-bootstrap skill)
- [ ] 1.2 Scaffold Nx monorepo root: package.json, nx.json, pnpm-workspace.yaml, .nvmrc (Node 24)
- [ ] 1.3 Bootstrap Python API workspace: apps/api with uv, FastAPI, Strawberry, pyproject.toml (api-bootstrap skill)
- [ ] 1.4 Bootstrap Next.js web workspace: apps/web with MUI, Apollo Client, Redux (web-bootstrap skill)
- [ ] 1.5 Create libs/py/common with shared domain types, error codes, and placeholder engine
- [ ] 1.6 Create libs/js/design-system and libs/js/notifications-ui shared packages
- [ ] 1.7 Set up Docker Compose: Postgres 16, API, web, Temporal dev server
- [ ] 1.8 Copy and activate CI/CD workflow templates from repo-bootstrap/github-actions

## 2. Observability Foundation

- [ ] 2.1 Implement app.logging module with typed emitters (log_startup, log_http, log_api, log_background_job)
- [ ] 2.2 Add RequestLoggingMiddleware with x-request-id lifecycle and correlation propagation
- [ ] 2.3 Configure OpenTelemetry instrumentation for FastAPI and Strawberry GraphQL
- [ ] 2.4 Add /health endpoint excluded from HTTP logging
- [ ] 2.5 Set up Prometheus metrics exporter with notifications_submitted_total and notifications_delivered_total stubs
- [ ] 2.6 Configure LOG_FORMAT and LOG_LEVEL environment-based defaults

## 3. Database Schema & Migrations

- [ ] 3.1 Create SQLAlchemy async models: applications, application_api_keys
- [ ] 3.2 Create models: channel_configs, templates (versioned, no locale)
- [ ] 3.3 Create models: notifications, notification_recipients, notification_attempts, notification_events
- [ ] 3.4 Create models: device_tokens, end_users, application_users
- [ ] 3.5 Create models: notification_categories, user_notification_preferences, user_channel_preferences
- [ ] 3.6 Add indexes: (application_id, created_at), (application_id, status), unique (application_id, idempotency_key), (provider_message_id)
- [ ] 3.7 Set default retention_policy (90 days) on applications table
- [ ] 3.8 Generate and apply initial Alembic migration
- [ ] 3.9 Create repository layer with mandatory application_id scoping on all queries

## 4. Multi-Tenancy & Authentication

- [ ] 4.1 Implement ApplicationService and ApplicationRepository (CRUD, tenant lookup)
- [ ] 4.2 Implement API key generation, hashing, storage, and validation middleware
- [ ] 4.3 Implement API key scope enforcement (notifications:send, notifications:read, devices:register, users:link)
- [ ] 4.4 Implement Google OIDC integration for tenant admin and end-user JWT issuance
- [ ] 4.5 Implement role-based authorization: platform_admin, tenant_admin, end_user, client_app
- [ ] 4.6 Add authorization checks before business logic in resolver and service layers
- [ ] 4.7 Implement audit logging for permission denials (kind="audit")
- [ ] 4.8 Implement AWS Secrets Manager integration for channel credential storage (secret_ref pattern)

## 5. Channel Configuration

- [ ] 5.1 Implement ChannelConfigService and ChannelConfigRepository
- [ ] 5.2 Support email channel config (SES region, from-address, secret_ref)
- [ ] 5.3 Support SMS channel config (SNS region, secret_ref)
- [ ] 5.4 Support FCM push config (project ID, secret_ref)
- [ ] 5.5 Support APNs push config (bundle_id, team_id, key_id, environment, secret_ref for .p8 key)
- [ ] 5.6 Implement notification category CRUD (key, name, is_mandatory)

## 6. Template Management

- [ ] 6.1 Implement TemplateService with versioned create, activate, and lookup by (application_id, key, channel)
- [ ] 6.2 Implement placeholder schema validation using JSON Schema
- [ ] 6.3 Implement template rendering engine with {{placeholder}} substitution
- [ ] 6.4 Implement TemplateRepository with version history queries
- [ ] 6.5 Add read-only GraphQL queries: templates (Connection), template (by ID) for tenant admin

## 7. GraphQL Notification Ingestion

- [ ] 7.1 Set up Strawberry GraphQL schema with Query and Mutation types
- [ ] 7.2 Implement NotificationService: create, cancel, query with idempotency deduplication (24h window)
- [ ] 7.3 Implement sendNotification mutation (single recipient)
- [ ] 7.4 Implement sendBulkNotifications mutation with max 10 recipient validation
- [ ] 7.5 Implement cancelNotification mutation with status guard (Queued/Scheduled only)
- [ ] 7.6 Implement notification(id) and notifications(where, search, first, after) queries with NotificationConnection
- [ ] 7.7 Implement registerDeviceToken mutation
- [ ] 7.8 Implement linkApplicationUser mutation
- [ ] 7.9 Add request-scoped DataLoaders for notification attempts and events
- [ ] 7.10 Wire Temporal workflow start after DB commit with 3x retry

## 8. Event Ingestion (SQS)

- [ ] 8.1 Implement SQS consumer service entrypoint with shared queue configuration
- [ ] 8.2 Implement message parsing and normalization to NotificationService.create path
- [ ] 8.3 Enforce per-message recipient limit (MAX_SQS_RECIPIENTS_PER_MESSAGE=100)
- [ ] 8.4 Implement tenant routing via applicationId message attribute
- [ ] 8.5 Implement idempotent consumption using idempotencyKey
- [ ] 8.6 Configure DLQ with maxReceiveCount and alert on poison messages
- [ ] 8.7 Propagate correlationId from SQS payload to notification correlation_id

## 9. Notification Processing (Temporal)

- [ ] 9.1 Set up Temporal worker with task queues: notification-send, notification-scheduled, retention-purge
- [ ] 9.2 Implement SendNotificationWorkflow: validate → preference gate → render → fan-out → aggregate → audit
- [ ] 9.3 Implement ScheduledNotificationWorkflow with workflow.sleep and child workflow trigger
- [ ] 9.4 Implement preference gating activity (category × channel, mandatory bypass)
- [ ] 9.5 Implement render_template_activity per channel
- [ ] 9.6 Implement aggregate_status_activity
- [ ] 9.7 Implement emit_audit_event_activity
- [ ] 9.8 Implement OrphanNotificationReconciler cron workflow (5-minute interval)
- [ ] 9.9 Implement RetentionPurgeWorkflow (daily, per-tenant retention_policy)
- [ ] 9.10 Configure per-channel retry policies (default 5 attempts, exponential backoff)

## 10. Channel Delivery Adapters

- [ ] 10.1 Define ChannelDeliveryPort interface and ChannelSendRequest/ChannelSendResult types
- [ ] 10.2 Implement SesEmailAdapter with provider_message_id tracking
- [ ] 10.3 Implement SnsSmsAdapter with phone validation and error classification
- [ ] 10.4 Implement FcmPushAdapter with invalid token cleanup
- [ ] 10.5 Implement ApnsPushAdapter with HTTP/2 JWT auth and .p8 key loading
- [ ] 10.6 Implement send_email_activity, send_sms_activity, send_push_android_activity, send_push_ios_activity
- [ ] 10.7 Implement record_attempt_activity with attempt_number and error_code
- [ ] 10.8 Add integration tests with LocalStack/mocks for each adapter

## 11. Delivery Tracking & Callbacks

- [ ] 11.1 Implement callback handler service with webhook signature verification
- [ ] 11.2 Implement SES delivery and bounce event processing via EventBridge
- [ ] 11.3 Implement SNS SMS delivery receipt processing
- [ ] 11.4 Implement provider_message_id → attempt lookup and status update
- [ ] 11.5 Implement idempotent callback processing (duplicate detection)
- [ ] 11.6 Implement parent notification status aggregation after callback
- [ ] 11.7 Implement append-only notification_events recording for all status transitions

## 12. Admin Dashboard (Web)

- [ ] 12.1 Set up Next.js app with MUI theme, Apollo Client, and Google OIDC login at /login
- [ ] 12.2 Build tenant admin layout with application selector and navigation
- [ ] 12.3 Build template management pages: list, create/edit, preview, version history
- [ ] 12.4 Build channel configuration pages: email, SMS, FCM, APNs setup forms
- [ ] 12.5 Build API key management page: create, view scopes, revoke
- [ ] 12.6 Build notification category management page with mandatory toggle
- [ ] 12.7 Build notification history page with status/channel/date filters and detail view
- [ ] 12.8 Build application metrics dashboard with submission/delivery/failure charts
- [ ] 12.9 Build end-user preference page at /preferences/[appSlug] with category × channel toggles
- [ ] 12.10 Build end-user notification history at /history/[appSlug]
- [ ] 12.11 Implement signed JWT unsubscribe deep links from email templates

## 13. End-User Features

- [ ] 13.1 Implement EndUserService and preference CRUD (per category × channel)
- [ ] 13.2 Implement user_channel_preferences for global channel overrides
- [ ] 13.3 Implement end-user GraphQL queries: myPreferences, updatePreference, myNotificationHistory
- [ ] 13.4 Enforce end-user scoping: users can only see their own preferences and history

## 14. Deployment & Operations

- [ ] 14.1 Create multi-stage Dockerfiles for API and web (node:24-alpine, non-root, HEALTHCHECK)
- [ ] 14.2 Finalize Docker Compose for local development with all services
- [ ] 14.3 Create Kubernetes manifests: API, SQS consumer, Temporal worker, callback handler, web deployments
- [ ] 14.4 Configure HPA for API, consumer, and worker pods
- [ ] 14.5 Set up Alembic migration as K8s Job in deploy pipeline
- [ ] 14.6 Configure External Secrets Operator for Secrets Manager integration
- [ ] 14.7 Add orphan reconciler and retention purge alerting rules
- [ ] 14.8 Document tenant onboarding runbook: create app, API key, channel config, templates
- [ ] 14.9 Write ADRs for key decisions: Temporal over Celery, no outbox, direct APNs, admin-only templates
