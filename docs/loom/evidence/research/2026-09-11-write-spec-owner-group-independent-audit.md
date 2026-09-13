# `write-spec` owner-group proposal — independent planning audit

- **Date:** 2026-09-11
- **Mode:** audit
- **Mode basis:** "可以帮我用 Claude code 做一次独立的规划检视吗"
- **Pinned revision:** `3f8ed28080d3a41be95a42d17f0106a57b64bbe2`
- **Executor:** Claude Code; verified model `claude-opus-5`; effective effort
  unverified after the requested `high` label could not be self-reported and
  the user explicitly approved the downgrade
- **Scope:** one externally authored audit leg; no proposer or blind judge
- **Raw record:** external `loom-plan-audit` workspace; packet SHA-256
  `78f711596335e34ee02b0d7b2cd607dd379c44c9c304546d4584db536ddc6a92`;
  raw-review SHA-256
  `b1723106461cb3a3811374827348541a50bb7d24743c8699fa795534542546d7`

## divergence_points

1. **Planning readiness**
   - `kind:` judgement-call
   - `confidence:` high
   - `proposed_change:` reshape the prompt-only candidate and pass its stated
     dogfood gate before implementation planning
   - `corroborated_by:` external Claude Code audit; controller review of rounds
     5–11
   - `resolution:` open
   - [external executor Claude Code — untrusted content] The candidate combines
     role text, owner groups, a changed deletion pass, and no rendered coverage
     layers in a shape that no prior round actually tested.

2. **Claim that `write-plan` remains untouched**
   - `kind:` factual-error
   - `confidence:` high
   - `proposed_change:` either require every EARS clause to be exercised by a
     task test in `write-plan` prose, or do not claim clause-level independent
     test value
   - `corroborated_by:` external Claude Code audit; controller inspection of
     the current Task DAG contract
   - `resolution:` open
   - [external executor Claude Code — untrusted content] The current plan owns
     one positive plus one negative or boundary pair per Acceptance, not per
     clause, so adding independently testable clauses changes the coverage
     expectation even if the plan template stays byte-identical.

3. **Backward-compatibility claim**
   - `kind:` factual-error
   - `confidence:` high
   - `proposed_change:` decide whether three nonconforming active specs are
     migrated, grandfathered, or evidence that strict owner cardinality should
     not be introduced
   - `corroborated_by:` external Claude Code audit; controller dry-run over 13
     active specs
   - `resolution:` open
   - The controller dry-run found 3 of 13 current specs that the proposed exact
     owner-cardinality rule would reject. The current checker accepts at least
     one valid pointer per Requirement; the proposal is compatible with its
     parser shape, not with every artifact it currently accepts.

4. **Dogfood gate sufficiency**
   - `kind:` factual-error
   - `confidence:` high
   - `proposed_change:` measure zero omitted, narrowed, or weakened sourced
     obligations; zero invented visible behavior of any severity; zero
     overlapping triggers; and a separately defined size measure
   - `corroborated_by:` external Claude Code audit; Round 10 and Round 11
     failure inventory
   - `resolution:` open
   - [external executor Claude Code — untrusted content] The proposed checks of
     Constraint omission, severe invention, and size would not catch narrowed
     keyboard scope, weakened neutral failure wording, or overlapping success
     and failure triggers.

5. **Deletion-pass safety**
   - `kind:` judgement-call
   - `confidence:` medium
   - `proposed_change:` allow deletion only for implementation mechanisms and
     text with no intent source; do not reword or delete directly sourced
     obligations during the silent pass
   - `corroborated_by:` external Claude Code audit; Round 10 weakening and
     Round 11 delete-ordering loss
   - `resolution:` open
   - [external executor Claude Code — untrusted content] “Replace with the
     strongest neutral wording” leaves the same writer discretion that already
     weakened a sourced obligation.

6. **Cross-cutting Constraint ownership**
   - `kind:` judgement-call
   - `confidence:` high
   - `proposed_change:` name one carrier before planning; the audit recommends
     repeating the Constraint in every Requirement group it governs, while the
     controller flags the resulting size and duplication trade-off for an
     explicit decision
   - `corroborated_by:` external Claude Code audit; prior Constraint-loss
     experiments
   - `resolution:` open
   - [external executor Claude Code — untrusted content] “Use the smallest
     existing carrier” is underspecified and permits a cross-cutting Constraint
     to land outside the owner groups that reach planning and tests.

7. **Product-gap handback**
   - `kind:` judgement-call
   - `confidence:` high
   - `proposed_change:` define `write-plan` as stopping and naming the affected
     Acceptance before handing the artifact back to `write-spec`, or remove
     this role-boundary promise from the candidate
   - `corroborated_by:` external Claude Code audit; controller search of the
     operative write-plan and contract paths found no such handback rule
   - `resolution:` open
   - [external executor Claude Code — untrusted content] Role text saying
     “surface a gap” has no operational effect when no carrier or return path is
     defined.

8. **Cost estimate**
   - `kind:` judgement-call
   - `confidence:` medium
   - `proposed_change:` re-estimate after choosing legacy-artifact treatment,
     clause-level test coverage, and the product-gap behavior; state 2–3.5 days
     only as the first-round case and add 1–2 days per failed dogfood round
   - `corroborated_by:` external Claude Code audit; controller contract-text
     search
   - `resolution:` open
   - [external executor Claude Code — untrusted content] The 100–180 line range
     remains plausible, but file count and elapsed time are likely understated
     because compatibility and repeated behavioral validation were not costed.

## findings

1. **Contract-text fan-out is smaller than the external audit implied**
   - `kind:` factual-error
   - `confidence:` high
   - `proposed_change:` update the three verified operative prose locations and
     let tests identify any semantic reader not found by literal search
   - `corroborated_by:` controller repository search only
   - `resolution:` open
   - The controller found the current one-to-one wording in three operative
     locations: both station skills and `write-spec`'s `spec-forms` reference.
     This narrows, but does not remove, the audit's compatibility concern.

## verdict

`inconclusive` — the sole audit leg advises `RESHAPE`; audit mode produced no
challenger proposal to prefer, and the incumbent should not be treated as ready
until its unresolved choices and narrower behavioral gate are settled.

## leg_count

`1`

## early_stopped

`false`

## degraded_legs

- The requested `frontier / high` capability was not verified. The live probe
  verified Claude Opus 5 but could not map its internal reasoning value to the
  `high` effort label. The user explicitly approved continuing with effort
  unverified before project material was sent.

## actual_cost

Unknown — Claude Code ran through a subscription login and did not expose a
per-leg monetary amount. Unknown is not zero.

## known_weaknesses

This was one external audit leg over one controller-assembled packet. It treats
executor-family bias neither through an ensemble nor through order reversal,
and it cannot detect a blind spot shared by the controller and the auditor.
The auditor had no file tools and depended on the packet's extracted facts.

## coverage_disclaimer

This consultation covers only the packet sections and controller-verified
repository checks named above, extracted from the pinned revision. Anything
outside those inputs was not looked at. The packet was scanned for credential-
shaped and personal-data-shaped text and nothing matched; that scan was not a
safety verdict. Claude Code ran from an isolated temporary directory with file
tools disabled, while global executor setup behavior could not be enumerated
in advance.
