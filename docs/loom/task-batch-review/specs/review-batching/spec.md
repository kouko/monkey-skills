## ADDED Requirements

### Requirement: REQ-99 — Second-pass review grouping
The system MUST form review dispositions only after authoring the complete atomic Task dependency graph.

#### Scenario: Eligible atomic Tasks are grouped after DAG completion
- GIVEN a complete acyclic Task graph whose Tasks retain their individual requirements, RED/GREEN criteria, modules, files, dependencies, and review weights
- WHEN the planner performs the review-grouping pass
- THEN it emits a Review Batch without merging or enlarging any member Task

#### Scenario: Planner does not group an incomplete DAG
- GIVEN a plan whose Task graph or dependency edges are not complete
- WHEN review grouping is attempted
- THEN plan validation rejects the grouping before execution

#### Scenario: Cyclic DAG is rejected
- GIVEN a fully declared Task graph containing a self-cycle or multi-Task dependency cycle
- WHEN the planner groups or validates review dispositions
- THEN validation rejects the plan and identifies the cycle before any Task dispatch

### Requirement: REQ-100 — Explicit review disposition
The system MUST declare exactly one review disposition for every executable Task.

#### Scenario: Batched Task has one Batch membership
- GIVEN an executable Task selected for aggregate review
- WHEN the plan is validated
- THEN the Task belongs to exactly one declared Review Batch

#### Scenario: Ineligible Task declares individual review
- GIVEN an executable Task that is not eligible for a Review Batch
- WHEN the plan is validated
- THEN the Task is explicitly assigned to individual review rather than inferred from a missing field

#### Scenario: Multiple Batch membership is rejected
- GIVEN one Task appears in two Review Batches
- WHEN the plan is validated
- THEN validation fails before SDD dispatch

#### Scenario: Contradictory or dangling disposition is rejected
- GIVEN a Task is both individual and batched, cites an unknown Batch, or a Batch cites a missing or non-executable Task
- WHEN the plan is validated
- THEN validation fails with every invalid reference and dispatches no Task

### Requirement: REQ-101 — Review Batch contract
The system MUST require every Review Batch to declare its identity, members, shared verdict question, review lane, aggregate verification, and boundary.

#### Scenario: Complete Batch declaration passes structural validation
- GIVEN a Batch with a unique ID, non-empty unique members, one verdict question, one review lane, reproducible aggregate verification, and a decidable boundary
- WHEN the Batch schema is validated
- THEN the declaration is accepted for semantic eligibility checking

#### Scenario: Missing or ambiguous Batch field fails validation
- GIVEN a Batch with an empty member set, duplicate member, missing field, multiple review lanes, or a verdict question that cannot be answered without future work
- WHEN the Batch schema is validated
- THEN validation fails with an actionable reason and no reviewer is dispatched

#### Scenario: Batch fields are untrusted data
- GIVEN a structural Batch field contains control characters, executable instructions, an unsafe path, or an identifier that cannot be parsed without ambiguity
- WHEN the declaration is validated
- THEN validation treats the value only as data, executes none of it, makes no normalization guess, and rejects the declaration with a field-specific diagnostic

#### Scenario: Aggregate verification is an inert requirement
- GIVEN Aggregate verification describes a reproducible check and may contain command-shaped prose
- WHEN the declaration is validated or later consumed by SDD
- THEN the value remains opaque data, is never executed as plan text, and SDD resolves the actual test command through its existing declared-first verification contract

#### Scenario: Validated declaration amendment requires revalidation
- GIVEN a Batch declaration has passed plan validation
- WHEN the planner changes membership, lane, verdict question, aggregate verification, boundary, or dependency edges
- THEN every prior validation and Packet becomes stale and the amended plan must pass all plan gates again before SDD can use it

### Requirement: REQ-102 — Fail-closed Batch eligibility
The system MUST retain individual review unless every Batch member shares one review lane, one end-to-end verdict question, and one closable review window.

#### Scenario: All eligibility predicates hold
- GIVEN Tasks with the same review lane, a shared end-to-end verdict question, the same closable review window, and one named capability boundary or module invariant
- WHEN none requires a user decision, external wait, deferred test, independent release point, distinct failure domain, or uncertain boundary
- THEN the planner may declare them as one Review Batch

#### Scenario: Exclusion forces individual review
- GIVEN any candidate member requires a user decision, external wait, deferred test, independent release point, distinct failure domain, or uncertain boundary
- WHEN the planner evaluates the candidate group
- THEN every affected Task retains individual review and no Batch lifecycle object is created

#### Scenario: Runtime invalidation discards Batch disposition
- GIVEN a valid planned Batch whose execution later exposes an exclusion or invalid boundary
- WHEN SDD re-evaluates the Batch before Packet creation
- THEN SDD discards the Batch review path and routes its members to individual review without reusing an aggregate Packet

#### Scenario: Review input cannot be proven fully consumable
- GIVEN a candidate aggregate scope cannot be delivered to or processed by the selected review lane without omission or truncation
- WHEN Batch eligibility is evaluated
- THEN the Batch fails closed to individual review or a newly validated smaller grouping, and no partial input can produce a passing verdict

### Requirement: REQ-103 — Implemented Task state
The system MUST record a Task as `implemented(<sha>)` only after its local mechanical verification passes against its committed final bytes.

#### Scenario: Verified Task records its own commit
- GIVEN a claimed Task whose local verification passes and whose member commit is reachable
- WHEN SDD records local implementation completion
- THEN the Task becomes `implemented(<member-sha>)`

#### Scenario: Verification failure cannot become implemented
- GIVEN a claimed Task whose local verification fails or whose final bytes are not committed
- WHEN SDD evaluates local completion
- THEN the Task does not enter `implemented`

#### Scenario: Non-member SHA is rejected
- GIVEN a claimed Task and a SHA that is missing, unreachable, belongs to another member, or identifies an aggregate or ledger-only commit
- WHEN SDD attempts to record `implemented(<sha>)`
- THEN the status write is rejected without changing the ledger

#### Scenario: Only SDD writes review-bound Task states
- GIVEN an implementer supplies a member commit and local verification evidence or a reviewer supplies a verdict
- WHEN an actor other than the SDD orchestrator attempts to write `implemented` or `done`
- THEN the ledger mutation is rejected; SDD alone may derive `implemented` from member evidence and `done` from an exact passing Packet

### Requirement: REQ-104 — Dependency readiness across review boundaries
The system MUST derive dependency readiness from Task status and shared Batch identity without adding a new dependency-edge type.

#### Scenario: Same-Batch consumer accepts implemented producer
- GIVEN producer and consumer Tasks belong to the same Review Batch
- WHEN the producer is `implemented(<sha>)`
- THEN the consumer is eligible for claim subject to its other dependencies

#### Scenario: Cross-Batch consumer waits for done producer
- GIVEN producer and consumer Tasks do not belong to the same Review Batch
- WHEN the producer is `implemented(<sha>)` but not `done(<sha>)`
- THEN the consumer is not ready

#### Scenario: Done producer releases every consumer
- GIVEN any consumer depends on a producer
- WHEN the producer is `done(<sha>)`
- THEN that dependency is satisfied

#### Scenario: Non-implemented producer releases no consumer
- GIVEN a producer is `pending`, `claimed`, or `blocked`
- WHEN readiness is evaluated
- THEN no dependent consumer is released by that edge

### Requirement: REQ-105 — Immutable aggregate Review Packet
The system MUST bind each Batch review to one immutable Packet containing the exact member-to-SHA mapping, reviewed bytes, Batch declarations, and aggregate verification evidence.

#### Scenario: Ready Batch materializes exact Packet
- GIVEN every Batch member is `implemented(<sha>)`, the boundary remains valid, and aggregate verification is reproducible
- WHEN SDD materializes the Review Packet
- THEN the Packet binds every member SHA and byte scope together with the verdict question, lane, boundary, and aggregate evidence

#### Scenario: Unready Batch cannot materialize Packet
- GIVEN any Batch member is not implemented or the Batch boundary cannot be proven valid
- WHEN Packet creation is attempted
- THEN creation fails and no reviewer is dispatched

#### Scenario: Packet input drift invalidates review
- GIVEN a frozen Packet
- WHEN any member bytes, member SHA, member set, verdict question, review lane, aggregate verification, or boundary declaration changes
- THEN the Packet and every verdict bound to it become stale and cannot be reused

#### Scenario: Packet cannot mutate in place
- GIVEN an existing frozen Packet
- WHEN a caller attempts to append, refresh, or rebind a member
- THEN the operation is rejected and a new Packet is required

#### Scenario: Packet contains only declared committed scope
- GIVEN Batch members declare their Task files, member SHAs, owned requirements, acceptance criteria, and aggregate evidence
- WHEN SDD materializes the Packet
- THEN it includes only bytes reproducible from those exact commits and declared scope, excludes untracked or repository-external content, and refuses any scope it cannot reproduce safely

#### Scenario: Requirement ownership is derived from verified authority
- GIVEN the validated plan and spec assign owned requirements, future requirements, and acceptance criteria to each member Task
- WHEN SDD materializes the Packet
- THEN it reproduces that mapping without omission or reassignment, rejects dangling, duplicate, or conflicting references, and treats any ownership amendment as plan and Packet invalidation

#### Scenario: Partial Packet publication is unusable
- GIVEN Packet materialization stops before every member, declaration, and aggregate-evidence field is durably present
- WHEN SDD resumes or review discovery examines the artifact
- THEN the partial Packet cannot be dispatched or mistaken for frozen and must be rebuilt

#### Scenario: Same SHA in a non-implemented status invalidates readiness
- GIVEN a Packet's member SHA and bytes still match but that member no longer has the corresponding `implemented(<sha>)` status
- WHEN dispatch or verdict reuse is attempted
- THEN the Packet is ineligible for review or reuse until current readiness is proven again

#### Scenario: Trusted aggregate command cannot be resolved or proven
- GIVEN Aggregate verification remains inert plan data
- WHEN SDD cannot uniquely resolve an applicable command through the existing declared-first contract, command execution fails, or the evidence does not satisfy the declared aggregate requirement
- THEN SDD executes no plan text, materializes no Packet, dispatches no reviewer, changes no Task status, and reports the failure through the existing verification recovery path

#### Scenario: Packet identity binds resolved aggregate verification
- GIVEN SDD resolves and executes the trusted aggregate verification command
- WHEN the Packet and its evidence identity are materialized
- THEN identity includes the resolution source, unambiguous command arguments, execution scope, and result, and any drift makes the Packet and prior verdict stale

#### Scenario: Verification identity persists no secret material
- GIVEN resolved command arguments or resolution context contains a secret, expanded credential, or credential path that cannot be persisted safely
- WHEN Packet identity is materialized
- THEN SDD stores no secret-bearing value, performs no redaction or equivalence guess, and fails closed without creating or reusing a Batch Packet

### Requirement: REQ-106 — One full reviewer fan-out per eligible Batch
The system MUST dispatch the applicable full-review arms once for an exact eligible Batch Packet instead of once per member Task.

#### Scenario: Eligible three-member Batch dispatches once
- GIVEN one exact Packet for three eligible non-mechanical Tasks in the same review lane
- WHEN SDD starts Batch review
- THEN each applicable reviewer arm receives one aggregate dispatch and no member receives a duplicate full-review fan-out

#### Scenario: Individual disposition preserves current fan-out
- GIVEN a Task whose review disposition is individual
- WHEN its local implementation is ready for review
- THEN SDD uses the existing Task-scoped reviewer fan-out

#### Scenario: Aggregate dispatch uses declared lane
- GIVEN an eligible Batch Packet with one declared review lane
- WHEN reviewers are selected
- THEN SDD uses the same lane-specific reviewer substitution rules that would apply to the members individually

#### Scenario: Empty reviewer-arm set cannot pass vacuously
- GIVEN a Batch lane resolves to zero applicable full-review arms and is not eligible for the existing mechanical disposition
- WHEN SDD attempts review aggregation
- THEN SDD rejects the Batch path instead of treating the empty result as passing

#### Scenario: Every expected arm must return one authoritative terminal result
- GIVEN multiple applicable arms review one exact Packet and return in any order, including pass, finding, timeout, cancellation, duplicate, or late results
- WHEN SDD aggregates the Batch verdict
- THEN it performs no ledger mutation until each expected arm has exactly one authoritative Packet-bound terminal result, and only an all-pass set may finalize

#### Scenario: Conflicting results from one arm fail closed
- GIVEN one expected arm yields duplicate, late, replayed, or conflicting Packet-bound terminal results
- WHEN SDD determines the authoritative result using the existing dispatch identity and arm binding
- THEN it performs zero ledger mutation unless exactly one result can be proven authoritative, and it never selects by arrival order or favorable verdict

#### Scenario: Reviewer result provenance is retained
- GIVEN an applicable arm returns a verdict or finding
- WHEN SDD accepts the result
- THEN the durable review evidence identifies the dispatch-bound arm, exact Packet, result or finding identity, immutable evidence identity, and original owner attribution without executing untrusted payload content or allowing SDD to rewrite reviewer ownership

### Requirement: REQ-107 — Finding attribution and repair
The system MUST bind every blocking Batch finding to a non-empty subset of the exact Packet's member Tasks before changing member statuses.

#### Scenario: Single-member finding reopens one Task
- GIVEN a blocking finding owned only by Task B in Batch [A, B, C]
- WHEN SDD resolves the Batch verdict
- THEN B returns to `pending` for rework while A and C remain `implemented` at their original SHAs

#### Scenario: Cross-member finding reopens all owners
- GIVEN a blocking seam finding owned by Tasks A and B
- WHEN SDD resolves the Batch verdict
- THEN A and B return to `pending` while every non-owner remains `implemented`

#### Scenario: Unassignable finding falls back without ledger mutation
- GIVEN a blocking finding with an empty, ambiguous, or outside-Batch owner set
- WHEN SDD attempts attribution
- THEN no member status changes and the members are routed to individual review

#### Scenario: Repaired member requires fresh Packet
- GIVEN an attributable finding caused Task B to produce a new member commit
- WHEN B returns to `implemented(<new-sha>)`
- THEN the prior Packet and verdict remain stale and SDD must freeze a new Packet before review

#### Scenario: Blocking finding cites a valid blocking ground
- GIVEN the Packet lists each member's owned requirements, acceptance criteria, actual change scope, and future requirements when present
- WHEN a reviewer marks a finding blocking
- THEN the finding cites an owned requirement, stated acceptance, direct regression, or safety defect; a future requirement alone cannot block the member

#### Scenario: Multiple attributable findings reopen owner union atomically
- GIVEN one Packet returns blocking findings owned by overlapping sets `{A, B}` and `{B, C}`
- WHEN SDD applies the blocking verdict
- THEN Tasks A, B, and C all return to `pending` in one atomic plan-file replacement while every non-owner remains unchanged

#### Scenario: Malformed or conflicting finding changes no ledger state
- GIVEN a finding is duplicated with conflicting content, cannot bind to the exact Packet, contains an invalid owner set, or cannot be parsed safely
- WHEN SDD processes the finding
- THEN it performs zero ledger mutation and uses the unassignable-finding individual-review fallback

#### Scenario: Unassignable finding dominates mixed finding set
- GIVEN one authoritative Packet decision contains attributable findings and at least one unassignable, malformed, or outside-Batch finding
- WHEN SDD resolves the complete finding set
- THEN it performs zero member status changes, skips owner-union rework, and routes every member to individual review

#### Scenario: Owner-union rework compares the authoritative decision
- GIVEN attributable finding application races with finalization, amendment, fallback, or another SDD session
- WHEN the atomic owner-union replacement is attempted
- THEN its compare-and-swap precondition covers the exact Packet, Batch disposition, complete authoritative arm outcomes, and every owner's `implemented(<sha>)`; the losing operation performs zero writes and `done` never moves backward

### Requirement: REQ-108 — Atomic Batch finalization
The system MUST finalize a passing Batch by atomically replacing every reviewed member's `implemented(<sha>)` with `done(<same-sha>)`.

The compare-and-swap guarantee covers every participating Loom writer: SDD and
`plan_card` mutations MUST acquire one stable plan-directory advisory lock
before reading the precondition and keep it through publication. Direct file
writers that bypass this protocol are not transaction participants and MUST
NOT be run concurrently with SDD; portable filesystem replacement cannot
serialize an actor that ignores the shared lock. This is one write protocol,
not a Batch lock manager or a second ledger.

#### Scenario: Exact passing snapshot finalizes all members
- GIVEN every applicable review arm passed one exact Packet and every member still equals the Packet's `implemented(<sha>)`
- WHEN SDD finalizes the Batch
- THEN all members become `done(<their-same-member-sha>)` in one atomic plan-file replacement

#### Scenario: Compare-and-swap precondition drift changes nothing
- GIVEN one member status, SHA, or membership differs from the passing Packet
- WHEN finalization is attempted
- THEN finalization fails and no member status changes

#### Scenario: Write interruption cannot expose partial done state
- GIVEN an injected failure during multi-member finalization
- WHEN the plan file is observed after the failed operation
- THEN it contains either all prior implemented statuses or all target done statuses, never a mixture

#### Scenario: Completed finalization retry is idempotent
- GIVEN every member already has the target `done(<sha>)` from the same exact Packet
- WHEN finalization is retried
- THEN the operation succeeds as a no-op without changing SHAs or creating another transition

#### Scenario: Torn pre-existing state is refused
- GIVEN a Batch ledger already contains an unexplained mixture of done and implemented members
- WHEN finalization or retry is attempted
- THEN the operation fails loudly rather than filling the remaining statuses

#### Scenario: Finalization compares the entire authoritative decision
- GIVEN finalization races with a plan amendment, finding application, fallback, or another SDD session that uses the shared Loom write protocol
- WHEN the atomic replacement is attempted
- THEN its compare-and-swap precondition includes the exact Packet, Batch disposition, member statuses and SHAs, all authoritative arm outcomes, and absence of open findings; the losing operation performs zero writes

#### Scenario: A writer that bypasses the shared lock is outside the transaction
- GIVEN a direct editor or filesystem tool can replace the plan without acquiring the Loom write lock
- WHEN SDD is about to mutate the same plan
- THEN the orchestrator prevents those operations from running concurrently rather than claiming cross-process CAS against a non-participating writer

### Requirement: REQ-109 — New-plan-only execution contract
The system MUST refuse execution of a newly invoked plan that lacks an explicit Batch-or-individual review disposition.

#### Scenario: New schema plan enters SDD
- GIVEN a plan generated by the updated writing-plans workflow and accepted by plan review
- WHEN SDD begins execution
- THEN every Task has a validated review disposition

#### Scenario: Historical plan is not treated as compatible execution input
- GIVEN a historical plan authored before the Task Batch Review schema
- WHEN it is supplied for new SDD execution
- THEN SDD refuses it as unsupported rather than silently inferring individual review

### Requirement: REQ-110 — Whole-branch verification remains mandatory
The system MUST retain cumulative whole-branch review and package verification after all Task and Batch checkpoints pass.

#### Scenario: Batch-reviewed branch still receives cumulative review
- GIVEN every Task is done through Batch or individual review
- WHEN the branch enters close-out
- THEN whole-branch code/docs review and the applicable full test gates still run

#### Scenario: Whole-branch finding is not erased by Batch pass
- GIVEN a Batch passed but cumulative review finds a cross-Batch or cross-plugin defect
- WHEN close-out resolves the finding
- THEN the branch remains unshippable until the defect is repaired and required review is repeated

### Requirement: REQ-111 — Review-cost change is evidence-gated
The system MUST evaluate Task Batch Review against the same representative work corpus used for the individual-review baseline.

#### Scenario: Candidate is compared on cost and safety
- GIVEN a representative corpus with atomic requirements, plans, review events, and known findings
- WHEN individual-review and Batch-review executions are compared
- THEN the evidence reports full reviewer dispatches, review rounds, false scope expansion, escaped known defects, elapsed work, maximum aggregate diff, and requirement-to-test traceability

#### Scenario: Baseline and candidate use one authorized corpus
- GIVEN the comparison corpus contains plans, review events, or known findings from real or synthetic work
- WHEN baseline and Batch candidate measurements run
- THEN both use the same minimum authorized corpus and known-finding oracle, and no unauthorized or secret content enters reviewer Packets or reports

#### Scenario: Dispatch reduction alone cannot justify adoption
- GIVEN Batch review reduces reviewer dispatches but loses a known defect or weakens requirement-to-test traceability on the comparison corpus
- WHEN adoption evidence is evaluated
- THEN the candidate does not satisfy this requirement
