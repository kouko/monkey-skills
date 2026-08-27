# Interaction complexity lens

Use this lens when a change adds or changes navigation, choices, states,
recovery, or actor handoffs. Assess the flow locally even when no upstream
project artifact exists; any upstream assessment is optional evidence only.

Add the following stable, addressable section after the seven flow dimensions:

```markdown
## Complexity handoff

- **Added complexity**: added decisions, states, branches, recovery paths, and
  actor handoffs.
- **Why it is worthwhile**: why each survivor matters to the user or operator.
- **Removed or avoided complexity**: collapsed or avoided paths, choices, and
  states.
- **Downstream risk**: downstream ambiguity that spec-expansion must resolve.
```

Collapse a path, choice, or state only when the resulting flow still achieves
the required user or operator outcome. If it does not, record the lost outcome
as a scope trade-off rather than claiming a complexity reduction.

For a static surface with no interaction or state change, write a reasoned N/A
that says why the lens does not apply. This section records interface-surface
judgment only: do not author behavioral guards, transition rules, or scenario
fan-out. Spec-expansion owns those behaviors.
