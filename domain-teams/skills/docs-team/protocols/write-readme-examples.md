# Write README — Worked Examples (Companion to write-readme.md)

Companion file containing 5 complete README examples spanning the
common project archetypes. Loaded by the `worker` agent via the
`additional:` field in full mode; **NOT** loaded in quick mode (per
`protocols/quick-write.md` §No Companion Load rule).

**Parent protocol**: `protocols/write-readme.md`
**Origin**: Examples 1, 2, 3, 4, and 5 are adapted from
[Trong-Tra/agent-skills `documentation-specialist`](https://github.com/Trong-Tra/agent-skills/tree/main/documentation-specialist)
`readme/examples.md`. Adaptations: condensed length, frontmatter
context for Diátaxis per-section gating, prose adjusted to docs-team's
Google + Microsoft style register.

## How to use this companion

When writing a README, identify the closest archetype from the table
below and use its example as a structural blueprint. Do not copy
verbatim — the example shows the **shape**, not the content.

| Project archetype | Example | Defining traits |
|-------------------|---------|-----------------|
| Small library / package | Example 1: `isoduration` | Single install command, minimal usage example, 30-line README |
| Full-stack application / service | Example 2: `Taskflow` | Docker-compose quickstart, configuration table, screenshot link |
| CLI tool | Example 3: `tfmigrate` | Multi-channel install, "How it works" 6-step list, backend matrix |
| Bad → Good rewrite | Example 4: `super-api` | Demonstrates 5 common failures and their fixes |
| Monorepo / workspace | Example 5: `Acme Platform` | Package table, root commands, "Adding a package" how-to |

---

## Example 1: Small Go library (~30 lines)

```markdown
# isoduration

Parse and format ISO 8601 durations in Go. Supports `P3Y6M4DT12H30M5S`
and all valid subsets.

[![Go Reference](https://pkg.go.dev/badge/github.com/org/isoduration.svg)](https://pkg.go.dev/github.com/org/isoduration)

## Install

​```bash
go get github.com/org/isoduration
​```

## Usage

​```go
package main

import (
    "fmt"
    "github.com/org/isoduration"
)

func main() {
    d, _ := isoduration.Parse("P1Y2M3DT4H5M6S")
    fmt.Println(d.Days()) // 428
}
​```

## Contributing

PRs welcome. Run `go test ./...` before submitting.

## License

MIT
```

**Why this works**: 30 lines. One example. Clear scope. Required
sections (Title / Short description / Install / Usage / Contributing /
License) all present, in order, License last. No fluff.

---

## Example 2: Full-stack application (~70 lines)

```markdown
# Taskflow

> Self-hosted task management with real-time collaboration. Designed
> for teams of 5-50 who outgrew spreadsheets but do not need
> enterprise complexity.

![Build](https://img.shields.io/github/actions/workflow/status/org/taskflow/ci.yml)
![License](https://img.shields.io/github/license/org/taskflow)

## Background

Built because existing tools either cost too much per seat or required
a SaaS dependency we did not want.

## Quickstart

Prerequisites: Docker, Docker Compose

​```bash
git clone https://github.com/org/taskflow.git
cd taskflow
docker-compose up
​```

Open http://localhost:8080. Default login: `admin@example.com` / `changeme`.

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `JWT_SECRET` | Yes | — | Min 32 characters |
| `PORT` | No | `8080` | HTTP server port |

## Architecture

See `docs/architecture.md` for component overview and data flow.

## Contributing

See `CONTRIBUTING.md`. All changes require tests.

## License

GPL-3.0
```

**Why this works**: Quickstart is one command (`docker-compose up`).
Configuration is a table, not prose. Architecture and Contributing
are linked, not inlined. License last.

---

## Example 3: CLI tool (~70 lines)

```markdown
# tfmigrate

Migrate Terraform state between S3, GCS, Azure Blob, and local
backends without manual `terraform state pull` workflows.

![Build](https://img.shields.io/github/actions/workflow/status/org/tfmigrate/release.yml)
![Version](https://img.shields.io/github/v/release/org/tfmigrate)

## Install

​```bash
curl -sSL https://raw.githubusercontent.com/org/tfmigrate/main/install.sh | sh

# or with Homebrew
brew install org/tap/tfmigrate
​```

## Usage

​```bash
# Migrate from S3 to GCS
tfmigrate plan \
  --from s3://my-bucket/terraform.tfstate \
  --to gcs://my-project/terraform.tfstate

# Review the plan, then apply
tfmigrate apply
​```

## Supported backends

| Backend | Plan | Apply | Lock handling |
|---------|------|-------|---------------|
| S3 | Yes | Yes | DynamoDB table |
| GCS | Yes | Yes | Generation precondition |
| Azure Blob | Yes | Yes | Lease blob |
| Local | Yes | Yes | File lock |
| HTTP | Plan only | No | — |

## How it works

1. Acquire locks on both source and destination
2. Download state from source
3. Validate state version compatibility
4. Upload to destination
5. Verify checksums match
6. Release locks

If any step fails, locks release and no state is modified.

## Configuration

Use environment variables or flags. Flags take precedence.

​```bash
export AWS_REGION=us-east-1
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
​```

## Contributing

See `CONTRIBUTING.md`. All changes require tests.

## License

MIT
```

**Why this works**: Usage example is realistic and complete. The
"How it works" section builds trust. Backend matrix sets expectations.
Multi-channel install accommodates different package managers.

---

## Example 4: Bad → Good rewrite

### Before (broken)

```markdown
# super-api

This is a very powerful API for doing things with data. It was built
by our team over the course of several months and represents a lot
of hard work.

## Getting Started

First, you need to understand our architecture. We use microservices
because they are the best. Our services communicate via gRPC. We
chose gRPC because it is fast.

## Installation

You will need to install Docker. Then you will need to clone the
repo. Then you will need to run docker-compose up. But first you
need to copy the env file and edit it. You will also need a database.

## API

POST /api/v1/things
GET /api/v1/things/:id
DELETE /api/v1/things/:id

## About Us

We are a team of passionate developers who believe in clean code...
```

**Problems**:
1. No one-liner explaining what it does
2. "Getting Started" is an architecture lecture, not steps
3. Installation is prose, not copy-paste commands
4. API section has no examples or response formats
5. "About Us" is irrelevant to a reader trying to use the project

### After (fixed)

```markdown
# SuperAPI

REST API for managing inventory and orders. Integrates with Stripe
for payments and ShipEngine for shipping labels.

![Build](https://img.shields.io/github/actions/workflow/status/org/super-api/ci.yml)

## Quickstart

Prerequisites: Docker, a Stripe test account

​```bash
git clone https://github.com/org/super-api.git
cd super-api
cp .env.example .env
# Add your Stripe test key to .env
docker-compose up
​```

The API is available at http://localhost:8000.

## Create your first order

​```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"items": [{"sku": "TSHIRT-001", "qty": 2}]}'
​```

Response:

​```json
{
  "id": "ord_123",
  "status": "pending_payment",
  "total": 4998,
  "currency": "USD"
}
​```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_SECRET_KEY` | Yes | Test or live key from Stripe dashboard |
| `SHIPENGINE_API_KEY` | No | Required only for label generation |
| `DATABASE_URL` | No | Defaults to Postgres in Docker Compose |

## API reference

See [docs/api.md](docs/api.md) for complete endpoint documentation.

## License

MIT
```

**Why the fix works**:
1. One-liner appears immediately and names the integrations
2. Quickstart replaces prose with copy-paste commands; prerequisites
   listed before commands
3. A complete request + response pair appears within the first 30
   seconds of reading
4. Configuration table is scannable
5. Removed "About Us" — readers came to use the API, not learn the
   team's history

---

## Example 5: Monorepo / workspace (~50 lines)

```markdown
# Acme Platform

Monorepo for Acme's internal platform tools and services.

## Packages

| Package | Path | Description |
|---------|------|-------------|
| `@acme/auth` | `packages/auth` | JWT authentication utilities |
| `@acme/db` | `packages/db` | Drizzle ORM schema and client |
| `@acme/ui` | `packages/ui` | Shared React components |
| `api` | `apps/api` | GraphQL API server |
| `web` | `apps/web` | Next.js frontend |
| `worker` | `apps/worker` | Background job processor |

## Development

Prerequisites: Node.js 20+, pnpm

​```bash
pnpm install
pnpm dev           # starts all apps in parallel
pnpm test          # runs tests across all packages
pnpm lint          # lints all packages
​```

## Adding a package

​```bash
cd packages
mkdir my-package
cd my-package
pnpm init
# Add to pnpm-workspace.yaml and root tsconfig.json
​```

## CI/CD

- Pull requests: lint, test, typecheck
- Merge to main: deploy `api` and `worker` to staging
- Release tag: deploy `web` to production

See [docs/ci.md](docs/ci.md) for details.

## License

MIT
```

**Why this works**: The package table is the map of the repository.
Development commands work at the root (no need to cd into each
package). "Adding a package" is documented because it is a common
contributor task. CI/CD section sets expectations for what happens
on merge.

## Sources

- [Trong-Tra/agent-skills `documentation-specialist`](https://github.com/Trong-Tra/agent-skills/tree/main/documentation-specialist) `readme/examples.md` — original 5 examples (adapted)
- [Standard README spec (RichardLitt)](https://github.com/RichardLitt/standard-readme/blob/main/spec.md) — required-sections rule referenced in each example annotation
