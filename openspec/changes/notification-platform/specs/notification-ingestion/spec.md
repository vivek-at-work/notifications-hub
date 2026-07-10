## ADDED Requirements

### Requirement: Send single notification

The system SHALL accept a notification request via the `sendNotification` GraphQL mutation and create a notification record with status `Queued` (or `Scheduled` if `scheduledAt` is in the future).

#### Scenario: Successful single send

- **WHEN** an authenticated client application submits a `sendNotification` request with valid template key, recipients, channels, and placeholders
- **THEN** the system creates a notification record, starts a Temporal workflow, and returns the notification ID and initial status

#### Scenario: Scheduled notification

- **WHEN** a client submits a `sendNotification` request with `scheduledAt` set to a future timestamp
- **THEN** the system creates a notification with status `Scheduled` and starts a `ScheduledNotificationWorkflow` that sleeps until the scheduled time

### Requirement: Send bulk notifications

The system SHALL accept bulk notification requests via the `sendBulkNotifications` GraphQL mutation with a maximum of 10 recipients per request.

#### Scenario: Successful bulk send within limit

- **WHEN** an authenticated client submits `sendBulkNotifications` with 10 or fewer recipients
- **THEN** the system creates notification records for each recipient and returns their IDs and statuses

#### Scenario: Bulk send exceeds recipient limit

- **WHEN** an authenticated client submits `sendBulkNotifications` with more than 10 recipients
- **THEN** the system rejects the request with a validation error and does not create any notification records

### Requirement: Idempotency key deduplication

The system SHALL deduplicate notification submissions using an `idempotencyKey` scoped per application within a 24-hour window.

#### Scenario: Duplicate idempotency key

- **WHEN** a notification was submitted with idempotency key "abc" within the last 24 hours
- **AND** the same application submits again with key "abc"
- **THEN** the system returns the existing notification without creating a duplicate

#### Scenario: Unique idempotency key

- **WHEN** no prior submission exists with key "xyz" for the application
- **AND** the application submits with key "xyz"
- **THEN** the system creates a new notification record

### Requirement: Cancel notification

The system SHALL allow client applications to cancel notifications that have not yet been sent.

#### Scenario: Cancel queued notification

- **WHEN** a client submits `cancelNotification` for a notification with status `Queued` or `Scheduled`
- **THEN** the system sets the notification status to `Cancelled` and terminates the associated Temporal workflow

#### Scenario: Cancel already sent notification

- **WHEN** a client submits `cancelNotification` for a notification with status `Sent`, `Delivered`, or `Processing`
- **THEN** the system rejects the request with an error indicating the notification cannot be cancelled

### Requirement: Query notification by ID

The system SHALL allow authenticated clients to query a single notification by ID scoped to their application.

#### Scenario: Query own notification

- **WHEN** a client queries `notification(id: "...")` for a notification belonging to their application
- **THEN** the system returns the notification with status, channels, recipients, attempts, and events

#### Scenario: Query another application's notification

- **WHEN** a client queries a notification ID belonging to a different application
- **THEN** the system returns null without leaking existence information

### Requirement: Query notification history

The system SHALL provide a paginated `notifications` query returning a `NotificationConnection` with filtering, search, and cursor-based pagination.

#### Scenario: Filter by status

- **WHEN** a client queries `notifications(where: { status: { eq: FAILED } })`
- **THEN** the system returns only notifications with status `Failed` for the authenticated application

#### Scenario: Search by correlation ID

- **WHEN** a client queries `notifications(search: "req-abc")`
- **THEN** the system returns notifications whose `correlationId` contains "req-abc"

### Requirement: Register device token

The system SHALL allow client applications to register push notification device tokens for their users.

#### Scenario: Register new device token

- **WHEN** a client submits `registerDeviceToken` with a valid platform (ios/android) and token
- **THEN** the system stores or updates the device token associated with the application user

#### Scenario: Re-register existing token

- **WHEN** a client submits `registerDeviceToken` with a token that already exists for the application
- **THEN** the system updates the `last_seen_at` timestamp without creating a duplicate

### Requirement: Link application user

The system SHALL allow client applications to link their external user IDs to platform end-user records.

#### Scenario: Link new user

- **WHEN** a client submits `linkApplicationUser` with an `externalUserId` not yet linked
- **THEN** the system creates an `application_users` record linking the external ID to an end-user

#### Scenario: Link existing user

- **WHEN** a client submits `linkApplicationUser` with an `externalUserId` already linked
- **THEN** the system returns the existing link without modification
