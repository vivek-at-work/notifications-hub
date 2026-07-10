## ADDED Requirements

### Requirement: Versioned templates per application and channel

The system SHALL store templates as immutable versioned records scoped by `application_id`, `key`, and `channel`.

#### Scenario: Create new template version

- **WHEN** a tenant admin saves a template edit in the admin UI
- **THEN** the system creates a new version record and marks it as the active version for that key and channel

#### Scenario: Template lookup at send time

- **WHEN** a send request references `templateKey: "order_confirmation"` for channel `EMAIL`
- **THEN** the system loads the latest active version for that application, key, and channel

### Requirement: Placeholder schema validation

The system SHALL define a `placeholders_schema` (JSON Schema) on each template and validate submitted placeholders against it before rendering.

#### Scenario: Valid placeholders

- **WHEN** a send request includes placeholders matching the template's schema
- **THEN** the system proceeds with template rendering

#### Scenario: Invalid placeholders

- **WHEN** a send request includes placeholders that fail schema validation (missing required field or wrong type)
- **THEN** the system rejects the request with a validation error identifying the invalid field

#### Scenario: Missing required placeholder

- **WHEN** a send request omits a placeholder marked as required in the schema
- **THEN** the system rejects the request with a validation error listing the missing fields

### Requirement: Template rendering

The system SHALL substitute placeholders into template subject and body during the send workflow rendering step.

#### Scenario: Render email template

- **WHEN** a template has subject "Order {{orderId}} confirmed" and body "Hi {{userName}}, your order is confirmed."
- **AND** placeholders are `{ "orderId": "ORD-123", "userName": "Alice" }`
- **THEN** the rendered output is subject "Order ORD-123 confirmed" and body "Hi Alice, your order is confirmed."

#### Scenario: Render SMS template

- **WHEN** a SMS template has body "Your OTP is {{otp}}. Valid for {{minutes}} minutes."
- **AND** placeholders are `{ "otp": "123456", "minutes": "5" }`
- **THEN** the rendered output is "Your OTP is 123456. Valid for 5 minutes."

### Requirement: Admin UI template authoring

The system SHALL provide template creation and editing exclusively through the admin web UI. Client applications MUST NOT create or modify templates via API in v1.

#### Scenario: Admin creates template via UI

- **WHEN** a tenant admin creates a new email template with key "welcome_email" in the admin UI
- **THEN** the system stores the template and makes it available for send requests referencing `templateKey: "welcome_email"`

#### Scenario: Client attempts template CRUD via API

- **WHEN** a client application attempts to call a template creation or update mutation
- **THEN** the system does not expose such mutations in the GraphQL schema

### Requirement: Read-only template queries for tenant admin

The system SHALL expose read-only GraphQL queries for tenant administrators to list and view templates.

#### Scenario: List templates

- **WHEN** a tenant admin queries `templates(where: { channel: { eq: EMAIL } })`
- **THEN** the system returns a paginated `TemplateConnection` for their application

#### Scenario: View template detail

- **WHEN** a tenant admin queries `template(id: "...")` for a template in their application
- **THEN** the system returns the template with key, channel, version, subject, body, and placeholders schema

### Requirement: No multi-locale support in v1

The system SHALL NOT support locale-specific template variants in v1. Each template key + channel combination has a single default template.

#### Scenario: Template without locale

- **WHEN** a tenant admin creates a template with key "password_reset"
- **THEN** the system stores it without a locale field and uses it as the default for all send requests referencing that key
