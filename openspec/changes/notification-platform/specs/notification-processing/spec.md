## ADDED Requirements

### Requirement: Send notification workflow

The system SHALL orchestrate notification delivery through a `SendNotificationWorkflow` that validates, gates preferences, renders templates, fans out to channels, records attempts, and aggregates status.

#### Scenario: Successful multi-channel send

- **WHEN** a notification is submitted with channels `[EMAIL, SMS]` and both channels succeed
- **THEN** the workflow records attempts for each channel, sets notification status to `Sent`, and emits an audit event

#### Scenario: Partial channel failure

- **WHEN** a notification is submitted with channels `[EMAIL, SMS]` and email succeeds but SMS fails after all retries
- **THEN** the workflow sets notification status to `Failed` and records the SMS failure reason on the attempt

#### Scenario: All channels skipped by preferences

- **WHEN** all channels are disabled by user preferences and no category is mandatory
- **THEN** the workflow sets notification status to `Skipped` without attempting delivery

### Requirement: Scheduled notification workflow

The system SHALL support future delivery via a `ScheduledNotificationWorkflow` that sleeps until `scheduled_at` then triggers the send workflow.

#### Scenario: Scheduled delivery fires

- **WHEN** a notification has `scheduled_at` set to a future time and the scheduled time arrives
- **THEN** the workflow updates status from `Scheduled` to `Queued` and starts a `SendNotificationWorkflow`

#### Scenario: Cancel before scheduled time

- **WHEN** a scheduled notification is cancelled before its `scheduled_at`
- **THEN** the scheduled workflow is terminated and status is set to `Cancelled`

### Requirement: Preference gating

The system SHALL check user notification preferences per category and channel before sending, unless the category is marked as mandatory.

#### Scenario: User opted out of SMS

- **WHEN** a notification targets a user who has disabled SMS for the notification's category
- **AND** the category is not mandatory
- **THEN** the SMS channel is excluded from the send and recorded as skipped

#### Scenario: Mandatory category bypasses opt-out

- **WHEN** a notification targets a user who has disabled email for a category marked `is_mandatory: true`
- **THEN** the email channel is still included in the send

### Requirement: Configurable retry policies

The system SHALL retry failed channel delivery attempts with exponential backoff, configurable per channel with a default of 5 maximum attempts.

#### Scenario: Transient failure retried

- **WHEN** an email send fails with a retryable error (e.g., SES throttling)
- **THEN** Temporal retries the activity with exponential backoff up to the configured maximum

#### Scenario: Permanent failure not retried

- **WHEN** an SMS send fails with a non-retryable error (e.g., invalid phone number)
- **THEN** the attempt is marked as `Failed` immediately without further retries

### Requirement: Status lifecycle

The system SHALL track notification status through the lifecycle: `Scheduled → Queued → Processing → Sent → Delivered | Failed | Cancelled | Skipped`.

#### Scenario: Status progression on success

- **WHEN** a notification is submitted without `scheduledAt`
- **THEN** status transitions: `Queued` → `Processing` → `Sent` → `Delivered` (upon provider callback)

#### Scenario: Status on failure

- **WHEN** all channel attempts fail after retries
- **THEN** notification status is set to `Failed`

### Requirement: Orphan notification reconciler

The system SHALL run a reconciler workflow every 5 minutes to heal notifications stuck in `Queued` status without an associated Temporal workflow.

#### Scenario: Orphan detected and healed

- **WHEN** a notification has status `Queued`, no `workflow_id`, and `created_at` older than 5 minutes
- **THEN** the reconciler attempts to start a Temporal workflow up to 3 times

#### Scenario: Reconciler fails to start workflow

- **WHEN** the reconciler cannot start a workflow after 3 attempts
- **THEN** the notification status is set to `Failed` with error code `WORKFLOW_START_FAILED`

### Requirement: Retention purge workflow

The system SHALL run a daily `RetentionPurgeWorkflow` that deletes notification records older than each tenant's retention policy (default 90 days).

#### Scenario: Purge expired notifications

- **WHEN** a tenant has default retention (90 days) and notifications exist older than 90 days
- **THEN** the purge workflow deletes those notifications, their attempts, events, and recipients

#### Scenario: Tenant with custom retention

- **WHEN** a tenant has `retention_policy.notification_history_days: 30`
- **THEN** the purge workflow deletes notifications older than 30 days for that tenant only
