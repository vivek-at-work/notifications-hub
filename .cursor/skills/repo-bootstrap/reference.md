# Repo Bootstrap — scaffold templates

Write these files at the **repository root** (not under `.cursor/skills/`).

## Root `SKILL.md`

```markdown
---
name: <repo-name>
description: workflow skill for this repository
---

# <repo-name>

## rules

- derive the repository name from the current folder with `basename "$PWD"`
- run one command at a time
- wait for each command to finish before continuing
- if a command prompts for input, stop and let the user answer in the terminal
- if a command fails, explain the failure and stop unless the user asks to continue
- default branches: main, development, stage
- do not push directly to main, development, or stage; use pull requests

## workflow

1. derive the repo name from the current folder
2. run commands one at a time and wait after each command
3. list github owners with `gh api user` and `gh api user/orgs`, then let the user pick an account or organization
4. create the github repo with `gh repo create <owner>/<repo>` under the selected owner
5. create main, development, and stage branches and protect them from direct push
6. create or update `.gitignore` from the repo-bootstrap reference
7. create `.github/CODEOWNERS` with the authenticated user as owner of each top-level folder (excluding `.venv`, `node_modules`, and `.nx`)
8. create `.github/PULL_REQUEST_TEMPLATE.md` from the repo-bootstrap reference
9. copy GitHub Actions CI/CD from `.cursor/skills/repo-bootstrap/github-actions/` into `.github/` (see repo-bootstrap reference — GitHub Actions CI/CD)
10. open the folder in cursor with `cursor .`
```

Replace `<repo-name>` with the actual directory name.

## `agents/openai.yaml`

```yaml
interface:
  display_name: "<repo-name>"
  short_description: "Workflow skill for the <repo-name> repository"
  default_prompt: "Use $repo-bootstrap to work in this repository."
```

Replace `<repo-name>` with the actual directory name.

## Directories

```text
.github/
agents/
references/
scripts/
assets/
```

## Pull request template

Create **`.github/PULL_REQUEST_TEMPLATE.md`** at the repository root during bootstrap. Use this **exact** content — do not modify:

```markdown
# Pull Request

## Summary
<!-- Briefly describe what changed and why. -->

## Related Work Item
- Issue/Ticket:
- Requirement/Story:

## Problem Statement
<!-- What problem or requirement does this change address? -->

## Implementation
<!-- Describe the approach taken to solve the problem. -->

## Changes Made
- 
- 
- 

## Files Modified
| File/Module | Purpose |
| ------------ | ------- |
|              |         |
|              |         |

## Assumptions
<!-- List any assumptions made during implementation. -->
- 

## Testing & Validation

### Automated Validation
- [ ] Build passes
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Linting passes
- [ ] Static analysis passes
- [ ] No automated tests applicable

### Manual Validation
<!-- Describe how the changes were manually verified. -->
- 

## Impact Assessment

### Breaking Changes
- [ ] No
- [ ] Yes (describe below)

Details:

### Performance Impact
- [ ] None
- [ ] Improved
- [ ] Potential impact (describe below)

Details:

### Security Impact
- [ ] No security impact
- [ ] Security-sensitive changes (describe below)

Details:

## Dependencies
- [ ] No new dependencies
- [ ] New dependencies added

If added, list them and explain why:
- 

## Known Limitations / Risks
<!-- Any known issues, trade-offs, or risks. -->
- 

## Rollback Plan
<!-- Describe how to safely revert this change if necessary. -->
- 

## Reviewer Notes
<!-- Areas where reviewers should pay special attention. -->
- 

---

# AI Agent Report

**Agent Name:**  
**Agent Version:**  
**Execution Date:**  
**Task/Issue ID:**  

## Request Received
<!-- Summarize the original request. -->

## Work Completed
<!-- Explain exactly what was implemented. -->

## Reasoning
<!-- Brief explanation of the implementation decisions. -->

## Files Changed
| File | Change Summary |
|------|----------------|
|      |                |

## Validation Performed
- Build:
- Tests:
- Lint:
- Manual Verification:

## Confidence Level
- [ ] High
- [ ] Medium
- [ ] Low

### If confidence is Medium or Low, explain why:
- 

## Follow-up Recommendations
<!-- Optional future improvements or technical debt identified. -->
- 

---

# Final Checklist

- [ ] Requirement fully implemented.
- [ ] Code follows project standards.
- [ ] Self-review completed.
- [ ] No unnecessary code or files included.
- [ ] Tests added or updated where appropriate.
- [ ] Documentation updated if required.
- [ ] Backward compatibility considered.
- [ ] Security implications reviewed.
- [ ] Performance impact considered.
- [ ] Rollback plan documented.
```

GitHub uses this file automatically when opening a new pull request.

```bash
mkdir -p .github
```

Write `.github/PULL_REQUEST_TEMPLATE.md` with the content above before the initial commit on `initial-setup`.

## Gitignore

Create or update **`.gitignore`** at the repository root during bootstrap. Dependency and cache directories must be ignored here — not listed in CODEOWNERS.

Use this template when the file does not exist. When it already exists, merge in any missing entries (especially `.venv/`, `node_modules/`, and `.nx/`) without removing custom rules.

```gitignore
# Dependencies
node_modules/
.pnpm-store/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
*.egg-info/
dist/
build/
*.egg
.ruff_cache/
.mypy_cache/
.pytest_cache/
htmlcov/
.coverage
.coverage.*
*.cover

# Environment
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Next.js
.next/
out/

# Nx
.nx/

# TypeScript / tooling caches
*.tsbuildinfo
.eslintcache

# Logs
*.log
npm-debug.log*
pnpm-debug.log*
yarn-debug.log*
yarn-error.log*

# Docker
docker-compose.override.yml

# Test artifacts
coverage/
test-results/

# Storybook
storybook-static/
```

Write `.gitignore` before CODEOWNERS and the initial commit on `initial-setup`.

## CODEOWNERS

Create **`.github/CODEOWNERS`** at the repository root during bootstrap. Branch protection sets `require_code_owner_reviews: true`, so this file must exist before protection is applied.

### Discover top-level directories

List every directory at the repository root. Include hidden directories (for example `.cursor`, `.github`); exclude:

| Directory | Reason |
|-----------|--------|
| `.git` | Not project content |
| `.venv` | Local Python environment — ignored via `.gitignore` |
| `node_modules` | Installed dependencies — ignored via `.gitignore` |
| `.nx` | Nx cache — ignored via `.gitignore` |

```bash
find . -maxdepth 1 -mindepth 1 -type d \
  ! -name '.git' ! -name '.venv' ! -name 'node_modules' ! -name '.nx' \
  | sed 's|^\./||' | sort
```

### Resolve the code owner

Use the authenticated GitHub user login — not the selected org owner when the repo is created under an organization:

```bash
github_login="$(gh api user --jq .login)"
```

### Generate the file

Write one CODEOWNERS line per directory from the `find` output:

- Path: `/<directory-name>/` (leading and trailing slash)
- Owner: `@<github_login>`

Example shell loop (run after `github_login` is set):

```bash
{
  echo "# Code owners — generated by repo-bootstrap"
  find . -maxdepth 1 -mindepth 1 -type d \
    ! -name '.git' ! -name '.venv' ! -name 'node_modules' ! -name '.nx' \
    | sed 's|^\./||' | sort | while IFS= read -r dir; do
    printf '/%s/ @%s\n' "$dir" "$github_login"
  done
} > .github/CODEOWNERS
```

Example output when `github_login` is `octocat`:

```text
# Code owners — generated by repo-bootstrap
/.cursor/ @octocat
/.github/ @octocat
/apps/ @octocat
/docs/ @octocat
/libs/ @octocat
/openspec/ @octocat
/scripts/ @octocat
```

### Rules

- Regenerate from the live directory listing at bootstrap time — do not hardcode folder names.
- Never add `.venv/`, `node_modules/`, or `.nx/` to CODEOWNERS; those directories belong in `.gitignore` only.
- Do not add a catch-all `* @user` line unless the user explicitly asks; each top-level folder must have its own line.
- If no top-level directories exist yet, write only the header comment and stop; tell the user CODEOWNERS is empty until folders are scaffolded.

```bash
mkdir -p .github
```

Write `.github/CODEOWNERS` before branch protection and before the initial commit on `initial-setup`.

## Branch protection payload

Write this **exact** JSON to `/tmp/branch-protection.json` (one command) before calling the GitHub API:

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "build",
      "test"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 2,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
```

Example write (run once, then wait):

```bash
cat > /tmp/branch-protection.json <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "build",
      "test"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 2,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
EOF
```

Apply to each default branch (**one command at a time**):

```bash
gh api --method PUT "repos/${github_owner}/${repo_name}/branches/main/protection" --input /tmp/branch-protection.json
gh api --method PUT "repos/${github_owner}/${repo_name}/branches/development/protection" --input /tmp/branch-protection.json
gh api --method PUT "repos/${github_owner}/${repo_name}/branches/stage/protection" --input /tmp/branch-protection.json
```

### Notes

- **No direct push** — all changes to `main`, `development`, and `stage` must go through pull requests.
- **2 approving reviews** required; stale reviews dismissed on new pushes.
- **CODEOWNERS** — `require_code_owner_reviews: true` requires `.github/CODEOWNERS` (created during bootstrap with one line per top-level folder).
- **Status checks** — `build` and `test` contexts must be reported by CI (strict mode); until CI exists, PRs cannot merge. Add GitHub Actions or remove/adjust contexts after bootstrap if needed.
- **Linear history** and **conversation resolution** required before merge.
- Org **rulesets** may conflict; if PUT returns 422/403, document the error and apply an equivalent ruleset in GitHub.
- Token needs admin access on the target repository.

## GitHub Actions CI/CD

Canonical templates ship with the **repo-bootstrap** skill under:

```text
.cursor/skills/repo-bootstrap/github-actions/
  actions/setup-toolchain/action.yml
  workflows/ci.yml
  workflows/cd.yml
```

During bootstrap, copy them into the repository:

```bash
mkdir -p .github/actions/setup-toolchain .github/workflows
cp .cursor/skills/repo-bootstrap/github-actions/actions/setup-toolchain/action.yml .github/actions/setup-toolchain/action.yml
cp .cursor/skills/repo-bootstrap/github-actions/workflows/ci.yml .github/workflows/ci.yml
cp .cursor/skills/repo-bootstrap/github-actions/workflows/cd.yml .github/workflows/cd.yml
```

### Layout

| Path | Purpose |
|------|---------|
| `.github/actions/setup-toolchain/action.yml` | Composite action: Node, pnpm, Python, `pnpm install`, API dev requirements |
| `.github/workflows/ci.yml` | **CI** — `pull_request` (all base branches); jobs `build`, `test` |
| `.github/workflows/cd.yml` | **CD** — `push` to `main`, `development`, `stage`; jobs `build`, `test`, `deploy` |

### Version pins (workflow `env`)

Align with [technology-stack.mdc](../../rules/technology-stack.mdc) and root toolchain files:

| Variable | Default | Source of truth |
|----------|---------|-----------------|
| `NODE_VERSION` | `24` | `.nvmrc` |
| `PNPM_VERSION` | `9.15.0` | `package.json` → `packageManager` |
| `PYTHON_VERSION` | `3.12.13` | `.python-version` |

### CI (`ci.yml`)

- **Trigger:** every `pull_request` (no base-branch filter)
- **Jobs:** `build`, `test` — names must match branch protection `contexts`
- **build:** Nx build api/web, Docker image build (base targets)
- **test:** Postgres service, pytest, web lint

### CD (`cd.yml`)

- **Trigger:** `push` to `main`, `development`, `stage`
- **Jobs:** `build`, `test` (same as CI), then `deploy`
- **deploy:** GitHub Environment by branch — `main` → `production`, `stage` → `staging`, `development` → `development`; builds release Docker images tagged with short SHA and branch name
- Registry push and helm upload are placeholders until infrastructure is configured (`scripts/helm-chart-upload-noop.sh`)

### Maintaining templates

When changing CI/CD in `.github/`, update the skill templates under `github-actions/` so future bootstraps stay in sync.

## Default branch layout

| Branch | Purpose (convention) |
|--------|----------------------|
| `main` | Production-ready; GitHub default branch |
| `development` | Integration / active development |
| `stage` | Pre-production / staging |

All three are created from the same initial commit during bootstrap, then protected.
