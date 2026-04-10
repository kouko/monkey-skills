# Infrastructure Conventions (Shared Standard)

This file is the single source of truth for infrastructure standards.
Both worker (when building) and evaluator (when reviewing) reference this file.

## Primary Source Anchors

This file is a project-specific operational guide. For foundational
principles, consult the dedicated primary-source standards:

- `standards/sre-practices.md` — Google SRE Book: SLI/SLO/SLA, error
  budgets, Four Golden Signals, toil reduction
- `standards/dora-metrics.md` — DORA 4 Key Metrics and capabilities model
  for measuring DevOps performance over time
- `standards/twelve-factor.md` — 12-Factor App methodology for cloud-native
  applications, with modern 2026 interpretations
- `standards/continuous-delivery.md` — Humble & Farley / Fowler deployment
  pipeline principles, release strategies (Blue/Green, Canary, Dark Launch)
- `standards/github-actions.md` — GitHub Actions workflow conventions and
  security hardening, used when GHA is the chosen CI/CD implementation

## Naming

- Resources: `{project}-{environment}-{service}-{resource}` (e.g., `myapp-prod-api-sg`)
- Environments: `dev`, `staging`, `prod` (never `production`, `stg`, or `prd`)
- Branches to environments: `main` -> `prod`, `develop` -> `staging`, `feature/*` -> `dev`
- Tags: use consistent key-value pairs (`env=prod`, `team=platform`, `managed-by=terraform`)

## IaC Organization

- One directory per environment or logical grouping (networking, compute, data)
- Shared modules in a `modules/` directory with versioned interfaces
- Variables in `variables.tf` (or equivalent), outputs in `outputs.tf`
- No inline resource definitions longer than 30 lines -- extract to modules

## Pipeline Stage Order

Standard stage sequence: lint -> test -> build -> scan -> deploy-staging -> verify -> deploy-prod
- Never skip `scan` for production deployments
- `verify` (smoke/integration tests on staging) must pass before production promotion

## Environment Tiers

| Tier | Purpose | Data | Access |
|------|---------|------|--------|
| dev | Development and experimentation | Synthetic/seed data only | Team-wide |
| staging | Pre-production validation | Anonymized production mirror | Team-wide |
| prod | User-facing | Real user data | Restricted, audited |

## Secrets Management

Aligns with 12-Factor III (Config): configuration and credentials stay
outside the codebase. See `standards/twelve-factor.md` §III for rationale.

- Never commit secrets to version control (use `.gitignore`, pre-commit hooks)
- Never embed secrets in CI/CD config files -- use platform secret stores
- Never log secret values -- mask in pipeline output
- Rotate secrets on a defined schedule (document rotation procedure)
- Use short-lived credentials (tokens, STS, OIDC) over long-lived keys when possible
- For GitHub Actions specifically, prefer OIDC for cloud authentication
  (see `standards/github-actions.md` §Secrets Management)

## Docker Best Practices

Aligns with 12-Factor II (Dependencies) and XI (Logs): images declare
explicit dependencies; containers log unbuffered to stdout/stderr for the
platform to collect. See `standards/twelve-factor.md` §II and §XI.

- Use multi-stage builds to separate build and runtime dependencies
- Run containers as non-root user (`USER` directive required)
- Use minimal base images (alpine, distroless, or slim variants)
- Pin base image versions with digest (not just tag)
- Include a `HEALTHCHECK` instruction
- Do not copy secrets into images -- inject at runtime via env or mounted secrets
- Write logs unbuffered to stdout/stderr -- never to files inside the container
