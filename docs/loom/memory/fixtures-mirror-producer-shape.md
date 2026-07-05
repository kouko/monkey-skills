---
name: fixtures-mirror-producer-shape
description: Test fixtures must mirror the producer's actual field shape — a hand-shaped fixture can certify code that fails on the real producer's output
type: practice
origin: PR #479 (loom-pipeline conductor v0.1, 2026-07-04)
---

A test fixture for a consumer module must mirror the PRODUCER's
actual output shape, not the consumer author's expectation of it.
Real case on PR #479: a fixture hand-written with a `name:` field
made the consumer's tests pass, certifying code that failed on the
real producer — which emits `station:`. The test suite green-lit the
exact bug it existed to prevent.

**Why:** a fixture invented from the consumer's assumptions encodes
those assumptions twice (in code and in test), so the test can never
disagree with the code; only the producer's real shape can.

**How to apply:** build fixtures by capturing or deriving from the
producing module's actual output (run the producer, copy its real
emission), and when a producer's shape changes, update fixtures from
the producer side — never patch the fixture to match the consumer.
