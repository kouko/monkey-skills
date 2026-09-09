# Simplify Loom publication
originator: kouko
kind: engineering
needs-design: yes — adds a user-invoked publication command and changes its visible output and failure behaviour
status: closed 2026-09-08 — PR #807

## Problem
Loom catches functional problems before publication, but publishing still costs unnecessary retries: CI rejects temporary commit titles that squash merge discards, and agents must manually construct a fragile canonical push and PR command.

## Proposed outcome
Validate the final PR title instead of every intermediate commit title, and provide one safe Loom publication command that validates the attestation before pushing the exact branch and opening its PR.

## Acceptance
1. A PR with a valid title is not blocked because an intermediate commit omits a scope.
2. A PR with an invalid final title is blocked with a useful error.
3. One publication command validates the matching attestation, pushes exactly the selected HEAD to its current origin branch, and opens at most one PR without manually composing canonical shell commands.
4. Publication does not replay the package suite or adversarial programs.
5. Unsafe repository, remote, branch, refspec, executable, or PR targeting is rejected before publication.

## Constraints
- Preserve the generated attestation as the only Loom publication contract.
- Preserve GitHub CI as the external functional trust boundary.
- Preserve explicit user authorization before publication and merge.
- Preserve the untracked `work/` in the main checkout.
- Do not restore compatibility with retired Loom contracts.

## Out of scope
- Combining or redesigning `finalize-review` in this change.
- Redesigning independent reviewer selection or vendor reliability.
- Researching Claude Code reviewer execution reliability or changing its integration.
- Adding path filters to unrelated repository CI jobs.
- Changing Loom family installation or release orchestration.
- Merging the resulting PR without separate authorization.

## Open questions
- none
