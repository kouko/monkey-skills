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

**Second instance — mock the real PRODUCER boundary, not an
intermediate projection (US SEC edgartools migration, branch
feat-us-sec-narrative-edgartools, 2026-07-12):** the offline tests
mocked `acquire_filing` (a *projection* fn returning a JSON **dict**
ref) instead of the real producer boundary `edgar.get_by_accession_
number` (which returns a raw edgartools Filing OBJECT). Downstream
`segment_filing` needs the raw object (`.obj()`/`.form`), so the
production path crashed (`'dict' object has no attribute 'form'`)
while the whole offline suite stayed green — the mock invented a
shape the projection never emits, masking a cross-function seam. Fix:
mock the real producer boundary so the acquire→segment seam runs
faithfully. **Corollary — a network-marked LIVE shape-anchor that
captures the producer's actual attributes is worth the flake budget:
it caught the plan's edgartools grounding wrong THREE times**
(`Filing.primary_document` doesn't exist → derive from `filing_url`;
`TenQ` has no `management_discussion` property → subscript
`obj["Part I, Item 2"]`; 8-K `obj()` is `CurrentReport`, not
`EightK`). Mocking one layer up from the real producer, and skipping
a live anchor, are the two ways a green suite certifies a crash.

**Third instance — a hand-shaped fixture can encode a SPEC ASSUMPTION
the real producer contradicts (US SEC financial-table xval, branch
feat-us-sec-financial-table-xval, 2026-07-13):** the brief assumed
edgartools exposes a rendered/scaled DISPLAY value (e.g. "$1,234"
millions) distinct from the full-magnitude fact. Task 10's tests
hand-shaped a `value_displayed: "$1,234"` cell to match that
assumption and passed — but the REAL captured fixture
(`xval_source_a_aapl_bs.json`, from the live anchor) shows
`value_displayed == numeric_value` on all 152 cells (edgartools has NO
retrievable scaled-display field across `get_statement` /
`facts.to_dataframe()` / even `render().to_dict()` — the "$" mantissa
is only a transient `__str__` formatting artifact). The whole-branch
code-quality reviewer caught it by running the check against the real
committed fixture (133/152 real cells produced garbage), not the
invented one — the exact fixture-grounding check that turns "tests
green" into "green on real data". Resolution required a live probe +
a user-approved design reframe (single-source → two-source), not a
test patch. **Takeaway: a fixture is only as trustworthy as its
distance from the real producer; when a spec ASSERTS an external
library's field, capture the library's real output before encoding
the assumption into a fixture.**
