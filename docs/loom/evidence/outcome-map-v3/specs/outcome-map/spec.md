## ADDED Requirements

### Requirement: REQ-75 — Outcome Map is a long-term control loop
The system MUST represent an Outcome Map as one persistent outcome-control loop that can advance through multiple independently closed delivery arcs.

#### Scenario: Closing a delivery preserves the wider loop
- GIVEN an active Map with one ready delivery and another open ticket or fog entry
- WHEN the delivery ticket closes
- THEN the Map remains active and exposes the next frontier work

### Requirement: REQ-76 — Ticket types are closure-exclusive
The system MUST accept exactly `grilling`, `research`, `prototype`, and `delivery` ticket types and MUST gate each type with its own closure evidence.

#### Scenario: Human direction decision closes grilling
- GIVEN a claimed grilling ticket
- WHEN a named human ratifies a value, direction, or trade-off decision
- THEN the ticket may close with that decision and ratification evidence

#### Scenario: Measured feasibility closes research
- GIVEN a claimed ticket whose question is settled by a reproducible feasibility measurement
- WHEN the factual conclusion and inspectable evidence are recorded
- THEN the ticket may close as research without prototype ratification

#### Scenario: Human reaction to a new candidate closes prototype
- GIVEN a claimed prototype ticket with a newly created candidate artifact
- WHEN a named human evaluates or selects the candidate
- THEN the ticket may close with the artifact and ratified evaluation evidence

#### Scenario: Formal outcome slice closes delivery
- GIVEN a claimed delivery ticket bound to its delivery arc
- WHEN the promised slice satisfies its formal delivery evidence contract
- THEN the ticket may close without asserting that the Map Destination is complete

#### Scenario: Generic task type is rejected
- GIVEN a schema-v3 ticket declaring `task` or `unblock`
- WHEN the Map is validated
- THEN validation fails and directs the author to classify by closure evidence

### Requirement: REQ-77 — Ticket lifecycle remains minimal
The system MUST persist ticket status only as `open`, `claimed`, `closed`, or `withdrawn`, MUST reserve `closed` for subtype closure evidence, and MUST derive finer delivery phases from owning delivery artifacts.

#### Scenario: Delivery advancement does not copy progress
- GIVEN a claimed delivery ticket whose Plan advances from implementation to review
- WHEN delivery progress is queried
- THEN the reported phase changes while the Ticket and MAP files remain byte-identical

#### Scenario: No-longer-needed ticket is withdrawn
- GIVEN an open or claimed ticket is obsolete, duplicate, descoped, or replaced and no nonterminal sibling still depends on it
- WHEN a named human ratifies withdrawal with a dated reason and optional replacement ticket
- THEN the ticket becomes withdrawn, preserves its history and bindings, and does not claim its subtype closure contract was satisfied

#### Scenario: Withdrawal would strand a dependent
- GIVEN a nonterminal ticket names the candidate withdrawal in `blocked-by`
- WHEN withdrawal is attempted
- THEN it is refused until the dependent is rewired or withdrawn

### Requirement: REQ-78 — Map clear requires outcome acceptance
The system MUST permit `active` to become `clear` only when fog is empty, every ticket is terminal (`closed` or `withdrawn`), and every authored Destination acceptance criterion is satisfied with valid evidence.

#### Scenario: Empty work list is insufficient
- GIVEN an active Map with empty fog and only terminal tickets
- WHEN at least one Destination acceptance criterion is unsatisfied or lacks evidence
- THEN validation rejects `state: clear`

#### Scenario: Complete outcome may clear
- GIVEN an active Map with empty fog, only terminal tickets, and valid evidence for every Destination acceptance criterion
- WHEN the Map is assessed for clear
- THEN the Map is eligible to transition to `clear`

### Requirement: REQ-79 — Delivery binding is reciprocal and canonical
The system MUST bind each delivery ticket to exactly one Brief through reciprocal normalized repository-relative paths and MUST forbid that relationship on non-delivery tickets.

#### Scenario: Reciprocal ticket and Brief validate
- GIVEN a delivery ticket whose `brief` path names a regular Brief and a Brief whose Outcome Map ticket path names that ticket
- WHEN the Map is validated
- THEN the binding is accepted

#### Scenario: Mismatched or escaping binding is rejected
- GIVEN a missing, duplicate, non-reciprocal, absolute, traversing, or store-escaping Ticket-to-Brief path
- WHEN the binding is validated
- THEN validation fails without changing either artifact

### Requirement: REQ-80 — Start delivery owns arc entry
The decision-map workflow MUST provide a Start delivery operation that creates or binds a Brief for a claimed delivery ticket without introducing a separate map-to-task skill.

#### Scenario: Start an unbriefed delivery
- GIVEN a claimed delivery ticket with no Brief binding
- WHEN Start delivery is invoked with a valid new Brief path
- THEN the Ticket and Brief receive reciprocal canonical pointers and the rest of the delivery work is delegated to loom-code

#### Scenario: Recover a partially published Brief
- GIVEN Start delivery published its expected Brief but could not bind the Ticket
- WHEN the operation fails or is retried
- THEN it preserves the Brief as a recoverable orphan, binds it on a valid retry, and never deletes a concurrent replacement

### Requirement: REQ-81 — Delivery progress is read-only
The system MUST resolve delivery progress through Ticket to Brief to Plan and MUST NOT store mutable Plan, Git, PR, or CI state in the Map or Ticket.

#### Scenario: Query a bound Plan
- GIVEN a Plan with one Source brief that reciprocally binds one delivery ticket
- WHEN delivery progress is queried
- THEN the output identifies the Ticket, Brief, Plan, and derived ledger phase without writing any source file

#### Scenario: Ambiguous Plan refuses
- GIVEN two active unsuperseded Plans citing the same bound Brief
- WHEN delivery progress is queried
- THEN the query fails with an actionable ambiguity and writes nothing

### Requirement: REQ-82 — Delivery closure uses current formal evidence
The system MUST reject delivery closure when required acceptance, review, verification, PR, or current exact-head check evidence is missing or stale.

#### Scenario: PR head drift invalidates readiness
- GIVEN a delivery whose recorded review and green checks refer to an older PR head
- WHEN the current PR head differs
- THEN the delivery remains non-closed and progress reports repair-required

#### Scenario: Current evidence permits closure
- GIVEN a delivery whose Brief acceptance, terminal Plan, whole-branch review, verification, and exact-head checks satisfy its closure contract
- WHEN formal delivery evidence is recorded
- THEN the delivery ticket may transition to closed

### Requirement: REQ-83 — Delivery owns one or more exclusive PRs
The system MUST allow one delivery ticket to cite multiple ordered PRs and MUST reject one PR being owned by multiple delivery tickets.

#### Scenario: Multi-PR slice remains open until complete
- GIVEN a delivery ticket whose promised slice requires two PRs
- WHEN only the first PR satisfies its declared role
- THEN the ticket remains claimed and progress names the remaining role

#### Scenario: Shared PR ownership is rejected
- GIVEN two delivery tickets that claim the same PR as delivery evidence
- WHEN closure is evaluated
- THEN validation refuses the ambiguous ownership

### Requirement: REQ-84 — Ticket closure re-enters charting
The workflow MUST record a closed ticket gist and route every newly exposed unknown to fog, a new typed ticket, or Out-of-scope before assessing Map clear.

#### Scenario: Delivery reveals another unknown
- GIVEN a delivery closes and exposes an unresolved question that affects the Destination
- WHEN work-through closes the session
- THEN the unknown is recorded and the Map remains active

### Requirement: REQ-85 — Schema-v2 migration classifies by closure evidence
The system MUST reject schema v2 as needing migration and MUST NOT rename v2 `task` or feasibility `prototype` tickets without inspecting their closure contracts.

#### Scenario: Inventory task migrates to research
- GIVEN a v2 task whose closure is a factual inventory answer
- WHEN migration is prepared
- THEN it is classified as research rather than delivery

#### Scenario: Implementation task migrates to delivery
- GIVEN a v2 task whose closure is a formally shipped outcome slice
- WHEN migration is prepared
- THEN it is classified as delivery and requires a canonical Brief relationship

#### Scenario: Machine feasibility prototype migrates to research
- GIVEN a v2 prototype closed by machine-measured feasibility evidence
- WHEN migration is prepared
- THEN it is classified as research while preserving historical ratification as provenance

#### Scenario: Ambiguous migration refuses
- GIVEN a v2 task whose closure evidence does not distinguish an answer from a delivered slice
- WHEN migration is prepared
- THEN migration refuses and names the classification evidence required

### Requirement: REQ-86 — Clear history is immutable
The system MUST preserve a clear or archived Map as historical evidence and MUST represent later regression or renewed work in a successor Map rather than rewriting the predecessor's closure.

#### Scenario: Regression after clear
- GIVEN a clear Map whose delivered behavior later regresses
- WHEN new outcome work is required
- THEN a successor Map cites the predecessor and the predecessor remains unchanged

#### Scenario: Active retirement is not success
- GIVEN an active Map with unresolved tickets or fog
- WHEN a named human ratifies retirement with a reason
- THEN the Map may become archived without being represented as clear

#### Scenario: Regression inside an active Map
- GIVEN a historically valid closed delivery ticket in a Map that is still active
- WHEN later evidence shows the delivered behavior has regressed
- THEN the old delivery evidence remains unchanged and a new fog entry or follow-up ticket records the current gap

#### Scenario: Archived Map rejects new work
- GIVEN an archived Map
- WHEN any actor attempts to add, claim, bind, resolve, or graduate work in it
- THEN the operation fails and preserves every historical relationship

### Requirement: REQ-87 — Multi-artifact operations are conflict-safe
Within its documented supported local-filesystem assumptions, the system MUST use atomic replacement for single-file transitions, MUST detect the full Map-and-Ticket read set changing before writing, and MUST make reciprocal binding, close-and-rechart, fog graduation, and retirement operations idempotent; when those assumptions or recovery fail, it MUST expose a broken state rather than report success.

#### Scenario: Concurrent claims have one winner
- GIVEN two sessions read the same frontier ticket revision
- WHEN both attempt to claim it
- THEN exactly one claim succeeds and the loser is told to re-read the authoritative ticket

#### Scenario: Reciprocal binding fails on the second write
- GIVEN Start delivery can update one side of a Ticket-to-Brief pair but the second write fails
- WHEN recovery runs or the operation is retried
- THEN it restores the previous pair or completes the same pair without creating a duplicate Brief

#### Scenario: Clear is revalidated before commit
- GIVEN a Map appears clear-eligible at one revision
- WHEN another session adds fog or changes a ticket before the state write
- THEN the clear transition fails as a conflict and the latest Map remains active

#### Scenario: Close and re-chart resumes after interruption
- GIVEN ticket closure, gist recording, and unknown routing were interrupted after a partial step
- WHEN work-through resumes with the same ticket and source revision evidence
- THEN it completes each missing effect exactly once or reports the conflicting authoritative state

#### Scenario: Terminal write is the final close step
- GIVEN a close-and-rechart operation has validated subtype evidence and prepared its gist and unknown-routing effects in a recoverable operation record
- WHEN the operation commits
- THEN all Map-side effects become recoverable before the Ticket is terminalized, and the terminal Ticket write is the final mutation

#### Scenario: Unsupported or uncertain filesystem semantics
- GIVEN the workflow cannot establish its documented atomic-replacement and path-integrity assumptions
- WHEN a mutating operation is requested
- THEN it refuses before mutation and names the unsupported assumption

#### Scenario: Fog graduation is interrupted
- GIVEN a graduation operation creates a Ticket but is interrupted before removing its source fog entry
- WHEN the same graduation is retried
- THEN it repairs the same fog-to-ticket relation exactly once or reports a conflicting authoritative state

#### Scenario: Retirement races descendant mutation
- GIVEN a retirement operation read the Map and all nonterminal Tickets
- WHEN any descendant Ticket changes before the archive state write
- THEN retirement loses the conflict and the Map remains non-archived

### Requirement: REQ-88 — Liveness, frontier, and resume are explicit
The workflow MUST distinguish absent, broken, single-live, and ambiguous-live Map selection and MUST report the next owning CTA for every frontier or claimed-ticket re-entry state.

#### Scenario: Broken Map is not absence
- GIVEN an existing Map fails schema validation
- WHEN liveness is assessed
- THEN the workflow reports broken and refuses to initialize a replacement Map

#### Scenario: Active Map has no frontier
- GIVEN an active Map whose tickets are all blocked or claimed, or whose only remaining gap is unsatisfied Destination acceptance
- WHEN the frontier is queried
- THEN the output distinguishes blockers, current owners, and acceptance gaps and names the corresponding wait, repair, or re-chart CTA

#### Scenario: Delivery re-entry names the owner
- GIVEN a claimed delivery ticket with a derived phase from unbriefed through ready
- WHEN a later session resumes it
- THEN progress names the authoritative artifact and next CTA for that phase without reconstructing prior conversation

### Requirement: REQ-89 — Evidence has fail-closed validity states
The system MUST distinguish valid, invalid, stale, unavailable, unauthorized, pending, and contradictory evidence and MUST query external PR and check truth live at delivery close rather than accepting cached status.

#### Scenario: External service is temporarily unavailable
- GIVEN a required PR or check query times out, is rate-limited, or returns a partial response
- WHEN delivery closure or Map clear is assessed
- THEN the result is retryable unavailable, no closure mutation occurs, and it is not reported as failed or absent

#### Scenario: Exact-head evidence changes before close
- GIVEN live checks were green for an observed PR head
- WHEN the head or required check set changes before the ticket write
- THEN close is refused and the new head must pass review and live verification

#### Scenario: Contradictory acceptance evidence
- GIVEN two current evidence sources disagree about a Destination acceptance criterion
- WHEN clear is assessed
- THEN the criterion remains unsatisfied and the contradiction is reported for resolution

### Requirement: REQ-90 — Destination acceptance has stable auditable grammar
The system MUST give every Destination acceptance criterion a never-reused `DA-<n>` identity, explicit open or satisfied state, an evidence pointer when satisfied, and human ratification when the criterion requires evaluative judgment.

#### Scenario: Objective criterion is satisfied
- GIVEN an open objective DA criterion and inspectable evidence that meets its authored test
- WHEN its state is changed to satisfied
- THEN the criterion retains its id and records the evidence pointer

#### Scenario: Evaluative criterion lacks ratification
- GIVEN a DA criterion whose authored test requires human judgment
- WHEN evidence is attached without a named dated ratification
- THEN the criterion cannot become satisfied

#### Scenario: Acceptance id is removed or reused
- GIVEN a previously authored DA id
- WHEN validation observes silent deletion or reuse for another criterion
- THEN validation fails and requires preservation or explicit retirement history

### Requirement: REQ-91 — Migration is previewable and idempotent
The system MUST produce a zero-write v2-to-v3 migration preview with source digests and proposed classifications before mutation, MUST preserve historical evidence, and MUST produce the same result without duplication when retried.

#### Scenario: Ambiguous preview writes nothing
- GIVEN a v2 Map containing a ticket whose closure type cannot be inferred from evidence
- WHEN migration preview runs
- THEN it names the ambiguity and no repository file changes

#### Scenario: Source changes after preview
- GIVEN an accepted migration preview for a known source digest
- WHEN any source artifact changes before apply
- THEN apply refuses and requires a fresh preview

#### Scenario: Applied migration is retried
- GIVEN a v2-to-v3 migration already completed for the same source mapping
- WHEN the operation is retried
- THEN it reports the existing result without duplicating tickets, bindings, evidence, or ids

### Requirement: REQ-92 — Fog and gist relations are monotonic
The system MUST keep fog and Destination-acceptance ids monotonic, MUST allow each fog entry to graduate at most once, and MUST maintain exactly one Decisions-so-far gist link for every closed ticket.

#### Scenario: Fog id is reused
- GIVEN a fog id that previously graduated or moved Out-of-scope
- WHEN another entry attempts to use that id
- THEN validation fails

#### Scenario: Closed ticket lacks or duplicates a gist
- GIVEN a closed ticket with zero or more than one Decisions-so-far link
- WHEN the Map is validated
- THEN validation fails and names the required one-to-one relation

### Requirement: REQ-93 — Charting and terminal records are mutation-guarded
The system MUST reject work-through operations while a Map is charting and, after a close or withdrawal transaction commits, MUST treat the complete persisted bytes and all relationships of every terminal ticket as immutable.

#### Scenario: Charting Map receives a work operation
- GIVEN a Map still in charting state
- WHEN an actor attempts to claim, bind, resolve, close, or clear work
- THEN the operation fails without mutation and identifies activation prerequisites

#### Scenario: Charting Map is abandoned
- GIVEN a charting Map that will not be activated
- WHEN a named human ratifies abandonment with a reason
- THEN the Map may become archived without being represented as clear

#### Scenario: Closed ticket receives a correction
- GIVEN a closed ticket whose conclusion or delivered behavior is now disputed
- WHEN an actor attempts to change its type, binding, claim, evidence, or Resolution
- THEN the mutation is refused and the workflow directs the correction to new fog or a follow-up ticket

#### Scenario: Withdrawn ticket receives a work operation
- GIVEN a withdrawn ticket
- WHEN an actor attempts to claim, bind, resolve, close, withdraw again, or edit its recorded disposition
- THEN the operation fails and the terminal ticket remains byte-identical

#### Scenario: Closed ticket receives a metadata edit
- GIVEN a closed ticket
- WHEN an actor attempts to edit its description, selection basis, graduation source, blockers, gist relationship, or any other persisted field
- THEN the operation fails and the terminal ticket and Map remain byte-identical

### Requirement: REQ-94 — Dependency graphs are same-Map and acyclic
The system MUST reject a ticket blocker graph containing a missing target, cross-Map target, self-edge, duplicate edge, or cycle and MUST forbid claiming a ticket until every blocker is closed.

#### Scenario: Concurrent edits create a cycle
- GIVEN two individually valid blocker edits would form a cycle when combined
- WHEN the later edit is applied against the current Map revision
- THEN the edit is rejected and the prior acyclic graph remains authoritative

#### Scenario: Blocked ticket is claimed
- GIVEN an open ticket with at least one non-closed blocker
- WHEN a claim is attempted
- THEN the claim fails and identifies the blocking ticket

### Requirement: REQ-95 — Archive preserves stable identity
The system MUST archive a Map by state transition at its stable path and MUST NOT physically relocate the Map or invalidate reciprocal artifact links.

#### Scenario: Clear Map is archived
- GIVEN a clear Map with delivery Briefs pointing to its Tickets
- WHEN the Map is archived
- THEN its directory and Ticket paths remain unchanged and every reciprocal link still validates

### Requirement: REQ-96 — Delivery closure policy is authored
Every delivery Brief MUST declare exactly one closure policy of `pr-ci`, `merged`, or `artifact`, MUST name policy-specific evidence, and MUST have at most one Plan; the workflow MUST NOT infer a weaker policy or create a second Plan for the same Brief.

#### Scenario: PR-CI policy closes at current reviewed head
- GIVEN a delivery Brief declaring `pr-ci`
- WHEN its whole-branch review, verification, repository-required checks, and live exact-head evidence pass
- THEN the delivery is closure-ready without requiring merge

#### Scenario: Merged policy has only a green open PR
- GIVEN a delivery Brief declaring `merged`
- WHEN its PR is green but not merged
- THEN the delivery remains claimed

#### Scenario: Artifact policy names no acceptance probe
- GIVEN a delivery Brief declaring `artifact`
- WHEN no artifact path and acceptance probe are authored
- THEN the binding or closure validation fails

#### Scenario: Second Plan cites the same Brief
- GIVEN one Plan already cites a bound delivery Brief
- WHEN another Plan attempts to cite the same Brief
- THEN the second relation is rejected rather than silently superseding the first Plan

#### Scenario: The only Plan becomes unusable
- GIVEN a claimed nonterminal delivery ticket whose Brief's sole Plan is abandoned or structurally unusable
- WHEN replacement work is needed
- THEN the owning delivery ticket is withdrawn with its history preserved and a new delivery ticket and Brief own the replacement Plan

### Requirement: REQ-97 — Claims are not transferable
The workflow MUST refuse any edit that reassigns a claimed Ticket to a different owner; an abandoned claimed Ticket MUST leave `claimed` only through Withdrawal.

#### Scenario: Second claim on an already-claimed Ticket is refused
- GIVEN a Ticket whose `claim:` line already names an owner
- WHEN another session attempts to claim that same Ticket
- THEN the claim is refused and the Ticket's `claim:` line is unchanged

#### Scenario: An abandoned claimed Ticket is withdrawn
- GIVEN a claimed Ticket that will not be worked further
- WHEN the Ticket is withdrawn
- THEN its history records `withdrawn-from: claimed`

### Requirement: REQ-98 — Retirement requires a fully valid store
The system MUST refuse charting, active, clear, or archived state transitions while any Map invariant is broken or any recoverable multi-artifact operation is incomplete.

#### Scenario: Retirement observes partial fog graduation
- GIVEN a Ticket exists for a fog graduation whose source fog entry has not yet been removed
- WHEN retirement is requested
- THEN retirement writes nothing and directs the operator to repair or complete the graduation first

#### Scenario: Retirement observes a clean stable snapshot
- GIVEN every Map, Ticket, fog, gist, binding, and in-flight-operation invariant validates at one stable revision
- WHEN an authorized retirement transition commits against that same revision
- THEN the archive state write may proceed
