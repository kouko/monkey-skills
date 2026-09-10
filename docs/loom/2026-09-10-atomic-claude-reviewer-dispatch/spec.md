# Atomic Claude reviewer dispatch — spec
intent: 2026-09-10-atomic-claude-reviewer-dispatch@f94da57d62c81dc1a382252128055434b8555c5e
pre-build-review: required — changes the installed runner CLI contract used across the Codex-to-Claude review boundary

## Requirements
REQ-1 — Apply a complete supported profile
  WHEN the caller supplies a resolved model and effort pair, the runner shall pass both values to the single Claude Code attempt → Acceptance #1

REQ-2 — Preserve atomic fallback
  IF either override is absent or the resolved profile is unsupported or unverified THEN the review path shall invoke the runner without either model or effort override → Acceptance #2

REQ-3 — Preserve shared execution policy
  WHILE the Claude second-vendor path is active, the Review station shall preserve the shared atomic fallback, retry budget, stdin prompt, no-session-persistence, and no-user-intervention rules → Acceptance #3

## Design decision
- agent-decided — Make `--model` and `--effort` an optional pair on the runner CLI because Claude Code 2.1.267 exposes both flags and the shared resolver already owns profile selection.
- agent-decided — Reject a partial CLI pair before spawning Claude instead of guessing the missing value, because a partial override cannot represent the resolver result.
- agent-decided — Represent resolver fallback by invoking the runner with neither flag; remove the static `sonnet` default because host-default behavior must remain observable rather than claimed as inheritance.
- agent-decided — Keep host rejection handling in the Review orchestrator: feed the failed pre-execution result to the resolver and invoke the returned override-free replacement in the same task attempt. The runner remains a one-attempt subprocess boundary and does not infer whether arbitrary Claude failures are routing failures.
- agent-decided — Preserve prompt delivery, output handling, timeout classification, credential boundaries, and session non-persistence unchanged because none causes the atomic-profile defect.

## Alternatives considered
- Let `--model` and `--effort` remain independently optional — rejected because it permits the exact partial override that violated the shared contract.
- Keep `sonnet` as the runner default and add only `--effort` — rejected because fallback would still force a model instead of omitting both overrides.
- Make the runner automatically retry without overrides on every non-zero Claude exit — rejected because quota, authentication, timeout, and reviewer failures are not evidence of host profile rejection and must not silently change execution semantics.
- Pass a new JSON profile object instead of two paired flags — rejected because the existing CLI already has one model flag and Claude Code exposes a matching effort flag; another serialization layer adds no contract value.

## Current state evidence
- Forward: `loom-code/skills/review/SKILL.md:55` starts the Codex-to-Claude reviewer path, but its command at line 59 supplies only `--model`.
- Reverse: `loom-code/skills/review/SKILL.md:46` requires the configured second-vendor reviewer and line 55 selects this runner when that vendor is Claude Code.
- Error: `loom-code/scripts/claude_reviewer.py:37` constructs an argv that always includes `--model`, while line 113 assigns the static `sonnet` default and exposes no effort input.
- Data: `loom-code/references/dispatch-profile.md:78` defines `overrides` as either one complete `{model, effort}` pair or `null`; lines 163-177 define override-free fallback and host-rejection recovery.
- Boundary: `loom-code/scripts/test_claude_reviewer.py:10` owns the runner subprocess contract; the checked-in Claude CLI evidence at `docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/claude-p-help-2026-09-05.txt:79` and line 130 grounds the two native flags.

## UI flows
- `claude_reviewer.py --model opus --effort medium --timeout-seconds 600` with a reviewer prompt on stdin → runs one non-persistent Claude attempt with both overrides and returns the raw reviewer output with exit 0 on success.
- `claude_reviewer.py --timeout-seconds 600` with a reviewer prompt on stdin → runs one non-persistent Claude attempt with neither override, allowing Claude Code to select its host defaults.
- Supplying only `--model` or only `--effort` → prints a paired-override validation error to stderr and exits 2 before starting Claude; the caller retries with both values or neither.
- A supported pair rejected by Claude before task execution → the Review caller feeds the rejection to the resolver and invokes the override-free replacement once in the same task attempt.
- Timeout, empty output, authentication, quota, or other process failure → retains the existing structured diagnostic and exit behavior; no internal model or effort fallback is attempted.
- In progress: the print-mode command emits no progress UI and waits up to the supplied timeout; this behavior is unchanged.
