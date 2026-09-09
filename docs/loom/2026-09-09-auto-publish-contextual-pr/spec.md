# Automatic contextual pull-request publication — spec
intent: 2026-09-09-auto-publish-contextual-pr@cc1631346d0d44e29ee964c47064fca0e07bcd02
confirmed-behavior: 2026-09-09 @4e82d08
pre-build-review: required — changes Loom's public Ship contract, outward publication authorization, privacy boundary, and cross-plugin PR composition

## Requirements

REQ-1 — Intent-derived publication authorization
  WHEN an intent explicitly confirmed automatic publication under the current contract reaches Ship with a matching Review attestation and passing publication safety checks, Loom shall push the selected branch, create or update one ready pull request with the contextual title and body, and begin CI observation without asking for publication confirmation again; an older intent without that explicit authorization shall require one publication decision before proceeding → Acceptance #1

REQ-2 — Self-contained pull-request context
  WHEN Loom composes the pull-request body, the body shall explain the original problem and timing, intended outcome, included and excluded scope, decisions and rejected alternatives, implementation, behaviour change, verification evidence, risks and rollback, and follow-ups using the intent, plan, Git change, attestation, and available CI evidence → Acceptance #2

REQ-3 — Information-bearing diagrams
  WHERE a change contains meaningful decision branches, component interactions, state transitions, or before-and-after behaviour flows, Loom shall include an appropriate Mermaid decision, architecture, sequence, state, or comparison diagram, while omitting diagrams that add no information to a simple change → Acceptance #3

REQ-4 — Auditable rationale boundary
  WHEN Loom explains a decision in the pull request, the explanation shall state the chosen option, material alternatives, evidence, trade-offs, and outcome without presenting hidden model reasoning or unsupported claims as chain-of-thought → Acceptance #4

REQ-5 — Publication failure boundary
  IF Review, attestation, secret or privacy checks, destination identity, remote state, pull-request creation or update, draft-to-ready conversion, or required CI fails or requires user action THEN Loom shall stop the affected publication or observation step and report the concrete blocker without bypassing it → Acceptance #5

REQ-6 — Separate merge authorization
  WHEN the pull request becomes ready to merge, Loom shall wait for separate explicit user authorization before changing the base branch → Acceptance #6

REQ-7 — Current-contract evidence only
  WHEN Loom produces and validates the contextual pull request, it shall use the current intent, plan, attestation, Git change, and CI state without requiring review.json, probe ledgers, legacy Task-trailer accounting, or retired SHA-alignment contracts, and shall ship regression evals for authorization eligibility, opt-out, PR creation and reuse, contextual-body update, draft-to-ready conversion, and CI terminal boundaries while recomputing the mechanism population and requiring a budget exception for any net increase → Acceptance #7

REQ-8 — Thirty-second task-local CI observation
  WHILE the Ship task remains active after opening or reusing the pull request, Loom shall check required CI every 30 seconds until all required checks pass, any required check fails or is cancelled, or user action is required, and shall not emit a user-facing update for every unchanged pending result → Acceptance #8

## Design decision

- agent-decided — Treat confirmation of the intent as authorization for the later non-forced branch push and ready pull-request creation. This removes a duplicated permission stop while preserving the user's ability to opt out before publication and preserving a separate merge decision.
- agent-decided — Require positive authorization evidence in the confirmed intent under the current contract. Contract upgrade alone never retroactively authorizes publication for an older intent.
- agent-decided — Keep publication orchestration in Ship and extend its single `publish` path rather than permitting agents to assemble independent `git push` and `gh pr create` sequences. The existing wrapper already binds repository, branch, remote, attestation, and PR identity at the outward boundary.
- agent-decided — Define one contextual PR schema owned by Loom Ship, with git-memory contributing durable Decision, Learning, and Gotcha material instead of owning the top-level body shape. This prevents two competing templates.
- agent-decided — Build PR context from current contract artifacts and recomputed Git state. Retired ledgers are deliberately not valid inputs.
- agent-decided — Make diagram slots semantic and conditional rather than imposing a count. A graph is required only when the relationship itself carries useful information.
- agent-decided — Interpret the requested CoT as an auditable decision record: inputs, alternatives, trade-offs, choice, and result. Private hidden reasoning is neither required nor represented.
- user-decided — CI polling is fixed at 30 seconds and exists only inside the active Ship task. It creates no scheduler and does not resume after the task or Desktop app stops.
- agent-decided — Observe required checks only for the terminal publication verdict; optional checks may be reported but cannot keep the Ship task alive indefinitely.
- agent-decided — Open a ready pull request, not a draft, because Review and the local publication gate have already completed. GitHub branch protection and CI remain the external merge boundary.
- agent-decided — When one matching PR already exists, update its title and body to the final contextual content and convert it from draft to ready only after Review and publication checks pass. Failure of any update is a publication blocker rather than a partially successful reuse.

## Alternatives considered

- Keep the Ship acceptance stop and only enrich the PR body — rejected because it preserves the duplicated authorization cost that motivated the change.
- Open a draft pull request before Review — rejected because it publishes unreviewed content and splits the existing content-bound Review and publication sequence.
- Infer authorization from phrases such as “ship it” at the end — rejected because a confirmed intent is an earlier, explicit and durable boundary, while the user can still opt out before publication.
- Treat every historically confirmed intent as authorized after upgrading Loom — rejected because those users confirmed requirements without being told that confirmation would later publish externally.
- Install a persistent 30-second scheduler — rejected because the requested observation belongs to one Ship execution and should not survive a stopped task or Desktop restart.
- Restore Loom 1.0's PR template verbatim — rejected because its Review section depends on retired review.json and probe-ledger accounting.
- Require a fixed set or minimum count of Mermaid diagrams — rejected because simple changes would acquire decorative, repetitive content.
- Use a repository-wide static GitHub PR template — rejected because it would affect non-Loom contributions and cannot synthesize change-specific evidence.

## Current state evidence

- Forward: `loom-code/skills/ship/SKILL.md:14` requires decision point ③ before publication, and `loom-code/skills/ship/SKILL.md:30` directs the agent into the single publish command afterward.
- Reverse: `loom-code/scripts/loom_checker.py:2684` parses the publish authorization, title, and body file; `loom-code/scripts/loom_checker.py:2782` performs the trusted publication sequence.
- Error: `loom-code/scripts/loom_checker.py:2710` rejects publication without `--confirm-authorized`; `loom-code/skills/ship/SKILL.md:50` describes CI inspection but sets no polling interval or terminal observation loop.
- Data: `loom-workflow/skills/git-memory/protocols/compose-pr.md:12` starts from Summary and Test plan, while its optional Memory section at line 49 carries decisions, learnings, gotchas, and conditional architecture diagrams rather than a complete Loom change narrative.
- Boundary: `loom-code/skills/ship/SKILL.md:57` keeps merge authorization separate; this change ends after task-local CI observation and does not alter branch-protection policy, merge execution, or non-Loom pull requests.

## UI flows

### Ship publication

- The user explicitly confirms automatic publication in the intent and later leaves the completed change to Loom → after Review and all publication safety checks pass, Loom pushes the selected branch and creates or updates one ready pull request without asking again.
- Loom reaches Ship with an older intent that never explicitly authorized automatic publication → Loom asks once before anything leaves the machine; that answer governs the remaining publication flow.
- The user says to stop before publication or not to open a pull request → Loom preserves the local reviewed branch and performs no outward publication.
- A publication safety check fails → Loom does not push or open the pull request and reports the named blocker and recovery boundary.
- The branch was already pushed and has one matching open pull request → Loom updates that pull request's title and complete contextual body instead of opening a duplicate; if it is a draft, Loom marks it ready only after Review and publication checks have passed.
- Updating the existing pull request or marking it ready fails → Loom reports the failure and does not describe the pull request as ready.

### Pull-request body

- The user or reviewer opens the pull request without the originating conversation → they can reconstruct the problem, intended result, scope, decisions, implementation, behaviour change, verification, risks, rollback, and follow-ups from the body.
- The change has meaningful decision branches, component interactions, states, or before-and-after flows → the body includes the corresponding Mermaid diagram with surrounding prose explaining what it shows.
- The change is simple and no relationship is clearer as a graph → the body remains complete in prose and contains no decorative diagram.
- Source evidence is missing for a claimed fact → Loom marks the limitation or omits the claim instead of filling the section with speculation.

### CI observation

- The ready pull request opens during an active Ship task → Loom checks required CI immediately and then every 30 seconds while required checks remain pending.
- Required CI remains unchanged and pending → Loom continues waiting without posting a new user-facing update every 30 seconds.
- All required checks pass → Loom reports the green terminal result and waits for separate merge authorization.
- Any required check fails or is cancelled → Loom stops polling, reports the failing check, and routes a functional failure back through Build and Review while allowing publication-only repair to reuse matching evidence.
- CI requires user action or cannot be observed reliably → Loom stops polling and states what action or missing access is required.
- The Codex task or Desktop app stops while CI is pending → observation ends and no persistent schedule is left behind or automatically resumed.

### Merge

- CI is green but the user has not authorized merge → Loom leaves the pull request open and does not change the base branch.
- The user explicitly authorizes merge after CI is green → Loom follows the existing guarded merge path.
