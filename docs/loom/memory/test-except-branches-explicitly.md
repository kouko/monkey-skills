---
name: test-except-branches-explicitly
description: A green suite can hide a crash in an except branch with zero coverage — e.g. catching tokenize.TokenizeError, which is not a real stdlib name (it's TokenError)
type: practice
origin: PR #454 (living-spec index capstone G PR-1, 2026-06-24)
---

A fully green test suite can hide a guaranteed crash inside an
`except` branch that no test ever executes. Real case: code caught
`tokenize.TokenizeError` — which is not a real name in Python's
stdlib (the actual exception is `tokenize.TokenError`) — so the
handler itself raises `AttributeError` the moment it is entered. A
95-test green suite hid this because the error path had zero
coverage.

**Why:** Python resolves attribute names at runtime, so a misspelled
exception class in an `except` clause is not caught by import,
linting alone, or any test that stays on the happy path; the crash
fires exactly when the code was supposed to degrade gracefully.

**How to apply:** write an explicit test for every error-handling
branch — feed it input that actually raises, and assert the handled
outcome. Treat an `except` clause with no covering test as untested
code, not as safety.
