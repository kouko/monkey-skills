# Brief Before Asking — Examples

Three side-by-side examples covering: low-complexity fork, medium-complexity fork, and the **Mode C demo** for "long explanation but user can't follow."

## Example 1 — Race Condition (Mode A: Proactive)

### ❌ Bad briefing (typical agent default)

> I noticed `BookingService.confirm()` might have a race condition under high concurrency. Should we add a lock?

**Missing**:
- Which line? How do two threads interleave?
- "Might have" — how likely? Seen in production?
- Lock options (DB-level / app-level / optimistic / serialization)? Each one's throughput impact?
- What if we don't fix it? Data corruption severity?
- Agent's own lean and reasoning?

### ✅ Good briefing (Mode A — Proactive)

> **Mental Model**
>
> This is the "seat reservation" confirmation step in booking flow. When a user clicks "Confirm," we (1) check the seat is available, then (2) write the booking. If two users click at the same time on the same seat, both may see it as available and both bookings get written — meaning two people get the same seat.
>
> **Situation**
> `BookingService.confirm()` lives in `services/booking.ts:88-142`. Flow: SELECT from `seats` (line 92) → INSERT into `bookings` (line 121). No transaction wrapping both. Stress test (50 concurrent requests, same event): reproduced double-booking 3 times.
>
> **Why this is a fork**
> Customer support reported 2 production double-booking cases last week. But the lock choice is non-trivial: app-level locks fail across multi-instance deploys; DB-level locks cost throughput; optimistic locking requires schema change. Picking wrong has real reversal cost.
>
> **Options**
> - **A. DB row-level lock (`SELECT ... FOR UPDATE`)**: ~10 lines change in confirm(). Throughput cost: 50 rps drops to ~35 rps on contested seats. Reversible.
> - **B. Optimistic lock (version column + retry)**: Schema change (add `seats.version` column, ~5 line migration); confirm() change ~25 lines + retry logic. Throughput preserved; retry cost spikes under contention. Schema change is harder to reverse.
> - **C. Redis distributed lock**: New dependency. ~15 lines in confirm() + Redis Sentinel for HA. Works across multi-instance deploys. Adds a failure mode (Redis unavailable).
>
> **My take**
> Lean B (optimistic lock). Reasoning: (1) contention on same seat is rare (only matters during launch of hot events, ~few times per quarter); (2) throughput is critical at our scale (>1k rps baseline); (3) team already uses optimistic locking pattern in InventoryService, low ramp-up. But if you're planning to roll out simultaneous-event flash sales (>100 rps contention per seat), I'd switch to A — retries would thrash under that load.
>
> **Open ends**
> - I don't know: flash-sale roadmap for next 2 quarters
> - Would flip my answer: if booking volume per second per seat exceeds ~20, switch to A
> - Need your call: schema-change tolerance — does the seats table have downstream consumers that would break on version column addition?

User can decide in ~90 seconds.

---

## Example 2 — Database Index (Mode B: Reactive on short question)

### Initial agent question (bad)

> The `getUserOrders` query looks slow. Want me to add an index?

### User reaction

> 什麼意思？

### Agent response (Mode B triggered)

> Going back to my earlier "add index" question, here's the full picture:
>
> **Mental Model**
>
> Whenever a user opens their "My Orders" page in the app, the backend runs a query to fetch that user's order history. Right now, when this user has many orders, the query is slow enough to hit our latency budget alert. The question is what technical move to make to speed it up.
>
> **Situation**
> Query is `getUserOrders` in `src/services/order/queries.ts:42-58`. LEFT JOINs `orders` (3.2M rows) / `shipments` (4.1M rows) / `users` (180K rows). EXPLAIN ANALYZE: full table scan on `orders.user_id`, cost 32k. Measured P95 ~850ms. Called from `/api/users/:id/orders` at ~120 rps.
>
> **Why this is a fork**
> Last week P99 climbed from 1.2s to 2.4s, tripping SLO alert. Need to fix this sprint. But we already have 47 indexes on `orders` — adding another isn't free (slower writes, more storage). "What index" matters, not just "do we add one."
>
> **Options**
> - **A. Single-column `idx_orders_user_id`**: ~180MB storage. INSERT cost +20% (2ms → 2.4ms). P95 850ms → ~80ms. Low risk, reversible.
> - **B. Composite covering `idx_orders_user_id_created_at`**: ~320MB storage. INSERT cost +40% (2ms → 2.8ms). P95 850ms → ~25ms (avoids heap fetch). If query pattern shifts later, may become dead index.
> - **C. Materialized view + scheduled refresh**: P95 ~10ms (pure read). Data staleness 5-10 min. Adds operational complexity (refresh scheduler, stale-view monitoring).
>
> **My take**
> Lean B (composite covering). Reasoning: (1) all callers already sort by `created_at` (verified in code), so covering pays off; (2) write rate on `orders` is ~50 rps, well within +40% headroom; (3) reversible (drop index) with no schema change. But if you're about to run a big historical-data import, switch to A to minimize write cost during import.
>
> **Open ends**
> - I don't know: any planned changes to read pattern over next 6 months
> - Would flip: if `created_at` ordering becomes optional (covering becomes wasted)
> - Need your value call: have you had bad experience with materialized views before? (affects whether C is on the table at all)
>
> ---
> **Restating my ask**: pick A, B, or C — or do you want me to spec out the materialized view path before deciding?

---

## Example 3 — Saga + Outbox (Mode C: Reactive on long explanation)

### Initial agent explanation (over-jargoned)

> We're using the saga pattern with eventual consistency via the outbox pattern. OrderService publishes domain events to Kafka, and InventoryService consumes via a consumer group with manual offset commits. We're seeing duplicate messages because the consumer crashes between processing and commit. The question is: do we add idempotency keys at the consumer level, or push them down to the domain aggregate?

### User reaction

> 太多術語，我跟不上

### Agent response (Mode C triggered — partial output, then pause)

> Let me step back and build the mental model first.
>
> **Mental Model**
>
> This is the "decrement inventory after order placed" async flow. After an order is written, we send a message to InventoryService telling it to decrement stock for the items ordered. Recently we found: the same message sometimes gets processed twice, so the same order decrements stock twice — meaning we sell items we don't have (oversells).
>
> If any of these terms in my previous turn were unfamiliar, ask and I'll expand:
>
> - **saga pattern**: a way to coordinate "multi-step transactions" that span across services
> - **outbox pattern**: a way to guarantee "writing to database" and "publishing a message" never end up with one succeeding and the other failing
> - **offset commit**: a "bookmark" in the message queue marking how far we've processed
> - **consumer group**: a way for multiple machines to share consumption of one message queue
>
> ---
>
> Does this mental model match what you understand? If yes, where would you like to drill in next:
> - **A. Why duplicate processing happens** (technical detail)
> - **B. Available solutions + my recommendation** (Options + My take)
> - **C. Expand one of the terms above**

### Why this works

- Agent did NOT dump the full 6-block briefing. The user already drowned in jargon once; dumping all 6 blocks would drown them again, even reordered.
- Agent surfaced **only the Mental Model + jargon dictionary** for terms already used.
- Agent **paused and asked the user to choose direction**. The user is now in control of how to drill.
- The 4 expanded glossary definitions are 1-sentence plain-language descriptions — each addresses "what does this term let me do" rather than "how does this term work."

This is the structurally different shape of Mode C.

---

## Anti-Patterns Demonstrated

These are concrete examples of common mistakes the skill must reject.

### Anti-Pattern 1 — Skipping Mental Model

```
**Situation**
`BookingService.confirm()` at services/booking.ts:88-142, no transaction
wrap, stress-test shows 3/50 double-booking under concurrent INSERT...
```

❌ User who doesn't already know what BookingService does is lost from sentence one.
Fix: prepend Mental Model.

### Anti-Pattern 2 — Mental Model Containing Jargon

```
**Mental Model**
OrderService has a race condition in the confirmation aggregate
under high contention, breaking idempotency guarantees.
```

❌ Three jargon terms (aggregate / race condition / idempotency) without definition. Mental Model is for plain English.
Fix: rewrite in business language.

### Anti-Pattern 3 — Fake Neutrality in My Take

```
**My take**
Both A and B are reasonable. Up to you which you prefer.
```

❌ Agent already read the code and investigated. Pretending neutrality is dishonest.
Fix: state an explicit lean with reasoning and conditional reversal.

### Anti-Pattern 4 — Unbalanced Options

```
**Options**
- **A. Add Redis cache**: it would simplify caching, improve perf,
  reduce DB load, scale better, and is the modern industry standard
  approach used by most large companies. Quantified: P95 latency
  expected to drop 65%, DB CPU drop ~30%, with new dependency on
  Redis Sentinel for HA, ~25 lines refactor in cache module.
- **B. Status quo**: keep current Caffeine.
```

❌ A is 5 lines of pro-positioning; B is 1 line. Even though both are technically listed, the framing is rigged.
Fix: equal depth — give B the same diff-level treatment.

### Anti-Pattern 5 — Mode C Trigger But Agent Dumps Full Briefing

```
User: 太多術語，我跟不上

Agent: [delivers full 6 blocks: Mental Model + Situation + Why + 
Options + My take + Open ends, all 600 words]
```

❌ User is drowning in jargon. Even a perfectly structured 6-block briefing is still 600 words and contains the same jargon. The user gets re-drowned, just in a tidier sequence.
Fix: Mode C delivers ONLY Mental Model + jargon glossary, then pauses.

### Anti-Pattern 6 — Bundled Forks

```
**Why this is a fork**
Should we (1) add a lock, (2) refactor the service, and (3) migrate
to event sourcing?
```

❌ Three independent forks. User has to disentangle them before answering. Each is a different decision with different stakes.
Fix: one briefing per fork. Sequence them.
