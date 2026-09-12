# Independent review packet — main-relative Loom model dispatch

## Decision statement

Decide whether Loom should restore dynamic subagent model and effort routing
using the main agent as the baseline, a model-first cost policy, evidence-only
high effort, and an automatic fallback to omitted overrides.

## Rejected options

- Fixed product model names in agent frontmatter: rejected because they bind
  the portable Loom contract to one host and age as model lineups change.
- Fixed role profiles such as reviewer=frontier/high: rejected because a role
  name does not prove task difficulty and historically caused early high use.
- Absolute standard/medium default for all engineering work: rejected because
  it discards a user-selected strong-model/low-effort baseline.
- A model availability search tree and persistent dispatch ledger: rejected as
  unnecessary complexity; routing is an optimization and can fall back to the
  main agent.
- Simultaneously raising model and effort for complex work: rejected because
  it pays twice before observing whether the stronger model was sufficient.

## Evidence paths

- `policy-fixture.md` — the first policy draft used in planning-stage dogfood.
- `historical-cases.md` — sanitized historical and boundary cases.
- `executor-output.md` — independent application of that draft.
- `report.md` — dogfood findings and evidence limits.
- `../../../../loom-code/skills/build/SKILL.md` — current Build station.
- `../../../../loom-code/skills/review/SKILL.md` — current Review station.
- `../../../../loom-code/scripts/test_agent_model_frontmatter.py` — current
  prohibition on static effort pins.

## Incumbent proposal

### 1. Portable vocabulary

Loom uses only:

```text
model:  economy < standard < frontier
effort: low < medium < high
```

Each host owns the mapping from these tiers to supported product identifiers.
The core policy contains no product model names.

### 2. Required inputs

At dispatch time the orchestrator reads:

```yaml
main_profile:
  model_tier: economy | standard | frontier | inherit
  effort: low | medium | high | inherit
host_capabilities:
  supports_model_override: true | false | unknown
  supports_effort_override: true | false | unknown
  guarantees_parent_inheritance: true | false | unknown
task_evidence:
  goal: <one sentence>
  acceptance: <checkable conditions>
  risk_signals: []
  failure_trajectory: []
```

If the main profile cannot be observed, the orchestrator omits both overrides
and records `host-default/unverified`; it does not guess tiers.

### 3. Task classification

Classify work from the dispatch packet, not role or round names:

| Class | Evidence | Adjustment |
|---|---|---|
| mechanical | exact targets plus mechanical verification | model -1, effort -1 |
| ordinary | bounded implementation, blind run, review, or probe with sufficient inputs and no complex signal | model 0, effort 0 |
| complex | cross-module reasoning, ambiguous debugging, design trade-off, security chain, irreversible architecture, or evidence conflict | model +1, effort handled model-first |
| insufficient-evidence | the observable packet cannot support one of the above | execute at main 0/0 and record uncertainty |

Precedence is `insufficient-evidence > complex > mechanical > ordinary`.
Crossing multiple files alone is not complex. Security language is complex
only when the requested judgment concerns a security property or attack path.

All tier arithmetic clamps at the declared minimum and maximum.

### 4. Model-first effort calculation

1. Resolve the model delta.
2. If a complex task successfully moves to a stronger model tier, keep the
   main effort unchanged for its first attempt.
3. If the model is already at `frontier`, a complex task may raise effort by
   one step for its first attempt.
4. A non-high main profile may never become high on initial dispatch; clamp
   such a result to medium.
5. A main-agent high may be inherited. Mechanical work reduces it to medium.

Examples:

| Main | Mechanical | Ordinary | Complex initial |
|---|---|---|---|
| economy/low | economy/low | economy/low | standard/low |
| standard/low | economy/low | standard/low | frontier/low |
| frontier/low | standard/low | frontier/low | frontier/medium |
| frontier/high | standard/medium | frontier/high | frontier/high |

### 5. Evidence-based escalation

Escalate one cause at a time:

1. Missing path, acceptance condition, or worked example: repair the packet
   and retry the same profile once.
2. The agent followed the request but misunderstood system relationships or
   could not distinguish two interpretations: raise model one tier, preserving
   effort.
3. Complete evidence produced shallow, unsupported, or unresolved reasoning:
   raise effort one step, initially no higher than medium.
4. High is allowed only when at least one is observable:
   - the same blocker survived a substantive fix;
   - reviewers reached mutually exclusive conclusions over the same evidence;
   - medium could not settle a high-risk decision with complete inputs;
   - a Review round-3 technical redesign requires adjudication;
   - a multi-step security attack chain remains unresolved;
   - the main agent already uses high.

A role name, round label, `NEEDS_REVISION`, missing input, additional search,
or transient executor error is not a high trigger.

### 6. Automatic fallback

Routing never asks the user to select a model, effort, retry, or fallback.

```text
attempt resolved overrides
  -> success: continue
  -> unsupported/rejected routing parameters:
       retry once with both model and effort omitted
         -> success: continue as inherited or host-default/unverified
         -> failure: EXECUTION_FAILED
```

Fallback does not claim that the requested stronger profile ran. Ordinary
Build and Review verification still judges the work product.

### 7. Bounded outcomes

- `ROUTED`
- `FALLBACK_TO_MAIN` when inheritance is guaranteed
- `FALLBACK_TO_HOST_DEFAULT` when inheritance is not guaranteed
- `EXECUTION_FAILED` when the override-free retry cannot execute
- `NON_CONVERGENT` when the existing bounded Review episode ends with blockers
- `REQUIREMENT_BLOCKED` when progress would require changing requirements,
  visible behavior, guarantees, credentials, or external authority

Changing model or effort never resets the existing three-round Review limit.

### 8. Minimal observable record

Keep the record in active task context; do not add a committed ledger:

```yaml
dispatch:
  main: standard/low
  task_class: complex
  uncertainty: false
  requested: frontier/low
  fallback_policy: omit-both-overrides-once
  fallback_triggered: false
  effective_profile: frontier/low | inherited | host-default/unverified
  escalation_reason: none | <observable trigger>
  outcome: ROUTED
```

Reviewer's actual vendor and model continue to use the existing attestation
surface. Other routing details remain session-observable, not publication
evidence.

### 9. Minimal implementation surface

- Add one shared `loom-code` dispatch-profile reference.
- Add short Build and Review wiring to read and apply it.
- Keep all four agent frontmatter files free of model and effort pins.
- Extend the existing frontmatter test and add focused prose-contract tests.
- Do not add a runtime resolver, ledger, attestation schema, role-specific
  profiles, or fixed product model names.

Estimated change: one new reference, three existing files modified, roughly
100–145 maintained lines. This estimate must be replaced by actual diff counts
if implemented.

### 10. Claims and open evidence

Planning-stage dogfood showed that, from the retained evidence, the policy
would authorize none of six historical direct-high dispatches as high. That
does not prove the historical choices were wrong because omitted trajectories
may have carried qualifying evidence.

No token, latency, quality, or success-rate reduction is claimed. Those need a
controlled same-input comparison after a runnable draft exists.

## Requested audit

Return a concise review with:

1. verdict: ACCEPT, ACCEPT_WITH_CHANGES, or REJECT;
2. factual errors versus judgment calls separated;
3. contradictions or non-executable transitions;
4. false-downgrade and false-upgrade risks;
5. whether fallback really needs no routing-related user decision;
6. the smallest concrete changes required before implementation;
7. any part that should be deleted rather than expanded.
