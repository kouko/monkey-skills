# Continuous Delivery (Shared Standard)

Continuous Delivery principles and deployment pipeline patterns as
authoritative reference for devops-team. Core concepts from Humble & Farley's
*Continuous Delivery* (2010) and Martin Fowler's bliki.

Primary sources:
- Humble, J. & Farley, D. *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*. Addison-Wesley, 2010. ISBN 978-0321601919
- [martinfowler.com/bliki/ContinuousDelivery.html](https://martinfowler.com/bliki/ContinuousDelivery.html)

## Core Principle

> **"Every commit should be releasable."**

Continuous Delivery is a discipline where you build software such that **the
software can be released to production at any time**. This is a property of
the build and deployment system, not a mandate to deploy every commit.

From Fowler:
> "You're doing continuous delivery when your software is deployable throughout
> its lifecycle, your team prioritizes keeping the software deployable over
> working on new features, anybody can get fast, automated feedback on the
> production readiness of their systems any time somebody makes a change to
> them, and you can perform push-button deployments of any version of the
> software to any environment on demand."

## Continuous Delivery vs Continuous Deployment

A frequently confused distinction:

| Term | Meaning |
|------|---------|
| **Continuous Delivery** | Every commit **could be** deployed to production automatically. The decision to deploy is still manual. |
| **Continuous Deployment** | Every commit **is** deployed to production automatically. Zero manual decisions. |

Continuous Delivery is a prerequisite for Continuous Deployment, but many
organizations stop at Continuous Delivery and keep a human "push" gate.
Both are valid; the choice depends on regulatory context, customer risk,
and team maturity.

## Deployment Pipeline

From Humble & Farley (Ch. 5) and
[martinfowler.com/bliki/DeploymentPipeline.html](https://martinfowler.com/bliki/DeploymentPipeline.html):

> "A deployment pipeline is an automated manifestation of your process for
> getting software from version control into the hands of your users."

The canonical pipeline has stages:

```
Commit → Commit stage → Acceptance test stage → UAT stage → Capacity stage → Release
```

Modern variants collapse stages based on automation maturity, but the
principle is **each stage acts as a filter; software that fails any stage
does not proceed**.

### Commit stage (fast feedback, seconds to minutes)
- Compile / build
- Unit tests
- Static analysis, linting
- Package as immutable artifact

### Acceptance test stage (minutes to hours)
- Automated acceptance tests against a production-like environment
- Integration tests
- Contract tests

### UAT stage (optional, for regulated contexts)
- Manual exploratory testing
- Stakeholder approval gate

### Production stage
- Deploy to production using a zero-downtime strategy
- Health check verification
- Automatic rollback on failure

## Key Practices

### Build Once, Deploy Many
From Humble & Farley: **"Build binaries only once."**

The same artifact is promoted through environments. Never rebuild for each
environment — rebuilding introduces variance and invalidates testing done
in earlier stages.

**Implementation**: CI produces a container image tagged with commit SHA;
that exact image is deployed to staging, then to production.

### Configuration Outside Artifacts
From 12-Factor III (Config): configuration is injected at deploy time, not
baked into the artifact.

**Implementation**: Environment variables or config files mounted at runtime.
The same container image runs in dev, staging, and prod with different
environment variables.

### Database Migration Discipline
Database migrations must be:
- **Backward-compatible** — the previous version of the app must still work
  after the migration
- **Forward-compatible** — the new version must work before the migration
- **Reversible** (where feasible) — a rollback strategy exists
- **Run separately from app deploy** — schema changes are their own deploy
  with their own risk profile

### Version Control Everything
Every deploy artifact, environment config, pipeline definition, IaC, and
database migration lives in version control. Manual changes to production
are forbidden.

## Release Strategies

From Fowler's bliki entries on release patterns:

### Blue/Green Deployment
From [martinfowler.com/bliki/BlueGreenDeployment.html](https://martinfowler.com/bliki/BlueGreenDeployment.html)

Two identical production environments (Blue and Green). Only one serves
live traffic. Deploy to the idle one, verify, then flip the load balancer.
Rollback = flip back.

**Best for**: High-availability services, regulated environments, predictable workloads.
**Cost**: 2× infrastructure during deploy.

### Canary Release
From [martinfowler.com/bliki/CanaryRelease.html](https://martinfowler.com/bliki/CanaryRelease.html)

Release to a small subset of users first. Monitor for regressions. Gradually
expand to 100% if healthy; rollback if not.

**Best for**: Services where real traffic reveals bugs that staging cannot;
services with gradual rollout tooling (service mesh, feature flags).
**Cost**: Requires traffic routing and metric aggregation across canary vs
main populations.

### Dark Launch
Release code to production **without exposing it to users**. Exercise the
new code path via shadow traffic or feature flag off. Validate performance
and correctness before turning on.

**Best for**: High-risk migrations, backend changes with no UI surface,
capacity testing.

### Feature Toggles
From [martinfowler.com/articles/feature-toggles.html](https://martinfowler.com/articles/feature-toggles.html)

Decouple deploy from release: ship code with the feature behind a toggle
(off), then turn the toggle on for a percentage of users or a specific segment.

**Best for**: A/B testing, gradual rollout, emergency kill switch.
**Cost**: Toggle lifecycle management (toggles must be removed after
rollout; stale toggles are tech debt).

## Zero-Downtime Deployment

Every production deploy must be zero-downtime. Users should not notice the
deploy occurred. This requires:

- **Rolling updates** — replace instances gradually
- **Health checks** — platform verifies new instance is ready before sending traffic
- **Graceful shutdown** — old instances drain in-flight requests (SIGTERM handling)
- **Backward-compatible schema changes** — database and API contracts work across versions
- **Connection draining** — load balancer stops sending new traffic before termination

## Sources

- Humble, J. & Farley, D. *Continuous Delivery*. Addison-Wesley, 2010.
- [Martin Fowler — ContinuousDelivery](https://martinfowler.com/bliki/ContinuousDelivery.html)
- [Martin Fowler — DeploymentPipeline](https://martinfowler.com/bliki/DeploymentPipeline.html)
- [Martin Fowler — BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Martin Fowler — CanaryRelease](https://martinfowler.com/bliki/CanaryRelease.html)
- [Martin Fowler — FeatureToggle](https://martinfowler.com/articles/feature-toggles.html)
