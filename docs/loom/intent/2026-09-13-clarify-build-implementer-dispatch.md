# Clarify Build implementer dispatch
originator: kouko
kind: engineering
needs-design: no — clarifies internal agent workflow prose and tests without changing a user-facing product surface
status: confirmed 2026-09-13

## Problem
The Build instructions say parallel work is optional without clearly separating scheduling from delegation. Main agents can therefore perform every implementation task themselves, bypassing the intended implementer role and its separation from coordination and review.

## Proposed outcome
Make implementer dispatch mandatory for every implementation task while keeping concurrent scheduling optional and preserving the main agent's coordinator role.

## Acceptance
1. Build and write-plan consistently state that every implementation task is dispatched to an implementer and only concurrent scheduling is optional.
2. Build requires the main agent to stop and report a blocker when implementer dispatch is unavailable instead of implementing the task itself.
3. Existing contract tests prevent optional parallel scheduling from being interpreted as optional implementer delegation.

## Constraints
- Change only the directly related Build, write-plan, and existing contract tests.
- Add no checker rule, attestation field, ledger, runtime gate, or other mechanism.
- Use test-first implementation and a closing reviewer distinct from the implementer.
- Do not push, create a pull request, or merge without separate authorization.

## Out of scope
- Changing model selection, dispatch-profile routing, reviewer-count policy, or publication behavior.
- Refactoring unrelated Loom workflow prose or tests.

## Open questions
- none
