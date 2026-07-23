---
name: producer-marker-inert-until-consumer-branches-on-it
description: A producer emitting a structured sentinel/refusal marker (e.g. dcf_compute's `{"not_applicable":"financial-sector"}`) is INERT until every consumer of that output explicitly branches on it — until then the downstream silently degrades (a null field, a dropped memo section), it never errors. Shipping the marker is only half the fix; wiring each consumer to recognize it belongs in the SAME change. The dual of a missing-field 0-default — same producer↔consumer contract, a sentinel instead of a value.
type: gotcha
origin: branch tw-fin-ixbrl-followups (2026-07-24, shipped as 2.32.1) — the 2.31.0 arc shipped dcf_compute's `not_applicable` financial-sector marker (producer side) and treated the DCF-guard as done; no consumer branched on it, so a financial-ticker memo silently rendered `intrinsic_mid: null` with no explanation until this follow-up arc wired the three render surfaces.
---

A producer that emits a NEW structured sentinel — a refusal object, a
`not_applicable` marker, a degraded-mode flag — has done nothing observable
until every consumer that reads that output grows an explicit branch for the
sentinel. `dcf_compute` shipped a flat `{"ticker", "not_applicable":
"financial-sector", "reason", "_provenance"}` object in 2.31.0; the producer's
own tests passed, the artifact-existence gate (`ls dcf.json`) passed, and the
arc was declared done. But no consumer branched on the marker: the memo
frontmatter's `intrinsic_mid` (sourced from `dcf.json`'s `mid`) resolved to a
silent `null`, the verdict prose keyed on an absent `rule_verdict` simply
vanished, and the reader saw a memo with no valuation section and no reason —
degraded, not errored.

**Why it hides:** emitting the marker feels like the fix — the guard is
"fail-loud" at the producer. But loudness at the producer is silence at the
consumer unless the consumer is taught to listen. A sentinel is inert data;
only a consumer `if marker: render N/A else: …` makes it behavior. The
producer's SDD triad never sees the consumer surfaces (different skills,
different plugins), so the per-task reviews all pass while the end-to-end memo
silently degrades. Only a live end-to-end dogfood on a real affected ticker
(here: 國泰金 2882.TW) — or a whole-branch review that traces the marker from
producer emit to every consumer read — surfaces it.

**How to apply:** when you add a producer-side sentinel/marker/refusal, grep
every consumer of that producer's output and wire each one to branch on the
sentinel IN THE SAME CHANGE — emitting it is half the work. Treat "producer
emits the marker" and "every consumer recognizes the marker" as one atomic
unit, not two arcs. And verify with an end-to-end run on a ticker/input that
actually triggers the marker, not just the producer's unit tests: a marker no
consumer reads is silent degradation, not a shipped feature. Dual of
[[market-canonical-must-satisfy-consumer-field-contract]] (missing field →
silent 0-default): there the producer omits a value; here the producer emits a
sentinel — both fail as a silently-wrong downstream that every producer-side
test stays green through.
