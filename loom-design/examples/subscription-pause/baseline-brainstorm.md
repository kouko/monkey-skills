# Baseline brainstorm — pause subscription up to 3 months

Seed: "Let a customer pause their paid subscription for up to 3 months."

## Requirements / behaviors

### Eligibility & entitlement
- Only customers with an **active, paid** subscription can pause. Trials, already-canceled, already-paused, and past-due/delinquent subscriptions are not eligible (or have explicit rules).
- Decide whether pause is a **self-serve** action (customer-initiated in UI/API) or **agent-assisted** (support only), or both.
- Define the **pause quota**: "up to 3 months" — is that a single contiguous pause of max 3 months, or a cumulative 3-month budget that can be split? Per billing year? Per subscription lifetime? This is the central ambiguity.

### Pause mechanics
- Customer chooses a **pause duration** (e.g., 1, 2, or 3 months) or a resume date. Max enforced at 3 months.
- Pause has a **start date** (immediate vs. scheduled — most commonly "at end of current billing period" to avoid mid-cycle proration).
- Pause has a defined **end/resume date** computed from start + duration.
- **Auto-resume**: subscription automatically reactivates and resumes billing on the resume date with no further action.
- Customer can **resume early** (un-pause before the scheduled end). Early resume should restore normal billing from the resume point.
- Customer can **extend** a pause up to the 3-month cap (if quota remains).
- Customer can **cancel** outright during a pause (pause is not a trap).

### Billing & money
- **No charges accrue** during the pause window (the core value prop). Decide: is it a hard freeze (no invoices) or a $0 invoice?
- **Proration policy** at pause start: if pausing mid-cycle, refund/credit the unused portion, or default to pausing at period end (cleaner). Pick one and document it.
- **Renewal date shift**: paused time pushes the next renewal/billing anchor forward by the pause length (the customer doesn't lose paid-for time).
- **Annual/prepaid plans**: pausing should extend the paid-through date by the pause duration rather than refunding.
- **Discounts/coupons/promo periods**: clarify whether promo clocks (e.g., "3 months 50% off") pause too or keep ticking.
- **Taxes/invoicing**: ensure no tax docs/invoices generated for $0 paused periods unless legally required.
- **Dunning**: a subscription in dunning (failed payment) cannot pause its way out of an owed balance — resolve outstanding balance first.

### Entitlement / access during pause
- Define **what the customer can do while paused**: typically downgraded/suspended access (no premium features) since they're not paying — OR retained read-only access. This is a product decision that must be explicit.
- Data retention: paused accounts keep their data; nothing deleted.

### State & lifecycle
- New subscription **state: `paused`** (distinct from active, canceled, past_due). Plus `pause_scheduled` if pause starts at period end.
- Clear state transitions: active → (pause_scheduled) → paused → active (resume). And paused → canceled.
- Store: pause_start, pause_end, pause_duration, pauses_used / quota_remaining, who initiated, reason (optional).

### Notifications
- Confirmation when pause is set (with resume date and what happens to access).
- Reminder before auto-resume (e.g., 3–7 days prior) so the customer isn't surprised by a charge.
- Confirmation on resume (billing restarts).
- Notification if quota is exhausted / pause request denied.

### API / integration
- API endpoints: pause, resume, extend, get pause status. Idempotent.
- Webhooks/events emitted: `subscription.paused`, `subscription.resumed`, `subscription.pause_scheduled` for downstream systems (entitlement service, analytics, CRM).
- Audit log of all pause actions.

### Admin / support
- Support agents can pause/resume/override on a customer's behalf and see pause history.
- Admin can configure the cap (3 months), quota window, and access-during-pause policy without a code change (ideally).

### Reporting / metrics
- Track pause as distinct from churn in revenue/retention metrics (paused ≠ churned; it's deferred revenue / retention-save).
- MRR reporting should reflect paused subs separately so paused revenue isn't counted as active or as churn.

## Edge cases & failure modes

- **Pause during dunning / past-due**: blocked until balance cleared.
- **Pause requested mid-cycle**: proration vs. defer-to-period-end collision; pick a deterministic rule.
- **Resume date lands on a non-existent/edge calendar day** (e.g., pause from Jan 31 for 1 month → Feb 28/29). Define month-arithmetic rule (clamp to last valid day).
- **Leap year / DST / timezone** boundary issues on resume-date computation; store/compute in UTC, render in customer TZ.
- **Quota exhaustion / double pause**: customer who already used 3 months tries again; second pause request while already paused (extend vs. reject).
- **Resume early then pause again**: does early-resumed unused time return to the quota budget, or is it forfeited?
- **Plan change while paused**: customer upgrades/downgrades/switches plan during pause — what price resumes? Block changes while paused, or apply on resume.
- **Cancellation while paused**: should be allowed; ensure no surprise charge, and stop the auto-resume.
- **Payment method expires during pause**: the auto-resume charge fails — need pre-resume payment-method check + dunning fallback, not silent reactivation failure.
- **Auto-resume race**: scheduled job to resume must be idempotent and not double-charge if retried; what if the job is down on the resume date (charge late? grace?).
- **Concurrent requests**: customer clicks pause twice, or pauses in UI while support pauses in admin — race/duplicate; needs locking/idempotency.
- **Currency/price change between pause and resume**: resume at old price or new? (Honor grandfathered price during the paused window.)
- **Refund/chargeback interaction**: chargeback filed for a period that's now paused.
- **Promo/trial-period subscription** tries to pause (should be ineligible or special-cased).
- **Pausing an annual plan near its renewal**: pause that would extend past contract term — how does it interact with renewal/auto-renew?
- **Team/seat-based subscriptions**: does pause apply to the whole account or per-seat? Seat count changes during pause.
- **Reactivation after cap**: subscription that was paused, resumed, and is now active again — does the 3-month budget reset, and when?
- **Tax jurisdiction change** during a long pause (customer moves) affecting resume invoice.
- **Entitlement-sync failure**: access not actually revoked/restored at pause/resume boundaries (downstream service out of sync with billing state).
- **Abuse**: serial pausing to get free access if access isn't suspended during pause; pause-resume-pause cycling to dodge price increases.

## Open questions

1. **Quota semantics**: Is "up to 3 months" a single max-3-month pause, a cumulative budget, and over what window (per year / per lifetime / resets after N months active)?
2. **Access during pause**: Full access retained, read-only, or suspended? (Drives the abuse model and the value prop.)
3. **Start timing**: Pause immediately (with proration) or at end of current billing period (no proration)? Default?
4. **Self-serve vs. support-only**, and is there an approval step?
5. **Billing anchor**: Does paused time push the renewal date forward, and does prepaid (annual) time get extended rather than refunded?
6. **Early resume**: Allowed? Does unused pause time return to the quota?
7. **Plan changes while paused**: Permitted, blocked, or queued for resume?
8. **Price honored on resume**: Grandfathered pre-pause price, or current price if it changed?
9. **Payment-failure-on-resume** policy: retry/dunning behavior, grace period, fallback to canceled vs. past_due.
10. **Eligibility exclusions**: trials, past-due, discounted/promo, annual, team/multi-seat — which are allowed?
11. **Reset rule**: When (if ever) does the 3-month allowance replenish?
12. **Reversibility / undo window**: Can a customer cancel a just-set pause within some window?
