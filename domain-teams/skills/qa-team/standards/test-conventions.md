# Test Conventions (Shared Standard)

This file is the single source of truth for testing standards.
Both worker (when writing test plans) and evaluator (when reviewing)
reference this file.

## Test Case Naming

- Scenario-based, not method-based
- Describe the situation and expected outcome, not the function under test
- Good: "User with expired token receives 401 and redirect to login"
- Bad: "test_validate_token_returns_false"
- Format: `{context} {action} {expected outcome}`

## Test Type Taxonomy

| Type | Scope | Boundary | When to Use |
|------|-------|----------|-------------|
| Unit | Single function/class | No external deps | Isolated logic, pure functions, algorithms |
| Integration | Module boundary | Real deps (DB, API) | Service interactions, data flow between modules |
| E2E | Full user journey | Entire system | Critical user paths, multi-step workflows |
| Performance | System under load | Production-like env | Latency, throughput, resource limits, SLO verification |
| Regression | Changed code paths | Varies | After refactoring, dependency updates, major changes |
| Smoke | Deployment sanity | Production | Post-deploy health checks, critical path verification |

When scope is ambiguous, classify by what breaks if the test fails:
- Single function -> unit
- Communication between components -> integration
- User-visible workflow -> E2E

## Pass/Fail Criteria Format

- Must be binary (pass or fail, no partial)
- Must be measurable (response code, value comparison, timing threshold)
- Must be specific (not "works correctly" or "behaves as expected")
- Good: "Response status is 200 AND body contains `user_id` field"
- Bad: "API returns the correct response"

## Risk Classification

| Level | Definition | Examples |
|-------|-----------|----------|
| High | Failure causes data loss, security breach, or revenue impact | Payment processing, auth flow, data migration |
| Medium | Failure degrades UX or breaks secondary features | Search ranking, notification delivery, report formatting |
| Low | Failure is cosmetic or affects internal tooling only | Admin dashboard styling, internal log formatting |

When classifying risk, consider:
- Frequency of use (daily vs monthly)
- Blast radius (one user vs all users)
- Data sensitivity (PII, financial, public)
- Reversibility (can the damage be undone?)
