# API Reference Structure (Shared Standard)

Structural requirements for API reference documentation. All API reference —
whether auto-generated from OpenAPI specs or hand-written — must cover the
same fields per operation.

Primary source: [OpenAPI Specification v3.2.0](https://spec.openapis.org/oas/latest.html)
(Linux Foundation, published 2025-09-19)

## Why OpenAPI as the vocabulary authority

OpenAPI is the formal industry standard for HTTP API description, maintained
by the Linux Foundation. Its object model (paths, operations, parameters,
responses, schemas) has become the de facto vocabulary for thinking about
API reference docs regardless of whether the docs are actually generated
from an OpenAPI spec.

Docs-team adopts OpenAPI **terminology and structural requirements** as the
baseline. Hand-written API reference docs should cover the same fields even
if they don't use OpenAPI tooling.

## Required Fields per Operation

Each endpoint / operation in an API reference must document:

### Summary and description
- **Summary**: 1-line purpose of the operation
- **Description**: 2-5 sentences explaining what, when to use, key constraints

### Request

- **HTTP method and path** (or function signature for non-HTTP APIs)
- **Parameters** — for each parameter:
  - Name (camelCase per OpenAPI convention)
  - Location (path / query / header / body)
  - Type (string, integer, boolean, object reference, etc.)
  - Required or optional
  - Default value (if optional)
  - Description (what it controls, valid values, constraints)
- **Request body schema** (if applicable) — reference a schema in `components/schemas` or define inline
- **Authentication** — which auth scheme applies (bearer, API key, OAuth scope)

### Response

- **Success response** — status code, content type, response schema
- **Error responses** — each error status code with example body and what causes it
- **Response headers** (if they carry meaning — e.g., `X-RateLimit-Remaining`)

### Example

- **Runnable request** — `curl` command, language-specific SDK snippet, or both
- **Example response body** — matching the schema, with realistic values
- **Error example** — at least one error case with example response

## OpenAPI 3.2.0 Object Model (Quick Reference)

```
openapi.yaml
├── info              # Title, version, description, contact, license
├── servers           # Base URLs for different environments
├── paths
│   └── /resource
│       └── get       # Operation
│           ├── summary
│           ├── description
│           ├── parameters
│           ├── requestBody
│           ├── responses
│           │   ├── "200"
│           │   └── "400"
│           ├── security
│           └── tags
└── components
    ├── schemas       # Reusable data structures
    ├── responses     # Reusable response definitions
    ├── parameters    # Reusable parameter definitions
    └── securitySchemes
```

Hand-written reference docs don't need this exact YAML structure, but they
should expose the **same information architecture** to readers.

## Parameter Documentation Standards

From [OpenAPI Best Practices](https://learn.openapis.org/best-practices.html):

- **camelCase** for parameter names (not snake_case or kebab-case)
- **Required parameters listed before optional** in each operation
- **Explicit type** on every parameter
- **Description on every parameter** — "id" is not enough; "The user's unique identifier (ULID)"
- **Valid ranges or enum values** where applicable — "Must be 1-100" or "One of: 'pending' | 'active' | 'archived'"
- **Reusable schemas** in `components/schemas` with `$ref` references — DRY at the schema level

## Benchmark Examples from Industry

Two API reference docs are widely cited as gold-standard:

- **Stripe** — three-column layout (description / request example / response example),
  every parameter has description/type/example, errors have their own section,
  cross-cutting concerns (pagination, idempotency, webhooks) documented once.
  See [Mintlify API doc recommendations](https://www.mintlify.com/library/our-recommendations-for-creating-api-documentation-with-examples).
- **Twilio** — persistent language selector (reader sees docs in their chosen SDK),
  runnable quickstarts per language, concept docs separated from reference docs
  (Diátaxis-aligned). See [Archbee API documentation examples](https://www.archbee.com/blog/api-documentation-examples).

## Separation: Reference vs Explanation

**API reference is not API explanation.** Reference docs describe *what* the
API does; explanation docs describe *why* it exists and *how* to think about it.

Reference:
- Parameters, types, schemas, error codes
- Exhaustive, mechanically consistent, scannable

Explanation:
- Design rationale, trade-offs, historical context
- Discursive, selective, opinionated

This is a direct Diátaxis alignment. Keep them in separate files and link
between them. Mixing reference and explanation in the same doc is a
Mode Clarity gate failure.

## Structural Consistency Rule

When writing or reviewing API reference docs, verify:

- **All operations follow the same template** — if one has an "Example Errors"
  section, all should. Inconsistency forces readers to guess.
- **Shared schemas referenced consistently** — `User` should appear as `User`
  everywhere, not `User` in one place and `user_object` in another.
- **Pagination, authentication, rate limiting documented once** — at the top
  of the API reference, not repeated per operation. Operations link to these
  cross-cutting docs.

## Sources

- [OpenAPI Specification v3.2.0](https://spec.openapis.org/oas/latest.html) — primary source, Linux Foundation standard
- [OpenAPI Best Practices](https://learn.openapis.org/best-practices.html) — parameter and schema conventions
- [Mintlify — API documentation recommendations](https://www.mintlify.com/library/our-recommendations-for-creating-api-documentation-with-examples) — Stripe benchmark analysis
- [Archbee — Best API documentation examples](https://www.archbee.com/blog/api-documentation-examples) — Twilio benchmark analysis
