# Pipeline Design Protocol

Design CI/CD pipelines that catch problems before they reach users.
Focus on fast feedback loops, clear failure messages, and reproducible builds.

**Grounded in**: Humble & Farley, *Continuous Delivery* (Addison-Wesley 2010)
and [Martin Fowler — DeploymentPipeline](https://martinfowler.com/bliki/DeploymentPipeline.html).
See `standards/continuous-delivery.md` for canonical principles (build once,
deploy many; every commit releasable; pipeline as a series of filters).

**Provider-agnostic**: This protocol designs the *logical* pipeline. The
concrete implementation target (GitHub Actions, GitLab CI, CircleCI,
Jenkins) is chosen in Phase 6 and shapes the output format. See
`standards/github-actions.md` for GitHub Actions specifics if GHA is chosen.

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

Design stages in order of fastest-feedback-first (Fowler's "commit stage"
principle: fail cheap and fast, fail expensive and slow). Skip stages that
don't apply.

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

## Phase 6: Implementation Target Selection

Choose the concrete CI/CD platform that will execute the logical pipeline
designed in Phases 1-5. Common options:

| Platform | Best for | Reference |
|----------|----------|-----------|
| **GitHub Actions** | Projects hosted on GitHub; tight integration with PRs and issues; broad ecosystem via marketplace actions | `standards/github-actions.md` |
| **GitLab CI** | Projects on GitLab; integrated container registry; mature auto-devops | docs.gitlab.com/ee/ci/ |
| **CircleCI** | Cross-provider projects; fast scheduling; Docker-first workflows | circleci.com/docs |
| **Jenkins** | On-prem or hybrid; extreme plugin flexibility; legacy migration path | jenkins.io/doc |

**For GitHub Actions** specifically, `standards/github-actions.md` documents:
- Workflow file structure and naming conventions
- Reusable workflow vs composite action decision
- Secrets management: repository / environment / organization tiers
- OIDC for cloud authentication (no long-lived credentials)
- Security hardening: SHA-pinning, minimal GITHUB_TOKEN permissions, SLSA attestation

Document the choice of target platform in the pipeline design output.
The protocol itself remains agnostic; the implementation files
(`.github/workflows/ci.yml` or `.gitlab-ci.yml` or `Jenkinsfile`) are
produced per the chosen target's conventions.

## Rules

- Fast feedback first: order stages by speed (lint < test < build < scan) — per Fowler's commit stage principle
- Fail early: cheapest checks run first
- Artifact immutability: build once, deploy everywhere (Humble & Farley §13)
- No secrets in pipeline logs: mask all sensitive values
- Pipeline configs are code: review them like application code
- Keep pipeline under 15 minutes for feature branches
- Document the chosen implementation target (Phase 6) — the protocol is agnostic, the output is not

## Output Format

1. **Pipeline Diagram**: ASCII or Mermaid showing stage flow and conditions
2. **Stage Definitions**: Per stage: trigger, commands, success criteria,
   failure behavior
3. **Branch Mapping**: Branch pattern to pipeline scope table
4. **Notification Plan**: Channel and content per event type
5. **Config Files**: Actual CI/CD config files (GitHub Actions, GitLab CI, etc.)
