# Continue after CI failure — spec
intent: 2026-09-10-continue-after-ci-failure@cdced7bac353712d43598f3e3987ae748436d92b
confirmed-behavior: 2026-09-10 @38ad321
pre-build-review: required — changes the public behavioral contract that coordinates CI failure handling across Loom stations

## Requirements

REQ-1 — Continue in the active task
  WHEN required CI fails while its publication task remains active, Loom shall inspect the available failure information and continue the same change instead of treating the publication command's failure as the end of the task → Acceptance #1

REQ-2 — Repair functional failures under existing verification
  WHEN the failure is functional or test-related, Loom shall keep the repair in the original change, reuse an existing test that exposes the root cause or add the smallest permanent regression case when coverage is missing, apply Build's test-first discipline, and rerun Closing Review before Ship whenever the functional digest changes → Acceptance #2

REQ-3 — Reuse evidence for publication-only repair
  WHEN a repair changes only publication content and the attestation still matches the functional digest, Loom shall fix and republish without repeating functional verification → Acceptance #3

REQ-4 — Stop only at a real decision or external blocker
  WHEN safe continuation would require changing requirements or guarantees, unavailable permission or diagnostic information, or recovery from a persistent external failure, Loom shall stop and report the concrete blocker → Acceptance #4

## Design decision

- agent-decided — Express continuation as coordination between the existing Ship, Build, Review, and Maintain responsibilities; do not add a recovery runtime, classifier, state, retry counter, command, hook, checker rule, or attestation field because the active task already owns orchestration.
- agent-decided — Treat an active unmerged change's CI failure as part of that change rather than Maintain intake, because creating another intent would duplicate its confirmed context.
- agent-decided — Specify observable outcomes rather than exact GitHub CLI commands, because command selection is replaceable implementation detail.
- agent-decided — Keep complete verification conditional on functional digest change, preserving existing evidence identity rather than equating every publication retry with new functional content.

## Alternatives considered

- Add a recovery script or persistent state machine — rejected because it creates a second lifecycle for behavior already owned by the active task.
- Re-enter the complete Build station after every failure — rejected because a repair needs Build's test-first discipline, not repeated intake or planning.
- Route every CI failure through Maintain — rejected because an active change already has an intent and verification episode.
- Encode exact GitHub CLI commands in the contract — rejected because that couples durable behavior to a replaceable tool interface.

## Current state evidence

- Forward: `loom-code/skills/ship/SKILL.md:116` — Ship begins required-CI observation after publication.
- Reverse: `loom-code/skills/ship/SKILL.md:92` — the single publication command enters the observation flow.
- Error: `loom-code/scripts/loom_checker.py:3193` — required action, cancellation, and failure return a publication block.
- Data: `loom-code/skills/review/SKILL.md:43` — functional-content digests identify review episodes and distinguish publication-only edits.
- Boundary: `loom-code/skills/maintain/SKILL.md:10` — Maintain currently owns incident intake, while this change excludes failures belonging to an active unmerged change.

## UI flows

- Required checks pass → the ready pull request is reported as today.
- A required check fails while the task remains active → the task reports the failure, inspects the available details, and continues repairing the same change without waiting for another instruction.
- The repair changes functional behavior → the task uses a test that reproduces the problem, applies the smallest fix, runs focused tests and the full closing verification, then checks required CI again.
- The repair changes only publication information → the task corrects it, preserves matching functional evidence, and checks required CI again without repeating functional verification.
- The failure cannot be diagnosed safely, needs unavailable permission, persists outside the task, or would change the agreed behavior → the task stops and reports the exact blocker and required next action.
- The task or Desktop app stops → no background recovery continues; later work resumes explicitly rather than relying on hidden persistent state.
