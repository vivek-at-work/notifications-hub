---
name: repo-bootstrap
description: Initializes the current folder as a git repository with main, development, and stage branches, lists GitHub orgs for owner selection, creates the GitHub repo with gh, scaffolds CODEOWNERS and the GitHub PR template, applies branch protection blocking direct pushes, commits, pushes, and opens Cursor. Use when bootstrapping a new repo, running repo bootstrap, or initializing git and GitHub for the current directory.
---

# Repo Bootstrap

## Overview

Initialize the current folder as a git repository, create the matching GitHub repository with `gh`, add **`.github/CODEOWNERS`** (current user owns every top-level folder explicitly) and **`.github/PULL_REQUEST_TEMPLATE.md`**, create **main**, **development**, and **stage** branches with **no direct push** allowed on any of them, and open the result in Cursor.

## Core rules

- Use the current folder name as the repository name.
- Never ask for a separate project name.
- Never create a new folder for the project.
- **Default branches:** `main`, `development`, `stage` — create all three on every bootstrap unless the user explicitly opts out.
- **Branch protection:** apply to `main`, `development`, and `stage` so direct pushes are blocked; changes must go through pull requests.
- **CODEOWNERS:** create `.github/CODEOWNERS` with the authenticated GitHub user as owner of every top-level directory except `.git`, `.venv`, `node_modules`, and `.nx` (see [reference.md](reference.md)) before branch protection and the initial commit.
- **Git ignore:** create or update root `.gitignore` from [reference.md](reference.md) so dependency and cache directories (including `.venv`, `node_modules`, and `.nx`) are never tracked.
- **PR template:** create `.github/PULL_REQUEST_TEMPLATE.md` from [reference.md](reference.md) before the initial commit.
- **CI/CD:** copy GitHub Actions templates from [github-actions/](github-actions/) into `.github/` (see [reference.md — GitHub Actions CI/CD](reference.md#github-actions-cicd)). Job names **`build`** and **`test`** must match branch protection status checks.
- Run one command at a time.
- After each command, wait for it to finish before continuing.
- If a command prompts for input, stop and let the user answer in the terminal.
- If a command fails, explain the failure and stop unless the user asks to continue.

## Workflow

### 1. Derive the repository name

Set the repository name from the current directory:

```bash
repo_name="$(basename "$PWD")"
```

Use that value for the GitHub repository and the skill scaffold. Do not prompt for a different name.

### 2. Initialize git in place

Create the repo with **`main`** as the initial branch:

```bash
git init -b main
```

If git already exists, continue only if the current folder is the intended project root and `main` is the default branch (or rename/create `main` before continuing).

### 3. List GitHub owners and let the user choose

Discover where the authenticated user can create repositories. Run **one command at a time** and wait for each to finish.

Get the personal account login:

```bash
gh api user --jq .login
```

Get organization logins the user belongs to:

```bash
gh api user/orgs --jq '.[].login'
```

**If either command fails** (not authenticated, missing `read:org`, network error):

- Explain the failure.
- Stop and tell the user to run `gh auth login`.
- Do not continue until authentication works.

**Build the owner list:**

| Kind | Value |
|------|--------|
| Personal | `<login>` from `gh api user` — label as `<login> (personal)` |
| Organization | each login from `gh api user/orgs` |

**If the user already named an owner** in the request — match case-insensitively; if valid, set `github_owner` and skip the question.

**Otherwise**, use **AskQuestion**:

- Prompt: `Under which GitHub account or organization should "<repo_name>" be created?`
- One option per owner (personal first, then orgs alphabetically).

Store:

```bash
github_owner="<selected-login>"
```

When the personal account is selected, set `github_login` to the same value. When an organization is selected, keep `github_login` as the authenticated user from `gh api user` — that user is written into CODEOWNERS.

```bash
github_login="<login-from-gh-api-user>"
```

Optionally ask visibility (`public` / `private`) unless already specified.

### 4. Create the GitHub repository with gh

Create the remote repo **without pushing** (scaffold and commit come first). Run **one command at a time**:

```bash
gh repo create "${github_owner}/${repo_name}" --remote origin --<public|private>
```

Do **not** pass `--source` or `--push` yet.

If creation fails, explain and stop unless the user asks to retry.

### 5. Create development and stage branches

Create local branches pointing at the same commit as `main`. Run **one command at a time**:

```bash
git branch development
```

Wait.

```bash
git branch stage
```

Wait.

Verify:

```bash
git branch --list main development stage
```

### 6. Push all default branches

Push each branch separately (**one command at a time**):

```bash
git push -u origin main
```

Wait.

```bash
git push -u origin development
```

Wait.

```bash
git push -u origin stage
```

Wait.

Ensure GitHub default branch is **`main`**:

```bash
gh repo edit "${github_owner}/${repo_name}" --default-branch main
```

Wait.

### 7. Initialize GitHub repo files

Create **`.github/CODEOWNERS`**, **`.gitignore`**, and **`.github/PULL_REQUEST_TEMPLATE.md`** before branch protection and the initial commit.

Run **one command at a time**:

```bash
mkdir -p .github
```

Wait.

Discover top-level directories at the repository root (include hidden directories such as `.cursor`; exclude `.git`, `.venv`, `node_modules`, and `.nx` — those belong in `.gitignore`, not CODEOWNERS):

```bash
find . -maxdepth 1 -mindepth 1 -type d \
  ! -name '.git' ! -name '.venv' ! -name 'node_modules' ! -name '.nx' \
  | sed 's|^\./||' | sort
```

Wait.

Write **`.github/CODEOWNERS`** using the procedure in [reference.md](reference.md#codeowners). Requirements:

- One line per top-level directory from the `find` output above
- Never include `.venv/`, `node_modules/`, or `.nx/` — even if they exist locally
- Path format: `/<folder-name>/ @<github_login>`
- Header comment: `# Code owners — generated by repo-bootstrap`
- Use the `github_login` value from step 3 (authenticated user, not necessarily `github_owner`)

Example when `github_login` is `octocat` and top-level folders are `apps`, `docs`, and `.github`:

```text
# Code owners — generated by repo-bootstrap
/apps/ @octocat
/docs/ @octocat
/.github/ @octocat
```

Verify:

```bash
test -f .github/CODEOWNERS
```

Wait.

Create or update root **`.gitignore`** using the template in [reference.md](reference.md#gitignore). If `.gitignore` already exists, ensure it includes at least the entries for `.venv/`, `node_modules/`, and `.nx/` from the template; add any missing sections without removing existing custom rules.

Verify:

```bash
test -f .gitignore
```

Wait.

Write **`.github/PULL_REQUEST_TEMPLATE.md`** using the **exact** markdown from the [Pull request template](reference.md#pull-request-template) section in [reference.md](reference.md). Do not shorten or modify the template.

Verify:

```bash
test -f .github/PULL_REQUEST_TEMPLATE.md
```

Wait.

### 7d. Scaffold GitHub Actions (CI/CD)

Copy the canonical workflow templates from this skill into the repository. Templates live under [github-actions/](github-actions/) and must be copied **before** branch protection (step 8) so required checks `build` and `test` match real jobs.

Run **one command at a time**:

```bash
mkdir -p .github/actions/setup-toolchain .github/workflows
```

Wait.

```bash
cp .cursor/skills/repo-bootstrap/github-actions/actions/setup-toolchain/action.yml .github/actions/setup-toolchain/action.yml
```

Wait.

```bash
cp .cursor/skills/repo-bootstrap/github-actions/workflows/ci.yml .github/workflows/ci.yml
```

Wait.

```bash
cp .cursor/skills/repo-bootstrap/github-actions/workflows/cd.yml .github/workflows/cd.yml
```

Wait.

Verify:

```bash
test -f .github/actions/setup-toolchain/action.yml && test -f .github/workflows/ci.yml && test -f .github/workflows/cd.yml
```

Wait.

**Intent (see [reference.md — GitHub Actions CI/CD](reference.md#github-actions-cicd)):**

- **CI** (`ci.yml`) — runs on every `pull_request`; jobs `build` and `test`
- **CD** (`cd.yml`) — runs on `push` to `main`, `development`, `stage`; same `build`/`test` plus `deploy`
- **DRY setup** — shared composite action at `.github/actions/setup-toolchain`

If the monorepo apps are not scaffolded yet (`apps/api`, `apps/web`), skip this step and add workflows when `api-bootstrap` / `web-bootstrap` complete — or copy templates and adjust paths later.

### 8. Apply branch protection (no direct push)

Block direct pushes on **`main`**, **`development`**, and **`stage`**.

Write the protection payload from [reference.md](reference.md) to `/tmp/branch-protection.json` (exact JSON — do not modify). Run the `cat > /tmp/branch-protection.json <<'EOF'` block from reference.md as **one command**, then wait.

Apply **one branch per command**:

```bash
gh api --method PUT "repos/${github_owner}/${repo_name}/branches/main/protection" --input /tmp/branch-protection.json
```

Wait.

```bash
gh api --method PUT "repos/${github_owner}/${repo_name}/branches/development/protection" --input /tmp/branch-protection.json
```

Wait.

```bash
gh api --method PUT "repos/${github_owner}/${repo_name}/branches/stage/protection" --input /tmp/branch-protection.json
```

Wait.

**Protection intent (from the JSON):**

- No direct push — pull requests required on all three branches
- **2 approving reviews**; dismiss stale reviews on new commits
- **CODEOWNERS review** required — `.github/CODEOWNERS` must exist (created in step 7)
- Required status checks: **`build`**, **`test`** (strict; must match CI job names)
- Linear history and resolved conversations required before merge
- No force-push or branch deletion; enforced on admins

**If protection fails** (403, 422, plan limits, org ruleset conflict, missing CODEOWNERS):

- Explain the error.
- Report which branches were protected successfully.
- Stop unless the user asks to continue without protection or to fix settings manually in GitHub.

### 9. Initial commit

```bash
git branch initial-setup
```

Wait.

```bash
git add .
```

Wait.

```bash
git commit -m "initialize repo bootstrap skill"
```

Wait.

```bash
git push -u origin initial-setup
```

Wait.



## Completion

The workflow is complete only when:

- GitHub repo exists under the selected owner
- **`.github/CODEOWNERS`** exists with one explicit owner line per top-level directory (excluding `.git`, `.venv`, `node_modules`, and `.nx`) and `@<github_login>` as the owner
- Root **`.gitignore`** exists and ignores `.venv/`, `node_modules/`, and `.nx/`
- **`.github/PULL_REQUEST_TEMPLATE.md`** exists with the exact template from [reference.md](reference.md)
- **`.github/actions/setup-toolchain/action.yml`**, **`.github/workflows/ci.yml`**, and **`.github/workflows/cd.yml`** exist (copied from [github-actions/](github-actions/) unless apps are not scaffolded yet)
- Branches **`main`**, **`development`**, and **`stage`** exist on the remote
- Branch protection (exact JSON in [reference.md](reference.md)) is applied to all three, or user accepted skipping after a documented failure
- Project files are committed and pushed on **`initial-setup`**
- Cursor has been opened

## Owner discovery (reference)

Fetch live values — do not hardcode org names. See [reference.md](reference.md).

## Additional resources

- Scaffold templates and branch protection JSON: [reference.md](reference.md)
- GitHub Actions CI/CD templates: [github-actions/](github-actions/)
