## ADDED Requirements

### Requirement: Tenant admin template management UI

The system SHALL provide a web UI for tenant administrators to create, edit, preview, and view version history of notification templates.

#### Scenario: Create email template

- **WHEN** a tenant admin navigates to the templates page and creates a new email template with key, subject, body, and placeholder schema
- **THEN** the system saves a new template version and displays it in the template list

#### Scenario: Preview template with placeholders

- **WHEN** a tenant admin previews a template with sample placeholder values
- **THEN** the UI renders the subject and body with placeholders substituted

#### Scenario: View template version history

- **WHEN** a tenant admin views a template's detail page
- **THEN** the UI displays all versions with creation timestamps and the active version indicator

### Requirement: Tenant admin channel configuration UI

The system SHALL provide a web UI for tenant administrators to configure channel providers (SES, SNS, FCM, APNs) with credentials stored in Secrets Manager.

#### Scenario: Configure email channel

- **WHEN** a tenant admin configures the email channel with SES region and from-address
- **THEN** the system saves the channel config and stores any credentials in Secrets Manager

#### Scenario: Configure iOS push channel

- **WHEN** a tenant admin configures the iOS push channel with bundle ID, team ID, key ID, and uploads a `.p8` key
- **THEN** the system stores the key in Secrets Manager and saves the config with `secret_ref`

### Requirement: Tenant admin notification history

The system SHALL provide a paginated notification history view for tenant administrators with filtering by status, channel, date range, and search.

#### Scenario: Filter notifications by status

- **WHEN** a tenant admin filters the history page by status "Failed"
- **THEN** the UI displays only failed notifications for their application

#### Scenario: View notification detail

- **WHEN** a tenant admin clicks on a notification in the history list
- **THEN** the UI displays the full notification detail including recipients, attempts, events, and rendered content

### Requirement: Tenant admin application metrics

The system SHALL display application-level metrics including submission counts, delivery rates, and failure rates over configurable time periods.

#### Scenario: View delivery metrics

- **WHEN** a tenant admin views the metrics dashboard for the last 7 days
- **THEN** the UI displays charts for notifications submitted, delivered, and failed by channel

### Requirement: End-user preference management

The system SHALL provide a standalone end-user portal at `/preferences/[appSlug]` where users authenticated via Google OIDC can manage notification preferences per category and channel.

#### Scenario: Opt out of SMS for a category

- **WHEN** an end user disables SMS for the "marketing" category
- **THEN** the system saves the preference and future marketing notifications skip SMS for that user

#### Scenario: Mandatory category cannot be disabled

- **WHEN** an end user views preferences for a category marked `is_mandatory`
- **THEN** the UI shows the category as non-disableable with an explanation

#### Scenario: Signed unsubscribe deep link

- **WHEN** an end user clicks an unsubscribe link in an email (signed JWT deep link to `/preferences/[appSlug]`)
- **THEN** the portal opens with the relevant category pre-selected for opt-out

### Requirement: End-user notification history

The system SHALL provide a notification history view for end users at `/history/[appSlug]` showing notifications sent to them.

#### Scenario: View own notification history

- **WHEN** an authenticated end user views their notification history for an application
- **THEN** the UI displays a paginated list of notifications addressed to them with status and channel

### Requirement: Standalone Google OIDC login

The system SHALL provide a standalone login page at `/login` using Google OIDC. Shell JWT passthrough and multizone hosting are not supported in v1.

#### Scenario: End user Google login

- **WHEN** an end user navigates to `/login` and authenticates with Google
- **THEN** the system creates or resolves an `end_users` record and redirects to the preferences or history page

#### Scenario: Tenant admin Google login

- **WHEN** a tenant admin navigates to `/login` and authenticates with Google
- **THEN** the system verifies their admin role binding and redirects to the admin dashboard

### Requirement: API key management UI

The system SHALL provide a web UI for tenant administrators to create, view scopes, and revoke API keys.

#### Scenario: Create API key in UI

- **WHEN** a tenant admin creates a new API key with selected scopes in the admin UI
- **THEN** the system displays the plaintext key once with a copy button and lists the key (hashed) in the key management page

#### Scenario: Revoke API key in UI

- **WHEN** a tenant admin revokes an API key
- **THEN** the key is marked as revoked and removed from the active keys list

### Requirement: Notification category management

The system SHALL provide a web UI for tenant administrators to define notification categories with optional mandatory flag.

#### Scenario: Create mandatory category

- **WHEN** a tenant admin creates a category "security_alerts" with `is_mandatory: true`
- **THEN** the category is saved and end users cannot opt out of it
