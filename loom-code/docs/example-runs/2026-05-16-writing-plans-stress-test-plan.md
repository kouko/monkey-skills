# Plan: Payments — Part 1 (card on file → single charge)

**Source brief**: inline chat brief, 2026-05-16 (payment processing module). Split into 4 sequential parts per writing-plans §Plan size ceiling — original brief's Smallest End State enumerated five distinct features (card on file, auto-billed monthly, dashboard receipts, webhook-driven status sync, refund flow), violating the 5-task ceiling. This is Part 1 of 4.
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible (see Notes for DAG)
**Plan-document-reviewer verdict**: PASS (2026-05-16, 12/12 checks; 3 observational notes recorded in `## Notes`)

## Part 1 scope (this plan)

True Smallest End State for replacing manual invoicing: **one SaaS customer can save a card on file and be charged once via an admin-triggered service call.** No webhooks, no dashboard, no auto-billing, no refunds. This is the minimum that proves the Stripe wiring works end-to-end against `src/payments/` + `src/components/billing/`.

Subsequent parts (separate brainstorming → plan → SDD cycles):
- **Part 2** — Webhook handler at `/api/webhooks/stripe` + signature verification + `payment_intent.succeeded` / `payment_intent.failed` events + idempotency.
- **Part 3** — Dashboard receipts (invoice/receipt data model, list + detail API + UI).
- **Part 4** — Auto-billed monthly subscription + refund flow + `charge.refunded` webhook.

## Task 1 — Add `stripe_customer_id` to tenant schema

- **Description**: Write a migration adding nullable `stripe_customer_id VARCHAR(64)` column to the existing tenant table (the brief states "integrate with our existing user/tenant model" — Stripe customers attach to the billable entity, which is the tenant). Add a unique partial index on the non-null values.
- **Module**: `migrations/` (whichever migration tool the repo uses — implementer detects via existing files)
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/migrations/` (implementer reads existing migrations for naming + tool convention)
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/src/models/tenant.ts` (or equivalent — implementer locates the tenant model)
- **Acceptance**:
  - **RED**: `migrations/<migration-name>.test.ts > tenants table has nullable stripe_customer_id VARCHAR(64) with unique partial index on non-null values` — fails before migration applied.
  - **GREEN**: migration applies cleanly forward + reverses cleanly; schema test passes; existing tenant model type definition updated to include the new optional field.
- **Dependencies**: none
- **Brief item covered**: "integrate with our existing user/tenant model" + "Card on file" (storage of Stripe customer reference)

## Task 2 — Create Stripe customer service (`ensureStripeCustomer`)

- **Description**: In `src/payments/customer.ts` (new file), write `ensureStripeCustomer(tenantId): Promise<string>` that: (a) reads the tenant; (b) if `stripe_customer_id` is set, returns it; (c) otherwise calls `stripe.customers.create({ metadata: { tenant_id } })`, persists the returned ID to the tenant row, and returns it. Idempotent — concurrent calls return the same ID (rely on DB unique constraint from Task 1 + catch the conflict).
- **Module**: `src/payments/customer.ts`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/src/models/tenant.ts` (tenant model + DB access pattern)
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/src/payments/` (verify directory exists or create — directory boundary only)
- **Acceptance**:
  - **RED**: `payments/customer.test.ts > ensureStripeCustomer creates and persists a Stripe customer for a tenant with no existing ID` — fails (function not implemented).
  - **GREEN**: test passes; second call with same tenantId returns cached ID without hitting Stripe (assert via mock call count); concurrent-call test passes (unique constraint catches race).
- **Dependencies**: Task 1 completes first (needs `stripe_customer_id` column).
- **Brief item covered**: "Card on file" (Stripe customer is the prerequisite for attaching a payment method) + "integrate with our existing user/tenant model"

## Task 3 — `POST /api/payments/setup-intent` endpoint

- **Description**: Add route handler that: (a) authenticates the caller and resolves their tenant; (b) calls `ensureStripeCustomer(tenantId)`; (c) creates a Stripe SetupIntent with `customer: customerId` and `usage: 'off_session'`; (d) returns `{ client_secret }` JSON. Tenant scoping enforced — caller must own the tenant.
- **Module**: `src/payments/routes.ts` (or equivalent existing routes file — implementer locates pattern)
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/src/payments/customer.ts` (produced by Task 2)
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/src/middleware/auth.ts` (existing auth pattern — implementer locates)
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/src/routes/` (existing route registration pattern)
- **Acceptance**:
  - **RED**: `payments/routes.test.ts > POST /api/payments/setup-intent returns 200 with client_secret for authenticated tenant owner` — fails (route not registered).
  - **GREEN**: test passes; unauthenticated request returns 401; cross-tenant request returns 403; Stripe SetupIntent created with `off_session` usage (assert via mock).
- **Dependencies**: Task 2 completes first.
- **Brief item covered**: "Card on file" (backend endpoint that issues the client_secret needed by frontend Stripe Elements)

## Task 4 — `CardForm` component using Stripe Elements

- **Description**: In `src/components/billing/CardForm.tsx` (new file), build a React component that: (a) fetches `client_secret` from `POST /api/payments/setup-intent` on mount; (b) renders Stripe `<PaymentElement>` inside `<Elements>` provider using the client_secret; (c) on submit, calls `stripe.confirmSetup()`; (d) shows success/error state. No styling beyond what Stripe Elements provides by default. Component takes no props except `onSuccess(setupIntent)`.
- **Module**: `src/components/billing/CardForm.tsx`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/src/components/` (existing component convention — patterns for fetch + auth + state)
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/package.json` (verify `@stripe/react-stripe-js` + `@stripe/stripe-js` dependencies — add if missing)
- **Acceptance**:
  - **RED**: `components/billing/CardForm.test.tsx > CardForm renders Stripe PaymentElement after fetching client_secret from /api/payments/setup-intent` — fails (component not implemented). Use Stripe's test-mode test card via `@stripe/stripe-js` mocks.
  - **GREEN**: test passes; error state renders when SetupIntent fetch fails; submit handler calls `confirmSetup` with the fetched client_secret; success callback fires with returned SetupIntent.
- **Dependencies**: none
- **Brief item covered**: "Card on file" (UI surface that collects the card) — explicitly placed at `src/components/billing/` per brief Decision.

## Task 5 — `chargeCustomer` service (one-time charge)

- **Description**: In `src/payments/charge.ts` (new file), write `chargeCustomer({ tenantId, amount, currency, description }): Promise<ChargeResult>` that: (a) loads tenant + `stripe_customer_id` (throws if absent); (b) loads the customer's default payment method (throws if absent); (c) creates a PaymentIntent with `customer`, `payment_method`, `amount`, `currency`, `description`, `off_session: true`, `confirm: true`; (d) returns `{ status, paymentIntentId, lastError? }`. No webhook listening yet — Part 1 returns whatever Stripe says synchronously; status sync via webhook arrives in Part 2.
- **Module**: `src/payments/charge.ts`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/src/payments/customer.ts` (produced by Task 2; reuse pattern)
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/loom-code-design/src/models/tenant.ts`
- **Acceptance**:
  - **RED**: `payments/charge.test.ts > chargeCustomer creates a PaymentIntent against the tenant's saved payment method and returns succeeded status` — fails (function not implemented).
  - **GREEN**: test passes; throws clearly when tenant has no `stripe_customer_id`; throws clearly when customer has no default payment method; surfaces Stripe error code intact when PaymentIntent fails (e.g. `card_declined`).
- **Dependencies**: Task 2 completes first
- **Brief item covered**: Bridges "Card on file" to billing — proves the saved card can be charged. Part 1 closes the end-to-end loop: save card → charge once. (Auto-billed monthly is explicitly Part 4.)

## Notes

**Dependency DAG**:
- Task 1 → Task 2 → Task 3 (sequential — schema → service → endpoint)
- Task 1 → Task 2 → Task 5 (sequential — schema → service → charge)
- Task 4 is fully parallel with Tasks 1–3 + 5 (frontend, mocked endpoint in test).

SDD-friendly dispatch order: `[Task 1, Task 4 in parallel] → [Task 2] → [Task 3, Task 5 in parallel]`.

Task 4 is independent because its tests use a mocked `/api/payments/setup-intent` endpoint; it only meets the real endpoint in manual smoke. Task 5 needs `ensureStripeCustomer` + populated `stripe_customer_id` from Task 2.

**Watch on Task 4 (reviewer note)**: CardForm with Stripe Elements + fetch + submit + four assertions sits at the upper edge of the ≤5-min ceiling. If the implementer subagent returns BLOCKED, natural child-split per Beck Child Test pattern: (4a) component shell with mocked client_secret fetch + render assertion; (4b) submit handler + `confirmSetup` + `onSuccess` + error-state assertion.

**Out of scope for Part 1** (explicit, to anchor reviewer + prevent scope creep):
- Webhook handler / signature verification / event handlers (Part 2).
- Idempotency for webhook events (Part 2).
- Invoice/receipt data model + dashboard UI (Part 3).
- Stripe Subscription / recurring billing (Part 4).
- Refund flow (Part 4).
- Email notifications (deferred — likely Part 4 or its own brief).

**Stripe version**: Implementer should pin a recent Stripe API version (e.g. `2025-08-27.basil` or whatever the repo currently uses if there's an existing Stripe touchpoint). Lock at one place — likely `src/payments/client.ts` if it doesn't exist (Task 2 may create it as a side-effect; reviewer should accept that).
