# Pipeline Design Protocol

Design CI/CD pipelines that catch problems before they reach users.
Focus on fast feedback loops, clear failure messages, and reproducible builds.

## Phase 1: Discover Existing Build Process

1. **Scan project**: Look for existing CI configs (.github/workflows,
   .gitlab-ci.yml, Jenkinsfile, .circleci), build scripts (Makefile,
   package.json scripts), and deployment scripts.
2. **Identify build requirements**: Language runtime, dependencies,
   build tools, test frameworks, artifact format.
3. **Note constraints**: Build time budget, runner environment
   (self-hosted vs cloud), required secrets, external service
   dependencies for tests.

## Phase 2: Define Pipeline Stages

Design stages in this order (skip stages that don't apply):

1. **Lint & Format**: Static analysis, code formatting checks.
   Fast feedback, fail early.
2. **Test**: Unit tests, then integration tests. Parallelize where
   possible. Report coverage if configured.
3. **Build**: Compile, bundle, or build container image. Tag
   artifacts with commit SHA or semantic version.
4. **Scan**: Dependency audit, container image scan, SAST.
   Non-blocking warnings for new advisories, blocking for
   critical/high severity.
5. **Deploy Staging**: Deploy to staging environment. Run smoke
   tests to verify deployment succeeded.
6. **Deploy Production**: Deploy with configured strategy
   (rolling, blue-green, canary). Require approval gate for
   production if team policy requires it.

## Phase 3: Branch Strategy Mapping

Map branches to pipeline behavior:

| Branch Pattern | Pipeline Scope | Deploy Target |
|----------------|---------------|---------------|
| `main` / `master` | Full pipeline | Production (via staging) |
| `develop` | Lint + Test + Build + Deploy | Staging |
| `feature/*` | Lint + Test + Build | None (artifact only) |
| `release/*` | Full pipeline | Staging + Production |
| `hotfix/*` | Full pipeline (expedited) | Production (via staging) |

Adapt to project's actual branching model.

## Phase 4: Environment Promotion Flow

1. Define promotion path: build -> staging -> production
2. Document approval requirements per stage
3. Define artifact immutability rule: same artifact promoted
   across environments, never rebuilt
4. Specify environment-specific config injection method
   (env vars, config files, secret manager)

## Phase 5: Failure Handling and Notification

1. **Per-stage failure**: Define behavior on failure (abort pipeline,
   continue with warning, retry with backoff)
2. **Notification channels**: Where to send results
   (Slack, email, PR comment, dashboard)
3. **Failure context**: Ensure logs, test reports, and scan results
   are attached or linked in notifications
4. **Flaky test policy**: How to handle intermittent failures
   (retry count, quarantine, auto-skip with ticket)

## Rules

- Fast feedback first: order stages by speed (lint < test < build < scan)
- Fail early: cheapest checks run first
- Artifact immutability: build once, deploy everywhere
- No secrets in pipeline logs: mask all sensitive values
- Pipeline configs are code: review them like application code
- Keep pipeline under 15 minutes for feature branches

## Output Format

1. **Pipeline Diagram**: ASCII or Mermaid showing stage flow and conditions
2. **Stage Definitions**: Per stage: trigger, commands, success criteria,
   failure behavior
3. **Branch Mapping**: Branch pattern to pipeline scope table
4. **Notification Plan**: Channel and content per event type
5. **Config Files**: Actual CI/CD config files (GitHub Actions, GitLab CI, etc.)
