# Use one reviewer only for mechanically proven low-risk changes
originator: kouko
kind: engineering
needs-design: no — this changes an internal review policy and has no user-facing product behaviour
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
Closing Review currently pays for two fresh-context reviewers on every change, even when a change is narrowly scoped and low risk. The fixed reviewer cost slows delivery and spends model quota without evidence that the second reviewer adds proportional value in those cases.

## Proposed outcome
Let Closing Review use one reviewer only when the repository can mechanically prove that the whole change is in a narrow low-risk class. Keep two reviewers as the default for every other case, including unknown or mixed changes, and keep the existing package, adversarial, attestation, and publication safeguards intact.

## Acceptance
1. A clean checkout can compute the required reviewer count from the actual change and gets one only for explicitly allowed low-risk cases.
2. Production/runtime code, skill or agent contracts, checker or hook logic, security/privacy-sensitive content, external interfaces, mixed scope, and unknown paths still require two reviewers.
3. Closing Review runs the computed number of fresh-context reviewers, and finalization rejects an attestation assembled with fewer reviewers than the same policy requires.
4. Existing package verification, adversarial execution, content-bound attestation, and Ship validation continue to work without a new user decision point or persistent review-lane state.
5. Automated tests prove both the narrow one-reviewer exception and fail-closed fallback, and operative guidance no longer contradicts the executable policy.

## Constraints
- The exception must be mechanically derived from repository evidence rather than declared by the agent or user.
- Unknown, malformed, or ambiguous inputs must require two reviewers.
- Keep the reviewer policy in one executable source of truth and avoid duplicating its allowlist across prose files.
- Do not add a new artifact schema, ledger, user-selectable lane, or checker mechanism unless implementation evidence shows it is unavoidable.

## Out of scope
- Removing fresh-context review from Closing Review.
- Changing reviewer models or cross-model dispatch.
- Redesigning package-suite reuse, adversarial verification, attestation contents, or Ship behaviour beyond consuming the reviewer requirement.
- Optimizing review quality or cost for medium- and high-risk changes.

## Open questions
- none
