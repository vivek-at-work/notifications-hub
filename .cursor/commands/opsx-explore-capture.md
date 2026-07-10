---
name: /opsx-explore-capture
id: opsx-explore-capture
category: Workflow
description: "Explore ideas and maintain a refined living discussion doc for the team"
---

Explore mode with **living documentation**. Think deeply like `/opsx-explore`, but continuously refine a shared doc others can read — without dumping the raw chat.

**IMPORTANT: Explore mode is for thinking, not implementing.** You may read files, search code, and investigate the codebase, but you must NEVER write application code or implement features. Updating the exploration doc in `docs/exploration/` **is allowed** — that is capturing thinking, not implementing.

**This extends `/opsx-explore`.** Follow all explore-mode stance, guardrails, and OpenSpec awareness from that command. The difference: after each meaningful exchange, **synthesize and update** the exploration doc.

---

## Input

The argument after `/opsx-explore-capture` is:

- **Topic slug** (kebab-case), e.g. `notification-platform` — preferred
- **Description**, e.g. `centralized notification microservice` — derive a slug from it
- **Nothing** — ask once for topic/slug, or infer from the current conversation if obvious

If the user continues an existing topic in a new session, reuse the same slug and read the existing doc first.

---

## Document Location

Each exploration lives in its own folder:

```
docs/exploration/
├── README.md                          # index of all explorations (maintain lightly)
└── <topic-slug>/
    └── discussion.md                  # the living, refined doc
```

**Paths:**
- Doc: `docs/exploration/<topic-slug>/discussion.md`
- Index: `docs/exploration/README.md`

On first use for a slug, create the folder and `discussion.md` from the template below. Add or update a row in the index README.

---

## The Refinement Rule (Critical)

**Do NOT append the chat transcript.** Each update is a **rewrite of truth**, not a log dump.

Before writing:

1. **Read** the existing `discussion.md` (if any).
2. **Extract** only durable insights from the latest exchange:
   - new decisions, changed decisions, clarified requirements
   - architecture that held up under scrutiny
   - questions answered vs still open
   - options explored and rejected (with brief why)
3. **Merge** into the doc:
   - update sections in place
   - remove or move to **Explored & Rejected** anything superseded
   - shorten redundant prose — prefer one clear paragraph over three overlapping ones
4. **Append** one short line to **Refinement log** (what changed this turn, not what was said verbatim).

If a decision reverses an earlier one, **delete the old claim** from active sections and note the reversal in Refinement log + Explored & Rejected if useful.

If nothing materially changed this turn (pure clarifying question, "yes continue", etc.), **skip the doc update** and say so briefly.

---

## Document Template

Use this structure for `discussion.md`. Omit empty sections; do not leave placeholder fluff.

```markdown
# Exploration: {Human-readable title}

| Field | Value |
|-------|-------|
| **Slug** | `{topic-slug}` |
| **Status** | `active` \| `ready-for-proposal` \| `archived` |
| **Last updated** | {YYYY-MM-DD} |
| **Related change** | `{openspec-change-name}` or _none yet_ |

## Summary

{2–4 paragraphs. Current best understanding. A new reader should grasp the problem and direction here alone.}

## Goals

- {bullet}

## Non-goals

- {bullet — explicit scope boundaries}

## Constraints & Context

- {stack, org, compliance, existing systems — only what matters}

## Key Decisions

| Decision | Rationale | Status |
|----------|-----------|--------|
| {e.g. Temporal for orchestration} | {why} | `accepted` |

## Architecture & Design

{Diagrams, flows, components — refined over time. Replace outdated diagrams; don't stack duplicates.}

## Open Questions

- [ ] {unresolved item}

## Explored & Rejected

| Option | Why rejected |
|--------|--------------|
| {e.g. Celery for retries} | {Temporal already chosen for scheduling + durable state} |

## OpenSpec Handoff

{When ready: which capabilities, change name, or artifacts to create. Leave empty while still exploring.}

## Refinement Log

| Date | Change |
|------|--------|
| {YYYY-MM-DD} | {one line: e.g. "Initial doc from notification platform architecture exploration"} |
```

---

## Index README (`docs/exploration/README.md`)

Keep a simple table. Create on first exploration if missing:

```markdown
# Exploration Discussions

Living design notes from `/opsx-explore-capture` sessions. Read `discussion.md` in each folder — not chat logs.

| Slug | Title | Status | Last updated |
|------|-------|--------|--------------|
| `{slug}` | {title} | active | {date} |
```

Update the row when the doc changes. Do not duplicate doc content in the index.

---

## Session Flow

### 1. Resolve topic

- Parse slug from input or ask once.
- Ensure `docs/exploration/<slug>/` exists; read `discussion.md` if present.

### 2. Explore (same as `/opsx-explore`)

- Curious, visual, grounded in codebase when relevant.
- Run `openspec list --json` at start if OpenSpec context may apply.
- Store selection: same rules as `/opsx-explore` when using OpenSpec CLI.

### 3. Refine doc (when the turn added substance)

- Apply the Refinement Rule above.
- Write `discussion.md`.
- Touch `docs/exploration/README.md` only if slug is new or status/date changed.

### 4. Respond to the user

- Continue the exploration conversation normally.
- End with a brief **Doc sync** line when you updated the file, e.g.:
  - _Doc sync: updated `docs/exploration/notification-platform/discussion.md` — added Temporal workflow design, closed push token question._
- If skipped: _Doc sync: no update this turn (no new decisions)._

---

## Status Transitions

| Status | Meaning |
|--------|---------|
| `active` | Still exploring; doc may change significantly |
| `ready-for-proposal` | Team agrees direction is solid; suggest `/opsx-propose` |
| `archived` | Superseded by OpenSpec change or abandoned; link to `openspec/changes/...` if applicable |

Offer status changes; do not flip to `ready-for-proposal` without user agreement.

---

## OpenSpec Relationship

| Insight type | Exploration doc | OpenSpec (later) |
|--------------|-------------------|------------------|
| Brainstorming the problem space | Summary, Goals | `proposal.md` |
| Design choice | Key Decisions, Architecture | `design.md` |
| Requirement | Goals, Open Questions | `specs/.../spec.md` |
| Implementation work | OpenSpec Handoff | `tasks.md` |

The exploration doc is **pre-proposal thinking**. When the user runs `/opsx-propose`, the doc is source material — not a substitute for OpenSpec artifacts.

Optionally set **Related change** in the doc when a change is created.

---

## Guardrails

Everything from `/opsx-explore`, plus:

- **Do refine, don't dump** — no chat transcripts, no turn-by-turn Q&A paste
- **Do supersede** — remove stale content when decisions change
- **Do keep Summary truthful** — it must match Key Decisions and Architecture
- **Do stay concise** — shorter and accurate beats long and redundant
- **Don't create application code** — only `docs/exploration/**` and index README
- **Don't auto-propose** — offer `/opsx-propose` when status is `ready-for-proposal`
- **Do visualize** — carry diagrams forward into the doc when they clarify architecture

---

## Example

```
/opsx-explore-capture notification-platform
```

First turn: user describes a centralized notification microservice → explore architecture → create `docs/exploration/notification-platform/discussion.md` with Summary, Goals, initial Architecture diagram, Open Questions.

Second turn: user picks Temporal over Celery → update Key Decisions, add Celery to Explored & Rejected, trim Architecture section, one Refinement log line.

Third turn: user asks about rate limiting → add Open Question; if no decision yet, do not add to Key Decisions.

When exploration feels complete → set Status to `ready-for-proposal` (with user OK) → OpenSpec Handoff lists suggested change name and capabilities.
