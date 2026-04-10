# Deploy Spec Writing Protocol

Write implementation-ready deployment specs (DEPLOY-SPEC.md).
If a TECH-SPEC.md exists, use it as the primary input for
understanding application requirements.
The DEPLOY-SPEC.md should trace back to TECH-SPEC.md sections.

A good deploy spec lets an engineer (or agent)
set up the full deployment pipeline by reading only this document.

## Phase 1: Environment Inventory

1. Define environment tiers and their purpose:
   - Development: local or shared dev environment
   - Staging: pre-production mirror
   - Production: user-facing environment
2. Document per-environment specifics:
   - Resource sizing (CPU, memory, storage)
   - Scaling policy (fixed, auto-scale triggers)
   - Network topology (VPC, subnets, security groups)
   - Data persistence (databases, volumes, backups)
3. Define environment promotion flow: dev -> staging -> production

## Phase 2: Deployment Strategy

Strategy selection follows Martin Fowler's release pattern catalog (see
`standards/continuous-delivery.md`). Cite the chosen pattern by name.

1. Select strategy with rationale (why this, not alternatives):
   - **Rolling**: gradual replacement, zero-downtime, simple
   - **Blue-Green** ([Fowler 2010](https://martinfowler.com/bliki/BlueGreenDeployment.html)):
     instant cutover via load balancer flip, easy rollback, 2× resources during deploy
   - **Canary** ([Fowler 2014](https://martinfowler.com/bliki/CanaryRelease.html)):
     gradual traffic shift to new version, monitor and decide, complex routing
   - **Dark Launch**: deploy code but route no user traffic; validate via shadow traffic
   - **Feature Toggles** ([Fowler 2017](https://martinfowler.com/articles/feature-toggles.html)):
     decouple deploy from release; turn features on/off at runtime; flag debt is a cost
2. Document deployment triggers (manual approval, auto on merge, scheduled)
3. Define deployment verification steps (smoke tests, health checks)

## Phase 3: Rollback Plan

1. Document rollback trigger conditions (error rate threshold, latency spike)
2. Define rollback procedure:
   - Automated rollback steps (revert image tag, restore config)
   - Manual intervention steps if automated rollback fails
3. Define rollback verification (how to confirm rollback succeeded)
4. Document data rollback strategy (if schema migrations involved)

## Phase 4: Secrets Management

Follows 12-Factor III (Config): secrets and environment-specific config
live outside the codebase, injected at runtime. See `standards/twelve-factor.md` §III.

1. Inventory all secrets (API keys, DB credentials, certificates, tokens)
2. Select secret management approach:
   - Cloud-native (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)
   - Self-hosted (HashiCorp Vault, Sealed Secrets)
   - CI/CD-native (GitHub Secrets + OIDC for cloud auth — see `standards/github-actions.md`)
3. Define secret rotation policy and procedure
4. Document access control (who/what can read each secret)

## Phase 5: Monitoring Baseline

Monitoring baseline is summarized in the deploy spec; the full monitoring
design is produced by `protocols/monitoring-design.md` and should be
invoked as a separate workflow or phase for any non-trivial service.

This phase captures the high-level intent so that deploy-spec consumers
understand what to expect, with the authoritative details living in the
monitoring spec.

1. Identify critical user journeys this service is responsible for
2. Note SLI categories from the **Four Golden Signals** (see `standards/sre-practices.md`):
   latency, traffic, errors, saturation
3. Document SLO targets for each critical journey (target %, window)
4. Reference the full monitoring spec produced via `protocols/monitoring-design.md`
5. Document log aggregation strategy (structured logs per 12-Factor XI, retention policy)

**Do not** write detailed instrumentation, dashboard, or alert rules here.
Those belong in the dedicated monitoring spec.

## Phase 6: CI/CD Pipeline Stages

1. Define pipeline stages in order:
   - Lint and static analysis
   - Unit and integration tests
   - Build artifacts (container image, binary, package)
   - Security scan (dependency audit, image scan)
   - Deploy to staging
   - Integration/smoke tests on staging
   - Deploy to production (with approval gate if needed)
2. Define branch-to-environment mapping
3. Document artifact versioning and tagging strategy
4. Define failure handling per stage (retry, abort, notify)

## Phase 7: Twelve-Factor Review (new cloud-native apps only)

For **new cloud-native applications** (containerized, stateless,
horizontally scalable), perform a 12-Factor compliance check before
finalizing the deploy spec. See `standards/twelve-factor.md` for each
factor's definition and modern interpretation.

Checklist:
- [ ] III Config: all config via env vars or secret manager
- [ ] V Build/release/run: immutable artifacts, build once, deploy many
- [ ] VI Processes: fully stateless
- [ ] VII Port binding: app binds its own port, no external web server
- [ ] IX Disposability: fast startup (<10s), graceful shutdown
- [ ] X Dev/prod parity: same engines and versions across environments
- [ ] XI Logs: unbuffered stdout/stderr, no local log files

**Skip this phase** for legacy monoliths, on-prem-bound services, or
stateful workloads (databases, brokers). Document the skip reason in the
deploy spec.

The Twelve-Factor Compliance gate (`rubrics/twelve-factor-compliance.md`)
auto-runs at SHOULD level if this phase is performed.

## Rules

- Self-contained: reading the spec alone must be enough to deploy
- Every decision includes rationale (why, not just what)
- Rollback plan is mandatory, not optional -- no deploy without undo
- Use concrete values (threshold numbers, resource sizes) over vague descriptions
- Mark each section READY/PARTIAL/BLOCKED -- no ambiguity about what's deployable
- Keep structure flat -- avoid deeply nested sections
- Cite primary sources for deployment strategies and SLI/SLO definitions

## Output Structure

Adapt section numbering and depth to the project. Typical structure:

1. Project Overview (deployment goals, non-goals, constraints)
2. Environment Inventory (per-tier: resources, networking, data)
3. Deployment Strategy (approach, triggers, verification)
4. Rollback Plan (triggers, procedure, verification)
5. Secrets Management (inventory, approach, rotation, access control)
6. Monitoring & Alerting (metrics, thresholds, SLIs/SLOs, logging)
7. CI/CD Pipeline (stages, branch mapping, artifact strategy)
8. External Dependencies (cloud services, third-party APIs, versions)
