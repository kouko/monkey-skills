# The Twelve-Factor App (Shared Standard)

Twelve-Factor methodology for cloud-native applications as authoritative
reference for devops-team. Used by worker when designing deploy specs, by
evaluator when running the Twelve-Factor Compliance gate.

Primary source: [12factor.net](https://12factor.net/) (Adam Wiggins / Heroku, 2011)
Modern companion: *Beyond the Twelve-Factor App* (Kevin Hoffman, O'Reilly 2016)

## Core Principle

A twelve-factor app is a methodology for building software-as-a-service
apps that:
- Use declarative formats for setup automation
- Have a clean contract with the underlying operating system
- Are suitable for deployment on modern cloud platforms
- Minimize divergence between development and production
- Can scale up without significant changes to tooling, architecture, or development practices

## The Twelve Factors

Each factor is listed with its **original definition**, a **modern 2026
interpretation**, and a **common violation** to watch for.

### I. Codebase
**Original**: "One codebase tracked in revision control, many deploys."
**Modern**: Still fully applicable. Mono-repo vs poly-repo is orthogonal —
the factor says one app = one codebase, not one codebase = one repo.
**Violation**: Sharing code via copy-paste across services instead of
extracting a shared library with its own codebase.

### II. Dependencies
**Original**: "Explicitly declare and isolate dependencies."
**Modern**: Lockfiles (`package-lock.json`, `Cargo.lock`, `Pipfile.lock`)
are the modern implementation. Container images are the isolation mechanism.
**Violation**: Relying on system-level packages (`apt install foo`) that
are not declared in the app's manifest.

### III. Config
**Original**: "Store config in the environment."
**Modern**: Environment variables for non-secret config; secret manager
(AWS Secrets Manager, Vault, Doppler) for secrets. Never commit config to
the codebase; never hardcode credentials.
**Violation**: `config.production.json` checked into git.

### IV. Backing Services
**Original**: "Treat backing services as attached resources."
**Modern**: Largely subsumed into managed cloud services (RDS, Cloud SQL,
Firebase, etc.). The core idea — swap a backing service without code
changes — remains important.
**Violation**: Hardcoding database hostnames or driver-specific imports in
business logic.

### V. Build, release, run
**Original**: "Strictly separate build and run stages."
**Modern**: CI pipelines enforce this via immutable artifacts. Build once,
promote the same artifact through environments.
**Violation**: Running `git pull && npm install` on the production server.

### VI. Processes
**Original**: "Execute the app as one or more stateless processes."
**Modern**: Kubernetes pods, serverless functions, containers. Any state
must live in a backing service (Factor IV).
**Violation**: Storing session state in local process memory.

### VII. Port binding
**Original**: "Export services via port binding."
**Modern**: The app itself binds to a port; the platform (K8s, load
balancer, ingress) handles routing. No need for an external web server
like Apache in front of the app.
**Violation**: Requiring Apache/nginx/IIS to be configured out-of-band.

### VIII. Concurrency
**Original**: "Scale out via the process model."
**Modern**: Reinterpreted as horizontal pod autoscaling (HPA) and
fargate/serverless scaling. Factor VIII's UNIX process model assumptions
are aged; the principle (horizontal scaling) is still correct.
**Violation**: Relying on a single large VM that must be manually resized.

### IX. Disposability
**Original**: "Maximize robustness with fast startup and graceful shutdown."
**Modern**: Containers die and restart constantly under orchestration.
Fast startup (≤10 seconds) and graceful shutdown (SIGTERM handling) are
non-negotiable.
**Violation**: Services that take 2 minutes to boot or drop in-flight
requests on shutdown.

### X. Dev/prod parity
**Original**: "Keep development, staging, and production as similar as possible."
**Modern**: Same database engine, same OS base image, same backing services
across environments. Docker + IaC make this easier than in 2011.
**Violation**: Developing on SQLite, deploying to Postgres.

### XI. Logs
**Original**: "Treat logs as event streams."
**Modern**: App writes unbuffered to stdout/stderr; the platform collects,
routes, and indexes (Datadog, Loki, CloudWatch Logs). App does not manage
its own log files.
**Violation**: Writing to `/var/log/myapp.log` inside the container.

### XII. Admin processes
**Original**: "Run admin/management tasks as one-off processes."
**Modern**: Largely irrelevant in serverless. In containerized apps,
`kubectl exec` or `docker exec` for database migrations and one-off tasks.
**Violation**: Embedding migration scripts that run on every app start.

## Modern Extensions (Hoffman 15-Factor)

Kevin Hoffman's *Beyond the Twelve-Factor App* (2016) adds three factors
for modern cloud-native apps:

- **API First** — design and publish API before implementation
- **Telemetry** — app-level metrics, domain-specific events, application
  performance monitoring
- **Authentication and Authorization** — security is a first-class concern,
  not an afterthought

These three are effectively required for modern cloud-native services but
are not scored by the Twelve-Factor Compliance gate (they have no direct
factor equivalents in the original 12).

## Adoption Evidence

- **Heroku** — 12-Factor originated as internal Heroku guidance
- **Google Cloud Run** — documentation explicitly references 12-Factor
- **AWS App Runner** — service constraints enforce 12-Factor compliance
- **Cloud Foundry** — 12-Factor is foundational
- **Kubernetes** — 12-Factor compatibility is the de facto standard for
  new app design

## Sources

- [12factor.net](https://12factor.net/) — canonical text (Adam Wiggins, 2011)
- [Twelve-Factor App Introduction](https://12factor.net/introduction) — background and motivation
- Hoffman, K. *Beyond the Twelve-Factor App*. O'Reilly, 2016.
- [Google Cloud Run: Twelve-Factor App](https://cloud.google.com/blog/products/gcp/7-best-practices-for-building-containers) — adoption guide
