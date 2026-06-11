# Proposal — Revenue Split (incoming-payment allocation)

**Seed:** "Let the system split each incoming payment across multiple revenue
accounts by configurable rules."

This is a spec-expansion draft produced by the GENERATE layer
(`spec-expansion` → `completeness-critic`). It is **not** complete — see the
coverage statement at the foot of this file and the non-empty
`## Blind spots` section. Domain pushed into real money-splitting and
double-entry ledger reality (conservation-of-money, rounding remainder,
immutability, reversals/refunds, idempotency).

---

## USM backbone

The happy-path spine — ordered user-journey steps, left to right:

| # | Step | Actor | Object(s) touched | Provenance |
|---|------|-------|-------------------|------------|
| 1 | Configure a split rule (allocation table + rounding policy + residual account) | Configurator | SplitRule, RevenueAccount | seeded (configurable rules) |
| 2 | Validate & activate the rule (sum-to-100% / non-overlapping effective window) | Configurator (maker) → Approver (checker) | SplitRule | inferred |
| 3 | Receive an incoming payment (webhook / settlement file) | Payment Ingest (external) | Payment | seeded (incoming payment) |
| 4 | Deduplicate on idempotency key / external id | System | Payment | critic-found |
| 5 | Match the payment to the rule in effect at its value date | System (matcher) | Payment, SplitRule | inferred |
| 6 | Execute a SplitRun: compute per-account allocations | System (engine) | SplitRun, SplitAllocation | seeded (split across accounts) |
| 7 | Distribute the rounding remainder to the residual account | System (engine) | SplitAllocation | critic-found |
| 8 | Balance-check: assert Σ allocations == splittable base to the minor unit | System (engine) | SplitRun, SplitAllocation | critic-found |
| 9 | Post double-entry ledger entries atomically | System | LedgerEntry | inferred |
| 10 | Reconcile against the settlement source / GL | Auditor | LedgerEntry, Payment | inferred |
| 11 | (Off-spine) Reverse / refund: emit compensating run + contra entries | System / Approver | SplitRun, LedgerEntry | critic-found |

The spine is steps 1→10; step 11 is the dominant off-happy-path branch
(refund / chargeback / reversal) that the seed implies but does not state.

---

## OOUX object model

Six first-class objects. Money is stored in **integer minor units** (never
float); the load-bearing invariant is **conservation of money** — the sum of
posted allocations equals the splittable base to the cent.

### Object inventory

| Object | One-line role |
|--------|---------------|
| **Payment** | A single inbound money event arriving to be split. |
| **SplitRule** | The configurable, versioned, effective-dated spec that divides a payment. |
| **RevenueAccount** | A destination GL account receiving one slice (credit side). |
| **SplitRun** | One execution of the engine against one Payment (the unit of work + audit record). |
| **SplitAllocation** | One slice: amount assigned to one account from one payment via one rule. |
| **LedgerEntry** | The immutable posted double-entry record that makes an allocation real. |

### Payment — state machine

Attributes: `id`, `external_id`, `idempotency_key`, `amount_minor`,
`currency`, `gross/fee/net_amount_minor` (which is the splittable base is a
declared field), `direction` (inbound/refund/chargeback),
`original_payment_id`, `source`, `received_at`, `value_date`,
`resolved_rule_set_id` + `version`, `allocated_total_minor`, `status`.

```
received → matching → matched → splitting → split_ok → posting → posted
received → duplicate (terminal, idempotency collision)
matching → unmatched → (manual-match) → matched | (cancel) → cancelled
matched → on_hold → (release) → matched
splitting → split_failed (no rule / rounding-unbalanced / engine error) → (fix) → splitting
posting → partial_posted → (retry) → posted | → posting_blocked
posted → reversing → reversed (terminal)   |   posted → refund_partial
terminal: posted, cancelled, duplicate, reversed
```

### SplitRule — state machine

Attributes: `rule_id` (stable), `version` (monotonic), `rule_type`
(percentage/fixed/tiered/waterfall), `allocation_table`
(`{account_id, weight_bps?, fixed_amount?, tier_bounds?, seq}`),
`rounding_policy` (half_even/half_up/floor/largest_remainder),
`residual_account`, `priority`, `scope_selector`, `effective_from/to`
(half-open `[from,to)`), `currency`, `created_by/validated_by/activated_by`.
Invariants: percentage Σ weight_bps == 10000; effective windows per
(rule_id, scope) non-overlapping; one residual account.

```
draft → validated → active → superseded (newer version activated)
draft → validated → scheduled (future effective_from) → active (clock reaches from)
validated → invalid (sum≠100% / overlapping window / bad scope) → (return to draft)
active → retired (end-of-life, no successor)
immutability: once it leaves draft, the allocation table is frozen → clone-to-new-version
```

### RevenueAccount — state machine

Attributes: `account_id`, `name`, `gl_code`, `currency`, `account_type`
(revenue/clearing/suspense/residual), `active`, `parent_account_id`,
`allow_residual`, `pending_allocation_count` (derived).

```
inactive ↔ active → frozen → (unfreeze) → active
active/inactive/frozen → closed (GUARDED: pending_allocation_count==0 & zero unsettled balance)
closed = terminal; never hard-delete while any historical allocation/entry references it
```

### SplitRun — state machine

Attributes: `id`, `payment_id`, `rule_set_id` + `version` (pinned),
`kind` (initial/re-split/reversal/refund), `supersedes_run_id`,
`reverses_run_id`, `idempotency_key`, `splittable_base_minor`,
`rounding_strategy`, `remainder_minor`, `remainder_account_id`,
`allocated_total_minor`, `balance_delta_minor` (MUST be 0 to post),
`failure_code`, `attempt_no`, `engine_version`.

```
queued → running → computed → balanced → posting → posted (terminal)
running → failed (NO_RULE / ACCOUNT_CLOSED / FX_MISSING / ENGINE_ERROR)
computed → unbalanced (balance_delta_minor != 0) → failed
posting → post_failed → (retry) → posting | → aborted (terminal)
failed → superseded (operator fixes rules → new run at queued)
posted → reversing → reversed (terminal, compensating run with negated allocations)
queued → cancelled (terminal)
```

### SplitAllocation — state machine

Attributes: `payment_id`, `rule_id`, `account_id`, `run_id`, `amount`
(minor units), `currency`, `rounding_adjustment` (signed, non-zero only on
the residual slice), `is_residual`, `computed_at`, `status`.

```
computed → balanced (Σ over run == payment) → posted → (reversed | refunded)
computed → unbalanced (Σ ≠ payment) → BLOCKS posting until remainder reassigned
```
Invariant: `Σ allocation.amount over a SplitRun == splittable base` including
signed `rounding_adjustment`. No allocation reaches `posted` outside a
balanced run.

### LedgerEntry — state machine

Attributes: `entry_id`, `allocation_id`, `debit_credit`, `amount` (positive;
direction in `debit_credit`), `currency`, `account_gl_code`, `posted_at`,
`reversal_of` (nullable), `immutable`, `journal_id`.

```
draft → posted (Journal commit, debits==credits) → immutable=true (TERMINAL row)
posted → [reverse] → creates NEW contra entry (reversal_of=entry_id, swapped leg, same amount)
         original row stays byte-for-byte intact; logical status = reversed-by-contra
NO deleted state, NO edit path — corrections are append-only contra entries
```
Invariants: within a Journal Σ debits == Σ credits at all times; posted is
terminal at the row level; reversal symmetry (contra nets original to zero).

---

## Path × edge matrix

The cartesian grid `backbone × object × CTA × state` over-generates; the
table below is **post-prune** — surviving legal paths + the edge cases each
lens surfaced. Illegal cells (e.g. "post a LedgerEntry for an unbalanced
run", "credit a closed account") are dropped.

### Surviving happy paths (state-transition legality lens)

| Path | Object | CTA | From → To state |
|------|--------|-----|-----------------|
| P1 | SplitRule | validate+activate | draft → validated → active |
| P2 | Payment | receive | (none) → received |
| P3 | Payment | match | received → matched |
| P4 | SplitRun | execute | queued → running → computed → balanced |
| P5 | SplitAllocation | compute+balance | computed → balanced |
| P6 | SplitRun | post | balanced → posting → posted |
| P7 | LedgerEntry | post | draft → posted (immutable) |

### Surviving edges (per lens)

| Lens | Edge case | Object/state |
|------|-----------|--------------|
| state-transition | No active rule matches the payment | Payment → unmatched / SplitRun → failed (NO_RULE) |
| state-transition | Rule matches but a target account is closed/frozen | SplitRun → failed (ACCOUNT_CLOSED) / route-to-suspense |
| state-transition | Refund/chargeback arrives | Payment → reversing; compensating SplitRun; contra LedgerEntries |
| state-transition | Out-of-order: refund arrives before original payment | Payment → unmatched (no original_payment_id resolvable) |
| BVA | Payment amount = 0 | reject or no-op split (declared) |
| BVA | Payment amount = 1 minor unit, N>1 accounts | remainder dominates; residual takes the penny |
| BVA | Percentage weights sum to 9999 or 10001 bps | SplitRule → invalid |
| BVA | Rounding remainder of N−1 pennies across N accounts | largest-remainder / residual assignment |
| BVA | Fixed amounts exceed payment (negative residual) | SplitRun → failed (over-allocation) |
| BVA | Max-precision / very large amount (overflow) | integer minor-unit bounds |
| CRUD | Create rule / Read run / Update = clone-new-version / Delete = retire (no hard delete) | SplitRule lifecycle |
| CRUD | RevenueAccount close blocked by pending allocations | RevenueAccount → closed (guarded) |
| CRUD | LedgerEntry has no Update/Delete — append-only | LedgerEntry immutability |
| permissions | Who may activate a rule (maker ≠ checker) | SplitRule activate (segregation of duties) |
| permissions | Who may reverse/refund (high-privilege) | SplitRun reverse |
| permissions | Auditor is read-only; cannot mutate ledger | LedgerEntry review |
| empty/error/loading | No residual account configured but remainder exists | SplitRun → unbalanced → failed |
| empty/error/loading | Empty allocation table | SplitRule → invalid |
| empty/error/loading | All target accounts inactive | SplitRun → failed |
| empty/error/loading | Engine mid-computation (loading) crash | SplitRun → failed (ENGINE_ERROR), no partial post |
| NFR/concurrency | Duplicate webhook delivery (same idempotency_key) | Payment → duplicate (short-circuit) |
| NFR/concurrency | Rule edited/activated while a run is computing | version-pinning at run start; activation race window |
| NFR/concurrency | Torn write during posting (partial post) | SplitRun → post_failed → retry (idempotent) |
| NFR/concurrency | Re-trigger of an already-posted run | idempotency short-circuit (no double-post) |
| NFR | Multi-currency: rule currency ≠ payment currency | FX needed; SplitRun → failed (FX_MISSING) if no rate |

---

## Provenance

Every emitted item is tagged. Lineage: `seeded` (in/entailed by the seed),
`inferred` (model-derived from OOUX/USM/lens priors), `critic-found`
(surfaced by the completeness-critic loop and re-seeded).

### seeded
- Object **Payment** ("each incoming payment").
- Object **RevenueAccount** ("multiple revenue accounts").
- Object **SplitRule** ("configurable rules").
- The split **CTA** — divide one payment across many accounts.
- Multiplicity: one payment → N accounts.

### inferred
- Objects **SplitRun**, **SplitAllocation**, **LedgerEntry** (the work unit,
  the slice, the posted record — accounting reality not stated in the seed).
- All six state machines.
- USM steps 2 (validate/activate), 5 (match), 9 (post), 10 (reconcile).
- Rule typing (percentage/fixed/tiered/waterfall), effective-dating,
  rule versioning + pinning.
- Actors: Configurator, Auditor, Payment Ingest.

### critic-found
- **Idempotency / duplicate-delivery** dedup (USM step 4) — system-layer
  concurrency lens.
- **Rounding remainder** distribution + **residual account** (USM step 7) —
  BVA + empty/error lens; the penny-conservation gap.
- **Balance-check gate** (USM step 8, Σ == base) — the conservation invariant
  the writer left implicit.
- **Reversal / refund / chargeback** branch (USM step 11) — state lens.
- **Maker ≠ checker** segregation of duties on rule activation — permissions
  lens.
- **Multi-currency / FX** mismatch (rule vs payment currency) — NFR lens.
- **Over-allocation / negative residual** (fixed amounts > payment) — BVA.
- **Out-of-order** refund-before-original — system-layer timing lens.
- **All-accounts-inactive / account-closed-mid-run** routing to suspense —
  state lens.
- **Append-only ledger** (no delete/edit; contra-entry only) — policy lens.

---

## Blind spots — needs human/field input

These gaps were *located* by the critic but **cannot be closed** from the
seed + LLM priors — they need the named human/field source. Inventing a
plausible value here would be worse than naming the gap.

- **Splittable base definition** — does a rule apply to *gross*, *net*, or
  *post-fee* amount? Changes every number. → **Finance/accounting owner**.
- **Rounding policy of record** — banker's rounding vs largest-remainder vs
  floor-to-residual; jurisdictions and contracts mandate specific policies. →
  **Accounting policy + legal**.
- **Revenue-recognition timing** — is "posted" the recognition event, or is
  recognition deferred (ASC 606 / IFRS 15 performance obligations)? →
  **Controller / external audit**.
- **Tax treatment** — does the split cross tax entities/jurisdictions
  (VAT/GST, withholding)? Per-account tax handling is unspecified. → **Tax
  advisor**.
- **FX rate source & timing** — when rule currency ≠ payment currency, which
  rate (transaction date / value date / settlement date) and which provider?
  → **Treasury**.
- **Data retention period** for payments + ledger (PII + financial records;
  often 7–10 yrs by jurisdiction). → **Legal/compliance**.
- **Authorization matrix** — exact roles permitted to create/activate/reverse
  rules; whether dual-control is legally required. → **Risk/compliance**.
- **SLA / latency / throughput** targets — settlement-file batch size, posting
  latency budget, peak TPS. → **Ops / SRE + business**.
- **Chargeback & dispute workflow** — does a chargeback auto-reverse the split
  or wait for dispute resolution? Timing and liability are policy. →
  **Payments ops + legal**.
- **Conflict resolution when two rules match** the same scope at the same
  priority — tiebreak is undefined. → **Product/business owner**.
- **Negative / partial-refund propagation policy** — pro-rata vs
  last-in-first-out vs rule-defined order across the conservation set. →
  **Finance owner**.

---

_Coverage relative to seed + 7 lenses (state-transition / BVA / CRUD /
permissions / empty-error-loading / NFR / policy-legal), 6 objects; critic
loop ran to K=2 consecutive dry rounds. **Not complete** — the blind spots
above need human/field input and the seed sets the ceiling._
