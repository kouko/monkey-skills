# Stock reservation — spec delta

## ADDED Requirements

### Requirement: Reserve stock against available-to-promise
The system MUST reserve the requested quantity for a pending order line only against available-to-promise (ATP = on_hand − reserved − quarantine − damaged), and MUST NOT let available go below zero.

#### Scenario: Full reservation when stock is available
- GIVEN a SKU at a warehouse with ATP = 10 and a pending order line for qty 4
- WHEN the reservation engine reserves the line
- THEN a reservation for qty 4 is created in state `reserved` AND the SKU's reserved increases by 4 AND ATP becomes 6

#### Scenario: Partial reservation spills remainder to backorder
- GIVEN a SKU with ATP = 3 and a pending order line for qty 5
- WHEN the reservation engine reserves the line
- THEN qty 3 is reserved (`partially_reserved`) AND qty 2 is recorded as backordered AND ATP becomes 0

#### Scenario: Zero stock backorders the whole line
- GIVEN a SKU with ATP = 0 and a pending order line for qty 2
- WHEN the reservation engine reserves the line
- THEN no quantity is held AND the line enters state `backordered` AND ATP stays 0

### Requirement: Prevent oversell under concurrency
The system MUST serialize concurrent reservations of the last available unit via atomic compare-and-decrement (or optimistic version check) so that exactly one succeeds.

#### Scenario: Two reservations race for the last unit
- GIVEN a SKU with ATP = 1
- WHEN two reservation requests for qty 1 are submitted concurrently
- THEN exactly one reservation succeeds and the other is rejected or backordered AND available never goes below 0

### Requirement: Honor reservation lifecycle to the ship boundary
The system MUST hold reserved stock through commit and pick, and MUST consume it (decrementing on_hand and reserved) only when the order ships.

#### Scenario: Reservation is consumed on ship
- GIVEN a `committed` reservation for qty 4 that has been picked
- WHEN the order ships
- THEN the reservation moves to `consumed` AND the SKU's on_hand and reserved both decrease by 4

#### Scenario: Shipped reservation cannot be reversed in place
- GIVEN a reservation in state `consumed`
- WHEN any release, expire, or re-activation is attempted on it
- THEN the transition is rejected AND any reversal must be a new return/RMA object

### Requirement: Release held stock when an order is cancelled before ship
The system MUST release a reservation's held quantity back to ATP when its order is cancelled at any point before the ship boundary.

#### Scenario: Pre-ship cancellation frees ATP
- GIVEN a pending order with a `reserved` reservation for qty 4 (ATP = 6)
- WHEN the order is cancelled before any units ship
- THEN the reservation moves to `released` AND the SKU's reserved decreases by 4 AND ATP returns to 10

### Requirement: Expire soft holds on TTL without disturbing in-flight picks
The system MUST auto-release a soft reservation when its TTL elapses, and MUST NOT expire a hard hold that is already committed or being picked.

#### Scenario: Soft hold expires on TTL lapse
- GIVEN a soft `reserved` reservation whose expires_at has passed and is not being picked
- WHEN the expiry sweep runs
- THEN the reservation moves to `expired` AND its held quantity returns to ATP

#### Scenario: TTL does not preempt an active pick
- GIVEN a reservation whose TTL elapses while a picker has it on an active pick task
- WHEN the expiry sweep runs
- THEN the reservation is NOT released out from under the active pick AND the conflict is logged

### Requirement: Reserve operations are idempotent under retry
The system MUST accept an idempotency key on each reserve call and return the original reservation for a repeated key rather than creating a second hold.

#### Scenario: Retried reserve with the same key does not double-hold
- GIVEN a reserve call with idempotency-key K that committed server-side but timed out client-side
- WHEN the client retries with the same key K
- THEN the server returns the original reservation AND no second hold is created

### Requirement: No reservation leak when the order write fails
The system MUST release or compensate a reservation whose order write fails after the reservation write commits, so no orphan hold remains.

#### Scenario: Order-write failure compensates the reservation
- GIVEN a reservation write that succeeds and a subsequent order write that fails
- WHEN the transaction or saga resolves
- THEN the reservation is released or compensated within the saga timeout AND no orphan hold remains in the ledger

### Requirement: Authorize reservation overrides and cross-actor releases
The system MUST reject an oversell-driving reserve or a release of another actor's reservation unless the acting actor holds the corresponding permission, and MUST record every override with actor identity, timestamp, and reason.

#### Scenario: Unauthorized oversell override is rejected and authorized override is audited
- GIVEN a reserve request that would drive available negative
- WHEN an actor without override permission attempts it
- THEN the request is rejected; AND WHEN an authorized actor overrides, the override is recorded with actor identity, timestamp, and reason in the ledger

### Requirement: Reconcile a short pick against contending reservations by priority
The system MUST resolve a short pick (fewer physical units than reserved) by fulfilling reservations in the stated priority order and backordering the shortfall.

#### Scenario: Short pick shorts the lower-priority reservation
- GIVEN reservations R_high (priority 1) and R_low (priority 5) each holding qty 1 of one SKU, and the picker finds only 1 physical unit
- WHEN the short pick is reconciled
- THEN R_high is fulfilled AND R_low is backordered per the priority policy AND the shortfall is recorded

### Requirement: Block reservations against an unavailable warehouse
The system MUST refuse to create a reservation against a warehouse that is frozen-for-count (within the frozen scope), offline, or closed, and MUST route existing in-scope holds to release or re-source.

#### Scenario: Freeze-for-count blocks new in-scope reservations
- GIVEN a warehouse whose zone for a SKU is in state `frozen-for-count`
- WHEN a reservation against that SKU in that zone is requested
- THEN the reservation is rejected AND existing in-scope holds are flagged to wait or be re-sourced
