# Main-relative subagent model dispatch — spec
intent: 2026-09-09-main-relative-model-dispatch@be39c611d5fb8bfc85ed35b888e420e515ff1e11
pre-build-review: required — the policy coordinates model and effort controls across Codex and Claude Code and changes the quality ceiling of every Loom subagent dispatch

## Requirements
REQ-1 — Evidence-based relative routing
  WHEN Loom dispatches a subagent with an observable main-agent profile, the dispatcher shall apply the normative evidence predicates and precedence in this spec to classify the task as mechanical, ordinary, or complex and derive the initial profile relative to the main agent without using the role name as routing evidence → Acceptance #1

REQ-2 — Portable model and effort vocabulary
  WHERE a host supports model or effort overrides, the dispatcher shall represent model capability as `economy < standard < frontier`, represent common effort as `low < medium < high < xhigh < max`, preserve inherited host-native values outside that effort range, and resolve each portable value through the selected model's verified host capabilities → Acceptance #2

REQ-3 — Automatic atomic fallback
  IF either main-profile component is unobservable or either override or the requested model-effort combination is unsupported, unknown, or rejected THEN the dispatcher shall omit both overrides, retry the rejected pre-execution attempt once, and report `inherited` only when parent inheritance is guaranteed, without asking the user to choose routing parameters → Acceptance #3

REQ-4 — Evidence-gated expensive effort
  WHEN routing would newly enter effort above `medium`, the dispatcher shall require the corresponding completed lower-profile attempt and retained failure trigger, allow `high` and `xhigh` only one step at a time on `frontier`, never newly generate `max` or a host-native extension, and preserve an already inherited higher effort without treating it as an escalation → Acceptance #4

REQ-5 — Replayable verification boundary
  The change shall provide deterministic tests for classification, all portable tier transitions, initial and escalation reachability, model-specific capability resolution, inherited host-native effort, atomic fallback, and the two-redispatch limit, while reserving live model calls for the reduced host-mapping calibration corpus → Acceptance #5

## Design decision
- Agent-decided — keep model and effort as two ordered dimensions rather than enumerating product-specific profile pairs, because the main-relative arithmetic and host mapping then remain independent.
- Agent-decided — initial `mechanical` routing lowers model by one and preserves effort; `ordinary` preserves both; `complex` raises model by one and preserves effort, falling through to a one-step effort increase only at the `frontier` ceiling.
- Agent-decided — cap newly generated initial effort at `medium`; inherited `high`, `xhigh`, `max`, or host-native effort remains unchanged so routing does not silently weaken a user-selected main profile.
- Agent-decided — require a completed `frontier/medium` failure matching a high trigger before entering `high`, and a completed `frontier/high` failure matching an xhigh trigger before entering `xhigh`; `max` and host-native extensions are inheritance-only.
- Agent-decided — retain the existing two-redispatch cap across packet repair and profile escalation; changing model or effort does not reset that budget or Review's three-digest limit.
- Agent-decided — count completed task executions after the initial completed execution against the two-redispatch cap; a host rejection before task execution and its single override-free replacement are one execution attempt, so the replacement neither consumes nor resets the task redispatch budget.
- Agent-decided — treat a profile as atomic: an unsupported or rejected component removes both overrides instead of claiming that a partially resolved profile ran.
- Agent-decided — resolve support per selected model immediately before dispatch; an unverified mapping is unsupported and is not silently clamped to a different effort.
- Agent-decided — keep the effective routing record in active task context only; do not introduce a persistent dispatch ledger, resolver service, or attestation field.

The portable transition rules are:

| Situation | Model transition | Effort transition |
|---|---|---|
| Mechanical initial dispatch | one tier down, clamped at `economy` | unchanged |
| Ordinary initial dispatch | unchanged | unchanged |
| Complex initial dispatch below `frontier` | one tier up | unchanged |
| Complex initial dispatch at `frontier` | unchanged | one tier up, but newly generated effort clamps at `medium` |
| Capability failure | one tier up; at `frontier`, use reasoning-depth handling | unchanged unless at model ceiling |
| Reasoning-depth failure | unchanged | one tier up subject to the `high` and `xhigh` gates |
| Requested profile unsupported or rejected | omit both overrides | omit both overrides |

The normative task-class predicates and precedence are:

1. `mechanical` applies first when the task has an exact transformation,
   bounded targets, and a mechanical oracle.
2. Otherwise `complex` applies when at least one checkable condition holds:
   the change affects an interface consumed by another module; at least two
   plausible causes remain after initial diagnosis; the task crosses a
   security or privacy trust boundary; it makes an irreversible architecture
   or data decision; or it reconciles mutually inconsistent evidence.
3. `ordinary` applies to everything else, including implementation, review,
   blind-run, and adversarial work that meets neither earlier predicate.

Missing task evidence is not a fourth class. When the missing field is
obtainable internally, repair the dispatch packet before execution. Otherwise
route as `ordinary`, record `insufficient-task-evidence`, and do not infer an
upgrade or downgrade from a role or round label. When either main model or main
effort cannot be observed reliably, do not infer a portable profile: omit both
overrides before dispatch and record `host-default/unverified`.

The initial completed task execution may be followed by at most two completed
redispatch executions. Packet repair and profile escalation each consume one
redispatch when the task executes. A host rejection of routing parameters
before task execution consumes no task attempt; its one override-free
replacement occupies the same attempt. When two redispatches have completed,
when the replacement is rejected or fails before a conforming execution, or
when no legal upward transition remains, routing returns `execution-failed`
and records the last profile that actually executed, or
`host-default/unverified` when none can be verified.

High triggers are limited to a blocker surviving a substantive fix, mutually exclusive conclusions over identical evidence, medium failing to settle a high-risk decision, round-3 technical redesign requiring adjudication, or an unresolved multi-step security chain. Xhigh requires either the same high-risk blocker and a checkable failure artifact after `frontier/high`, or mutually exclusive independent `frontier/high` conclusions over identical evidence. Missing inputs, role names, round labels, more search, and transient executor errors are not effort-escalation evidence.

## Alternatives considered
- Keep only `low`, `medium`, and `high` — rejected because it cannot preserve a main agent already using `xhigh` or `max` and loses cross-host decision flexibility.
- Put Codex `ultra` into the common ladder — rejected because Claude Code has no matching value and a provider-specific tier would make the portable policy dishonest.
- Automatically substitute `frontier/low` for `standard/medium` — rejected because the controlled Claude corpus found better recall and latency but higher equivalent cost, so it is a selective quality upgrade rather than a savings rule.
- Silently clamp unsupported effort to the nearest lower host value — rejected because the effective profile would differ from the requested atomic profile without a reliable quality claim.
- Allow initial `high`, `xhigh`, or `max` for complex roles — rejected because a role label does not demonstrate reasoning-depth failure and public plus local evidence does not justify routine expensive effort.
- Add a persistent dispatch ledger or adaptive resolver service — rejected because session-local routing evidence and deterministic adapter tests meet the acceptance criteria with less state and no migration burden.

## Current state evidence
- Forward: `loom-code/skills/build/SKILL.md` under `## 2. Implement test first` permits implementation-agent dispatch but provides no model or effort calculation.
- Reverse: `loom-code/skills/review/SKILL.md` under `## 2. Choose the risk lane` requires fresh reviewers and a configured second vendor but does not define a relative execution profile.
- Error: `loom-code/skills/review/SKILL.md` under `## 4. Converge within one bounded episode` handles malformed or unavailable executors, while unsupported routing parameters have no shared host-neutral fallback contract.
- Data: `loom-code/scripts/test_agent_model_frontmatter.py` under `test_no_agent_pins_effort` enforces inherited effort in agent frontmatter, leaving dynamic profile selection to dispatch time.
- Boundary: `docs/skill-dogfood/2026-09-09-loom-main-relative-dispatch-plan/policy-fixture.md` under `## Evidence boundary` limits existing dogfood to effort authorization and excludes unmeasured model-tier cost claims.

## UI flows
N/A — this engineering policy changes internal subagent dispatch and has no user-facing command, screen, or external API surface.
