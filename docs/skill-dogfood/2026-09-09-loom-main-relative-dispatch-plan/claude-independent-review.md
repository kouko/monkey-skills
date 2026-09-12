# Independent advisor report — Claude Code audit

## Outcome

```yaml
mode: audit
mode_basis: "可以再整理當前的規劃 然後用 claude code 獨立 review 嗎"
mode_override: false
leg_count: 1
early_stopped: false
verdict: ACCEPT_WITH_CHANGES
requested_tier: frontier/medium
verified_model: claude-opus-5
verified_effort: medium
verification_status: passed
actual_cost_usd: 1.0726025
```

The audit's own result JSON and persisted Claude Code session record share the
same session id. The result's `modelUsage.canonicalModel`, the session record's
`message.model`, and its top-level `effort` establish the verified settings.
Generated answer text was not used as verification evidence.

## Evidence limitation

Claude ran with all filesystem tools disabled. It reviewed the packet text
only and could not independently open the packet's cited evidence files.
Claims that depend on those files remain unverified rather than accepted.

## Blocking changes before implementation

1. High-effort escalation must require the model already to be `frontier`;
   otherwise `standard/low` can jump to `standard/high`, violating model-first.
2. At the frontier model ceiling, a model-escalation cause must fall through
   to the effort step instead of becoming a no-op.
3. Escalation needs a hard cap and terminal outcome. Reuse the existing limit
   of two redispatches instead of adding another number.
4. State that `frontier/medium` plus complex work intentionally stays
   unchanged after the initial-high clamp.
5. Treat unknown host capabilities as false. A known unsupported override is
   omitted before dispatch instead of attempted and rejected.
6. Narrow `cross-module reasoning`: require an interface change consumed by
   another module, or an equivalent checkable condition, so `complex` does not
   become the default class.
7. Give `insufficient-evidence` a packet-repair action before dispatch, or
   merge it into `ordinary` and retain only an uncertainty marker.
8. Make mechanical work model-first in the downward direction too: decrement
   model while preserving effort, unless asymmetry is justified explicitly.
9. State that current dogfood validates the effort dimension only; it does not
   measure the cost or frequency of model-tier upgrades.

## Contradictions and risks

- `complex` currently overlaps common multi-module Build work, risking
  systematic false upgrades to `frontier`.
- Evidence conflict appears both as a complex classifier and a high trigger,
  allowing faster escalation than "one cause at a time" suggests.
- Main-agent `high` is inheritance, not an escalation trigger; listing it in
  both places makes the policy look more permissive than it is.
- Mechanical `model -1, effort -1` changes both dimensions at once and can
  over-downgrade broad but syntactically simple changes.
- `REQUIREMENT_BLOCKED` may require user input, but that is a requirement
  decision rather than a routing decision. The no-user-decision claim should
  be scoped to routing only.

## Delete rather than expand

- Remove the constant `fallback_policy` field from per-dispatch records.
- Keep only two of `requested`, `fallback_triggered`, and `effective_profile`;
  fallback occurrence is derivable from requested versus effective.
- Remove station outcomes `NON_CONVERGENT` and `REQUIREMENT_BLOCKED` from the
  routing outcome enum.
- Remove the duplicated "main already uses high" escalation trigger.
- Remove `insufficient-evidence` as a separate class unless it owns a distinct
  pre-dispatch repair action.

## Unverified factual claims

- The historical claim that none of six direct-high dispatches would still be
  authorized under the proposal.
- The 100–145 line implementation estimate.
- Whether `test_agent_model_frontmatter.py` prohibits static effort pins as
  well as static model pins.

## Coverage disclaimer

This consultation covers only the text embedded in
`claude-review-packet.md`. The cited repository files were not available to the
executor because tools were disabled. The findings are an independent review
of the proposed policy, not independent verification of its historical data.
