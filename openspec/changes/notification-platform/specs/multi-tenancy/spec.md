## ADDED Requirements

### Requirement: Application tenant isolation

The system SHALL isolate all data by `application_id` such that no tenant can access another tenant's notifications, templates, configurations, or credentials.

#### Scenario: Cross-tenant data access attempt

- **WHEN** application A queries or mutates data with application B's ID
- **THEN** the system returns null or a permission error without revealing that the resource exists

#### Scenario: Repository query scoping

- **WHEN** any repository method executes a database query
- **THEN** the query MUST include an `application_id` filter derived from the authenticated principal

### Requirement: API key authentication for S2S clients

The system SHALL authenticate client applications using hashed API keys with configurable scopes.

#### Scenario: Valid API key

- **WHEN** a request includes a valid API key in the `Authorization` header
- **THEN** the system resolves the key to an `application_id` and grants scopes defined on the key

#### Scenario: Invalid or expired API key

- **WHEN** a request includes an invalid, revoked, or expired API key
- **THEN** the system returns a 401 authentication error and logs an audit event

#### Scenario: Insufficient scope

- **WHEN** a request uses an API key without the required scope (e.g., `notifications:send`)
- **THEN** the system returns a 403 permission error and logs an audit event with `kind="audit"`

### Requirement: Google OIDC authentication for human users

The system SHALL authenticate tenant administrators and end users via Google OIDC, issuing JWTs with role and tenant claims.

#### Scenario: Tenant admin login

- **WHEN** a user authenticates via Google OIDC and has a `tenant_admin` role binding for application X
- **THEN** the system issues a JWT with `role: tenant_admin` and `application_id: X`

#### Scenario: End user login

- **WHEN** a user authenticates via Google OIDC and has an `end_users` record
- **THEN** the system issues a JWT with `role: end_user` and `end_user_id`

#### Scenario: Platform admin login

- **WHEN** a user authenticates via Google OIDC and has a `platform_admin` role
- **THEN** the system issues a JWT with `role: platform_admin` granting access to all tenants

### Requirement: Authorization before business logic

The system SHALL enforce authorization checks before executing any business logic in resolvers and services.

#### Scenario: Unauthorized send attempt

- **WHEN** an unauthenticated request calls `sendNotification`
- **THEN** the system returns an authentication error without creating any database records

#### Scenario: Tenant admin accessing own application

- **WHEN** a tenant admin queries templates for their bound application
- **THEN** the system returns the application's templates

### Requirement: Per-tenant channel credential isolation

The system SHALL store channel credentials in AWS Secrets Manager with per-tenant `secret_ref` ARNs. Database records MUST NOT contain plaintext credentials.

#### Scenario: Channel config creation

- **WHEN** a tenant admin configures an email channel with SMTP credentials
- **THEN** the system stores credentials in Secrets Manager and saves only the ARN in `channel_configs.secret_ref`

#### Scenario: Credential retrieval at send time

- **WHEN** a send workflow needs channel credentials for application X
- **THEN** the adapter loads credentials from Secrets Manager using application X's `secret_ref` only

### Requirement: API key management

The system SHALL allow tenant administrators to create, rotate, and revoke API keys via the admin UI.

#### Scenario: Create API key

- **WHEN** a tenant admin creates a new API key with scopes `notifications:send` and `notifications:read`
- **THEN** the system stores a hashed key, returns the plaintext key once, and associates it with the application

#### Scenario: Revoke API key

- **WHEN** a tenant admin revokes an API key
- **THEN** subsequent requests using that key are rejected with a 401 error
