# Shared dispatch profile

This is the normative, host-neutral contract for choosing a Loom subagent's
model and reasoning effort. Product model names stay in host adapters; role
names and agent frontmatter stay outside the routing decision.

## Inputs and record

The dispatcher receives an observable main model, observable main effort,
task evidence, retained failure evidence, redispatch count, and the selected
model's verified host capabilities. It records the task class, uncertainty,
target profile, execution mode, effective profile, outcome, and one
evidence-grounded reason in active task context only.

If either main-profile component is unavailable, the dispatcher uses the
atomic fallback in this contract instead of inferring a portable baseline.

## Executable resolver

Before a host-native spawn, a station invokes the packaged standard-library
oracle by its host-provided absolute plugin root and supplies exactly one
observed-state JSON object on standard input:

```text
# Claude Code
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch_profile.py

# Codex
python3 <injected loom-code plugin root>/scripts/dispatch_profile.py
```

The initial event has this shape (the five complex predicates are
`changed_consumed_interface`, `multiple_plausible_causes`, `trust_boundary`,
`irreversible_decision`, and `inconsistent_evidence`):

```json
{
  "event": "initial",
  "main_profile": {"model": "standard", "effort": "medium"},
  "task_evidence": {"changed_consumed_interface": true},
  "capabilities": {
    "economy": ["low", "medium"],
    "standard": ["low", "medium", "high"],
    "frontier": ["low", "medium", "high", "xhigh", "max"]
  },
  "inheritance_guaranteed": true,
  "completed_redispatches": 0
}
```

`capabilities` is fresh host-adapter input for the portable model tiers, not a
universal product-model table. A verified host-native effort may appear in the
selected model's array only so an observed main value can be inherited. The
resolver never generates such a value.

After an execution, use `"event": "after-execution"` and add `last_attempt`
with typed `completed`, `success`, and `conforming` observations plus the
effective `profile`. `success` reports whether the completed work satisfied
its acceptance conditions. `conforming` reports whether the output is
structurally usable and contains enough evidence to classify its result;
`conforming: false` means the output cannot be graded and receives no routing
escalation. When `failure_kind` identifies that completed output as
`malformed-response`, retry the same effective profile without model or effort
escalation. A missing or different kind fails closed. That retry consumes the
shared completed-redispatch budget. A completed capability-quality or reasoning-depth failure therefore
uses `success: false` and `conforming: true` plus its `failure_kind`.

A capability-quality failure means the completed task omitted a checkable
obligation, produced an oracle-verifiable wrong result, or failed to connect
required system relationships; it is not a provider error. `failure_trigger`
is required only for a transition into `high` or `xhigh`; low-to-medium and
non-routing failures omit it.

For a pre-execution host rejection, use `"event": "host-rejection"`, the same
`inheritance_guaranteed` and `completed_redispatches` fields, and
`"rejection_retried": false`. This event does not require `capabilities`.
Apply the returned override-free replacement in the same task attempt. If that
replacement is also rejected, repeat with `rejection_retried` set to true; the
resolver returns `execution-failed`.

The resolver emits one deterministic JSON object. `overrides` is either the
complete portable pair or `null`; a station must never reconstruct a partial
pair. `outcome` is `dispatch`, `routed`, or `execution-failed`. Unknown fields,
unknown events, malformed types, and malformed JSON exit non-zero without a
decision. The caller retains the returned record in active task context. A
redispatch decision includes `next_redispatch`; only after that task execution
completes does the caller pass this value as `completed_redispatches` in the
next event. A pre-execution rejection keeps the earlier completed count.

## Task classification and initial route

<!-- gate: dispatch-profile.relative-routing -->
Classification precedence is `mechanical > complex > ordinary`:

1. `mechanical` requires an exact transformation, bounded targets, and a
   mechanical oracle.
2. Otherwise, `complex` requires at least one checkable condition: a changed
   interface consumed by another module, two plausible causes after initial
   diagnosis, a security or privacy trust boundary, an irreversible
   architecture or data decision, or mutually inconsistent evidence.
3. `ordinary` covers every remaining task.

For `mechanical`, the dispatcher must lower the model by one tier and preserve
effort.
For `complex`, the dispatcher must raise the model by one tier and preserve
effort.
For `ordinary`, the dispatcher must preserve both model and effort.
Model changes clamp at `economy` and `frontier`. At the `frontier` ceiling, a
complex route raises effort by one portable tier, subject to the initial and
expensive-effort limits below.

When task evidence needed for classification can be repaired internally,
repair it before execution. Otherwise route as `ordinary` and record
`insufficient-task-evidence`. Role names and round labels are not routing
evidence.

## Portable tiers and inheritance

The portable model ladder is `economy < standard < frontier`. The portable
effort ladder is `low < medium < high < xhigh < max`. A host adapter maps each
portable value to the selected model only after verifying that exact
model-effort combination.

An initial dispatch may newly enter only `low` or `medium`. If the main agent
already carries `high`, `xhigh`, `max`, or a host-native effort outside the
portable ladder, the dispatcher must preserve the inherited effort unchanged.
For a host-native inherited value, the dispatcher must preserve an inherited
host-native effort unchanged. Inherited effort is baseline preservation rather
than escalation.

Portable arithmetic must use `xhigh` as its generation ceiling. A host-native
effort and `max` must remain inheritance-only values.
An inherited `max` remains `max`; a host-native value such as Codex `ultra`
remains host-native and inheritance-only.

## Evidence-gated effort escalation

Reasoning-depth escalation moves from `low` to `medium` on the current model.
Further escalation to `high` or `xhigh` is allowed only on `frontier`. Before
each expensive-effort move, the dispatcher must retain the matching failure
trigger.

Below `frontier`, a capability-quality failure raises the model one tier and
preserves effort. At `frontier`, capability-quality uses the same effort
handling as reasoning-depth: `low` raises to `medium`, and the transition does
not bypass the `high` or `xhigh` evidence gates.

Entering `high` requires a completed `frontier/medium` attempt and one of:

- the same blocker survived a substantive fix;
- mutually exclusive conclusions were reached over identical evidence;
- medium failed to settle a high-risk decision;
- a round-3 technical redesign requires adjudication; or
- a multi-step security chain remains unresolved.

Entering `xhigh` requires a completed `frontier/high` attempt plus either a
checkable artifact showing the same high-risk blocker or mutually exclusive
independent conclusions over identical evidence. The only newly generated
high-effort sequence is
`frontier/medium` → `frontier/high` → `frontier/xhigh`.

Missing inputs, role names, round labels, additional search, and transient
executor failures are insufficient escalation evidence. `max` and
host-native extensions are inherited only.

## Atomic host fallback

Immediately before dispatch, the host adapter must verify the selected model
accepts the requested effort.
Unknown capability or an unsupported model, effort, or model-effort
combination is unsupported. In every unsupported or unobservable case, the
dispatcher must omit both overrides. It records `inherited` only when the host
guarantees parent inheritance; otherwise it records
`host-default/unverified`.

If the host rejects a supposedly supported profile before task execution,
retry once with both overrides omitted. This replacement occupies the same
task attempt. The dispatcher must preserve an atomic profile. A partial profile
is never claimed as the effective profile, and routing completes without a
user model-or-effort decision.

One task permits at most two completed redispatches after its initial
completed execution. Packet repair and capability escalation consume this
shared budget when task execution occurs; changing model or effort does not
reset it. The dispatcher must ensure that every successful execution returns
`routed` regardless of its position in the budget. When no legal transition
remains or another completed execution would exceed the budget, return
`execution-failed` and record the last verifiable effective profile.
