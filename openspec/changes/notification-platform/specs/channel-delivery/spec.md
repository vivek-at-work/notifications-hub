## ADDED Requirements

### Requirement: Email delivery via SES

The system SHALL deliver email notifications through an `SesEmailAdapter` using AWS SES.

#### Scenario: Successful email send

- **WHEN** the send workflow invokes `send_email_activity` with a rendered email template
- **THEN** the adapter sends via SES, returns a `provider_message_id`, and records the attempt as `Sent`

#### Scenario: SES throttling error

- **WHEN** SES returns a throttling error
- **THEN** the adapter classifies it as retryable and Temporal retries the activity

### Requirement: SMS delivery via SNS

The system SHALL deliver SMS notifications through an `SnsSmsAdapter` using AWS SNS as the default provider.

#### Scenario: Successful SMS send

- **WHEN** the send workflow invokes `send_sms_activity` with a rendered SMS body and valid phone number
- **THEN** the adapter sends via SNS, returns a `provider_message_id`, and records the attempt as `Sent`

#### Scenario: Invalid phone number

- **WHEN** the phone number format is invalid
- **THEN** the adapter classifies it as non-retryable and the attempt is marked `Failed` immediately

### Requirement: Android push via FCM

The system SHALL deliver Android push notifications through a `FcmPushAdapter` using Firebase Cloud Messaging.

#### Scenario: Successful FCM push

- **WHEN** the send workflow invokes `send_push_android_activity` with a device token and rendered push payload
- **THEN** the adapter sends via FCM and records the attempt as `Sent`

#### Scenario: Invalid FCM token

- **WHEN** FCM returns an invalid registration token error
- **THEN** the adapter marks the attempt as `Failed` and the device token is flagged for cleanup

### Requirement: iOS push via direct APNs

The system SHALL deliver iOS push notifications through an `ApnsPushAdapter` using direct Apple Push Notification service (HTTP/2 + JWT auth). The system MUST NOT use FCM as a relay for iOS.

#### Scenario: Successful APNs push

- **WHEN** the send workflow invokes `send_push_ios_activity` with a device token and rendered push payload
- **THEN** the adapter sends via APNs HTTP/2 API using the tenant's `.p8` key from Secrets Manager and records the attempt as `Sent`

#### Scenario: APNs authentication failure

- **WHEN** the `.p8` key or team/bundle configuration is invalid
- **THEN** the adapter classifies it as non-retryable and the attempt is marked `Failed`

### Requirement: Hexagonal adapter pattern

The system SHALL implement all channel delivery through a `ChannelDeliveryPort` interface, enabling future channel additions without modifying orchestration logic.

#### Scenario: Adapter interface contract

- **WHEN** a new channel adapter is implemented
- **THEN** it MUST implement `send(request: ChannelSendRequest) → ChannelSendResult` and be injectable into the send workflow activities

### Requirement: Per-tenant credential loading

The system SHALL load channel credentials from AWS Secrets Manager at send time using the tenant's `channel_configs.secret_ref`.

#### Scenario: Load SES credentials

- **WHEN** sending email for application X
- **THEN** the `SesEmailAdapter` loads credentials from the ARN stored in application X's email `channel_config`

#### Scenario: Missing channel configuration

- **WHEN** a send request includes a channel with no `channel_config` for the application
- **THEN** the attempt is marked `Failed` with error code `CHANNEL_NOT_CONFIGURED`

### Requirement: Provider message ID tracking

The system SHALL store the `provider_message_id` returned by each channel adapter on the corresponding `notification_attempts` record for callback correlation.

#### Scenario: SES message ID stored

- **WHEN** SES returns a message ID for a sent email
- **THEN** the attempt record stores that ID as `provider_message_id`
