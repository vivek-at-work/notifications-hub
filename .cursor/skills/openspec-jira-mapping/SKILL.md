---
name: openspec-jira-mapping
description: Maps OpenSpec change artifacts (proposal, design, specs, tasks) to Jira Epics, Stories, sub-tasks, and Confluence pages. Use when exporting an OpenSpec change to Jira, creating backlog items from openspec/changes/, syncing planning artifacts to Atlassian, or when the user asks how OpenSpec maps to Jira.
license: MIT
compatibility: Requires openspec CLI. Jira MCP optional for issue creation.
---

# Mapping OpenSpec Artifacts to Jira

OpenSpec and Jira serve different layers of the same work. OpenSpec is your planning + requirements + implementation contract in git; Jira is your delivery tracker for sprints, ownership, and status. There is no built-in sync in this repo — the mapping is a convention you define.

## When to Use

- OpenSpec change artifacts are complete (`proposal`, `design`, `specs`, `tasks`)
- User asks to create Jira backlog from an OpenSpec change
- User asks how OpenSpec artifacts map to Jira

## Prerequisites

1. Resolve the change: `openspec status --change "<name>" --json`
2. Read artifacts from `changeRoot` / `artifactPaths` in the status JSON
3. **Ask the user for Jira details** — do **not** run project-intelligence or discover project metadata automatically
4. For issue creation: draft → user approval → create via Jira MCP

## Workflow

Copy this checklist and track progress:

```
- [ ] Step 0: Ask user for Jira details
- [ ] Step 1: Read OpenSpec change artifacts
- [ ] Step 2: Create Epic from proposal.md
- [ ] Step 3: Publish design.md to Confluence (link from Epic)
- [ ] Step 4: Create Stories from Capabilities (specs/)
- [ ] Step 5: Map Requirements/Scenarios to Story AC
- [ ] Step 6: Create sub-tasks from tasks.md checkboxes
- [ ] Step 7: Apply traceability labels and links
- [ ] Step 8: Write or update `jira-mapping.json` at the repo root with epic, story, and sub-task keys
```

### Step 0 — Ask user for Jira details

Do **not** run project-intelligence. Ask the user directly and wait for answers before creating issues.

Ask **one question at a time**. Use selectable options when the answer is bounded; use free text when it is open-ended.

Collect at minimum:

| Field | Example question |
|-------|------------------|
| **Project key** | "Which Jira project key should I use? (e.g. NH, PROJ)" |
| **Epic issue type** | "Which issue type for the Epic?" — Epic / Initiative / other |
| **Story issue type** | "Which issue type for Stories?" — Story / Task |
| **Sub-task issue type** | "Which issue type for sub-tasks?" — Sub-task / Task |
| **Components** | "Which Jira component(s) should these issues use?" (optional) |
| **Extra labels** | "Any additional labels besides repo name and spec title?" (optional) |
| **Priority** | "Default priority for Stories?" — Highest / High / Medium / Low |
| **Confluence space** | "Confluence space key for design.md?" (optional, if publishing design) |
| **Parent Epic key** | "Link under an existing Epic?" — provide key or skip |

Do not invent or guess project keys, components, or labels. If the user skips optional fields, proceed without them.

Only continue to Step 1 after required fields (project key, issue types) are confirmed.

Derive the **repo name** from the git repository root directory (e.g. `notifications-hub`). If unclear, ask the user once in Step 0.

### Required labels on every Jira issue

Every Epic, Story, and sub-task **must** include these two labels:

| Label | Source | Example |
|-------|--------|---------|
| **Repo name** | Git repo root directory name (or user override from Step 0) | `notifications-hub` |
| **Spec title** | OpenSpec capability folder name under `specs/` | `notification-ingestion` |

**Spec title by issue type:**

| Jira issue | Spec title label |
|------------|------------------|
| **Epic** | Change name (same as `openspec/changes/<change-name>/`) | `notification-platform` |
| **Story** | Capability folder name from `specs/<capability>/spec.md` | `multi-tenancy` |
| **Sub-task** | Same spec title as its parent Story | `notification-ingestion` |
| **Foundation Story** (no spec file) | Use `tasks.md` section slug or change name | `platform-scaffolding` |

Use the raw kebab-case value as the Jira label (no prefix). Also apply any extra labels the user provided in Step 0.

**Example labels on a Story:**

```
notifications-hub, notification-ingestion
```

### Step 1 — Read OpenSpec change

```bash
openspec status --change "<name>" --json
```

Read:
- `proposal.md` — Epic description
- `design.md` — Confluence content
- `specs/<capability>/spec.md` — one Story per capability
- `tasks.md` — sub-tasks

### Step 2 — Create Epic

Use the **project key** and **Epic issue type** from Step 0.

From `proposal.md`:
- **Summary:** Change name in title case (e.g. "Notification Platform")
- **Description:** Why, What Changes, Impact sections
- **Labels:** `<repo-name>`, `<change-name>` (spec title for Epic)

### Step 3 — Confluence from design.md

Publish `design.md` to Confluence. Link from Epic description. Do not paste full design into Jira.

### Step 4 — Stories from Capabilities

Use the **Story issue type**, **priority**, **components**, and **extra labels** from Step 0.

One Story per capability listed in `proposal.md` → `specs/<capability>/spec.md`.

**Labels on each Story:** `<repo-name>`, `<capability>` (spec title from folder name).

Foundation work in `tasks.md` with no spec (e.g. monorepo scaffolding) → separate Story under Epic.

### Step 5 — Acceptance Criteria from specs

For each `### Requirement:` block → AC group heading.
For each `#### Scenario:` block → AC bullet (WHEN/THEN → Given/When/Then).

### Step 6 — Sub-tasks from tasks.md

Use the **Sub-task issue type** from Step 0.

Each `- [ ] N.M` checkbox → Jira sub-task under the matching Story.

**Labels on each sub-task:** `<repo-name>`, `<capability>` (same spec title as parent Story).

Include traceability footer: `openspec: <change>/tasks.md#N.M`

### Step 7 — Traceability

**Required labels on every issue:**
- `<repo-name>` — git repository name
- `<spec-title>` — change name (Epic), capability name (Story/sub-task)

**Optional labels** (if user provided in Step 0): e.g. `openspec:<change-name>`, team tags

**Jira description footer:**
```
OpenSpec: openspec/changes/<change>/specs/<capability>/spec.md
```

**Optional in OpenSpec/commits/PRs:** `JIRA: <KEY>`

## Recommended Hierarchy

```
OpenSpec                              Jira
─────────────────────────────────────────────────────────────
Change: notification-platform    →    Epic (or Initiative → Epic)
  proposal.md                    →    Epic description (Why / What / Impact)
  design.md                      →    Confluence page OR Epic "Technical Design" section
  specs/<capability>/spec.md     →    Story (one per capability)
    Requirement                  →    Acceptance Criteria heading
    Scenario                     →    AC bullet / BDD test case
  tasks.md ## N. Section          →    Story or Task (optional grouping)
  tasks.md - [ ] N.M item        →    Sub-task
```

Visually:

```
┌─────────────────────────────────────────────────────────────┐
│  JIRA EPIC: Notification Platform                           │
│  (from proposal.md)                                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ STORY            │  │ STORY            │                 │
│  │ notification-    │  │ multi-tenancy    │                 │
│  │ ingestion        │  │ (spec)           │                 │
│  │                  │  │                  │                 │
│  │ AC ← Requirements│  │ AC ← Requirements│                 │
│  │   ← Scenarios    │  │   ← Scenarios    │                 │
│  ├──────────────────┤  ├──────────────────┤                 │
│  │ Sub-task ← 7.1   │  │ Sub-task ← 5.1   │                 │
│  │ Sub-task ← 7.2   │  │ Sub-task ← 5.2   │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                             │
│  Confluence ← design.md (architecture, decisions, risks)  │
└─────────────────────────────────────────────────────────────┘
```

## Artifact-by-Artifact Mapping

| OpenSpec artifact | Jira artifact | What to copy / link |
|-------------------|---------------|---------------------|
| **Change** (`notification-platform/`) | **Epic** | Epic title: "Notification Platform". Labels: `<repo-name>`, `<change-name>` |
| **proposal.md → Why** | Epic **Description** (Problem) | 1–2 sentence motivation |
| **proposal.md → What Changes** | Epic **Description** (Scope) | Bullet list of deliverables |
| **proposal.md → Capabilities** | Epic **child Stories** | One Story per capability name |
| **proposal.md → Impact** | Epic **Description** (Impact) or Risks section | Infra, deps, systems affected |
| **design.md** | **Confluence page** linked from Epic | Goals, decisions, architecture diagram, risks. Too long for Jira fields |
| **design.md → Decisions** | Story **Technical notes** or **Spike** (if unresolved) | e.g. "Decision: Temporal + SQS" |
| **design.md → Open Questions** | **Spike** or Epic blockers | Each question → Spike if research needed |
| **specs/*/spec.md** | **Story** (per capability) | Story title = capability name in human form. Labels: `<repo-name>`, `<capability>` |
| **Requirement:** blocks | Story **Acceptance Criteria** | One AC group per requirement |
| **Scenario:** blocks | AC bullets or **Test sub-tasks** | WHEN/THEN → Given/When/Then |
| **tasks.md → ## N. heading** | **Story** or **Task** | Optional: merge with matching capability Story |
| **tasks.md → N.M checkbox** | **Sub-task** | Direct 1:1 mapping; assignable, estimable. Labels: `<repo-name>`, parent Story spec title |
| **tasks.md → ## 13. Testing** | Sub-tasks under each Story OR separate **Test task** | Don't orphan testing at Epic level only |
| **tasks.md → ## 14. Documentation** | **Task** / **Sub-task** | ADRs, K8s manifests |

## What Goes Where (Field Guide)

| Content | Best home |
|---------|-----------|
| Business motivation | Epic description |
| Architecture diagrams | Confluence (link from Epic) |
| Technical decisions & trade-offs | Confluence or Epic "Technical approach" |
| Testable behavior (SHALL/MUST) | Story Acceptance Criteria |
| Implementation steps | Sub-tasks |
| Definition of Done | Epic or Story template |
| ADR references | Sub-task or Confluence |

**Rule of thumb:** If QA can verify it → **Story AC**. If a dev needs a checklist → **Sub-task**. If architects need context → **design.md / Confluence**.

## Suggested Creation Order

1. Epic from `proposal.md`
2. Confluence from `design.md` (link to Epic)
3. Stories from Capabilities list
4. Paste Requirements/Scenarios into each Story's AC
5. Sub-tasks from `tasks.md` checkboxes
6. Sprint planning by phase (see [reference.md](reference.md))

## Mapping Patterns to Avoid

| Don't | Do instead |
|-------|------------|
| One Epic sub-task per Scenario | Group scenarios under Story AC |
| Paste entire `design.md` into Jira | Confluence + link |
| One giant Story for all tasks | Split by capability or task section |
| Duplicate spec text in every sub-task | Sub-tasks reference Story AC |
| Create Jira before OpenSpec is stable | Propose in OpenSpec first, then export to Jira |

### Step 8 — Write `jira-mapping.json` (repo root)

After creating Jira issues, persist a **machine-readable dump** at the **repository root**:

```
<repo-root>/jira-mapping.json
```

This file is the single source of truth for OpenSpec task ↔ Jira key mappings across all changes in the repo. **Commit it** after each export or when new sub-tasks are created.

**When to update:**

- After Step 6–7 (initial export) — add a `changes.<change-name>` entry
- When additional sub-tasks are created later — merge new keys into `tasks`
- When a Story or Epic key changes — update in place and bump `updated_at`

**Do not** scatter per-change YAML files under `openspec/changes/`. Use only the repo-root JSON dump.

**Schema:**

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
| `version` | Schema version (currently `1`) |
| `repo` | Git repository directory name |
| `project` | Default Jira project key used for this export |
| `changes.<change>` | One object per OpenSpec change name |
| `changes.<change>.epic` | Epic key |
| `changes.<change>.stories."N"` | Optional Story key for `tasks.md` §N |
| `changes.<change>.tasks."N.M"` | Sub-task key for checkbox N.M |
| `created_at` / `updated_at` | ISO-8601 timestamps (UTC) |

**Merge rules:**

1. Read existing `jira-mapping.json` if present; otherwise start with `{ "version": 1, "repo": "<name>", "project": "<key>", "changes": {} }`.
2. Set or replace `changes.<change-name>` for the current export.
3. Preserve other `changes.*` entries untouched.
4. Write pretty-printed JSON (2-space indent) and commit with the mapping export.

`/opsx-apply-milestone` reads `jira-mapping.json` → `changes.<change>.tasks` for Jira status sync.

## Two-Way Status Sync

| When | OpenSpec | Jira |
|------|----------|------|
| Planning done | Artifacts complete | Epic + Stories created; write `jira-mapping.json` |
| Milestone starts | `/opsx-apply-milestone` scope resolved | Mapped sub-tasks in scope → **In Progress** |
| Dev finishes item | `- [x]` in `tasks.md` | Mapped sub-task → **Done** |
| Story AC met | Spec scenarios pass in tests | Story → Done (manual or separate workflow) |
| Change shipped | `openspec archive` | Epic → Done |

Use **`--no-jira`** on `/opsx-apply-milestone` to skip transitions.

## Additional Resources

- Concrete example (`notification-platform`): [reference.md](reference.md)
