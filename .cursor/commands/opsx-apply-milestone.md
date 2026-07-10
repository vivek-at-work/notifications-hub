---
name: /opsx-apply-milestone
id: opsx-apply-milestone
category: Workflow
description: Implement scoped tasks.md sections on a feature branch, then prepare a PR checkpoint
---

Implement a **scoped slice** of an OpenSpec change on a dedicated git branch, then stop and prepare a pull request. Scope is expressed with **`only`**, **`until`**, **`from`/`to`**, or an explicit **section list**.

**Related:** Unbounded implementation → `/opsx-apply`. Archive when all tasks done → `/opsx-archive`.

**Store selection:** Same as `/opsx-apply` — pass `--store <id>` on OpenSpec read/write commands when the change lives in a registered store.

---

## Scope modes (combine change name + one scope expression)

Parse the user message into: **change name**, **scope mode**, **section number(s)**, and optional flags.

| Mode | Syntax examples | Tasks included |
|------|-----------------|----------------|
| **`only`** | `only 6`, `§6 only`, `section 6 only` | Pending tasks in **§N only** |
| **`until`** | `until 6`, `through 6`, `up to §6` | Pending tasks in **§1 … §N** (all sections from the start through N) |
| **`from` … `to`** | `from 4 to 6`, `from 4 until 6`, `§4-6`, `4..6` | Pending tasks in **§A … §B** inclusive |
| **`specific`** | `specific 3,5,6`, `sections 3 5 6`, `§3 §5 §6` | Pending tasks in **listed sections only** (execution order = numeric) |
| **Shorthand** | `6` (bare number) | Same as **`only 6`** |
| **PR prep only** | `checkpoint`, `pr only`, `prepare pr` | No implementation — verify tests + draft PR for current branch/work |

**Defaults when omitted:**

| Input missing | Default |
|---------------|---------|
| Change name | Infer from context; if ambiguous → `openspec list --json` + ask |
| Scope mode | **`only`** if a single section number is given |
| Base branch | `main` / `master` from `origin/HEAD` or ask |
| Branch name | Auto-generate from scope (see below) |
| Create PR | **No** — draft only unless user says `push pr` / `create pr` |
| Jira sync | **Yes** if `jira-mapping.json` exists at repo root with an entry for the change; skip with notice if missing. Opt out with `--no-jira` |

### Examples (all valid)

```text
/opsx-apply-milestone notification-platform only 6
/opsx-apply-milestone notification-platform until 6
/opsx-apply-milestone notification-platform from 4 to 6
/opsx-apply-milestone notification-platform from 4 until 6
/opsx-apply-milestone notification-platform specific 3,5,6
/opsx-apply-milestone notification-platform sections 2 3
/opsx-apply-milestone notification-platform 4-6
/opsx-apply-milestone notification-platform 6 --base main
/opsx-apply-milestone notification-platform until 6 --branch feat/nh/m1-foundation
/opsx-apply-milestone notification-platform checkpoint until 6
/opsx-apply-milestone notification-platform only 7 --no-jira
```

Always announce parsed scope:

```text
Using change: <name>
Scope: <mode> — §… (titles)
Branch: <branch>
Jira: <N sub-tasks from jira-mapping.json, or "skipped — no mapping">
```

---

## Jira sync at milestone start

When Jira sync is enabled (default), **before any implementation (step 5)** the command **must**:

1. Read `<repo-root>/jira-mapping.json`
2. Resolve Jira keys for **every `N.M` task id in the milestone scope**
3. Transition matching issues to the correct **start-of-work** status via Jira MCP

This runs in **step 4b** immediately after the scope summary and branch setup — never deferred until checkpoint.

**Do not** guess Jira keys from task text or prior chat. **Only** use keys from `jira-mapping.json` → `changes.<change-name>`.

---

## Milestone = tasks.md section

Sections are `## N. Title` headers in the change's `tasks.md`.

- Work **only** on unchecked tasks (`- [ ]`) inside the resolved scope
- Mark each completed task: `- [ ]` → `- [x]`
- **Never** implement tasks outside the resolved scope

**Resolve scope algorithm:**

1. Parse `tasks.md` — build ordered list of sections `{ n, title, tasks[] }`.
2. Apply mode:
   - **`only N`** → `[N]`
   - **`until N`** → `[1..N]`
   - **`from A to B`** → `[A..B]` (require A ≤ B; else ask)
   - **`specific`** → sorted unique list (must exist in file)
3. Filter to sections that have **at least one** `- [ ]` task, unless user asked for **`checkpoint`** / **`pr only`** (then include completed sections for summary only).

If scope is empty (all tasks in range already `[x]`), report completion and offer: widen scope, next section, or PR checkpoint.

---

## Branch naming

Auto-generate from change + scope:

| Scope | Branch pattern |
|-------|----------------|
| `only 6` | `feat/<change>/milestone-6-<short-slug>` |
| `until 6` | `feat/<change>/milestone-until-6` |
| `from 4 to 6` | `feat/<change>/milestone-4-6` |
| `specific 3,5,6` | `feat/<change>/milestone-3-5-6` |

`<short-slug>` = kebab-case from section title (≤30 chars). User override: `--branch <name>`.

---

## Steps

### 1. Select change and parse scope

Same as `/opsx-apply` step 1 for change selection.

Parse scope mode + section(s) from the user message. If mode or sections are ambiguous, use **AskQuestion** with options:

- Only §N
- Until §N (§1–§N)
- From §A to §B
- Specific sections (user lists numbers)

Read `tasks.md` and validate every section number exists.

### 2. OpenSpec context

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

Read all `contextFiles`. If `state: "blocked"`, stop and suggest `/opsx-continue`.

### 3. Git — create or verify branch

**Before any code changes** (skip if `checkpoint` / `pr only` and user only wants PR draft):

```bash
git status
git branch --show-current
git fetch origin
```

Create or checkout the scope branch from `<base-branch>` unless already on the intended branch.

**Guardrails:**

- Do **not** commit, push, or open a PR unless the user explicitly asks
- No destructive git commands
- Uncommitted work on the wrong branch → stop and ask (stash / commit / abort)

### 4. Show scope summary

Display:

- Schema name
- **Scope mode** and **section list** with titles (e.g. `until 6 → §1–§6: Scaffolding … Template Management`)
- Per-section: complete / remaining task counts
- Branch name
- Overall change progress: `X/Y` tasks

- Branch name
- Overall change progress: `X/Y` tasks
- **Jira (preview):** count of scoped `N.M` ids with keys in `jira-mapping.json`; list unmapped ids if any

If **`checkpoint`** / **`pr only`**: skip to step 6 (no step 5). Still run **step 4b** if Jira sync is enabled and user did not pass `--no-jira`.

### 4b. Jira — resolve keys and transition at milestone start

**Timing:** Run this step **once per invocation**, after step 4 (scope summary) and step 3 (branch), **before step 5 (implementation)**. This is the milestone **start** Jira sync.

Sync Jira issue status with the milestone scope using keys from the repo-root mapping dump and Jira MCP.

**Skip this step when:**

- User passed **`--no-jira`**
- `<repo-root>/jira-mapping.json` is missing (announce: *Jira sync skipped — jira-mapping.json not found*)
- `jira-mapping.json` exists but has no `changes.<change-name>` entry (announce: *Jira sync skipped — no mapping entry for `<change-name>`*)
- Jira MCP is unavailable or not authenticated (announce and continue implementation)
- Mode is **`checkpoint`** / **`pr only`** and user only wants a PR draft (unless they asked to sync Jira status)

#### 4b.1 Load mapping file

From the **git repository root** (not the change folder):

```bash
# Path (always repo root)
jira-mapping.json
```

Parse JSON. Navigate to:

```
changes.<change-name>.tasks     # required for sub-task sync
changes.<change-name>.stories   # optional — Story per tasks.md §N
changes.<change-name>.epic      # optional — for PR Related Work Item only
```

If JSON is invalid, announce the parse error and skip Jira sync (do not block implementation).

#### 4b.2 Resolve Jira keys for this milestone scope

1. From the resolved scope (step 1), collect every **`N.M` task id** in included sections (e.g. `only 7` → `7.1`, `7.2`, … `7.8`; `until 6` → all ids in §1–§6).
2. For each `N.M`, look up `changes.<change-name>.tasks["N.M"]` in `jira-mapping.json`.
3. Build two lists:
   - **`mapped`:** `{ taskId, jiraKey }` for ids with a key
   - **`unmapped`:** task ids in scope with no key in the file
4. Optionally resolve **Story** keys for scoped section numbers: `changes.<change-name>.stories["N"]` for each section `N` in scope.

Report before transitioning:

```text
Jira mapping (notification-platform, only §8):
  Mapped:   8.1→DQH-301, 8.2→DQH-302, …
  Unmapped: (none) | 8.4 (no key in jira-mapping.json)
  Stories:  §8→DQH-160
```

Unmapped ids are **warnings only** — continue implementation.

#### 4b.3 Transition to start-of-work status (milestone start)

For each entry in **`mapped`** whose `tasks.md` checkbox is still `- [ ]`:

1. Call **`jira_get_transitions`** for `jiraKey`
2. Call **`jira_transition_issue`** using the first transition whose name matches (case-insensitive):
   - **In Progress** (preferred)
   - **In Development**
   - **Started**
   - **Active**
3. Log: `DQH-301 (8.1) → In Progress`

**Story (optional, same milestone start):** For each scoped section `N` with a `stories["N"]` key, if the Story is not already In Progress, transition it using the same name-matching rules. Log: `DQH-160 (§8 Story) → In Progress`.

**Do not** transition Epic automatically unless the user explicitly asks.

Run transitions **one issue at a time**. If a transition fails (already In Progress, wrong workflow, permission error), log the outcome and **continue** with remaining keys.

**Already Done in Jira:** If the issue is already Done/Closed/Resolved, skip the In Progress transition and log: `DQH-301 (8.1) → skipped (already Done)`.

#### 4b.4 Mapping file reference

**File:** `<repo-root>/jira-mapping.json`

```json
{
  "version": 1,
  "repo": "notifications-hub",
  "project": "DQH",
  "changes": {
    "notification-platform": {
      "epic": "DQH-144",
      "stories": { "8": "DQH-160" },
      "tasks": {
        "8.1": "DQH-301",
        "8.2": "DQH-302"
      }
    }
  }
}
```

See [openspec-jira-mapping](../../skills/openspec-jira-mapping/reference.md#jira-mappingjson-repo-root) for format and creation workflow.

#### 4b.5 During implementation (step 5)

When marking a checkbox `- [x]` in `tasks.md`, if that `N.M` has a key in `jira-mapping.json`:

1. Call **`jira_get_transitions`** then **`jira_transition_issue`** → **Done** (or **Closed** / **Resolved** — match project workflow)
2. Log: `DQH-301 (8.1) → Done`

#### 4b.6 At checkpoint (step 6)

- Confirm all completed in-scope mapped sub-tasks are **Done** in Jira (idempotent — skip if already Done)
- Include **Epic**, **Story**, and **sub-task** keys in the PR checkpoint under **Related Work Item** from `jira-mapping.json`
- Summarize Jira activity: keys moved In Progress at start, keys moved Done during session

### 5. Implement scoped tasks

Walk sections **in numeric order** within the resolved scope.

For each pending task:

```
Working on §N — task N.M: <description>
[...implementation...]
✓ Task complete
```

Follow `/opsx-apply` guardrails: minimal diffs, mark checkboxes immediately, pause on ambiguity/errors.

**Stop when:**

- All pending tasks in scope are `[x]`, or
- Blocker / user interrupt, or
- Next pending task falls **outside** scope (do not start it)

**Mode-specific stop rules:**

| Mode | Stop after |
|------|------------|
| `only N` | §N complete |
| `until N` | §N complete (§1…§N all done) |
| `from A to B` | §B complete |
| `specific` | Every listed section complete |

### 6. Milestone checkpoint — verify and prepare PR

Run test command(s) for touched areas. Report pass/fail with evidence. **Do not claim success without running tests.**

Output:

```markdown
## Milestone complete — PR checkpoint

**Change:** <name>
**Scope:** <mode> — §… (titles)
**Branch:** <branch>
**Scope progress:** <complete>/<total> tasks in scope
**Overall progress:** <X>/<Y> tasks in change
**Jira:** <keys moved In Progress, or "skipped">

### Completed this session
- [x] <task ids/descriptions by section>
- Jira Done: <KEY (N.M), …> (if synced)

### Test results
<command + outcome>

### Suggested PR
**Title:** feat(<scope>): <description> (<change> <scope-label>)
**Base:** <base-branch>

## Summary
- ...

## Related Work Item
- Issue/Ticket: <Epic KEY>
- Requirement/Story: <Story KEY for scoped section(s)>
- Sub-tasks: <list completed keys>

## Test plan
- [ ] ...

### Next steps
1. **Commit** — ask me to commit
2. **Push + PR** — ask me to push and `gh pr create`
3. **Next scope** — after merge, e.g. `/opsx-apply-milestone <change> only 7` or `until 8`
4. **Pause** — keep branch as-is
```

**Scope label in PR title examples:**

- `only 6` → `(§6)`
- `until 6` → `(§1–§6)`
- `from 4 to 6` → `(§4–§6)`
- `specific 3,5,6` → `(§3,§5,§6)`

If user explicitly requested PR creation, follow **creating-pull-requests** rules. Otherwise draft only.

### 7. Resume after merge

Next invocation uses a **new branch from updated base** with the next scope (e.g. after `until 6` merges → `only 7` or `until 8`).

---

## Output during implementation

```
## Scope: only §8 (change: notification-platform)
Branch: feat/notification-platform/milestone-8-transactional-outbox-sqs
Sections: §8

Jira (milestone start):
  8.1→DQH-301 In Progress, 8.2→DQH-302 In Progress, …
  §8 Story DQH-160 → In Progress

Working on §8 — task 8.1: Implement outbox write in NotificationService...
✓ Task complete — DQH-301 → Done
```

---

## Guardrails

- **Respect parsed scope** — never implement tasks outside it
- **Branch first** — before code (except `checkpoint` / `pr only`)
- **No silent git** — no commit/push/PR without explicit request
- **Tests before checkpoint**
- **Jira sync (optional)** — when `<repo-root>/jira-mapping.json` has `changes.<change>` and not `--no-jira`:
  - **Milestone start (step 4b, before code):** load mapping → resolve scoped `N.M` keys → pending sub-tasks → **In Progress**; optional Story per scoped §N → **In Progress**
  - **Each completed checkbox (step 5):** mapped sub-task → **Done**
  - **Checkpoint (step 6):** confirm Done; list Epic/Story/sub-task keys in PR draft
  - Never invent keys — only `jira-mapping.json`
- Include story key in PR when known from mapping or `openspec-jira-mapping`

---

## Scope cheat sheet

```text
only 6          →  §6
until 6         →  §1 + §2 + … + §6
from 4 to 6     →  §4 + §5 + §6
specific 3,5,6  →  §3 + §5 + §6  (not §4)
6               →  only §6 (shorthand)
checkpoint …    →  no code; PR draft for current work in scope
```

(Use `openspec/changes/<name>/tasks.md` as source of truth for section titles and task lists.)
