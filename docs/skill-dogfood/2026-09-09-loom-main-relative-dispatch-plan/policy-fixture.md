# Draft policy fixture — main-relative Loom dispatch

This is an evaluation fixture, not an installed Loom contract.

## Inputs

- `main_profile`: model tier and effort observed for the main agent. If either
  value is unavailable, omit both overrides and record `host-default/unverified`.
- `host_capabilities`: whether model override, effort override, and parent
  inheritance are supported. `unknown` is treated as `false`; if either
  override is not supported, omit both before dispatch so the profile remains
  atomic rather than partially claimed.
- `task_evidence`: concrete work, boundaries, verification method, and retained
  failure trajectory. Role names and round labels are not task evidence.

Product model names remain host-local mappings. The portable vocabulary is
`economy < standard < frontier` and
`low < medium < high < xhigh < max`.

The five effort tiers are the cross-host comparison domain, not a promise that
every model accepts every value. A host adapter resolves only values supported
by the selected model. A host-only value above the portable range, such as
Codex `ultra`, is retained as an inherited native value but is never generated
by portable tier arithmetic.

## Classification

Apply the first supported class; otherwise use `ordinary`.

1. `mechanical`: exact transformation, bounded targets, and mechanical oracle.
2. `complex`: at least one checkable condition holds:
   - changes an interface consumed by another module;
   - two or more plausible causes remain after initial diagnosis;
   - crosses a security or privacy trust boundary;
   - makes an irreversible architecture or data decision;
   - reconciles mutually inconsistent evidence.
3. `ordinary`: everything else, including implementation, review, blind run,
   and adversarial work whose concrete evidence meets neither class above.

Missing task evidence does not create a fourth class. Repair the packet before
dispatch when the missing field is obtainable internally. Otherwise route as
`ordinary` with `uncertainty: insufficient-task-evidence`; never infer an
upgrade or downgrade from a role or round name.

## Initial profile

Model moves before effort:

- `mechanical`: model -1, effort unchanged.
- `ordinary`: model unchanged, effort unchanged.
- `complex`: model +1, effort unchanged.
- When `complex` begins at the `frontier` model ceiling, raise effort one tier
  instead, but an initial dispatch may newly enter only `low` or `medium`.
- A main agent already using `high`, `xhigh`, `max`, or a host-only native
  value may pass that effort through unchanged. This is inheritance, not a new
  routing upgrade.

All deltas clamp at tier boundaries and at the initial-dispatch ceiling.
Therefore `frontier/medium` plus complex work remains `frontier/medium`; this
zero adjustment is intentional because the model is capped and initial high is
forbidden. Inherited values above medium remain unchanged rather than being
silently lowered.

## Escalation

Allow at most two redispatches for one task. Each redispatch handles one
observed cause:

1. Incomplete input: repair the packet and retry the same profile; this does
   not consume a capability escalation.
2. Capability failure: raise model one tier and keep effort unchanged. At the
   `frontier` ceiling, fall through to reasoning-depth handling.
3. Reasoning-depth failure with complete evidence: raise effort one tier.
   Entering `high` additionally requires the model already be `frontier` and
   one concrete high trigger below. Entering `xhigh` requires a completed
   `frontier/high` attempt and one concrete xhigh trigger below. Routing never
   newly enters `max`.

High triggers are limited to:

- the same blocker survived a substantive fix;
- reviewers reached mutually exclusive conclusions over the same evidence;
- medium failed to settle a high-risk decision;
- a round-3 technical redesign requires adjudication;
- a multi-step security chain remains unresolved.

Xhigh triggers are limited to:

- the same high-risk blocker remains after a completed `frontier/high` attempt,
  with complete inputs and a checkable failure artifact; or
- independent `frontier/high` reviewers still reach mutually exclusive
  conclusions over identical evidence.

Main-agent `high`, `xhigh`, `max`, or a host-only native value is inheritance,
not a trigger. A role name, `NEEDS_REVISION`, round number, missing input, more
search, or a transient executor error is not by itself evidence for high or
xhigh. Exhausting two redispatches returns
`execution-failed`; changing model or effort never resets a station's own
review-round limit.

Because the redispatch cap is two, not every starting profile can reach every
recognized effort tier. For example, an initial `frontier/medium` may reach
`frontier/high` and then `frontier/xhigh`; it cannot newly reach `max`.

## Host fallback

Before dispatch, the host adapter verifies that the selected model accepts the
requested effort. A portable value with no verified mapping is unsupported; it
is not silently clamped to a different effort. When either override capability
or that mapping is `false` or `unknown`, omit both overrides before dispatch.
If a capability declared `true` is nevertheless rejected, retry once with both
overrides omitted. Record the result as `inherited` only when the host
guarantees parent inheritance; otherwise record `host-default/unverified`.
This fallback does not ask the user and never claims that the requested profile
ran.

Routing itself never asks the user to choose a model, effort, fallback, or
retry. A later requirement decision may still require the user, but it is not a
routing outcome.

## Required output for each case

Return:

```yaml
case: <id>
task_class: mechanical | ordinary | complex
uncertainty: none | insufficient-task-evidence
target_profile: <model-tier>/<portable-effort-tier> | <model-tier>/<host-native-effort> | host-default/unverified
execution: override | omit-unsupported | omit-after-rejection
effective_profile: <model-tier>/<portable-effort-tier> | <model-tier>/<host-native-effort> | inherited | host-default/unverified
outcome: routed | execution-failed
reason: <one sentence grounded only in the case evidence>
```

`target_profile` is the profile sought by the latest initial or redispatch
decision before host fallback. On `execution-failed`, `effective_profile` is
the last profile that actually ran.

`execution` records whether fallback actually happened; do not add a duplicate
fallback outcome, flag, or constant policy field to each dispatch record.

## Evidence boundary

The current historical dogfood tests whether high effort is authorized from
retained evidence. It does not measure model-tier upgrade frequency, token
cost, latency, or quality. Model-tier cost requires a separate controlled
replay before implementation claims savings.
