# Conditional operations

Read only the section whose trigger fires. The core SDD loop, review packet,
verdict table, retry caps, ledger rule, model selection, and status routing stay
in `SKILL.md`.

## Capacity-error recovery

When a subagent call returns a usage-limit or `529 Overloaded` error, do not
silently retry. Finish and commit tasks already `DONE` in the wave, then use
`dispatch-hygiene-notes.md` §Capacity-error recovery for the three recovery
options and retrospective reviewer dispatch after capacity returns.

## User-question delivery

Use these rules only when `SKILL.md`'s ask policy says a question is warranted:

1. Describe outcomes, not internal agent mechanics.
2. Translate jargon and expand acronyms on first use; terms introduced by the
   user in this session are fine.
3. Explain numbers (`PASS 12/12` becomes “all 5 tasks checked out”) before
   showing machine detail.
4. Open with one line stating the current state and what the choice changes.
   Put that anchor inside the structured question field. Never offer a CLI
   command before confirming it exists. For a mid-arc question (SDD gate ③
   asks, kickoff-briefing escalations, complex-fork briefs), extend that same
   line into a direction anchor: name the remote goal (`docs/loom/PURPOSE.md`'s
   `**Why:**` line, or the governing map's Destination when the plan's
   `## Notes` carries a `Map part: <map-id> / Part: <name>` line), the near
   goal (the plan's `Goal:` line), and this
   decision's relation to them — one sentence, not a new field.
   Discovery-phase (brainstorming) questions are exempt: direction is itself
   the topic there.
5. Offer at most four options; do not add an explicit “Other”. Invite free-form
   input for open design questions, not closed factual questions.
6. Combine questions only when they share one topic and can be judged together.
7. Prefer the host's structured question tool for non-trivial choices. A prose
   question is valid only when its first line contains the same state-and-stakes
   anchor.

For the calibrated good/bad example, read `dispatch-hygiene-notes.md` §Worked
example. For a complex fork, apply `loom-code/hooks/family-reception.md` §Brief before a
complex fork.

### Progress-card delivery

`python3 scripts/plan_card.py <plan-path> --set-status
"T<N>=<status>"` and `--set-stage "<text>"` print the card after the flip. Use
the repo-root script when present, otherwise the plugin-shipped copy. Relay its
output in the conversation language using `loom-code/hooks/family-relay.md` §(a2). If
neither script or the relay contract exists, render goal, task table, stage,
and next action inline. Always re-read the plan; never compose the card from
memory or copy its template here.

When the host provides task tools, mirror the plan tasks and update the mirror
with each ledger flip. This is display-only: the plan's `Status` remains the
source of truth. Hosts without task tools skip this silently.

## Review-weight mechanics

Read when a plan declares `Review-weight: mechanical` or `Review-weight:
prose`; otherwise run the full reviewer pair.

### Mechanical self-check

This lane requires implementer `DONE` and all three checks:

1. **Content match.** The Description must name either a literal target/diff or
   a deterministic sync script plus its SSOT. For a literal, confirm the
   post-edit string in every declared file or compare the exact diff. Before
   trusting a sync script, require it to be clean and absent from `Files
   touched`; then re-run it and require zero diff, or run its paired drift test.
2. **Scope match.** The commit diff must be a subset of `Files touched`, with no
   changes outside the exact target.
3. **Suite green.** Run the resolved package test command after the commit.

Any failure or ambiguity falls back to the full reviewer pair. All three
passing resolve the task as `DONE` without reviewer verdicts. The plan-time
eligibility gate is `plan-document-reviewer` Check 16.

### Prose and record-class routing

`Review-weight: prose` keeps spec-reviewer and substitutes docs-reviewer for
code-quality-reviewer. It applies only when declared and actual changed files
are authored `.md` prose; any code, config, or generated artifact falls back to
the full reviewer pair. Docs-reviewer receives the same immutable packet and
reviews the contract-class subset. Its verdict occupies the quality column of
the normal verdict table.

Classify contract-class versus record-class with
`requesting-code-review` §Classification. All-record-class work dispatches only
spec-reviewer and records `code-quality slot: N/A — record-class prose`; mixed
work sends only the contract-class subset to docs-reviewer. The record-only
lane resolves from spec-reviewer's verdict alone.

## Batch review and individual fallback

Read when a validated new plan assigns a Task to a Review Batch. Apply this
ordered fail-closed sequence; do not skip ahead after a failure:

1. Require each member's committed final bytes to pass its resolved Task-local
   mechanical verification, then let only SDD write `implemented(<sha>)`.
2. When some members are not implemented but the common boundary is still
   valid and the current closable window can still finish, park the implemented
   member: keep its status unchanged, create no Packet, dispatch no reviewer,
   and perform no additional ledger mutation. Advance to the next runnable Task
   in the same Batch. Temporary incompleteness is not individual fallback and
   introduces no timeout, size threshold, configuration, or Batch state.
3. Once the complete member set is implemented, run the mandatory
   `check_review_batches.py` checker and require Batch readiness under its
   validated DAG, lane, boundary, and current closable window. Revalidate
   after any member or plan change. Only an invalid boundary or proof that this
   window cannot close selects individual fallback.
4. Issue the exact sealed `ExecutionAuthorityProjection` from the checker's
   canonical current-plan payload and the trusted plan, spec, and ownership
   records. A caller-created, missing, or context-mismatched projection stops
   here: zero Packet, dispatch, and mutation.
5. Resolve an executable aggregate command through verification-before-
   completion's declared-first rule. `Aggregate verification` in the plan is
   inert identity-bearing description; never parse or execute it as shell.
6. Execute only the resolver's argument vector in its approved scope. Require
   successful evidence and a persistable safe identity, then issue the exact
   `SafeResolutionReceipt` consumed by `review_batch.py`.
7. Materialize one immutable aggregate Packet from the complete implemented
   snapshot, exact committed bytes, validated ownership and boundary, and that
   receipt. Only after `validate_packet` accepts it may reviewer dispatch occur.
8. Select the existing lane arms: full is spec plus code-quality; authored
   prose is spec plus docs; all-record-class prose is spec only. Mechanical is
   not an aggregate full-review lane. Dispatch each selected arm exactly once
   against the same Packet and require one authoritative terminal result each.
9. Reduce with `resolve_aggregate_review`. A finalize or reopen result must
   carry the reducer-issued sealed transition authority for the exact Packet,
   declaration and dispositions, complete member snapshot, complete arm
   outcomes and findings, action, owner union, and closed finding set. Under
   the shared plan lock, plan-card re-reads the current declaration and member
   statuses and requires an exact match before writing. All-pass atomically
   finalizes; attributable blocking findings atomically reopen the owner union;
   a repaired owner repeats Task-local verification and forces a fresh Packet;
   missing authority, any authority/current-plan drift, or wait/refuse performs
   zero mutation. The receipt is passed directly and is never persisted as
   Batch state.
10. On `individual_fallback`, perform zero Batch ledger mutation and route every
   member through the existing individual path, including a fresh per-Task
   immutable context packet and the existing lane-specific reviewer loop. This
   individual fallback does not create Batch state, retry state, or another
   queue.

Any failure in checker, projection issuance, resolution, execution, evidence,
or safe identity creates no Packet, dispatches no reviewer, mutates no status,
and uses the existing verification recovery path. An ineligible boundary or
unassignable finding selects individual fallback; it is not permission to guess
a smaller group.

### Result file for `apply-result`

`batch_review_cli.py apply-result --result-file <json>` reads one JSON object
the orchestrator assembles from the reviewer arms' terminal results. No script
emits it (`task_batch_replay.py` consumes comparison files; it never writes a
result file). Its keys are exactly what `_cmd_apply_result` reads:

- top level: `{arm_bindings, terminal_results}` — no other key.
- each `arm_bindings` entry: `{packet_identity, arm, dispatch_identity,
  evidence_identity}`.
- each `terminal_results` entry: `{packet_identity, arm, dispatch_identity,
  dispatch_evidence_identity, result_identity, evidence_identity, terminal,
  verdict, findings}`.
- each `findings` entry: `{finding_id, packet_identity, owners, blocking,
  ground, ground_ref, location, severity, reason}`.

`packet_identity` is required on every binding, result and finding, and must
equal the identity the `packet` subcommand emitted for this Batch. A missing
or mismatched value refuses the whole file before any finding is interpreted;
a result given for another packet means re-send the dispatch.

A finding's `ground_ref` must equal the referent its `ground` names
**verbatim**: for `owned_requirement`, one string of the owner's
`owned_requirements` exactly as the plan ledger states it; for
`stated_acceptance`, one `acceptance` entry; for `direct_regression` or
`safety_defect`, one `declared_files` path. A shorthand (`R3c` where the
ledger carries the full requirement string) does not match, so the finding is
`unassignable_finding` and the reducer selects `individual_fallback` — the
Batch's saving is lost exactly when a defect was found.

The CLI's seal binds bytes and identities, not reviewer authenticity. A
hand-written PASS whose identities match the right packet is
indistinguishable from a real reviewer's result; the orchestrator's dispatch
discipline (one fan-out per Batch, results copied from the reviewers'
returns) owns that property, and the CLI cannot check it.

## Orchestrator command hygiene

Read when the orchestrator edits after review, runs commands, or handles
version metadata:

- Before editing a file located through shell inspection, use the host's file
  read operation on that file. The edit tool tracks read-tool calls, not bytes
  that happened to be printed, so `grep` / `sed` / `cat` output does not satisfy
  the precondition: the first edit fails with a not-yet-read error, and in a
  batch that failure repeats on every remaining target.
- Apply `dispatch-hygiene-notes.md` §Environment hygiene to direct commands.
- For version parsing or manifest work, confirm a library is standard-library
  before importing it; do not add a third-party parser accidentally.

## Reviewer-retry research

Read `research-escalation.md` before the third re-dispatch when round two
repeats the same unresolved question, immediately when a finding includes
`evidence_needed:`, or before surfacing a semantics/convention `BLOCKED` state.
Do not use this escalation for missing dependencies or broken test
infrastructure.

## Role prompt catalog

Read only the prompt for the role being dispatched:

- `../../../agents/implementer.md`: worker; code, tests, and status.
- `../../../agents/spec-reviewer.md`: binary spec coverage verdict.
- `../../../agents/code-quality-reviewer.md`: three-valued quality verdict.
- `../../../agents/docs-reviewer.md`: prose quality verdict for its eligible lane.

Each role carries the managed baseline from `../../../scripts/_baseline.md`.
Spec-reviewer does not evaluate code quality; quality reviewers do not evaluate
spec coverage.

The skill-local `standards/`, `rubrics/`, and `checklists/` are generated
functional copies of the canonical code-team knowledge layer. Change the
canonical source, run `python3 loom-code/scripts/distribute.py`, and let
`verify-drift.py` enforce identity. See `../../../scripts/canonical/README.md`.
