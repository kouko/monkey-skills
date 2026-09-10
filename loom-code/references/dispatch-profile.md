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

## Task classification and initial route

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

Reasoning-depth escalation moves one effort tier at a time and only on the
`frontier` model. Before each move, the dispatcher must retain the matching
failure trigger.

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
