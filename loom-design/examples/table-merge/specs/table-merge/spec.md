# table-merge

## ADDED Requirements

### Requirement: Merge eligibility
The system MUST allow a server to merge two distinct open tables into one
surviving check, and MUST reject the merge when either table is ineligible.

#### Scenario: Two open tables merge into one check
- GIVEN two distinct tables that are both OPEN, each with an active check carrying in-progress items
- WHEN the server selects one as source and the other as target and confirms the merge
- THEN the target's check survives carrying every item from both checks, and the source check is voided

#### Scenario: Self-merge is rejected
- GIVEN a single open table selected as both source and target
- WHEN the server attempts to confirm the merge
- THEN the system rejects the merge and leaves the check unchanged

#### Scenario: Source table with a settled check is blocked
- GIVEN a source table whose check is fully-paid or closed
- WHEN the server attempts to merge it into a target
- THEN the system blocks the merge and requires a manager override before any reopen

#### Scenario: Empty source check merges as a no-op on lines
- GIVEN a source table that is OPEN but whose check carries zero items
- WHEN the server confirms the merge
- THEN the target check is unchanged in its line set and the source table is released

### Requirement: Surviving-check identity and audit tombstone
The system MUST preserve one surviving check identity and MUST retain the
non-surviving check as a void tombstone linked to the survivor, never deleting it.

#### Scenario: Loser check becomes an auditable tombstone
- GIVEN a confirmed merge of source check S into surviving check T
- WHEN the migration completes
- THEN S is marked voided with a merged_into pointer to T, T records S in merged_from, and S's check number is retired for the service

### Requirement: Fired kitchen items migrate without re-firing
The system MUST move already-fired items to the surviving check without
re-sending them to the kitchen, and MUST re-label their KDS tickets to the
surviving check.

#### Scenario: Fired items keep their cook state
- GIVEN a source check with items in FIRED or IN-PREP state
- WHEN the merge is confirmed
- THEN those items appear on the surviving check with their original fire state and fired-at time, the kitchen receives no new fire, and their KDS ticket now points to the surviving check

### Requirement: Seat-collision resolution
The system MUST resolve seat-number collisions between the two checks before
completing the merge, and MUST cascade the chosen seat re-mapping to every
child item in a single transaction.

#### Scenario: Both checks have a seat 1
- GIVEN a source and target check that each contain a seat numbered 1
- WHEN the server resolves the collision by offset-renumber
- THEN the incoming seats are renumbered after the survivor's seats and every migrated item's seat reference is updated atomically with no orphaned items

### Requirement: Total recalculation after merge
The system MUST recalculate the surviving check's totals from raw lines after
the merge — subtotal, then check-scoped discounts, then service-charge and
auto-gratuity thresholds, then tax — applying rounding once to the final total.

#### Scenario: Two small parties cross the auto-gratuity threshold
- GIVEN a source check for party of 3 and a target check for party of 3, with auto-gratuity applying at party of 6 or more
- WHEN the merge is confirmed
- THEN the surviving check shows party of 6, auto-gratuity is applied to the combined subtotal, and the server is shown the newly added charge

#### Scenario: Totals are recomputed from raw lines, not summed pre-rounded
- GIVEN two checks each with an independently rounded total
- WHEN the merge recalculates the surviving total
- THEN the tax and rounding are computed once on the combined raw line base so the result does not double-round

### Requirement: Captured-payment safety
The system MUST NOT silently move a captured tender, and MUST preserve each
tender's origin-check provenance when a partially-paid check participates in a merge.

#### Scenario: Partially-paid check merges only as the surviving target
- GIVEN a check that already has a captured partial payment
- WHEN a server attempts to use it as the merge source
- THEN the system blocks it as a source and permits it only as the surviving target, where the captured tender stays attached and the balance due is recomputed against the new total

#### Scenario: Undo is refused after a payment batch has settled
- GIVEN a merged surviving check whose captured tender's batch has already settled
- WHEN the server attempts to undo the merge
- THEN the system refuses the in-place undo and requires a manager-authorized refund instead

### Requirement: Cross-server ownership resolution
The system MUST resolve server-of-record before completing a merge of two
checks owned by different servers, and MUST NOT drop the non-surviving
server's sales/tip credit silently.

#### Scenario: Two servers' checks merge
- GIVEN a source check owned by server A and a target check owned by server B
- WHEN the merge is confirmed
- THEN the system requires the server or a manager to assign ownership or a tip-split map before completing, and the non-surviving server's line-level credit is retained

#### Scenario: Merging another server's table requires authority
- GIVEN a source table in a different server's section
- WHEN a server attempts to merge it
- THEN the system requires a section claim/transfer or a manager override before allowing the merge

### Requirement: Atomic, idempotent, audited merge
The system MUST apply the merge as a single atomic transaction, MUST be safe
to retry without double-applying, and MUST record an immutable audit entry for
every merge.

#### Scenario: Crash mid-merge leaves no orphaned state
- GIVEN a merge in progress that fails after items move but before a tender is re-attached
- WHEN the transaction is rolled back or retried
- THEN no items are orphaned from a voided check and no tender is left detached, leaving the two checks in their pre-merge state

#### Scenario: Concurrent merge of the same source is serialized
- GIVEN two servers who attempt to merge the same source table at the same time
- WHEN both confirm
- THEN the source is locked so only one merge applies and the second is rejected with a stale-state message

#### Scenario: Every merge is auditable
- GIVEN a confirmed merge
- WHEN the migration completes
- THEN an immutable audit entry records who performed it, when, the source and surviving check ids, and the resolved ownership
