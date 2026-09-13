# Retry malformed reviewer output without routing escalation
originator: maintenance-loop
kind: engineering
needs-design: no — no user-visible product behavior changes
evidence: [loom-code/skills/review/SKILL.md, loom-code/references/dispatch-profile.md, loom-code/scripts/dispatch_profile.py, loom-code/scripts/claude_reviewer.py, loom-code/agents/reviewer.md, loom-code/scripts/test_dispatch_profile_resolver.py]
status: confirmed 2026-09-12
publication: manual — no push, pull request, or merge is authorized

## Problem
Closing Review may receive substantive reviewer output whose verdict and findings are usable but whose shape violates the reviewer contract, such as `PASS_WITH_NOTES` with more than three `notes`. The Review contract permits one same-digest retry before a conforming verdict exists, but the shared resolver currently turns the resulting completed, unsuccessful, non-conforming observation into `execution-failed / no-legal-redispatch`.

## Proposed outcome
Make the executable dispatch decision agree with Closing Review: a completed malformed reviewer response can be retried on the same effective profile without treating malformed output as capability evidence or adding another review round.

## Acceptance
1. A completed `malformed-response` with `success: false` and `conforming: false` returns a same-profile dispatch decision rather than `execution-failed` when the shared redispatch budget remains.
2. The retry does not change model or effort and consumes the existing completed-redispatch budget.
3. Incomplete execution, unknown failure kinds, and an exhausted redispatch budget still fail closed.
4. The reviewer schema remains the source of the three-note limit, the Review orchestrator remains responsible for validating reviewer content and enforcing its one same-digest retry, and the Claude runner remains a single-attempt transport boundary.

## Constraints
- Do not add a reviewer loop, retry ledger, checker rule, persistent state, output parser, or new outcome/schema field.
- Keep `claude_reviewer.py` single-attempt and content-agnostic.
- Preserve the distinction between malformed output and capability-quality or reasoning-depth failures.
- Do not modify the capture-intent feature branch.

## Value case
GO — the existing contracts already promise the retry and the resolver already carries the necessary profile and count; a narrow transition plus regression coverage closes the mismatch without another mechanism.

## Out of scope
- Relaxing the reviewer output contract or accepting more than three notes.
- Changing review-round or functional-digest limits.
- Adding provider-specific parsing or retry behavior.
- Push, pull request creation, or merge.

## Open questions
- none
