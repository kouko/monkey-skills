# Write API Reference Protocol

Write API reference documentation following OpenAPI 3.2.0 structural
requirements. This is a specialization of `write-reference.md` for the
HTTP API sub-case where the OpenAPI vocabulary applies.

**Vocabulary reference**: `standards/diataxis-taxonomy.md` §Reference
**Structure reference**: `standards/api-reference-structure.md` (mandatory)
**Style reference**: `standards/style-conventions.md`
**General reference protocol**: `protocols/write-reference.md` (parent)
**Pre-writing reference**: `standards/pre-writing-checklist.md` — apply before Phase 0

## When to Use This Protocol

Use this protocol when documenting:
- HTTP REST API
- GraphQL API (with adaptation)
- gRPC service (with adaptation)
- Library API where OpenAPI-equivalent structure is appropriate

Use `write-reference.md` (parent) for non-API references: CLI, config
schema, file format, protocol specification.

## Phase 0: Context Discovery

1. **Apply pre-writing checklist** (`standards/pre-writing-checklist.md`)
2. **Confirm an OpenAPI / equivalent spec exists**:
   - If yes → auto-generate from spec; this protocol covers the descriptive
     prose that augments generated reference, not regeneration of the spec
   - If no → hand-write following OpenAPI structural requirements
3. **Identify cross-cutting concerns**: authentication, rate limiting,
   pagination, error code conventions, versioning policy
4. **Locate benchmark references** for comparison: Stripe, Twilio,
   GitHub, Anthropic — pick one whose tone matches the API's audience

## Phase 1: Document Cross-Cutting Concerns First

Before per-operation pages, write a single Cross-Cutting Concerns page
covering things that apply to every operation:

- **Authentication**: scheme(s), where credentials go (header / query /
  body), token lifetime, refresh model
- **Rate limiting**: limits, window, headers exposing remaining quota,
  what happens on 429
- **Pagination**: convention (cursor / offset / page-token), default
  size, maximum size, navigation links
- **Error responses**: error envelope shape, standard error codes used
  across operations
- **Versioning**: how versions are selected (URL / header / parameter),
  deprecation policy

Operations link to this page rather than restating these concerns.

## Phase 2: Document Each Operation Consistently

Per `standards/api-reference-structure.md` §Required Fields per Operation,
every operation must document:

### Summary and description
- One-line summary
- 2-5 sentence description

### Request
- HTTP method and path (or function signature)
- Parameters with: name, location (path / query / header / body), type,
  required flag, default, description, valid values
- Request body schema (if applicable) — reference shared schema or define inline
- Authentication requirement

### Response
- Success response: status code, content type, response schema
- Error responses: each error status with example body and trigger
- Response headers (when meaningful, e.g. `X-RateLimit-Remaining`)

### Example
- Runnable request (`curl` + at least one SDK)
- Example response body with realistic values
- At least one error example

## Phase 3: Apply Consistency Rules

Per `standards/api-reference-structure.md` §Structural Consistency Rule:

- **All operations follow the same template** — if one has "Example
  Errors", all should
- **Shared schemas referenced consistently** — `User` is `User`
  everywhere, never `user_object` or `userPayload`
- **camelCase for parameter names** (OpenAPI convention)
- **Required parameters listed before optional**
- **Cross-cutting concerns documented once**, not per operation

The Consistency Pass is the most-skipped phase and the most-felt by
readers. Always run it.

## Phase 4: Examples Are Realistic, Not `foo`/`bar`

Use realistic placeholders and values:
- Identifiers: `usr_01HF8...` (ULID), not `123` or `id1`
- Names: `alice@example.com`, not `foo@bar.com`
- Amounts: `4998` cents (representing $49.98), not `100`
- Currencies: `"USD"` explicitly, never inferred

Realistic examples reduce reader cognitive load and reveal edge cases
(e.g. cents-vs-dollars, ID format) that `foo`/`bar` hides.

## Phase 5: Separate Reference From Explanation

API reference is **not** API explanation. This is a direct Diátaxis rule:

- Reference: parameters, types, schemas, error codes — exhaustive,
  mechanically consistent, scannable
- Explanation: design rationale, trade-offs, how-to-think-about it —
  discursive, selective

Keep them in separate files. The reference links to "Concepts" or
"Guides" pages where Explanation lives.

## Rules

- **Auto-generate when possible.** If the API has an OpenAPI spec,
  hand-writing reference is wasteful and drifts from source of truth.
- **camelCase parameter names.** OpenAPI convention; deviate only if
  the API itself uses a different convention consistently.
- **Every operation has at least one error example.** Success-only
  examples create a false sense of reliability.
- **No "see above" / "see below".** Use explicit links to the section.
- **No marketing copy.** "Powerful endpoint" / "easy to use" /
  "intuitive" belong in marketing pages, not reference.
- **Idempotency, side effects, and rate-limit cost** documented per
  operation when they vary from defaults.

## Output Structure

```markdown
---
title: {API name} API Reference
last_reviewed: {YYYY-MM-DD}
applies_to: v{X.Y}
owner: {team}
mode: reference
---

# {API name} API Reference

{One-paragraph scope: what API this covers, what it does NOT cover.}

## Cross-cutting concerns

### Authentication
### Rate limiting
### Pagination
### Errors
### Versioning

## {Resource 1}

### Create {resource}

**Method**: `POST /v1/{resources}`
**Auth**: Bearer token
**Idempotency**: yes (Idempotency-Key header)

{1-line summary + 2-5 sentence description}

**Request body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
{...}

**Responses**:

| Status | Description |
|--------|-------------|
| `201` | Resource created |
| `400` | Invalid input — see error envelope |
| `409` | Duplicate idempotency key with different body |

**Example request**:

​```bash
curl -X POST https://api.example.com/v1/payments \
  -H "Authorization: Bearer sk_test_..." \
  -H "Idempotency-Key: 8e1f9c..." \
  -d '{"amount": 4998, "currency": "USD"}'
​```

**Example response**:

​```json
{
  "id": "pay_01HF8...",
  "amount": 4998,
  "currency": "USD",
  "status": "succeeded"
}
​```

**Example error** (400):

​```json
{
  "error": {
    "code": "validation_failed",
    "message": "amount must be greater than 0",
    "field": "amount"
  }
}
​```

### {Other operations follow the same template}

## {Resource 2}
{Same template}
```

## Example

Single-operation walk-through showing the per-operation template
filled out for a different domain (Notes API). Cross-cutting concerns
have been documented separately at the top of the reference (not shown
here) so the operation page links to them rather than restating.

```markdown
## Notes

### Create a note

**Method**: `POST /v1/notes`
**Auth**: Bearer token (see [Authentication](#authentication))
**Idempotency**: yes (`Idempotency-Key` header)
**Rate limit**: 60 req/min per token (see [Rate limiting](#rate-limiting))

Creates a new note under the authenticated user's workspace.

**Request body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | yes | — | 1-200 chars; trimmed |
| `body` | string | yes | — | Markdown; max 100,000 chars |
| `tags` | string[] | no | `[]` | Lowercase, kebab-case; max 16 items |
| `pinned` | boolean | no | `false` | Pinned notes appear first in the workspace list |

**Responses**:

| Status | Description |
|--------|-------------|
| `201` | Note created |
| `400` | Validation failed — see error envelope |
| `409` | Duplicate `Idempotency-Key` with a different body |
| `429` | Rate limit exceeded — `Retry-After` header set |

**Example request**:

​```bash
curl -X POST https://api.example.com/v1/notes \
  -H "Authorization: Bearer sk_test_abc123" \
  -H "Idempotency-Key: 7f3e2a8d-1b4c-4f5a-9e2d-8c1a3b4f5e6d" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q3 launch checklist",
    "body": "# Ship plan\n\n- Code freeze 2026-09-15\n- Soak window 3 days",
    "tags": ["launch", "q3"],
    "pinned": true
  }'
​```

**Example response** (201):

​```json
{
  "id": "note_01HF8XK7P2Q4R5S6T7U8V9W0XY",
  "title": "Q3 launch checklist",
  "body": "# Ship plan\n\n- Code freeze 2026-09-15\n- Soak window 3 days",
  "tags": ["launch", "q3"],
  "pinned": true,
  "created_at": "2026-04-29T10:30:00Z",
  "workspace_id": "ws_01HF7..."
}
​```

**Example error** (400):

​```json
{
  "error": {
    "code": "validation_failed",
    "message": "title must be 1-200 characters",
    "field": "title"
  }
}
​```

### List notes

**Method**: `GET /v1/notes`
{...same template — pagination via `?cursor=` and `?limit=` per
[Pagination](#pagination)}
```

**Why this works**: every operation field documented (method / auth /
idempotency / rate limit / request fields with type-required-default-
description / response status table / runnable curl / realistic JSON
response / error example). Cross-cutting concerns (auth, rate limiting,
pagination) link to top-of-reference sections instead of restating.
Realistic placeholder values (`sk_test_abc123`, ULID-style IDs,
markdown body content) reduce reader cognitive load. The second
operation (`GET /v1/notes`) is sketched to show the template is
consistent across all operations — readers expect the same fields in
the same order on every page.

## Mode Clarity Check

This API reference passes the Mode Clarity gate (run via
`rubrics/diataxis-mode-clarity.md`) if:

- Structure mirrors the API (resources → operations → fields)
- Every operation follows the same template (consistency check)
- Cross-cutting concerns documented once at the top
- No design rationale or "why we built it this way" embedded
- Examples are minimal, runnable, with realistic values
- Error examples present alongside success examples

## Sources

- `standards/api-reference-structure.md` — required fields per operation, OpenAPI vocabulary
- `protocols/write-reference.md` — parent protocol; this is the API specialization
- [OpenAPI Specification v3.2.0](https://spec.openapis.org/oas/latest.html) — Linux Foundation standard
- [Stripe API Reference](https://stripe.com/docs/api) — three-column layout benchmark
- [Twilio API Reference](https://www.twilio.com/docs/usage/api) — multi-language SDK switching benchmark
