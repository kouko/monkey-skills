---
name: market-canonical-must-satisfy-consumer-field-contract
description: When a new data source fills a canonical/normalized structure that downstream analysis reads, its output must emit EVERY field the consumers read — a partial schema silently resolves missing fields to 0/default (e.g. dcf_compute net_debt=0), producing wrong results with no error. The producer's own tests pass; only whole-branch review comparing producer output to consumer field-reads catches it.
type: practice
origin: branch xbrl-tw (2026-07-19) — TW iXBRL canonical replaced the yfinance stub in pack_tw memo-fetch but omitted total_debt/cash/capex/ebit/fcf; dcf_compute silently zeroed them, overstating every TW equity value
---

When a new producer (a market data client) replaces or fills a canonical
structure that a separate consumer skill reads, the producer's field set must
be a **superset** of what every consumer reads. In investing-toolkit the TW
iXBRL canonical builder emitted `total_assets/liabilities/equity` + cash-flow
totals but omitted `total_debt`/`cash`/`capex`/`ebit`/`fcf`. The consumer
`analysis-dcf/dcf_compute.py` does `total_debt = (_safe_get_series(bs,
"total_debt") or [0.0])[0]` — a documented safe-default that silently
resolved to **0.0**, making `net_debt = 0` for every TW ticker and
**overstating equity value** in every TW memo, with no error raised.

**Why:** the producer's own SDD tests (parser, canonical, wiring) all passed —
they assert the producer's *stated* fields, not the consumer's *required*
ones. The two skills live in different directories; the per-task triad never
sees the contract. Only the whole-branch code-review, reading the canonical
output against `dcf_compute`'s field-reads, caught it. Even after the fix, a
subtler variant survived (total_debt = LT-only, omitting short-term borrowings
→ same upward-bias direction, smaller magnitude) — caught by the *next*
whole-branch pass.

**How to apply:** when a task wires a new producer into an existing canonical
consumed elsewhere, **grep the consumer for the exact keys it reads** and
assert the producer emits all of them, with a real traced value — before
declaring the wiring done. A field silently defaulting to 0 in a valuation is
a wrong answer, not a missing feature. Related: [[fixtures-mirror-producer-shape]].
