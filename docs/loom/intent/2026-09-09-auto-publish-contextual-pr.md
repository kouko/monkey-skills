# Automatically publish a contextual pull request
originator: kouko
kind: product
needs-design: yes — Ship behaviour and the pull-request content visible on GitHub both change, and no current UI-flow document defines the contextual PR structure
evidence: [loom-code/skills/ship/SKILL.md, loom-workflow/skills/git-memory/protocols/compose-pr.md]
status: confirmed 2026-09-09
publication: automatic — authorized 2026-09-09 by kouko

## Problem
Loom can finish implementation and verification, but still asks the user again before pushing and opening a pull request. By that point the user may also have forgotten the original problem, decisions, trade-offs, and validation history, while the pull request does not consistently reconstruct that context for a new reader.

## Proposed outcome
Confirmation of the intent authorizes Loom to publish the completed branch automatically after Review passes: push the branch, open a ready pull request, and check required CI every 30 seconds until it reaches a terminal result. The pull request becomes a self-contained account of the change, using diagrams when decision paths, architecture, or before-and-after behaviour are materially clearer visually.

## Acceptance
1. When I confirm an intent and its implementation later passes Review and publication safety checks, Loom pushes the branch, opens or reuses a ready pull request, and starts checking required CI every 30 seconds without asking me for publication confirmation again.
2. I can open the pull request without remembering the earlier conversation and understand the original problem, intended outcome, scope, decisions and rejected alternatives, implementation, behaviour change, verification evidence, risks, rollback, and follow-ups.
3. When a change has meaningful branching decisions, component interactions, or behaviour-flow changes, the pull request uses an appropriate Mermaid decision, architecture, sequence, or before-and-after diagram; simple changes are not padded with diagrams that add no information.
4. The published explanation exposes checkable decision rationale and evidence, without claiming or fabricating private chain-of-thought.
5. Failed Review, failed publication checks, privacy or secret findings, an unsafe destination, a diverged remote, or a failed push still stops publication and reports the concrete blocker.
6. Merging into the base branch still requires separate explicit user authorization.
7. The mechanism works from Loom's standard intent, plan, attestation, Git diff and CI evidence without restoring review.json, probe ledgers, or legacy SHA-accounting contracts.
8. CI observation ends when all required checks pass, any required check fails or is cancelled, or user action is required; unchanged pending state does not produce a new user-facing update every 30 seconds.

## Constraints
- The policy and PR structure must be reusable by repositories adopting Loom, not tailored to monkey-skills.
- Existing attestation validation, deterministic publication safety, non-forced push, repository and branch identity checks, secrets scanning, and risk-based privacy handling remain enforced automatically.
- A request to stop before publication or to avoid opening a PR overrides the default authorization before the outward action occurs.
- Pull-request prose follows the user's conversation language where the host can establish it; repository-defined artifact conventions still govern committed files.
- CI observation lives only for the active Ship task; it does not create a persistent scheduler and does not resume automatically after the Desktop app or task stops.

## Value case
GO — repeated end-of-flow confirmation adds user effort without adding a distinct safety decision, while incomplete PR context makes review and later maintenance depend on remembering the originating conversation. Loom already owns the verified publication boundary, so consolidating authorization and generating the context there removes recurring cost without automating merge.

## Out of scope
- Automatically merging a pull request.
- Bypassing failed review, CI, attestation, privacy, secret, destination, or remote-state checks.
- Restoring review.json, replay ledgers, legacy Task-trailer accounting, or other retired contract machinery.
- Requiring a fixed number of Mermaid diagrams or publishing hidden model reasoning.
- Introducing a repository-wide static GitHub pull-request template for non-Loom changes.

## Open questions
- none
