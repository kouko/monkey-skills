# Stable Claude Code second reviewer — spec
intent: 2026-09-10-stabilize-claude-second-reviewer@4548d118dbe922ca555c106edcb4bb486f1fe0c6
confirmed-behavior: 2026-09-10 @57f75dc
pre-build-review: required — changes the public cross-vendor Closing Review contract and its failure states

## Requirements

REQ-1 — Real read-only review
  WHEN a Codex-hosted full-lane change selects Claude Code as its second vendor, the Closing Review shall invoke Claude Code non-interactively with the complete reviewer input, repository read access, no repository write authority, and a structured verdict accepted by the existing reviewer contract → Acceptance #1

REQ-2 — Representative readiness
  WHEN Claude Code is considered available for second-vendor review, Loom shall verify the execution conditions needed by the real review and distinguish authentication, model, permission, timeout, process, and malformed-output failures → Acceptance #2

REQ-3 — Bounded failure handling
  WHEN a Claude reviewer execution fails before a conforming verdict exists, the Closing Review shall use only its existing one retry for the same functional digest and shall report the concrete diagnosis after a second failure without changing reviewer identity or review-round accounting → Acceptance #3

REQ-4 — End-to-end evidence
  The implementation shall include a clean controlled dogfood path that reviews a minimal real repository change, validates the complete verdict fields, and proves the reviewer left the repository unchanged → Acceptance #4

## Design decision

- agent-decided — Define one cross-vendor invocation contract at the Review boundary, because the current presence probe and reviewer output contract leave their execution seam unspecified.
- agent-decided — Use Claude Code's non-interactive restricted read-only surface and structured-output support when confirmed by the installed CLI, because bypassing permissions would grant authority the reviewer does not need.
- agent-decided — Keep failure categories observable but avoid persistent execution state; the active Closing Review already owns the single retry and terminal result.
- agent-decided — Reuse the existing attestation verdict shape and bounded episode instead of creating a vendor-specific result schema or retry counter.

## Alternatives considered

- Keep prose only and let each agent assemble a Claude command — rejected because the incident occurred at this unspecified seam and cannot be regression-tested consistently.
- Treat `claude --version` as sufficient readiness — rejected because the observed health probe proves only that the executable starts, not that a repository review can complete.
- Run Claude with bypassed permissions — rejected because a reviewer needs read access only and excess authority would weaken independence and safety.
- Add a daemon, queue, or persistent dispatch ledger — rejected because execution belongs to one active Review and existing retry accounting already bounds failure.

## Current state evidence

- Forward: `loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md` — "Detect it with `command -v <cli>` and a probe that it runs" admits Claude after only a version probe.
- Reverse: `loom-code/skills/review/SKILL.md` — "A configured second vendor remains required" selects the cross-vendor path but does not define its executable call.
- Error: `loom-code/skills/review/SKILL.md` — "A second executor failure ends the episode as `EXECUTION_FAILED`" bounds retries without requiring a concrete diagnostic category.
- Data: `loom-code/agents/reviewer.md` — the `## Output` YAML block defines the verdict fields the external reviewer must return.
- Boundary: `loom-code/skills/review/SKILL.md` — "Keep this episode in the active task context" excludes persistent workers and restart recovery.

## UI flows

- User selects Claude Code as the second reader for a full-lane change → Closing Review starts one non-interactive read-only Claude review and returns a contract-valid verdict.
- Claude review is running → the active task waits for that invocation; no background task, repository mutation, or repeated status output is created.
- Claude returns a malformed response or a transient execution failure → Closing Review reports the diagnosed category internally and retries once against the same functional content.
- The retry returns a valid verdict → Closing Review continues using that verdict without consuming an extra review round.
- Authentication, model access, read permission, or another non-recoverable requirement is unavailable → the active task identifies the missing requirement and stops without a blind retry.
- A second transient execution fails, the command times out, or the result remains malformed → the active task reports `EXECUTION_FAILED` with the concrete category and recovery information, then stops.
- The controlled dogfood completes → the report shows valid reviewer fields and identical repository state before and after the Claude invocation.
