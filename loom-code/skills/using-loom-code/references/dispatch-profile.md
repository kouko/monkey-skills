# Portable subagent dispatch profile

This is loom-code's single policy for choosing a subagent's capability and
reasoning budget. Resolve it **before** every host-native spawn. The policy
never names a vendor model: its stable vocabulary is `economy`, `standard`,
and `frontier`, paired with `low`, `medium`, and `high` effort.

## Resolve the dispatch profile

1. Classify the task: routine mechanical work → `economy`; ordinary feature,
   integration, or rubric review → `standard`; architecture, security-sensitive
   work, or an adversarial second opinion → `frontier`.
2. Select effort: `low` for deterministic mechanical work, `medium` for normal
   implementation and checklist review, `high` for architecture or high-stakes
   judgment.
3. Apply the reviewer rule: reviewers run one tier below the implementer when
   that still meets the task's floor. A code-quality reviewer for a `frontier`
   architecture task remains `frontier`.
4. Put the resolved `tier` and `effort` in the dispatch packet, then use the
   current host adapter below. The dispatch packet—not an agent file's hidden
   default—is loom-code's source of truth.

## Failure and fallback policy

- A `frontier` request must not silently downgrade. If the host cannot provide
  a same-tier model, fail loud and surface the unavailable capability.
- `economy` and `standard` may make at most one retry after a rejected model or
  effort. The retry must still meet the requested tier; otherwise report the
  failure rather than silently inherit a weaker parent session.
- A host policy, organization allowlist, or environment override can win over
  loom's request. Do not infer effective capability from the child agent's
  self-report. For `frontier`, unavailable **or unverified** effective
  capability halts the dispatch and is surfaced; lower tiers may continue with
  `effective_runtime: unverified` only when their requested floor still holds.

## Claude Code adapter

Translate the resolved tier to Claude's current family aliases:

| Loom tier | Claude model | Default effort |
| --- | --- | --- |
| `economy` | `haiku` | `low` |
| `standard` | `sonnet` | `medium` |
| `frontier` | `opus` | `high` |

Pass `model` on the `Agent` dispatch. This host's documented loom call shape
does not expose a per-invocation `effort` field, so `effort` is a requested
budget rather than a dynamically enforceable setting: compatible reviewer
frontmatter supplies the `standard` / `medium` baseline, and a `frontier` task
halts unless the host exposes evidence that its effective effort meets `high`.
Claude Code can resolve family aliases to a permitted newer model; a blocked
`frontier` alias still follows the failure policy above rather than being
treated as approval to use the parent model.

## Codex adapter

Use the current `spawn_agent` tool's advertised model enum and pass its direct
`model` and `reasoning_effort` fields. Map the current cheapest, balanced, and
frontier entries in that enum to `economy`, `standard`, and `frontier` at
dispatch time; do not embed those product names in the shared policy.

Use a non-full context fork when the host requires that for per-child model or
effort overrides. A user or project `.codex/agents/*.toml` role may still exist
for other Codex purposes, but it is **not the loom dispatch mechanism** and
must not be presented as loom's source of truth. If role configuration could
override a direct spawn request, use the generic role-prompt path and report
the conflict rather than guessing which setting won.

## Dispatch record

Every station includes this compact record in its packet and final status when
the host exposes it:

```text
dispatch_profile: tier=<economy|standard|frontier>; effort=<low|medium|high>
effective_runtime: <host metadata or unverified>
```

The record is observability, not a promise that a provider accepted a request.
