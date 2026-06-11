# Revenue Split — delta

## ADDED Requirements

### Requirement: Configurable split rules
The system MUST allow a Configurator to define a versioned, effective-dated
split rule that allocates an incoming payment across multiple revenue accounts
by percentage, fixed amount, tiered, or waterfall type.

#### Scenario: Activate a valid percentage rule
- GIVEN a draft rule whose percentage weights sum to exactly 100.00% (10000 bps)
- WHEN the Configurator validates and activates it
- THEN the rule transitions draft → validated → active and becomes selectable for matching payments

#### Scenario: Reject a rule whose weights do not sum to 100%
- GIVEN a draft percentage rule whose weights sum to 99.99% (9999 bps)
- WHEN the Configurator attempts to validate it
- THEN the rule transitions to invalid and cannot be activated until corrected

#### Scenario: Editing an active rule clones a new version
- GIVEN an active rule version
- WHEN the Configurator changes its allocation table
- THEN the change creates a new version and the prior version is frozen and retained for audit and replay

### Requirement: Split each incoming payment across accounts
The system MUST execute a SplitRun for each matched incoming payment that
computes one SplitAllocation per target revenue account using the rule version
in effect at the payment's value date.

#### Scenario: Split a payment across multiple revenue accounts
- GIVEN an active 60/40 percentage rule and an incoming payment of 100.00
- WHEN the engine executes a SplitRun against the payment
- THEN it produces two allocations of 60.00 and 40.00 crediting their revenue accounts

#### Scenario: No active rule matches the payment
- GIVEN an incoming payment whose scope matches no active rule at its value date
- WHEN the engine attempts to match it
- THEN the payment transitions to unmatched and no allocations are posted

### Requirement: Conserve money to the minor unit
The system MUST ensure the sum of a SplitRun's allocations equals the
splittable base to the minor unit before any ledger entry is posted, and MUST
block posting of an unbalanced run.

#### Scenario: Distribute the rounding remainder to the residual account
- GIVEN a rule that splits 100.00 three ways (33.33% each) with a designated residual account
- WHEN the engine computes the allocations
- THEN the remaining 0.01 minor unit is assigned to the residual account so the allocations sum to exactly 100.00

#### Scenario: Block posting of an unbalanced run
- GIVEN a SplitRun whose allocations sum to a value not equal to the splittable base
- WHEN the engine reaches the balance check
- THEN the run transitions to unbalanced → failed and no ledger entry is posted

#### Scenario: Reject over-allocation by fixed amounts
- GIVEN a fixed-amount rule whose amounts exceed the payment amount
- WHEN the engine computes the allocations
- THEN the run fails with an over-allocation error and posts nothing

### Requirement: Post immutable double-entry ledger records atomically
The system MUST post the ledger entries for a balanced SplitRun atomically as
balanced double-entry records, MUST mark posted entries immutable, and MUST
never delete or edit a posted entry.

#### Scenario: Atomic posting of a balanced run
- GIVEN a balanced SplitRun
- WHEN the engine posts its ledger entries
- THEN all debit and credit entries commit in one journal whose debits equal its credits, or none commit

#### Scenario: Posted entries are immutable
- GIVEN a posted ledger entry
- WHEN any actor attempts to edit or delete it
- THEN the operation is refused because posted entries are append-only

### Requirement: Deduplicate incoming payments
The system MUST reject a duplicate incoming payment that collides on its
idempotency key or external id so a payment is split at most once.

#### Scenario: Duplicate webhook delivery is short-circuited
- GIVEN a payment that has already been received with idempotency key K
- WHEN a second delivery arrives with the same idempotency key K
- THEN the second delivery is marked duplicate and produces no new SplitRun or allocations

### Requirement: Reverse a payment via compensating entries
The system MUST handle a refund or chargeback of a posted payment by emitting a
compensating SplitRun whose contra ledger entries neutralize the original
postings without deleting them.

#### Scenario: Refund reverses the split
- GIVEN a payment whose split has been posted
- WHEN a full refund is received for that payment
- THEN a compensating SplitRun posts contra entries that net the original allocations to zero while the original entries remain intact

### Requirement: Guard revenue-account lifecycle
The system MUST prevent crediting an allocation to a revenue account that is
not active and MUST refuse to close an account that still has pending
allocations.

#### Scenario: Block a split targeting a closed account
- GIVEN a rule whose target revenue account is closed or frozen
- WHEN the engine executes a SplitRun against a matched payment
- THEN the run fails with an account-closed error and routes nothing to the closed account

#### Scenario: Refuse to close an account with pending allocations
- GIVEN a revenue account with one or more pending allocations
- WHEN a Configurator attempts to close it
- THEN the close is refused until the pending allocations are drained or reassigned

### Requirement: Enforce segregation of duties on rule activation
The system SHOULD require that the actor who activates a split rule is distinct
from the actor who created it, enforcing maker-checker control over revenue
allocation configuration.

#### Scenario: Same actor cannot both create and activate
- GIVEN a rule created by actor A under a maker-checker policy
- WHEN actor A attempts to activate that same rule
- THEN activation is refused and a distinct approver is required
