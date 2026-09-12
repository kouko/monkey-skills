# Dogfood report — main-relative Loom dispatch plan

## Final result

```yaml
verdict: PASS
cases: 16
historical_cases: 10
fallback_and_boundary_cases: 6
claude_independent_review: ACCEPT_WITH_CHANGES
claude_verified_model: claude-opus-5
claude_verified_effort: medium
```

The policy passed the final blind replay after incorporating Claude's blocking
findings. This remains planning-stage behavioral evidence, not an installed
skill activation test and not a cost benchmark.

## What changed after independent review

- Model moves first in both directions; mechanical work lowers model only.
- High requires a frontier model plus concrete failure evidence.
- Frontier model escalation falls through to reasoning-depth escalation.
- Redispatch is capped at two attempts and ends as `execution-failed`.
- `complex` requires a checkable boundary, ambiguity, irreversible decision,
  or evidence conflict; role labels and generic cross-module work do not count.
- Unknown or partial host override support atomically omits both overrides.
- Per-dispatch records no longer duplicate constant fallback policy or a
  derivable fallback outcome.
- Missing task evidence routes ordinary with an uncertainty marker after any
  internally obtainable packet fields are repaired.

## Final historical replay

| Cases | Classification and target | Result |
|---|---|---|
| H01–H02 | ordinary + insufficient evidence; `standard/low` | PASS |
| H03 | ordinary; `standard/low` | PASS; false frontier upgrade removed |
| H04–H05 | concrete privacy-boundary complex; `frontier/low` | PASS |
| H06–H10 | label-only evidence; ordinary + uncertainty; `standard/low` | PASS; no inferred high |
| H11 | runtime rejects declared overrides; omit both once | PASS; no user decision |
| H12 | mechanical from `frontier/high`; `standard/high` | PASS; no double downgrade |
| H13 | partial host capability | PASS; atomic omit |
| H14 | reasoning failure at frontier ceiling | PASS; falls through to `frontier/medium` |
| H15 | medium failed a high-risk decision | PASS; justified `frontier/high` |
| H16 | third consecutive capability failure | PASS; stops after two redispatches |

## Model-tier counterfactual

For H01–H10, comparing the new target model with the historical effective
model:

| Direction | Count | Cases |
|---|---:|---|
| Upgrade | 2 | H04, H05 |
| Downgrade | 4 | H06, H08, H09, H10 |
| Unchanged | 4 | H01, H02, H03, H07 |

This is a routing-count comparison only. It does not establish token, latency,
cost, or quality savings. In particular, the two moves from `standard` to
`frontier` may offset some effort savings; a controlled same-input model-tier
replay is still required before making a total-cost claim.

## High-effort result

The retained evidence authorizes none of the six historical direct-high
dispatches H05–H10 as high. The revised policy authorizes high only in H15,
where the case explicitly says medium failed to settle a high-risk decision
and the model is already frontier.

This does not prove the historical high runs were wrong. Their encrypted or
omitted failure trajectories may have contained qualifying evidence.

## Iteration record

1. Initial replay: `PASS_WITH_FINDINGS`; found missing safe execution for
   insufficient evidence, role-label leakage, fallback-state ambiguity, and
   implicit host inputs.
2. Claude audit: `ACCEPT_WITH_CHANGES`; found unbounded escalation, a
   non-model-first high path, broad complex classification, and unmeasured
   model-tier cost.
3. First revised blind replay: `FAIL`; host capabilities were missing from the
   cases and H03's Oracle still encoded a false frontier upgrade.
4. Second revised replay: `PASS_WITH_FINDINGS`; all Oracles matched, leaving
   partial-capability representation and dynamic escalation coverage.
5. Final replay: `PASS`; H01–H16 matched, including atomic fallback, frontier
   fallthrough, justified high, and the two-redispatch cap.

## Evidence boundary

- `executor-output.md` preserves the original 12-case run and should not be
  read as the final policy output.
- `claude-independent-review.md` contains the verified external audit and its
  packet-only limitation.
- The historical corpus omits encrypted prompts and reasoning trajectories.
- No controlled same-input cost or quality experiment has been run across
  model tiers.
