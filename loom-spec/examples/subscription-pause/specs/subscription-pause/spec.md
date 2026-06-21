# Subscription Pause — Delta

## ADDED Requirements

### Requirement: Pause eligibility & duration cap
The system MUST allow a customer to pause only an `active` paid subscription,
for a requested duration of at least one billing increment and at most 3
months, and MUST reject durations outside that range.

#### Scenario: Pause an active subscription within the cap
- GIVEN a customer with an `active` paid subscription
- WHEN they request a pause of 2 months
- THEN the subscription transitions to `pause_pending` then `paused` on confirm
- AND a resume date 2 months out is recorded

#### Scenario: Reject duration over the 3-month cap
- GIVEN a customer with an `active` paid subscription
- WHEN they request a pause of 3 months and 1 day
- THEN the request is rejected with an over-cap error
- AND the subscription remains `active`

#### Scenario: Reject zero or negative duration
- GIVEN a customer with an `active` paid subscription
- WHEN they request a pause of 0 months
- THEN the request is rejected as invalid
- AND no PauseRequest is created

#### Scenario: Allow the exact 3-month boundary
- GIVEN a customer with an `active` paid subscription
- WHEN they request a pause of exactly 3 months
- THEN the request is accepted (boundary inclusive)

#### Scenario: Block pausing a non-active subscription
- GIVEN a customer whose subscription is `canceled` or `expired`
- WHEN they attempt to request a pause
- THEN the pause action is unavailable and the request is rejected

### Requirement: Confirmation, idempotency & no duplicate pause
The system MUST require explicit confirmation before a pause takes effect, MUST
treat repeated identical pause submissions idempotently, and MUST prevent
pausing a subscription that is already paused.

#### Scenario: Confirm before the pause applies
- GIVEN a customer who requested a pause (subscription is `pause_pending`)
- WHEN they review the preview and confirm
- THEN the subscription transitions to `paused`

#### Scenario: Abandoned request expires without effect
- GIVEN a `pause_pending` request that is never confirmed
- WHEN the request's expiry elapses
- THEN the request transitions to `expired` and the subscription stays `active`

#### Scenario: Double-submit creates a single pause
- GIVEN a customer who submits the same pause request twice in quick succession
- WHEN both submissions are processed
- THEN exactly one PauseRequest exists and no double credit/charge occurs

#### Scenario: Block pausing an already-paused subscription
- GIVEN a subscription already in `paused`
- WHEN a customer attempts to pause it again
- THEN the duplicate pause is rejected and the resume action is offered instead

### Requirement: Billing suspension & proration during pause
The system MUST suspend recurring charges for the paused period and MUST apply
the configured proration/credit policy to any partially-consumed period, never
charging for suspended time.

#### Scenario: No recurring charge while paused
- GIVEN a subscription in `paused`
- WHEN a billing cycle boundary is reached during the pause window
- THEN no recurring charge is issued for that suspended period

#### Scenario: Proration applied to a mid-period pause
- GIVEN a subscription paused partway through a paid period
- WHEN the pause is applied
- THEN the unused portion is prorated per the configured credit/refund policy

### Requirement: Auto-resume at window end
The system MUST automatically resume a paused subscription when its pause window
elapses, restoring `active` status and the recurring billing schedule.

#### Scenario: Auto-resume restores active billing
- GIVEN a subscription in `paused` whose pause window has elapsed
- WHEN the scheduler runs the resume job
- THEN the subscription transitions to `active`
- AND the next invoice is scheduled per the normal cycle

#### Scenario: Resume charge fails on expired payment method
- GIVEN a paused subscription whose saved payment method expired during the pause
- WHEN auto-resume attempts the resume charge
- THEN the failure is surfaced (not silent) and the account enters the dunning/retry flow

### Requirement: Manual early resume, extend & cancel
The system MUST let an authorized customer resume early, extend (only while
cumulative duration stays within the 3-month cap), or cancel a pause.

#### Scenario: Manual early resume before the window ends
- GIVEN a subscription in `paused` with time remaining in its window
- WHEN the customer chooses to resume now
- THEN the subscription transitions to `active` immediately and billing resumes

#### Scenario: Extension blocked when it would exceed the cap
- GIVEN a subscription paused for 2 months
- WHEN the customer requests a 2-month extension (total 4 months)
- THEN the extension is rejected for exceeding the 3-month cap

### Requirement: Authorization & audit for pause actions
The system MUST restrict pause actions to the owning customer or an authorized
admin, MUST deny pause attempts against subscriptions the actor does not own,
and MUST audit any admin-initiated pause or cap override.

#### Scenario: Deny pausing another customer's subscription
- GIVEN customer A authenticated
- WHEN A attempts to pause customer B's subscription
- THEN the action is denied and no state change occurs

#### Scenario: Admin override of the cap is audited
- GIVEN an authorized admin pausing on a customer's behalf beyond the 3-month cap
- WHEN the override is applied
- THEN the pause succeeds and an audit record with actor and reason is written

### Requirement: Atomic application under failure
The system MUST apply a pause atomically with the payment provider, leaving no
half-applied state if a downstream call fails.

#### Scenario: Billing/PSP failure leaves no half-applied pause
- GIVEN a confirmed pause request
- WHEN the payment-provider call fails during application
- THEN the pause is not partially applied and the request is retryable or rolled back
