# Baseline brainstorm — split payment across revenue accounts

Seed: "Let the system split each incoming payment across multiple revenue accounts by configurable rules."

## Requirements / behaviors

**Core splitting**
- On receiving a payment, evaluate the applicable split rule(s) and allocate the payment amount across one or more target revenue accounts.
- Support multiple allocation methods:
  - Percentage-based (e.g. 70% / 30%).
  - Fixed-amount (e.g. $5 platform fee, remainder to merchant).
  - Mixed (fixed amounts taken first, percentage applied to the remainder).
  - Priority/waterfall (fill account A up to a cap, overflow to B).
- The sum of all allocations must exactly equal the original payment amount — no money created or lost.
- Each split produces a set of allocation records (ledger entries), one per destination account, traceable back to the source payment.

**Rule configuration**
- Rules are configurable without code changes (data/config-driven, not hardcoded).
- A rule has: matching criteria (when it applies), allocation method, ordered list of destinations with their parameters, effective date range, and an active/inactive flag.
- Rule selection: support matching by attributes such as product/SKU, merchant, channel, currency, payment method, or amount band.
- Deterministic rule resolution when multiple rules could match (explicit priority / specificity ordering, documented tie-break).
- A default/fallback rule (or explicit "no rule" behavior) when nothing matches.
- Versioning: changing a rule must not retroactively alter already-split historical payments; old payments keep the rule version that processed them.

**Accounts**
- Destination revenue accounts must be validated as existing and active before allocation.
- Support currency consistency between payment and destination accounts (or an explicit conversion step).

**Correctness & money handling**
- Use exact/decimal arithmetic (never floats) for money.
- Define a documented rounding policy and a remainder-assignment rule (largest-remainder method or "assign residual cents to a designated account") so percentages always reconcile to the exact total.
- Allocations are atomic: either all destination entries are written or none are (no partial split).

**Auditability**
- Every split is recorded with: source payment id, rule id + version, method, inputs, computed allocations, timestamp, and actor (system/user).
- Splits are reproducible — re-running the same rule on the same payment yields identical allocations.
- Support a dry-run / preview mode that shows the proposed split without committing.

**Operations**
- Idempotency: processing the same payment event twice (retry, duplicate webhook) must not double-allocate.
- Handle refunds / reversals / chargebacks: reverse or proportionally claw back the original allocations.
- Handle partial payments and later top-ups against the same invoice.
- Reporting: per-account revenue totals derivable from allocation records.

**Non-functional**
- Performance: splitting should be fast enough for the expected payment volume; consider sync vs async processing.
- Concurrency-safe under simultaneous payments.
- Observability: metrics + logs for rule matches, fallbacks, and reconciliation failures.

## Edge cases & failure modes

**Arithmetic / rounding**
- Percentages don't divide evenly (e.g. $0.01 split 3 ways, or 33/33/34) — residual cents must land somewhere deterministically.
- Percentages that don't sum to 100% (config error) — reject or normalize? Must be defined.
- Fixed amounts that exceed the payment total (e.g. $5 fee on a $3 payment) — underflow handling.
- Negative or zero payment amounts.
- Very large amounts / overflow.
- Floating-point drift if money isn't stored as integer minor units or decimals.

**Rule resolution**
- No matching rule.
- Multiple matching rules with equal priority (ambiguous tie).
- Rule references a destination account that has been deleted/deactivated.
- Rule edited mid-flight while a payment is being processed.
- Effective-date boundary: payment timestamp exactly at a rule's start/end.
- Circular or self-referential waterfall configuration.

**Currency**
- Payment currency ≠ destination account currency, with no conversion configured.
- Multi-currency split with stale or missing FX rate.
- Rounding after FX conversion breaking the sum-to-total invariant.

**Lifecycle / concurrency**
- Duplicate payment event (webhook retry) → double split.
- Crash between computing the split and persisting it → orphaned or missing allocations.
- Concurrent edits to the same rule.
- Refund arriving before the original split is committed.
- Partial refund that doesn't map cleanly back to integer-cent allocations.

**Config / data integrity**
- Empty destination list.
- Single destination (degenerate "split").
- Duplicate destination account listed twice in one rule.
- Cap/waterfall caps that are all lower than the payment amount (overflow with nowhere to go).

## Open questions

- **Money model**: are amounts stored as integer minor units, decimals, or floats? What scale/precision?
- **Rounding policy**: largest-remainder, banker's rounding, or designated residual account? Who decides per rule?
- **Sum invariant strictness**: hard-fail on configs that can't sum to total, or auto-normalize with a warning?
- **Rule matching dimensions**: which attributes are in scope for v1 (merchant, SKU, channel, currency, amount band, payment method)?
- **Tie-break semantics**: how is rule priority expressed — explicit priority field, specificity, or creation order?
- **Multi-currency**: in or out of scope for v1? If in, where does FX rate come from and when is conversion applied (before or after split)?
- **Refund/reversal handling**: proportional claw-back vs reverse-in-full vs out of scope for v1?
- **Sync vs async**: split inline with payment capture, or downstream event-driven?
- **Authorization**: who can create/edit/activate split rules, and is approval/review required?
- **Historical immutability**: confirm that rule changes never re-split past payments — is there a need to re-run/backfill ever?
- **Idempotency key**: what uniquely identifies a payment event for dedup (payment id, provider event id)?
- **Fallback behavior**: when no rule matches — reject the payment, route 100% to a default account, or hold for manual handling?
- **Preview/approval**: is a dry-run/preview required before a rule goes live?
