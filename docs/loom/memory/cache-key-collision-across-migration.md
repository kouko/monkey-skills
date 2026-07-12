---
name: cache-key-collision-across-migration
description: A new function reusing a legacy cache key but writing an incompatible payload shape under an immutable TTL is a never-self-healing 'works on my machine' landmine — give each payload shape a distinct key + a cross-function pre-seed regression test
type: gotcha
origin: branch feat-us-sec-narrative-edgartools (US SEC regex→edgartools narrative migration, 2026-07-12)
---

During the regex→edgartools narrative migration, a NEW cached fetch
(`fetch_narrative_sections`, emitting `sections` as a **list**) initially
reused the SAME cache key `narrative_{accession}` under the SAME
immutable/permanent TTL as the LEGACY `fetch_narrative` (emitting
`sections` as a **dict**). The legacy fn was still wired to the CLI, so
real machines already had dict-shaped payloads on disk. The moment the
CLI rewired to the new fn, any machine with a warm legacy cache got a
schema-passing `load_cache` HIT of the WRONG shape → `TypeError`, and the
immutable TTL meant it **never self-heals**. Invisible on a clean cache
(every test machine), it only fires on a pre-warmed one — a classic
"works on my machine" landmine. Caught by a per-task code-quality
reviewer tracing the two functions' key + payload, not by the tests.

**Why:** a cache key is a contract; two producers writing incompatible
payloads under one key silently corrupt each other across a migration
boundary. An immutable/permanent TTL removes the self-healing a short TTL
would give (a bad entry never expires away), so the corruption is
permanent for anyone who cached the old shape.

**How to apply:** when a migration adds a function that writes a
DIFFERENT payload shape to a cache, give it a DISTINCT key (suffix the
shape/version into the key, e.g. `narrative_sections_{accession}` vs the
legacy `narrative_{accession}`) — never reuse the legacy key. Add a
cross-function regression test that pre-seeds the legacy key with the OLD
shape and asserts the new function does NOT alias it (reads its own key →
miss → fresh fetch). Treat immutable-TTL caches as especially dangerous:
they can never expire a poisoned entry. See also
[[fixtures-mirror-producer-shape]] (same migration, sibling seam bug).
