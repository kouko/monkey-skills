# Sanitized historical dispatch cases

These cases retain only observable main settings, dispatch metadata, and a
short task label. Encrypted prompts and reasoning records are excluded.
The historical profile is evidence of what happened, not the expected answer.

| ID | Main profile | Host capabilities | Observable task evidence | Historical dispatch | Source session |
|---|---|---|---|---|---|
| H01 | standard/low | model=yes; effort=yes; inheritance=yes | `branch_code_review`; no task body or failure trajectory supplied | inherited/inherited | `[redacted-session]` |
| H02 | standard/low | model=yes; effort=yes; inheritance=yes | `branch_skill_review`; no task body or failure trajectory supplied | inherited/inherited | `[redacted-session]` |
| H03 | standard/low | model=yes; effort=yes; inheritance=yes | `metrics_quality_review`; independent metrics quality judgment, no conflict supplied | standard/medium | `[redacted-session]` |
| H04 | standard/low | model=yes; effort=yes; inheritance=yes | `privacy_judge`; judgment across a privacy trust boundary | standard/medium | `[redacted-session]` |
| H05 | standard/low | model=yes; effort=yes; inheritance=yes | `privacy_commit_closeout`; work crosses a privacy trust boundary, no failed-medium evidence supplied | standard/high | `[redacted-session]` |
| H06 | standard/low | model=yes; effort=yes; inheritance=yes | `spec_risk_review`; no task body or failed-medium evidence supplied | frontier/high | `[redacted-session]` |
| H07 | standard/low | model=yes; effort=yes; inheritance=yes | `impl_w0_01`; no task body or failure supplied | standard/high | `[redacted-session]` |
| H08 | standard/low | model=yes; effort=yes; inheritance=yes | `adv_w0_02`; no task body or unresolved attack chain supplied | frontier/high | `[redacted-session]` |
| H09 | standard/low | model=yes; effort=yes; inheritance=yes | `impl_w0_01_fix_r2`; fix/round label only, no blocker trajectory supplied | frontier/high | `[redacted-session]` |
| H10 | standard/low | model=yes; effort=yes; inheritance=yes | `adv_branch_end_r3`; round/adversary label only, no redesign evidence supplied | frontier/high | `[redacted-session]` |
| H11 | standard/low | model=yes; effort=yes declared, runtime rejects override; inheritance=unknown | exact ordinary task with model/effort override rejected by host | rejected | fallback fixture |
| H12 | frontier/high | model=yes; effort=yes; inheritance=yes | exact mechanical rename over a supplied path list and passing checker command | not historically dispatched | boundary fixture derived from the policy |
| H13 | standard/low | model=yes; effort=unknown; inheritance=unknown | concrete complex interface change consumed by another module | not historically dispatched | partial-capability boundary fixture |
| H14 | frontier/low | model=yes; effort=yes; inheritance=yes | complete evidence shows reasoning-depth failure; no high trigger | not historically dispatched | frontier-ceiling boundary fixture |
| H15 | frontier/medium | model=yes; effort=yes; inheritance=yes | medium failed to settle a high-risk decision | not historically dispatched | high-trigger boundary fixture |
| H16 | standard/low | model=yes; effort=yes; inheritance=yes | three consecutive capability failures with complete input | not historically dispatched | redispatch-cap boundary fixture |

## Oracle

- H01-H02: ordinary with `uncertainty: insufficient-task-evidence`, target
  `standard/low`, high not allowed.
- H03: ordinary, target `standard/low`, high not allowed.
- H04-H05: complex, target `frontier/low`, high not allowed. This is a model
  counterfactual only; current evidence cannot compare its cost or quality
  with the historical lower-model dispatches.
- H05-H10: high is not justified by the supplied evidence. The task class may
  be ordinary or complex only when concrete task evidence supports it. Missing
  evidence routes ordinary with `uncertainty: insufficient-task-evidence`.
- H11: retry once with both overrides omitted; do not ask the user.
- H12: mechanical and model-first; frontier/high becomes standard/high.
- H13: target `frontier/low`, but partial capability support atomically omits
  both overrides; effective profile is `host-default/unverified`.
- H14: frontier ceiling falls through to reasoning depth and becomes
  `frontier/medium`; high is not allowed.
- H15: the concrete trigger permits `frontier/high`; high is allowed only
  because the model is already frontier.
- H16: stop after two redispatches with `execution-failed`; never ask the user
  and never reset the retry count by changing a profile dimension.
