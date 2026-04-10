# Infrastructure Conventions (Shared Standard)

This file is the single source of truth for infrastructure standards.
Both worker (when building) and evaluator (when reviewing) reference this file.

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

- Never commit secrets to version control (use `.gitignore`, pre-commit hooks)
- Never embed secrets in CI/CD config files -- use platform secret stores
- Never log secret values -- mask in pipeline output
- Rotate secrets on a defined schedule (document rotation procedure)
- Use short-lived credentials (tokens, STS) over long-lived keys when possible

## Docker Best Practices

- Use multi-stage builds to separate build and runtime dependencies
- Run containers as non-root user (`USER` directive required)
- Use minimal base images (alpine, distroless, or slim variants)
- Pin base image versions with digest (not just tag)
- Include a `HEALTHCHECK` instruction
- Do not copy secrets into images -- inject at runtime via env or mounted secrets
