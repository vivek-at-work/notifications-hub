# OpenSpec → Jira Reference

## Concrete Example for notification-platform

### 1 Epic

**NH-1 — Notification Platform** (Epic)

**Description** (from `proposal.md`):

- **Why:** Centralize email/SMS/push so client apps don't reimplement channels, retries, templates, tracking
- **What:** GraphQL API, multi-tenant isolation, Temporal processing, 3 channels, admin dashboard
- **Impact:** New monorepo, Postgres, Temporal, AWS SQS/SES/SNS/KMS
- **OpenSpec:** `openspec/changes/notification-platform/proposal.md`

**Link:** Confluence page from `design.md`

### 9 Stories (from proposal.md Capabilities)

Each Story maps to a spec file under `specs/`:

| OpenSpec spec | Jira Story (example key) | tasks.md sections |
|---------------|--------------------------|-------------------|
| `notification-ingestion` | NH-10 Send & query notifications via GraphQL | §7 |
| `multi-tenancy` | NH-11 Multi-tenant auth & isolation | §4, §5 |
| `template-management` | NH-12 Template CRUD & rendering | §6 |
| `notification-processing` | NH-13 Async processing & status lifecycle | §8, §9 |
| `channel-delivery` | NH-14 Email, SMS, push adapters | §10 |
| `delivery-tracking` | NH-15 Provider webhooks & delivery status | §11 |
| `event-ingestion` | NH-16 SQS event ingestion | §8 |
| `observability` | NH-17 Logging, tracing, metrics | §2 |
| `admin-dashboard` | NH-18 Admin web UI | §12 |

Foundation work (§1 Monorepo, §3 Database) can be:

- **Story:** "NH-5 Platform scaffolding & data model" (Epic child, no spec yet), or
- Sub-tasks under the first stories that need them

### Story AC from a Requirement + Scenarios

From `specs/notification-ingestion/spec.md`:

**Story NH-10 — Notification Ingestion**

**Acceptance Criteria** (from Requirement: *Idempotency key deduplication*):

```
AC1: Duplicate idempotency key
  GIVEN a notification was submitted with idempotency key "abc" in the last 24h
  WHEN the same application submits again with key "abc"
  THEN return the existing notification (no duplicate created)

AC2: Unique idempotency key
  GIVEN no prior submission with key "xyz"
  WHEN the application submits with key "xyz"
  THEN create a new notification record
```

Each `#### Scenario:` block becomes one AC or one test case.

### Sub-tasks from tasks.md

Under **NH-10**, sub-tasks from §7:

| Sub-task | OpenSpec source |
|----------|-----------------|
| Set up Strawberry GraphQL schema | `tasks.md` 7.1 |
| Implement NotificationService | 7.2 |
| Implement idempotency deduplication | 7.3 |
| Add sendNotification mutation | 7.4 |
| … | … |

Use the exact numbering in the sub-task description for traceability:

```
openspec: notification-platform/tasks.md#7.4
```

## Traceability Conventions

Use consistent linking in both directions:

### jira-mapping.json (repo root)

Maintain **`<repo-root>/jira-mapping.json`** after creating Jira issues (Steps 6–8). `/opsx-apply-milestone` reads this file to transition sub-tasks **In Progress** at scope start and **Done** when `tasks.md` checkboxes are checked.

```json
{
  "version": 1,
  "repo": "notifications-hub",
  "project": "NH",
  "changes": {
    "notification-platform": {
      "epic": "NH-1",
      "stories": {
        "7": "NH-10"
      },
      "tasks": {
        "7.1": "NH-201",
        "7.2": "NH-202"
      },
      "created_at": "2026-07-09T12:00:00Z",
      "updated_at": "2026-07-09T12:00:00Z"
    }
  }
}
```

| Field | Purpose |
|-------|---------|
| `project` | Jira project key (for JQL fallback / validation) |
| `changes.<change>.epic` | Epic key — included in PR **Related Work Item** |
| `changes.<change>.stories."N"` | Optional Story key for section **N** |
| `changes.<change>.tasks."N.M"` | Sub-task key for checkbox **N.M** |

**Creation:** When exporting from OpenSpec, write each sub-task key returned by Jira MCP into `changes.<change>.tasks` as issues are created. Merge into the existing repo-root file if it already exists. Commit the JSON dump to the repo.

**Without this file:** milestone commands skip Jira transitions and only mention keys if present in commit/PR text.

**Required labels on every Jira issue:**
- `<repo-name>` — e.g. `notifications-hub`
- `<spec-title>` — e.g. `notification-ingestion` (capability folder name)

**In Jira description footer:**
  ```
  OpenSpec: openspec/changes/notification-platform/specs/notification-ingestion/spec.md
  ```

**In OpenSpec** (optional, in `tasks.md` or commit messages):
- `JIRA: NH-10` on related task lines

**In PRs:**
- `NH-10` in title/body links code → Story

## Sprint Planning by Phase

| Sprint | tasks.md sections | Focus |
|--------|-------------------|-------|
| 1 | §1, §2, §3 | Scaffolding + observability foundation |
| 2 | §4–§7 | Auth, templates, GraphQL ingestion |
| 3 | §8–§10 | Outbox, Temporal, channels |
| 4 | §11–§14 | Delivery tracking, dashboard, tests, deploy |

## Summary

For `notification-platform`:

- **1 Epic** = the change
- **9 Stories** = 9 capability specs
- **AC** = Requirements + Scenarios from each spec
- **Sub-tasks** = `tasks.md` checkboxes (72 items)
- **Confluence** = `design.md`
- **Labels/links** = `notifications-hub` + capability name on every issue; OpenSpec paths in descriptions
