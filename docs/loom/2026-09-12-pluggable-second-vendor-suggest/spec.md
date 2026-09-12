# Pluggable second-vendor suggestion — spec
intent: 2026-09-12-pluggable-second-vendor-suggest@54bff8efe0fbe0a08b35d0610040f8e3cc5ae8ba
confirmed-behavior: 2026-09-12 @7444651
pre-build-review: required — changes the public workflow contract and coordinates behavior across independently installable plugins

## Requirements
REQ-1 — Non-blocking default
  WHERE second-vendor suggestion mode is configured, the Loom workflow shall continue with no second vendor unless the user explicitly opts in before Closing Review → Acceptance #1

REQ-2 — Evidence-based suggestion
  WHEN a full-lane change has an available different-vendor CLI, the Loom workflow shall emit one non-blocking notice and shall strengthen it to an evidence-grounded recommendation when a declared high-risk signal is present → Acceptance #2

REQ-3 — Small-lane information boundary
  WHEN a small-lane change has an available different-vendor CLI, the Loom workflow shall report availability without permitting another reviewer for that change; IF no different-vendor CLI is available THEN it shall emit no notice, and every path shall return a checkable reason → Acceptance #3

REQ-4 — Response timing
  WHEN the user responds to a suggestion before Closing Review, the Loom workflow shall use an explicit opt-in for that change and otherwise retain no second vendor; an opt-in after Closing Review starts shall not change the active reviewer identities → Acceptance #4

REQ-5 — Backward-compatible modes
  The Loom workflow shall preserve the existing behavior of none, ask, and fixed-CLI second-vendor settings while adding suggestion mode as a separate value → Acceptance #5

REQ-6 — Replaceable policy boundary
  The Loom workflow shall resolve suggestion decisions through one deterministic no-I/O policy contract whose risk rules are not duplicated by skills, hooks, checkers, or provider adapters → Acceptance #6

REQ-7 — Repository adoption
  WHERE this repository's kickoff defaults are read, the Loom workflow shall select suggestion mode instead of ask mode → Acceptance #7

## Design decision
- agent-decided — Add `suggest` as a new mode rather than redefining `none`, because existing repositories must retain their explicit no-suggestion choice.
- agent-decided — Place availability, lane, and risk resolution in one host-neutral pure module that accepts observed facts and returns an action plus reason; skills own timing and presentation, provider adapters own execution, and the checker owns only grammar and recomputable invariants.
- agent-decided — Evaluate suggestion eligibility after the plan has established the lane and risks, because intent confirmation happens before that evidence exists and must not guess future risk.
- agent-decided — Keep the decision only in active task context and the plan's existing risk/question record; adding a suggestion ledger would create persistent state solely for an optional notice.
- user-decided — Configure this repository for `suggest`, with `none` as the effective default unless the user opts in before Closing Review.
- user-decided — Use Claude Code as the second-vendor reviewer for this change's Closing Review.

## Alternatives considered
- Redefine `none` to permit risk suggestions — rejected because it would silently change an existing explicit opt-out.
- Keep the complete decision tree in skill prose — rejected because the same risk logic would drift across hosts and independently installed plugins.
- Ask during intent confirmation after a preliminary risk guess — rejected because it remains blocking and the plan-level evidence does not exist yet.
- Automatically enable the second vendor on high risk — rejected because it would authorize quota use and repository data egress without an explicit opt-in.
- Build a generic policy-plugin framework — rejected because one bounded second-vendor policy does not justify a new extension system.

## Current state evidence
- Forward: `loom-code/skills/write-plan/SKILL.md` at `The second-reviewer suggestion, at most once per change` routes `ask` during intent confirmation.
- Reverse: `loom-code/hooks/session-start` at `fold the once-per-change second-vendor suggestion` instructs the host to include that blocking choice at decision point 1.
- Error: `loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md` at `ask one plain sentence` makes the user answer on every full-lane change and provides no non-blocking risk path.
- Data: `loom-code/contract/manifest.yaml` at `kickoff_defaults` currently admits only a fixed CLI, `none`, or `ask`.
- Boundary: `loom-code/skills/review/SKILL.md` at `A configured second vendor remains required` consumes the selected vendor; reviewer dispatch, verdict semantics, attestation, and publication remain outside the selection policy.

## UI flows
### Loom task conversation
- A change enters intent confirmation with suggestion mode configured → Loom asks only for intent and applicable one-way-door decisions; it does not ask whether to use a second vendor.
- A full-lane plan has a usable different-vendor tool and a qualifying risk → Loom shows one message naming the risk, recommends the available second vendor, says it will continue without that vendor unless the user opts in before Closing Review, and continues without waiting.
- A full-lane plan has a usable different-vendor tool and no qualifying risk → Loom shows one informational message that the tool is available, says it will continue without that vendor unless the user opts in before Closing Review, and continues without waiting.
- A small-lane plan has a usable different-vendor tool → Loom shows one informational message that the tool is available for full-lane changes but does not offer to add another reviewer to this change.
- No usable different-vendor tool is present → Loom shows no second-vendor message and continues with the lane's normal readers.
- The user explicitly accepts the suggestion before Closing Review → Loom confirms that the named second vendor will review this change and uses it at Closing Review.
- The user declines or does not answer before Closing Review → Loom starts Closing Review without a second vendor and does not ask again.
- The user accepts after Closing Review has started → Loom keeps the active reviewers unchanged and says the preference can apply to the next change.
- The second-vendor tool becomes unavailable after an accepted suggestion → Loom reports the concrete execution or authorization failure under the existing Review rules; it does not silently replace the vendor or reinterpret the earlier choice.
