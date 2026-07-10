# Architecture Decision Records (ADRs)

This repository uses ADRs to capture architecture decisions by area.

## Structure

- `docs/adr/backend/` — API, database, Temporal, and integration decisions
- `docs/adr/web/` — frontend and UX decisions

Numbering is local to each area (`0001-short-title.md`, `0002-short-title.md`, …).

## Status Values

`Proposed` · `Accepted` · `Rejected` · `Superseded`

## Minimal Template

```markdown
# ADR-0001: Title

## Status

Proposed

---

# Context

- Why this decision is needed

---

# Decision

- What was decided

---

# Consequences

## Positive

- Benefit

## Negative

- Trade-off
```

Add accepted ADRs as features are implemented. OpenSpec design decisions in `openspec/changes/notification-platform/design.md` may be promoted into ADRs when stabilized.
