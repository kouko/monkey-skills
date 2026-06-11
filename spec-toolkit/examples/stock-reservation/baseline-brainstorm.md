# Baseline brainstorm — reserve stock for a pending order

Seed: "Let a warehouse reserve stock for a pending order before it ships."

The core idea: when an order is created/confirmed but not yet shipped, set aside ("hold")
the units it needs so no other order can promise the same physical units. Reserved stock
is still physically present in the warehouse but is no longer **available to promise** (ATP).

Working model of the quantities involved (this is the crux of the whole feature):

```
on_hand        = physically present units
reserved       = units committed to pending orders (not yet shipped)
available      = on_hand - reserved          <- the number new orders can draw from
```

A reservation moves units from `available` into `reserved`. Shipping moves them out of
both `reserved` and `on_hand`. Cancelling moves them from `reserved` back to `available`.

---

## Requirements / behaviors

### Creating a reservation
- Given an order line for SKU X, quantity Q, at warehouse W, when the order is confirmed,
  reserve Q units: `available` must decrease by Q, `on_hand` unchanged.
- A reservation is scoped to a **(SKU, warehouse, order)** tuple — you reserve specific
  inventory at a specific location, not "global" stock. Multi-warehouse must be a first-class concept.
- Reserve only if `available >= Q`. If not, the reservation fails (or partially fills — see open questions).
- A reservation has a **lifecycle/state**: `RESERVED → (FULFILLED | RELEASED | EXPIRED)`.
  Each transition is explicit and auditable.
- Multi-line orders: an order reserves across several SKUs. Decide whether it's all-or-nothing
  (atomic per order) or line-by-line independent.

### Releasing / consuming a reservation
- On ship/fulfillment: convert reservation to a real outbound movement — decrement both
  `reserved` and `on_hand` by the shipped quantity; reservation state → FULFILLED.
- On order cancellation: release the reservation — `reserved -= Q`, units return to `available`,
  state → RELEASED.
- On order edit (quantity changed): adjust the existing reservation up or down rather than
  duplicating it (idempotent re-reserve, not additive).
- Partial shipment: ship part of the reserved quantity; the remainder stays reserved.

### Expiry / holds
- Reservations for *unconfirmed/pending* carts should optionally **expire** after a TTL
  (e.g. 15 min for a checkout hold) so abandoned carts don't sink available stock forever.
- A background process (or lazy check on read) must reclaim expired reservations back to available.

### Correctness invariants (the spec should assert these)
- `reserved >= 0` and `available >= 0` at all times — never negative.
- `available = on_hand - sum(active reservations)` holds after every operation (no drift).
- Sum of all active reservation quantities for a SKU/warehouse never exceeds `on_hand`
  (you cannot reserve units you don't have).
- Each reservation is idempotent by a key (order line id / idempotency token): re-sending
  the same reserve request must not double-reserve.

### Concurrency / consistency
- Two orders racing for the last unit: exactly one wins; the other fails cleanly. No
  oversell. Requires atomic check-and-decrement (DB transaction with row lock, conditional
  update `WHERE available >= Q`, or compare-and-swap), not read-then-write.
- All quantity mutations happen inside a transaction; partial failures roll back.

### Auditability / observability
- Every reservation change is recorded as an immutable ledger event (who, when, qty, reason,
  resulting balances) — inventory disputes are common, so an event log is more trustworthy
  than a mutable counter.
- Current balances should be derivable from the ledger (or at least reconcilable against it).

### API surface (minimum)
- `reserve(order_id, sku, warehouse, qty, [idempotency_key, ttl])` → reservation_id | failure
- `release(reservation_id)` / `release(order_id)`
- `fulfill(reservation_id, shipped_qty)`
- `adjust(reservation_id, new_qty)`
- `get_availability(sku, warehouse)` → on_hand / reserved / available
- Clear, typed failure for insufficient stock (not a generic error).

---

## Edge cases & failure modes

- **Oversell race**: concurrent reservations for the last unit — must serialize; one fails.
- **Reserve more than available**: reject vs partial-fill — needs an explicit policy.
- **Reserve zero or negative quantity**: reject with validation error.
- **Double reserve** (retry/network replay): idempotency key dedups; second call returns the
  first result, doesn't stack.
- **Release a reservation that's already released / fulfilled / expired**: idempotent no-op,
  not an error and not a double-credit to available.
- **Fulfill more than reserved**: reject (can't ship units you didn't hold).
- **Fulfill after expiry/release**: the stock may already be gone or re-promised — must fail safely.
- **Stock shrinks below reservations** (cycle count finds fewer units, damage, theft): now
  `reserved > on_hand`. Need a reconciliation/over-allocation policy — who gets bumped?
- **Negative available**: must be structurally impossible, but the spec should say what
  happens if data corruption produces it (alarm + block, don't silently serve).
- **Order cancelled after partial shipment**: only the unshipped remainder is released.
- **Order modified mid-flight** (qty up when no stock left): partial adjust or reject.
- **Cross-warehouse**: order needs 10, warehouse A has 6, B has 4 — split across warehouses
  or fail? (allocation strategy)
- **Expired reservation that the customer then pays for**: re-reserve attempt may now fail
  because stock was reclaimed — checkout must handle "your held item is no longer available".
- **Clock/TTL issues**: expiry depends on time; clock skew or a stalled reaper job leaks holds.
- **Duplicate/zombie reservations** from a crashed process between reserve and commit — orphan
  holds that never release. Need a sweep or transactional outbox.
- **Backorder / preorder**: reserving against stock not yet on hand (incoming PO) — explicitly
  in or out of scope.
- **Returns / restock**: returned units re-enter `on_hand`; should they auto-fill waiting
  backorders? (interaction, not core, but worth flagging.)
- **Bundles / kits**: one ordered item reserves multiple component SKUs.
- **Unit-of-measure mismatch** (cases vs eaches) if the system tracks both.

---

## Open questions

1. **Granularity of "available"**: a single counter per (SKU, warehouse), or lot/bin/serial-level
   reservation? Counter is simpler; serialized goods (lots, expiry dates, serial numbers) need
   the finer grain.
2. **All-or-nothing per order, or per line?** Does a multi-line order fail entirely if one line
   can't be reserved, or reserve what it can and backorder the rest?
3. **Partial fulfillment policy**: allowed by default, or only with explicit opt-in?
4. **Insufficient stock = hard reject or partial reserve + backorder?** Drives the whole API shape.
5. **Reservation TTL**: do pending/confirmed orders expire at all, or only cart-stage holds?
   What's the default TTL and who can override it?
6. **Multi-warehouse allocation**: auto-split across warehouses, prefer-nearest, or single-source?
   Is this feature in scope or does the caller pre-pick the warehouse?
7. **Source of truth**: mutable balance row vs append-only event ledger vs both (with the row as
   a cache/projection)? Affects audit, reconciliation, and concurrency design.
8. **Consistency model**: strong/transactional (one DB) vs eventual (distributed inventory across
   regions)? Eventual consistency reintroduces oversell risk and needs compensation.
9. **Who owns expiry reclamation** — a background reaper, or lazy reclaim on the next read/reserve?
10. **Backorder / preorder in scope?** Reserving against future inbound stock changes the
    availability formula.
11. **How are physical stock corrections handled** (cycle counts, damage) when reservations
    already exceed the corrected on-hand — bump policy, priority order, notifications?
12. **Idempotency contract**: is the key the order-line id, or a client-supplied token? How long
    is it retained?
13. **Permissions / actors**: which roles can reserve, force-release, or override holds (e.g. a
    warehouse manager freeing stuck stock)?
14. **Reporting needs**: do downstream systems need real-time "available to promise" reads, and
    at what latency/consistency guarantee?
