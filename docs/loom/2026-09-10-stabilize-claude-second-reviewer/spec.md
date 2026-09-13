# Claude Code empty-output and timeout handling — spec
intent: 2026-09-10-stabilize-claude-second-reviewer@d511eb1c7d53b7fc0dd11be7705f8335c5bb2622
confirmed-behavior: 2026-09-10 @8f567ee
pre-build-review: required — changes the public cross-vendor Closing Review contract and its failure states

## Requirements

REQ-1 — Valid review result
  WHEN Claude Code returns a conforming reviewer verdict, the Closing Review shall accept it through the existing reviewer contract without an additional model preflight → Acceptance #1

REQ-2 — Invalid output diagnosis
  WHEN Claude Code exits with empty, whitespace-only, missing-result, or unparsable output, the Closing Review shall classify the attempt as invalid output and retain its exit status and available standard error instead of accepting it as a verdict → Acceptance #2

REQ-3 — Timeout diagnosis
  WHEN Claude Code exceeds the formal review timeout, the Closing Review shall terminate the attempt, classify it as a timeout, and retain its elapsed time and available error output → Acceptance #3

REQ-4 — Existing retry boundary
  WHEN a Claude review returns invalid output or times out, the Closing Review shall use only its existing one retry against the same functional digest and shall report the concrete diagnosis after a second failure without changing reviewer identity or review-round accounting → Acceptance #4

## Design decision

- agent-decided — Add only the minimum executable boundary needed to distinguish a conforming result, invalid output, and timeout, because those are the observed failures.
- agent-decided — Invoke the formal review directly with no model-backed readiness call, because a representative preflight would duplicate cost without preventing later failure.
- agent-decided — Reuse the existing attestation verdict shape and one executor retry instead of creating vendor-specific state or retry accounting.

## Alternatives considered

- Keep prose only and let each agent interpret empty output and timeout — rejected because the observed failures cannot be regression-tested consistently.
- Run a model-backed health review before the real review — rejected because it doubles model work and can still succeed before the formal call fails.
- Add a daemon, queue, or persistent dispatch ledger — rejected because execution belongs to one active Review and existing retry accounting already bounds failure.

## Current state evidence

- Forward: `loom-code/skills/review/SKILL.md` — "A configured second vendor remains required" selects the cross-vendor path but does not define how empty output or timeout is represented.
- Reverse: `loom-code/agents/reviewer.md` — the `## Output` YAML block defines the only conforming result the invocation may accept.
- Error: `loom-code/skills/review/SKILL.md` — "A second executor failure ends the episode as `EXECUTION_FAILED`" bounds retries without requiring a concrete diagnostic category.
- Data: `loom-code/agents/reviewer.md` — the reviewer verdict fields remain the accepted data shape.
- Boundary: `loom-code/skills/review/SKILL.md` — "Keep this episode in the active task context" excludes persistent workers and restart recovery.

## UI flows

- User selects Claude Code as the second reader for a full-lane change → Closing Review starts the formal Claude review directly, with no separate model-backed preflight.
- Claude returns a valid verdict → Closing Review accepts it through the existing reviewer contract.
- Claude returns empty, whitespace-only, missing-result, or unparsable output → Closing Review records invalid output with exit status and available standard error, then retries once against the same functional content.
- Claude exceeds the formal timeout → Closing Review terminates the attempt, records timeout with elapsed time and available error output, then retries once against the same functional content.
- The retry returns a valid verdict → Closing Review continues using that verdict without consuming an extra review round.
- The retry again returns invalid output or times out → the active task reports `EXECUTION_FAILED` with both attempts' concrete diagnostics, then stops.
