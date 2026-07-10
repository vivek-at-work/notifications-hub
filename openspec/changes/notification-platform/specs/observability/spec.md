## ADDED Requirements

### Requirement: Structured logging

The system SHALL emit all application logs through the centralized `app.logging` module using typed emitters (`log_startup`, `log_http`, `log_api`, `log_background_job`). Direct use of Python's `logging` module in application code is prohibited.

#### Scenario: GraphQL request logged

- **WHEN** a GraphQL mutation is executed
- **THEN** the system emits an `api-log` with `kind: graphql`, operation name, and `request_id`

#### Scenario: Temporal activity completion logged

- **WHEN** a Temporal activity completes (success or failure)
- **THEN** the system emits a `background-job-log` with workflow ID, activity name, duration, and status

#### Scenario: Permission denial audited

- **WHEN** an authorization check fails
- **THEN** the system emits an `api-log` with `kind: audit` including the actor, resource, and denial reason

### Requirement: Request correlation

The system SHALL propagate `x-request-id` from HTTP requests through GraphQL, Temporal workflows, activities, and notification events as `correlation_id`.

#### Scenario: End-to-end correlation

- **WHEN** a client sends a request with header `x-request-id: req-789`
- **THEN** all logs, traces, and the notification's `correlation_id` contain `req-789`

#### Scenario: SQS correlation

- **WHEN** an SQS message includes `correlationId: evt-456`
- **THEN** all logs and traces for that processing path contain `evt-456`

### Requirement: OpenTelemetry tracing

The system SHALL instrument every GraphQL request with a root span and child spans for resolvers, services, repository calls, and database queries.

#### Scenario: Trace hierarchy

- **WHEN** a `sendNotification` mutation is processed
- **THEN** the trace contains spans: GraphQL Request → resolver → NotificationService.create → repository.insert → Temporal start_workflow

#### Scenario: Async trace propagation

- **WHEN** a Temporal workflow executes channel send activities
- **THEN** child spans are created for each activity, service call, and remote API invocation

### Requirement: Sensitive data redaction

The system SHALL never log or trace passwords, secrets, tokens, API keys, authorization headers, credentials, or PII. Sensitive values MUST be redacted.

#### Scenario: API key redaction

- **WHEN** an API key is referenced in a log context
- **THEN** the value appears as `***REDACTED***`

#### Scenario: Recipient PII in traces

- **WHEN** a notification is processed with email or phone recipients
- **THEN** trace attributes do not contain the raw email address or phone number

### Requirement: Prometheus metrics

The system SHALL expose Prometheus metrics for notification submission, delivery, processing duration, and infrastructure health.

#### Scenario: Submission counter

- **WHEN** a notification is submitted
- **THEN** the metric `notifications_submitted_total{application_id, channel}` is incremented

#### Scenario: Delivery counter

- **WHEN** a notification reaches `Delivered` or `Failed` status
- **THEN** the metric `notifications_delivered_total{application_id, channel, status}` is incremented

#### Scenario: Processing duration

- **WHEN** a send workflow completes
- **THEN** the metric `notification_processing_duration_seconds{channel}` records the elapsed time

### Requirement: Health endpoints

The system SHALL expose `/health` endpoints on all services, excluded from HTTP request logging.

#### Scenario: API health check

- **WHEN** a GET request is made to `/health`
- **THEN** the system returns 200 with service status and does not emit an `http-log` entry

### Requirement: Orphan reconciler alerting

The system SHALL emit a metric and alert when the orphan reconciler heals more than a configurable threshold of stuck notifications in a single run.

#### Scenario: Reconciler threshold alert

- **WHEN** the reconciler heals more than 10 orphan notifications in one 5-minute run
- **THEN** the metric `orphan_notifications_reconciled_total` is incremented and an alert is triggered
