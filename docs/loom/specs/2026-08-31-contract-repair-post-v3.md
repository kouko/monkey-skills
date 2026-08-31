# Contract repair after Outcome Map v3 + Task Batch Review

> Entry artifact (frozen brief). Ratified 2026-08-31 by kouko after a
> three-round review: (1) general review of merged #765/#766, (2) an
> adversarial opus verification of the findings, (3) an independent-advisor
> codex audit leg (gpt-5.6-sol @ effort high, 320,571 tokens, record at
> /tmp/advisor-v3-output.txt), plus a live-mechanism review of the batch
> review pipeline contributed during ratification. Verbatim record:
> "ＯＫ 幫我做吧" (2026-08-31) following the item-by-item presentation of
> all decisions below.

## Goal

Repair the operational and governance defects introduced by #765 (Outcome Map
v3) and #766 (Task Batch Review) without reverting either: ratify v3
retroactively with a recorded decision trail, enforce the invariants v3
documented but did not implement, restore the cross-store boundary contract
v3 deleted, unblock the live plans #766 refuses, and give the batch review
pipeline its missing executable orchestration path (the "adapter").

## Decisions (all ratified)

### Governance (loom-workflow + repo docs)

| # | Decision |
|---|---|
| R1 | **Retroactive v3 ratification.** `docs/loom/outcome-map-v3/proposal.md` moves `Status: exploration` → `Status: ratified — kouko, 2026-08-31` (one user-ratified line). The v3 plan's empty `## Decision Log` (docs/loom/plans/2026-08-30-outcome-map-v3.md) is filled with the itemized v3 semantic decisions, each tagged `user-ratified: kouko, 2026-08-31`. Ratification basis: this arc's conversation (v3 semantics were presented with codex's design verdict and the owner approved the repair arc). |
| R2 | **Proposal-status intake gate.** New small checker refusing a plan/change arc whose source proposal carries a non-ratified status; wired as one line into the existing writing-plans intake contract (alongside check_onramp_choice / check_queue_relation). Closes the "Status: exploration merged as major version" hole. |
| R3 | **v3 invariant enforcement** (map_store.py, TDD): (a) `state: active` requires ≥1 Destination Acceptance entry; (b) the `user-ratified:` line validator rejects empty values; (c) objective DA evidence must be a resolvable pointer (existing commit SHA / PR number / artifact path — non-empty string no longer suffices). |
| R4 | **Migration repair** (migrate_map_v3.py): nonterminal (open/claimed) v2 tickets may migrate via an explicit classification manifest (ticket slug → target type, authored at migration time) instead of demanding closure evidence they cannot have. Ambiguous CLOSED tickets still refuse. |
| R5 | **Live map repair**: family-relocation MAP.md gains ratified Destination Acceptance entries (drafted from its Destination prose, each tagged `user-ratified: kouko, 2026-08-31`); the two live tickets migrate under R4's manifest; the retired relay remnant in task-inventory-consumers.md ("解決方式：建立 backlog 條目排程此盤點工作") is rewritten to direct-execution semantics. |
| R6 | **Cross-store boundary restored** (decision-map/references/map-format.md): the three deleted rules return — promotion close-and-cite (`origin: promoted to <ticket>`), map→backlog travel release-only, reopen-promoted-entries-on-archive — defined at ONE point in map-format, cited by decision-map SKILL.md, with regression tests asserting both the map-side and backlog-side (loom-code template) contracts. Also extend check_contract_citations.py's scan set to include loom-workflow (it currently scans loom-code only). |

### Batch review pipeline (loom-code)

| # | Decision |
|---|---|
| R7 | **SDD batch-review adapter**: one executable orchestrator entrypoint in loom-code/scripts (CLI) providing the single assembly-free execution path: `ready` (batch readiness check) → `packet` (build sealed ReviewPacket from the validated plan) → `record-dispatch` (write a dispatch receipt — the idempotency record) → `apply-result` (feed the terminal verdict through resolve_aggregate_review + atomic ledger write). Built by wiring review_batch.py's existing sealed-packet and resolve functions behind a CLI (task_batch_replay.py is a dispatch-metrics comparison harness, not the chain — corrected 2026-08-31 with kouko's approval after plan-review round 2 falsified the original "extract from task_batch_replay.py" premise); tested by driving the subcommands on a synthetic validated plan. Documented as the executable call contract in subagent-driven-development SKILL.md's batch checkpoint. |
| R8 | **Idempotency**: a crash after reviewer dispatch is recoverable via the dispatch receipt — re-entry refuses a second dispatch for a batch whose receipt exists and has no terminal result yet (re-collect instead of re-send). Multi-batch readiness is operationalized inside the `ready` subcommand (a batch is ready when every member is implemented(<sha>) and no member participates in another non-terminal batch). |
| R9 | **Whole-branch entry disambiguation** (prose, SDD skill): after every batch is finalized (or individually resolved), the run necessarily enters the existing whole-branch review — stated as an unconditional sequence step, removing the interactive-mode ambiguity. |
| R11 | **Batch path end-to-end walkable** (added 2026-08-31 with kouko's approval — "做吧" — after the first real dogfood of R7 found the batch pipeline broken at three points outside the adapter; supersedes plan DL-1's out-of-scope ruling). (a) Referent grammar: `owned_requirements` accepts every `Brief item covered` referent plan-format admits (REQ-<n>, BI-<n>, quote) — non-empty is the only requirement — in both check_review_batches.py and review_batch.py's projection validator. (b) SHA grammar: `plan_card.py --set-status` expands `implemented(<short>)`/`done(<short>)` to the 40-hex form via `git rev-parse` at write time, so the CLI's 40-hex rule is met by construction. (c) Ledger write-back: `apply-result` performs the atomic Batch status update (finalize → every member `done(<sha>)`, reopen → owner union back to pending) through plan_card's `atomic_batch_status_update`; the repo-root `scripts/plan_card.py` stays the exec shim onto `loom-code/scripts/plan_card.py` it already is (plan-review amendment round 1 falsified the "two divergent copies" premise — the orchestrator misread a `diff -q` of shim vs. full script; corrected 2026-08-31), pinned by a test so it is never replaced with a second full copy. (d) Pilot: this arc's own `map-side-invariants` Batch is driven through the four CLI steps end to end as the acceptance proof. |
| R10 | **Live plans unblocked**: the four nonterminal plans identified by the audit (2026-08-24-cross-host-review-gate-hardening{,-part-2,-part-3}, 2026-08-24-review-binding-remediation) are amended with `individual` review dispositions + a minimal `## Review Batches` section. Historical/terminal plans are NOT touched (no permanent runtime compatibility — the refusal stands for terminal records). |

### Explicitly rejected (ratified)

- **No revert of #765 or #766** (codex verdict accepted: taxonomy and
  fail-closed architecture are sound).
- **No "default to individual until pilot passes"** — batch grouping stays the
  default; the fail-closed fallback bounds the risk, and the first real
  dogfood of R7's entrypoint IS the pilot (owner chose this over paying the
  transitional cost of individual-default).
- **No CAS/renameat2 simplification in this arc** — codex judged the
  pathname-exchange layer over-engineered, but it is not defective; simplifying
  it is out of scope here (a cheap-hardening candidate for a later arc, not a
  repair).

## Out of scope

- Renaming `grilling` → `decision` (codex suggestion; separate arc — touches
  every existing grilling ticket's semantics).
- One-Plan-per-Brief lifetime rigidity (codex suggestion; design change, not
  a repair).
- The `grilling`/prototype/research reclassification of already-closed tickets.
- Queue-layer physical relocation (family-relocation fog F-1..F-4).

## Execution order

1. Governance docs (R1) + map_store invariant tests-first (R3) + migration
   manifest (R4) — decision-map side.
2. Boundary restoration (R6) with regression tests.
3. Live map repair (R5) once R3/R4 land.
4. Adapter entrypoint (R7, R8) with replay-harness-as-test, TDD.
5. Prose disambiguation (R9) + live-plan amendments (R10) + intake gate (R2).
6. Version bumps: loom-workflow + loom-code (skill/scripts content changed in
   both; codex mirror manifests via the existing sync script).

## Verification floors

- `python3 -m pytest loom-workflow/skills/decision-map/scripts/ -q` green
  (new RED tests: active-without-DA, empty user-ratified, unresolvable
  evidence, manifest-migration for open tickets, boundary prose greps).
- `python3 -m pytest loom-code/scripts/ -q` green (adapter subcommands,
  receipt idempotency refusal, boundary template tests).
- `python3 loom-code/scripts/check_contract_citations.py` green with the
  extended scan set.
- `python3 loom-code/scripts/check_review_batches.py <amended plan>` exit 0
  for each of the four amended plans.
- `map_store.py validate` on the repaired family-relocation map: exit 0; and
  the migrated tickets validate under v3.
## Design-side on-ramp

fired: rows 0 — user chose direct

Basis: design exploration was completed before this brief via three review
rounds plus the codex audit; the user ratified the arc on 2026-08-31.

## Queue relation

unqueued — this arc repairs defects in contracts merged <48h ago; it is not a
queued bet and does not displace any backlog entry. Map-side ownership:
family-relocation (its live tickets are repaired here as R5).
