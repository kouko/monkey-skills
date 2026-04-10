# GitHub Actions Conventions (Shared Standard)

GitHub Actions workflow conventions and security hardening as reference for
devops-team. Used when `pipeline-design.md` Phase 6 (Implementation Target
Selection) picks GitHub Actions as the concrete CI/CD surface.

**devops-team's pipeline-design protocol is provider-agnostic.** This
standard only applies when the selected implementation target is GitHub
Actions. GitLab CI, CircleCI, and Jenkins are equally valid choices; they
each would need their own conventions document if adopted.

Primary source: [docs.github.com/en/actions](https://docs.github.com/en/actions)
Security reference: [docs.github.com/en/actions/security-guides](https://docs.github.com/en/actions/security-guides)
Supply chain: [slsa.dev](https://slsa.dev/)

## Workflow File Structure

### Location
All workflow files live in `.github/workflows/` at the repo root. Files at
other paths are ignored by GitHub Actions.

### Naming convention
Use kebab-case descriptive names that indicate the trigger or purpose:

| Filename | Purpose |
|----------|---------|
| `ci.yml` | Main CI (lint, test, build) on push and PR |
| `release.yml` | Tag-triggered release pipeline |
| `deploy-staging.yml` | Deploy to staging environment |
| `deploy-prod.yml` | Deploy to production (usually manual trigger) |
| `nightly.yml` | Scheduled nightly jobs (security scans, dependency updates) |
| `docs.yml` | Documentation build and publish |

One workflow per file. Avoid combining unrelated jobs into one file.

### Workflow structure

```yaml
name: CI                           # required, shows in UI
on: [push, pull_request]           # explicit triggers
permissions:                       # mandatory — see Security Hardening below
  contents: read
concurrency:                       # prevent overlapping runs
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
      - name: Run tests
        run: npm test
```

## Reusable Workflows vs Composite Actions

| | Reusable Workflow | Composite Action |
|---|-------------------|------------------|
| **Scope** | Orchestrates multiple jobs | Packages multiple steps within a job |
| **Location** | `.github/workflows/reusable-*.yml` | `action.yml` in a repo or directory |
| **Invocation** | `uses: owner/repo/.github/workflows/reusable-ci.yml@sha` | `uses: owner/repo/path@sha` |
| **Sharing** | Cross-repo orchestration, multi-job pipelines | Step-level reuse within a job |
| **Best for** | Full CI patterns used by many repos | Repeated step sequences (setup Node, configure cache, etc.) |

**Decision rule**: Start with composite actions. Move to reusable workflows
only when you need multiple jobs, matrix strategies, or environment
protection rules shared across repos.

## Secrets Management

### Three tiers of secrets

| Tier | Scope | Use case |
|------|-------|----------|
| **Repository secrets** | One repo | Project-specific API keys |
| **Environment secrets** | One repo + one environment | Deploy-time credentials (prod vs staging) |
| **Organization secrets** | Multiple repos (selectable) | Shared credentials across an org |

Use **environment secrets** for anything tied to a specific environment
(staging vs prod). Environment secrets combine naturally with environment
protection rules (required reviewers, wait timers, deployment branches).

### OIDC for cloud authentication (preferred)

**Do not store long-lived AWS/GCP/Azure credentials as secrets.** Use
GitHub's OIDC token exchange to obtain short-lived cloud credentials:

```yaml
permissions:
  id-token: write           # required for OIDC
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@SHA
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-role
          aws-region: us-east-1
```

The cloud IAM trust policy validates the GitHub OIDC token claims (repo,
branch, workflow) and issues temporary credentials. Benefits:

- No long-lived credentials to rotate or leak
- Credentials scoped to a specific repo + workflow
- Audit trail via cloud IAM

### Never do these
- ❌ `echo "${{ secrets.TOKEN }}"` in a `run:` step (logs may leak)
- ❌ Hardcode secrets in workflow YAML
- ❌ Use the same secret across repositories when environment secrets would isolate them
- ❌ Store cloud root credentials as secrets (use OIDC)

## Security Hardening

### SHA-pin third-party actions (CRITICAL)

**Always pin third-party actions to a full commit SHA**, not a tag or branch.
Tags can be moved; SHAs cannot.

```yaml
# ❌ Wrong — tag can be moved
- uses: actions/checkout@v4

# ✅ Correct — SHA pin with tag as comment for readability
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
```

Official GitHub-owned actions (`actions/*`) are lower-risk but still
benefit from SHA pinning.

Automate SHA updates with Dependabot (`dependabot.yml` with
`package-ecosystem: "github-actions"`).

### Minimal GITHUB_TOKEN permissions

The default `GITHUB_TOKEN` has broad write permissions unless restricted.
**Always set `permissions:` explicitly**, defaulting to `contents: read`:

```yaml
permissions:
  contents: read              # workflow default
jobs:
  release:
    permissions:
      contents: write          # only this job can write
      id-token: write          # only this job can use OIDC
```

### Supply chain attestation (SLSA)

For production build artifacts, generate SLSA build provenance:

```yaml
jobs:
  build:
    permissions:
      contents: read
      attestations: write
      id-token: write
    steps:
      - uses: actions/attest-build-provenance@SHA
        with:
          subject-path: 'dist/*.tar.gz'
```

This produces a cryptographically signed record of what was built, how,
and from what source — verifiable by consumers downstream.

## Matrix Strategy

For multi-version testing:

```yaml
jobs:
  test:
    strategy:
      fail-fast: false           # don't cancel siblings on first failure
      matrix:
        node-version: [18.x, 20.x, 22.x]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
```

Keep matrix dimensions meaningful. Every matrix cell is a full job —
excessive dimensions (10+) slow CI and burn runner minutes.

## Concurrency Groups

Prevent overlapping deploys to the same environment:

```yaml
concurrency:
  group: deploy-prod
  cancel-in-progress: false    # queue, don't cancel, for prod deploys
```

For CI jobs on PRs, cancel in-progress runs when a new commit is pushed:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Environments for Approval Gates

Link workflows to [environments](https://docs.github.com/en/actions/deployment/targeting-different-environments) for:
- Required reviewers before deploy
- Wait timer before deploy
- Deployment branch restrictions
- Environment-scoped secrets

```yaml
jobs:
  deploy-prod:
    environment:
      name: production
      url: https://app.example.com
    runs-on: ubuntu-latest
```

When `environment: production` has required reviewers configured, this
job pauses until a reviewer approves.

## Sources

- [docs.github.com/en/actions](https://docs.github.com/en/actions) — official reference
- [GitHub Actions security guides](https://docs.github.com/en/actions/security-guides) — hardening guide
- [Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions) — SHA pinning, permissions
- [OIDC with cloud providers](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect) — short-lived credentials
- [slsa.dev](https://slsa.dev/) — Supply-chain Levels for Software Artifacts
- [actions/attest-build-provenance](https://github.com/actions/attest-build-provenance) — SLSA attestation action
