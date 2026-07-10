## ADDED Requirements

### Requirement: Per-channel attempt records

The system SHALL record each delivery attempt per channel on the `notification_attempts` table with attempt number, status, provider message ID, error code, and timestamp.

#### Scenario: Record successful attempt

- **WHEN** an email is successfully sent via SES
- **THEN** the system creates an attempt record with `channel: EMAIL`, `status: Sent`, and the SES message ID

#### Scenario: Record failed attempt with retries

- **WHEN** an SMS send fails on attempt 2 of 5 with a retryable error
- **THEN** the system creates an attempt record with `attempt_number: 2`, `status: Failed`, and the error code

### Requirement: Append-only notification events

The system SHALL maintain an immutable audit trail in `notification_events` for all status transitions and significant actions.

#### Scenario: Status change event

- **WHEN** a notification status changes from `Queued` to `Processing`
- **THEN** the system appends a `notification_events` record with `event_type: STATUS_CHANGED` and the new status

#### Scenario: Delivery callback event

- **WHEN** a provider callback confirms delivery
- **THEN** the system appends a `notification_events` record with `event_type: DELIVERED` and the provider payload

### Requirement: Provider callback handling

The system SHALL process delivery callbacks from AWS EventBridge (SES bounces/deliveries, SNS receipts) via a dedicated callback handler.

#### Scenario: SES delivery confirmation

- **WHEN** EventBridge delivers an SES delivery event with a matching `provider_message_id`
- **THEN** the callback handler updates the attempt status to `Delivered` and aggregates the parent notification status

#### Scenario: SES bounce notification

- **WHEN** EventBridge delivers an SES bounce event
- **THEN** the callback handler updates the attempt status to `Failed` with bounce reason and sets notification status to `Failed`

#### Scenario: Unknown provider message ID

- **WHEN** a callback arrives with a `provider_message_id` not found in the database
- **THEN** the callback handler logs a warning and discards the event without error

### Requirement: Webhook signature verification

The system SHALL verify the authenticity of all incoming provider webhooks before processing.

#### Scenario: Valid SES/SNS signature

- **WHEN** a callback request includes a valid AWS SNS/SES signature
- **THEN** the callback handler processes the event

#### Scenario: Invalid signature

- **WHEN** a callback request has an invalid or missing signature
- **THEN** the callback handler rejects the request with a 403 error and logs an audit event

### Requirement: Status aggregation

The system SHALL aggregate per-channel attempt statuses into the parent notification status after all channel attempts complete or callbacks arrive.

#### Scenario: All channels delivered

- **WHEN** all channel attempts reach `Delivered` status
- **THEN** the parent notification status is set to `Delivered`

#### Scenario: Mixed results

- **WHEN** email is `Delivered` but SMS is `Failed`
- **THEN** the parent notification status is set to `Failed`

### Requirement: Idempotent callback processing

The system SHALL process duplicate callbacks for the same `provider_message_id` without creating duplicate events or status changes.

#### Scenario: Duplicate delivery callback

- **WHEN** two identical delivery callbacks arrive for the same `provider_message_id`
- **THEN** the system processes the first and ignores the second without error
