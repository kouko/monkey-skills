# Pluggable second-vendor suggestion — spec
intent: 2026-09-12-pluggable-second-vendor-suggest@a725da6bb6da7fe842b0f901aa5a9b93d4241712
confirmed-behavior: 2026-09-12 @c74fd56
pre-build-review: required — changes the public workflow contract and coordinates behavior across independently installable plugins

## Requirements
REQ-1 — Non-blocking default
  WHERE second-vendor suggestion mode is configured, the Loom workflow shall continue without a second vendor unless the user explicitly opts in before Closing Review → Acceptance #1

REQ-2 — Evidence-based suggestion
  WHEN a full-lane change has an available different-vendor CLI, the Loom workflow shall emit one non-blocking notice and shall strengthen it to an evidence-grounded recommendation when a declared high-risk signal is present → Acceptance #2

REQ-3 — Small-lane information boundary
  WHEN a small-lane change has an available different-vendor CLI, the Loom workflow shall report availability without permitting another reviewer for that change; IF no different-vendor CLI is available THEN it shall emit no notice, and every path shall return a checkable reason → Acceptance #3

REQ-4 — Response timing
  WHEN the user responds to a suggestion before Closing Review, the Loom workflow shall use an explicit opt-in for that change and otherwise retain no second vendor; an opt-in after Closing Review starts shall not change the active reviewer identities → Acceptance #4

REQ-5 — Remove silent-off mode
  The Loom workflow shall preserve ask and fixed-CLI behavior while rejecting the removed none setting with migration guidance to use suggestion mode → Acceptance #5

REQ-6 — Replaceable policy boundary
  The Loom workflow shall resolve suggestion decisions through one deterministic no-I/O policy contract whose risk rules are not duplicated by skills, hooks, checkers, or provider adapters → Acceptance #6

REQ-7 — Repository adoption
  WHERE this repository's kickoff defaults are read, the Loom workflow shall select suggestion mode instead of ask mode → Acceptance #7

## Design decision
- user-decided — Remove `none` immediately rather than retaining a legacy silent-off alias; `suggest` owns the default outcome of continuing without a second vendor when there is no opt-in.
- agent-decided — Place availability, lane, and risk resolution in one host-neutral pure module that accepts observed facts and returns an action plus reason; skills own timing and presentation, provider adapters own execution, and the checker owns only grammar and recomputable invariants.
- agent-decided — Evaluate suggestion eligibility after the plan has established the lane and risks, because intent confirmation happens before that evidence exists and must not guess future risk.
- agent-decided — Keep the decision only in active task context and the plan's existing risk/question record; adding a suggestion ledger would create persistent state solely for an optional notice.
- user-decided — Configure this repository for `suggest`, with no second vendor selected unless the user opts in before Closing Review.
- user-decided — Use Claude Code as the second-vendor reviewer for this change's Closing Review.

### Policy contract
The version 1 policy receives exactly these fields:

- `contract_version`: integer `1`.
- `configured_mode`: `ask`, `suggest`, or `fixed`; `fixed_vendor` is required only for `fixed`.
- `host_vendor`: `claude`, `codex`, or `gemini`.
- `lane`: `small` or `full`.
- `usable_vendors`: a unique set drawn from `claude`, `codex`, and `gemini`, excluding `host_vendor`. A vendor enters this set only when `command -v <cli>` produces non-empty output and `<cli> --version` exits 0; discovery never installs, authenticates, or invokes a model-backed task. The policy orders candidates as Claude, Codex, then Gemini after excluding the host, so caller order cannot change the result.
- `risk_evidence`: a unique array of objects shaped `{signal, anchors}`. `signal` is drawn from `security-or-privacy-boundary`, `public-contract-or-persistent-format`, `cross-system-or-provider-integration`, `review-verification-or-publication-mechanism`, `critical-behavior-not-fully-automated`, and `irreversible-data-or-architecture`; `anchors` is a non-empty unique array of `path :: verbatim anchor` strings from the confirmed intent, spec, plan Risk fields, or cumulative diff. The write-plan station supplies observed evidence, while this contract alone maps each canonical signal to notice behavior.
- `review_started`: boolean.
- `response`: `pending`, `decline`, or `accept`; `response_vendor` is required only for `accept` and must identify a usable vendor.

The version 1 policy returns exactly these fields:

- `effective_vendor`: a vendor id or null.
- `notice_vendor`: the vendor id the skill names, or null when no notice is emitted.
- `notice_kind`: `no-notice`, `availability`, `recommendation`, `selection-confirmed`, or `next-change-only`.
- `recommendation_reasons`: the validated `{signal, anchors}` objects in the canonical signal order listed above; the skill presents these returned anchors and does not classify or reconstruct risk.
- `opt_in_eligible`: boolean.
- `wait_for_user`: always false for `suggest`.
- `reason_code`: one stable machine-readable value describing the selected path.

For `suggest`, no usable vendor returns `no-notice` with both vendor fields null; otherwise the first canonical candidate becomes `notice_vendor`. A full-lane change with zero evidence objects returns `availability`; one or more validated objects returns `recommendation` with every grounded object in canonical order. A small-lane change returns `availability` with the canonical `notice_vendor`, empty recommendation reasons, and `opt_in_eligible: false` regardless of supplied risk evidence. A full-lane acceptance before Review returns `selection-confirmed` with both vendor fields set to the accepted vendor; decline or no response leaves both vendor fields null. Acceptance after Review starts returns `next-change-only` with `notice_vendor` set to the requested vendor and `effective_vendor` null. The module rejects unknown fields, unknown enum values, duplicate set members or signals, empty or malformed anchors, wrong types, a host vendor in `usable_vendors`, missing mode-dependent fields, unavailable accepted vendors, and other contradictory inputs as `input-error` without emitting a policy decision.

The stable `reason_code` population is `mode-not-suggest`, `no-usable-vendor`, `small-lane-availability-only`, `small-lane-no-opt-in`, `small-lane-declined`, `full-lane-availability`, `full-lane-risk-recommendation`, `selection-accepted`, `selection-declined`, `no-response`, and `response-too-late`. For a full-lane change before Review, `response: pending` produces the initial availability or recommendation notice; after Review starts, the same response produces no notice and `no-response`. A decline produces no notice and `selection-declined`; an acceptance uses `selection-accepted` before Review and `response-too-late` afterward. Skills display the returned notice fields; they do not infer a reason from input fields.

Small-lane response handling is fixed independently of risk evidence:

| Response | Before Review | After Review starts |
|---|---|---|
| `pending` | `availability`, canonical `notice_vendor`, null `effective_vendor`, `opt_in_eligible: false`, `small-lane-availability-only` | `no-notice`, null vendor fields, `opt_in_eligible: false`, `no-response` |
| `decline` | `no-notice`, null vendor fields, `opt_in_eligible: false`, `small-lane-declined` | same |
| `accept` | `next-change-only`, requested `notice_vendor`, null `effective_vendor`, `opt_in_eligible: false`, `small-lane-no-opt-in` | same |

Thus a small-lane response can never select or dispatch another reviewer for the active change. `next-change-only` is informational and creates no persisted preference; a later full-lane change evaluates its own repository setting and active-task response.

For `ask` and `fixed`, the policy returns `reason_code: mode-not-suggest` and does not replace their existing orchestration. The removed `none` value is rejected by the kickoff-default grammar with guidance to migrate to `suggest`; the policy never accepts or aliases it.

## Alternatives considered
- Retain `none` as a legacy silent-off alias — rejected by the user in favor of removing the state now; old configurations fail with explicit migration guidance instead of changing silently.
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
