## ADDED Requirements

### Requirement: SQS notification ingestion

The system SHALL consume notification requests from a shared AWS SQS queue, normalizing them to the same `NotificationService` path used by GraphQL ingestion.

#### Scenario: Valid SQS message processed

- **WHEN** an SQS message contains a valid notification payload with `applicationId`, `templateKey`, `channels`, `recipients`, and `placeholders`
- **THEN** the consumer creates a notification record and starts a Temporal workflow, identical to the GraphQL path

#### Scenario: SQS message with scheduled delivery

- **WHEN** an SQS message includes a `scheduledAt` field in the future
- **THEN** the consumer creates a notification with status `Scheduled` and starts a `ScheduledNotificationWorkflow`

### Requirement: Tenant routing via message attributes

The system SHALL route SQS messages to the correct tenant using the `applicationId` message attribute.

#### Scenario: Message with valid application ID

- **WHEN** an SQS message has message attribute `applicationId` set to a registered application
- **THEN** the consumer resolves the application and processes the notification under that tenant

#### Scenario: Message with unknown application ID

- **WHEN** an SQS message has message attribute `applicationId` set to a non-existent application
- **THEN** the consumer rejects the message to the DLQ with error `UNKNOWN_APPLICATION`

### Requirement: Per-message recipient limit

The system SHALL enforce a maximum of 100 recipients per SQS message, configurable via `MAX_SQS_RECIPIENTS_PER_MESSAGE` environment variable.

#### Scenario: Message within recipient limit

- **WHEN** an SQS message contains 100 or fewer recipients
- **THEN** the consumer processes the message normally

#### Scenario: Message exceeds recipient limit

- **WHEN** an SQS message contains more than 100 recipients
- **THEN** the consumer rejects the message to the DLQ with error `RECIPIENT_LIMIT_EXCEEDED` without partial processing

### Requirement: Idempotent SQS consumption

The system SHALL deduplicate SQS messages using the `idempotencyKey` field, consistent with GraphQL ingestion deduplication.

#### Scenario: Duplicate SQS message

- **WHEN** an SQS message with idempotency key "bulk-123" was already processed
- **THEN** the consumer acknowledges the message without creating a duplicate notification

### Requirement: SQS dead letter queue

The system SHALL route messages that fail processing after the maximum receive count to a dead letter queue.

#### Scenario: Poison message sent to DLQ

- **WHEN** an SQS message fails processing 3 times (configurable `maxReceiveCount`)
- **THEN** the message is moved to the DLQ and an alert is emitted

### Requirement: Correlation ID propagation

The system SHALL propagate the `correlationId` from SQS message payloads as the notification's `correlation_id`, matching the `x-request-id` convention used by GraphQL ingestion.

#### Scenario: Correlation ID from SQS payload

- **WHEN** an SQS message includes `"correlationId": "evt-456"`
- **THEN** the created notification record stores `correlation_id: "evt-456"`
