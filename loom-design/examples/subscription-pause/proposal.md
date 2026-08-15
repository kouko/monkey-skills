# Proposal — Subscription Pause

> **Seed:** "Let a customer pause their paid subscription for up to 3 months."
>
> GENERATE-layer spec draft produced by `loom-spec:spec-expansion` (3 phases)
> then extended by `loom-spec:completeness-critic` (loop-until-dry, 7 lenses).
> This is **coverage relative to seed + lenses**, never a completeness claim.

---

## USM backbone

*Phase ① artifact — the happy-path spine of ordered user-journey steps.*
Extraction folds in here: actors, journey, objects, CTAs — each tagged
`seeded` / `inferred`.

**Actors**
- **Customer** — the paying subscriber initiating the pause (`seeded` — "a customer").
- **Billing system** — charges, prorates, schedules resume (`inferred`).
- **Payment provider / PSP** — Stripe-class processor that holds the saved
  payment method and runs the resume-charge (`inferred`).
- **Support agent / admin** — may pause on a customer's behalf, may override
  the 3-month cap (`inferred`).
- **Scheduler / cron** — the unattended actor that fires auto-resume when the
  pause window ends (`inferred`).
- **Dunning / collections system** — the actor that owns past-due accounts; a
  pause request collides with its jurisdiction (`inferred`, critic-confirmed).

**Backbone steps (B1…B8 — the spine)**

| # | Step | Actor | CTA | Object touched | Provenance |
|---|------|-------|-----|----------------|------------|
| B1 | View active subscription & eligibility | Customer | `read` | Subscription | inferred |
| B2 | Request a pause (choose duration ≤ 3 mo) | Customer | `requestPause` | PauseRequest | seeded |
| B3 | System validates eligibility & duration | Billing | `validate` | PauseRequest | inferred |
| B4 | Confirm pause (preview resume date, billing effect) | Customer | `confirmPause` | PauseRequest | inferred |
| B5 | Subscription enters `paused`; access changes | Billing | `applyPause` | Subscription | seeded (entailed) |
| B6 | Pause window elapses (≤ 3 mo) | Scheduler | `elapse` | Pause | inferred |
| B7 | Auto-resume: re-activate + resume billing | Scheduler/Billing | `resume` | Subscription | inferred |
| B8 | Customer back to active / next invoice issued | Billing | `charge` | Invoice | inferred |

**Off-spine but seed-adjacent (named here, expanded in the matrix):** early
manual resume (B5→B7 before B6), pause cancellation, pause extension, pause
*during* a free trial, pause of an already-past-due account.

---

## OOUX object model

*Phase ② artifact — object inventory (ORCA per object) + each object's state
machine. Fanned out per-object (disjoint objects, parallel-shaped work).*

### Object: Subscription
- **Relationships:** has-many Invoices; has-one current PauseRequest/Pause;
  belongs-to Customer; references a Plan and a PaymentMethod.
- **CTAs:** `read`, `requestPause`, `confirmPause`, `applyPause`, `resume`,
  `cancel`, `changePlan`, `extendPause`, `cancelPause`.
- **Attributes:** `status`, `plan_id`, `current_period_end`, `paused_at`,
  `resume_at`, `pauses_used_in_window`, `cancel_at_period_end`,
  `payment_method_id`, `dunning_state`, `trial_end`.
- **State machine:**
  - States: `trialing`, `active`, `pause_pending` (requested, not yet effective),
    `paused`, `past_due`, `canceled`, `expired`.
  - Transitions:
    - `active → pause_pending` (requestPause, valid)
    - `pause_pending → paused` (confirmPause / period boundary reached)
    - `pause_pending → active` (customer abandons confirm; request expires)
    - `paused → active` (resume — auto at B6, or manual early resume)
    - `paused → canceled` (customer cancels while paused)
    - `paused → paused` (extend, only if cumulative ≤ 3 mo cap)
    - `active → past_due` (charge fails — orthogonal, gates pause eligibility)
    - `trialing → pause_pending?` ← **illegal/undecided** (BVA + policy lens)
    - `past_due → pause_pending?` ← **illegal/undecided** (policy lens)

### Object: PauseRequest
- **Relationships:** belongs-to Subscription; created-by Actor (customer or admin).
- **CTAs:** `create`, `validate`, `confirm`, `expire`, `withdraw`.
- **Attributes:** `requested_duration`, `requested_at`, `requested_by`,
  `effective_date`, `expires_at`, `status`, `reason_code`.
- **State machine:** `draft → pending → confirmed` (→ becomes a Pause) |
  `pending → expired` (not confirmed in time) | `pending → withdrawn`.

### Object: Pause (the active pause instance / window)
- **Relationships:** belongs-to Subscription; produces a resume event.
- **CTAs:** `start`, `extend`, `endEarly`, `elapse`, `read`.
- **Attributes:** `start_date`, `scheduled_end`, `actual_end`, `duration_used`,
  `extension_count`, `initiated_by`.
- **State machine:** `scheduled → running → ended` (elapse or endEarly) |
  `running → running` (extend, ≤ cap).

### Object: Invoice / Billing cycle
- **Relationships:** belongs-to Subscription; references a payment attempt.
- **CTAs:** `prorate`, `suspend`, `resumeCharge`, `void`, `issue`.
- **Attributes:** `period_start`, `period_end`, `amount`, `prorated`, `status`.
- **State machine:** `scheduled → suspended (during pause) → resumed → charged` |
  `charged → failed → retried` (dunning).

### Object: Plan / Entitlement
- **Relationships:** referenced-by Subscription; gates feature access.
- **CTAs:** `read`, `downgradeAccessOnPause`, `restoreOnResume`.
- **Attributes:** `price`, `features`, `access_during_pause` (none/read-only/full).
- **State machine:** `full → restricted (paused) → full (resumed)`.

### Object: Customer / Account
- **Relationships:** has-many Subscriptions; has-one PaymentMethod.
- **CTAs:** `requestPause`, `authenticate`, `viewStatus`.
- **Attributes:** `account_status`, `locale`, `tax_region`, `consent_state`.

---

## Path × edge matrix

*Phase ③ artifact — cartesian grid `backbone × object × CTA × state`, then
pruned through 7 lenses. Illegal cells dropped; surviving paths + surfaced
edges below. The grid deliberately over-generates; pruning is the work.*

### Grid (shape)
`8 backbone steps × 6 objects × ~9 CTAs × ~7 states` ≈ several hundred raw
cells. Most are illegal (e.g. `resume` on a `canceled` subscription) or
duplicate. The lens pass below keeps the legal/load-bearing survivors.

### Surviving paths & edges (post-prune, grouped by lens)

**Lens — state-transition legality** (keep legal, flag invalid, drop impossible)
- ✅ P1 `active → pause_pending → paused` (canonical happy path).
- ✅ P2 `paused → active` via auto-resume at window end.
- ✅ P3 `paused → active` via **manual early resume** before window ends.
- ✅ P4 `paused → paused` extend, **only if** cumulative duration ≤ 3 mo.
- ✅ P5 `pause_pending → active` (customer abandons confirm → request expires).
- ⚠️ E1 `trialing → pause_pending` — **invalid-or-undecided**: pausing a trial
  is ambiguous (no paid period to suspend). Flag, do not silently allow.
- ⚠️ E2 `past_due → pause_pending` — **flag**: pausing to dodge a failed charge.
- ⛔ drop `canceled → paused`, `expired → resume` (impossible).

**Lens — BVA (boundary-value analysis)** (data edges)
- ⚠️ E3 duration = **0 months** / negative → reject.
- ⚠️ E4 duration = **exactly 3 months** → allowed (boundary inclusive).
- ⚠️ E5 duration = **3 months + 1 day** → reject (off-by-one over the cap).
- ⚠️ E6 **cumulative across multiple pauses** in a rolling window hits 3 mo:
  is the cap *per-pause* or *per-window*? Boundary depends on policy (blind spot).
- ⚠️ E7 pause requested with **0 days remaining** in current billing period
  (effective-date == period boundary) — does it start now or next period?
- ⚠️ E8 resume_at lands on a **non-existent calendar date** (pause on Jan 31 for
  1 month → Feb 31?) → date-normalization edge.

**Lens — CRUD completeness per object**
- ✅ Create: PauseRequest created (B2). Read: customer/admin can read pause
  status + resume date (B1). Update: extend / change duration before confirm.
- ⚠️ E9 **Delete/cancel a pending request** before it takes effect (withdraw).
- ⚠️ E10 **Cancel an active pause** (resume immediately) vs let it run.
- ⚠️ E11 Read for **anonymous/expired-session** actor → must not leak status.

**Lens — permissions** (who may perform each CTA; unauthorized paths)
- ✅ P6 Customer may pause **their own** subscription.
- ⚠️ E12 Customer attempts to pause **another customer's** subscription → deny.
- ⚠️ E13 **Admin/support** pauses on behalf of customer → allowed + audited.
- ⚠️ E14 Admin **overrides the 3-month cap** → allowed only with audit + reason.
- ⚠️ E15 Pause CTA exposed to a **read-only / unauthenticated** role → deny.

**Lens — empty / error / loading states**
- ⚠️ E16 Customer has **no active subscription** → pause CTA absent/disabled.
- ⚠️ E17 **Loading**: eligibility check pending → no double-submit (idempotency).
- ⚠️ E18 **Error**: billing API down at confirm → request neither lost nor
  half-applied (atomicity).
- ⚠️ E19 Subscription **already paused** → block duplicate pause; show resume CTA.

**Lens — NFR (performance / security / concurrency / network / timing)**
- ⚠️ E20 **Concurrency**: customer clicks pause while scheduler fires renewal
  charge → race between `applyPause` and `charge`.
- ⚠️ E21 **Idempotency**: double-submit of `requestPause` must not create two
  pauses / double-credit.
- ⚠️ E22 **Network/partial-failure**: pause recorded locally but PSP
  not-notified → resume-charge later fails silently.
- ⚠️ E23 **Timing/ordering**: auto-resume job runs late (cron lag) → customer
  paused longer than 3 mo; SLA on resume punctuality.
- ⚠️ E24 **Security**: pause endpoint as a way to suppress dunning / evade a
  charge — abuse vector.

**Lens — policy / legal** (added by critic, see below)
- ⚠️ E25 **Proration / refund** on pause mid-period — refund the unused days or
  carry forward? Money-movement, legally sensitive.
- ⚠️ E26 **Annual / prepaid plans** — what does "pause" mean when already paid
  for the year? Extend the term vs credit?
- ⚠️ E27 **Coupons / discounts / committed contracts** — does the pause pause
  the discount clock? Does it breach a minimum-term commitment?
- ⚠️ E28 **Tax / invoicing jurisdiction** — a suspended invoice may still have
  tax-reporting obligations in some regions.
- ⚠️ E29 **Consumer-protection / cooling-off** law may mandate pause rights or
  forbid auto-resume without re-consent (region-dependent).

---

## Provenance

Every emitted item tagged `seeded` / `inferred` / `critic-found`.

**seeded** (in or directly entailed by the seed text)
- Actor: Customer.
- Object: Subscription (a *paid* subscription).
- CTA: pause (`requestPause`).
- Constraint: maximum duration **3 months** (the cap).
- Entailed: a `paused` state distinct from `active`; a resume after the window.

**inferred** (derived from OOUX/USM/lens priors — not in the seed)
- Actors: Billing system, PSP, Admin/support, Scheduler.
- Objects: PauseRequest, Pause, Invoice/Billing cycle, Plan/Entitlement,
  Customer/Account.
- Backbone steps B1, B3, B4, B6, B7, B8.
- Edges E1–E24 except where re-tagged critic-found below.
- Manual early resume, pause extension, pause cancellation, confirm-preview.

**critic-found** (surfaced by the completeness-critic loop, re-seeded)
- Actor: **Dunning/collections system** (R1, lens 1 — missing actor).
- Entitlement/access semantics during pause: none/read-only/full (R1, lens 2).
- **Proration / refund on mid-period pause** — E25 (R1, lens 5).
- **Annual/prepaid plan pause semantics** — E26 (R2, lens 5).
- **Coupon/discount/committed-contract interaction** — E27 (R2, lens 5).
- **Tax/invoicing-jurisdiction obligation during pause** — E28 (R2, lens 4).
- **Consumer-protection / cooling-off / re-consent on auto-resume** — E29
  (R2, lens 5).
- **Cron-lag SLA on resume punctuality** — E23 (R1, lens 3).
- **Pause-as-dunning-evasion abuse vector** — E24 (R2, lens 4).
- **Per-pause vs per-rolling-window cap semantics** — E6 (R1, lens 2 boundary).
- **Payment-method expiry during pause** (R3, lens 3 — re-seeded scenario S-RESUME-FAIL).

---

## Blind spots — needs human/field input

*The critic's load-bearing output. Non-empty by rule. These are
unknowable-from-seed business/domain/legal facts — naming the gap, never
inventing the answer.*

- **B1 — Cap semantics: per-pause vs per-rolling-window vs lifetime.** "Up to 3
  months" does not say whether a customer can pause 3 mo, resume, then pause 3
  mo again next quarter. *Source: product/billing policy owner.*
- **B2 — Proration & refund policy.** Pause mid-period: refund unused days,
  carry credit forward, or freeze the clock? Money movement with finance/legal
  implications. *Source: finance + legal.*
- **B3 — Entitlement during pause.** Does the customer keep read-only access,
  full access, or lose access entirely while paused? Affects entitlement
  service + churn metrics. *Source: product owner.*
- **B4 — Annual/prepaid & committed-contract handling.** What "pause" means for
  already-paid annual plans or minimum-term commitments is undefined.
  *Source: contracts/legal + billing.*
- **B5 — Auto-resume re-consent & dunning.** If the saved payment method is
  expired/declined at resume, what is the policy — retry schedule, grace,
  auto-cancel, notify? And does any jurisdiction require fresh consent before
  re-charging after a pause? *Source: legal (per-region) + payments ops.*
- **B6 — Consumer-protection / regulatory mandates.** Some jurisdictions
  legislate pause/cancellation rights and cooling-off; the seed gives no
  region. The actual legal jurisdiction(s) cannot be derived from the seed.
  *Source: legal review per operating region.*
- **B7 — Resume-punctuality SLA.** Acceptable cron lag for auto-resume (and who
  eats the cost of an over-long pause) is a business SLA, not derivable.
  *Source: ops/SRE + product.*
- **B8 — Abuse threshold.** Whether/when repeated pausing constitutes abuse
  (e.g. pausing to dodge dunning) and the enforcement response is a policy
  judgment. *Source: risk/fraud + product.*
- **B9 — Tax obligations on suspended invoices.** Whether a suspended billing
  period carries tax-reporting duties is region- and entity-specific.
  *Source: tax/accounting.*
- **B10 — Notification & comms requirements.** What the customer must be told,
  when (pause-confirmed / X days before auto-resume / resume-charged), and via
  which channel — partly legally mandated, partly product. *Source: product +
  legal.*

---

**Coverage statement:** This draft represents **coverage relative to the seed +
7 lenses** (state-transition / BVA / CRUD / permissions / empty-error-loading /
NFR / policy-legal), extended by **3 critic rounds** (loop terminated after
2 consecutive dry rounds, K=2). It is **not complete** — the 10 blind spots
above are unresolved business/legal/domain facts that no generator can
manufacture and that require human/field input before implementation.
