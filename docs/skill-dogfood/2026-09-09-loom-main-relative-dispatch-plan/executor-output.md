# Executor output

```yaml
case: H01
task_class: ordinary
initial_delta: {model: 0, effort: 0}
initial_effort: low
high_allowed: no
fallback: omit-both-overrides
reason: A branch code review is ordinary review work, and no failure trajectory supports escalation.
---
case: H02
task_class: ordinary
initial_delta: {model: 0, effort: 0}
initial_effort: low
high_allowed: no
fallback: omit-both-overrides
reason: A branch skill review is ordinary review work, and no failure trajectory supports escalation.
---
case: H03
task_class: complex
initial_delta: {model: +1, effort: +1}
initial_effort: medium
high_allowed: no
fallback: omit-both-overrides
reason: Independent metrics-quality judgment requires cross-cutting reasoning, but no qualifying high-effort trigger is supplied.
---
case: H04
task_class: complex
initial_delta: {model: +1, effort: +1}
initial_effort: medium
high_allowed: no
fallback: omit-both-overrides
reason: Privacy judgment is security-sensitive reasoning, but no prior failure or unresolved chain justifies high effort.
---
case: H05
task_class: insufficient-evidence
initial_delta: {model: unknown, effort: unknown}
initial_effort: unknown
high_allowed: no
fallback: omit-both-overrides
reason: The closeout label does not reveal the underlying work class, and the case supplies no conflict or failed-medium evidence permitting high effort.
---
case: H06
task_class: ordinary
initial_delta: {model: 0, effort: 0}
initial_effort: low
high_allowed: no
fallback: omit-both-overrides
reason: The supplied evidence establishes a review but not a high-risk decision or failed-medium trajectory.
---
case: H07
task_class: ordinary
initial_delta: {model: 0, effort: 0}
initial_effort: low
high_allowed: no
fallback: omit-both-overrides
reason: The case explicitly describes ordinary implementation and supplies no escalation evidence.
---
case: H08
task_class: ordinary
initial_delta: {model: 0, effort: 0}
initial_effort: low
high_allowed: no
fallback: omit-both-overrides
reason: An adversarial probe is ordinary by policy unless evidence shows an unresolved security chain, which is absent here.
---
case: H09
task_class: insufficient-evidence
initial_delta: {model: unknown, effort: unknown}
initial_effort: unknown
high_allowed: no
fallback: omit-both-overrides
reason: A fix and round label alone neither identifies the work class nor demonstrates a blocker that survived a substantive fix.
---
case: H10
task_class: ordinary
initial_delta: {model: 0, effort: 0}
initial_effort: low
high_allowed: no
fallback: omit-both-overrides
reason: An adversarial task is ordinary by default, while the round-3 label provides no evidence of technical-redesign adjudication.
---
case: H11
task_class: insufficient-evidence
initial_delta: {model: unknown, effort: unknown}
initial_effort: inherit
high_allowed: insufficient-evidence
fallback: omit-both-overrides
reason: The host rejection requires one retry with both overrides omitted, but the case provides no task evidence for classification or high-effort eligibility.
---
case: H12
task_class: mechanical
initial_delta: {model: -1, effort: -1}
initial_effort: medium
high_allowed: no
fallback: omit-both-overrides
reason: An exact rename over supplied paths with a passing checker command is mechanically verifiable, so frontier/high reduces to standard/medium.
```

## Executor-reported ambiguities

- The output enum cannot represent `host-default/unverified` after fallback.
- H05 and H09 do not contain enough work evidence for a deterministic profile.
- `risk review` does not distinguish an ordinary review from a high-risk decision.
- The required `fallback` field expresses policy even when fallback did not occur.
