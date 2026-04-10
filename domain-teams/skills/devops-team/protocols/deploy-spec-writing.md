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

1. Select strategy with rationale (why this, not alternatives):
   - Rolling: gradual replacement, zero-downtime, simple
   - Blue-green: instant cutover, easy rollback, double resources
   - Canary: traffic splitting, risk reduction, complex routing
   - Feature flags: code-level toggling, no infra change, flag debt
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

1. Inventory all secrets (API keys, DB credentials, certificates, tokens)
2. Select secret management approach:
   - Cloud-native (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)
   - Self-hosted (HashiCorp Vault, Sealed Secrets)
   - CI/CD-native (GitHub Secrets, GitLab CI Variables)
3. Define secret rotation policy and procedure
4. Document access control (who/what can read each secret)

## Phase 5: Monitoring Baseline

1. Define what to observe:
   - Application metrics (latency, error rate, throughput)
   - Infrastructure metrics (CPU, memory, disk, network)
   - Business metrics (relevant domain KPIs)
2. Set alert thresholds with escalation paths:
   - Warning: team notification (Slack, email)
   - Critical: on-call page with runbook link
3. Define SLIs and SLOs for critical paths
4. Document log aggregation strategy (structured logs, retention policy)

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

## Rules

- Self-contained: reading the spec alone must be enough to deploy
- Every decision includes rationale (why, not just what)
- Rollback plan is mandatory, not optional -- no deploy without undo
- Use concrete values (threshold numbers, resource sizes) over vague descriptions
- Mark each section READY/PARTIAL/BLOCKED -- no ambiguity about what's deployable
- Keep structure flat -- avoid deeply nested sections

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
