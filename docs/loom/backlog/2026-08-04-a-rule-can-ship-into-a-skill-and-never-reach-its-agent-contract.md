---
name: 2026-08-04-a-rule-can-ship-into-a-skill-and-never-reach-its-agent-contract
description: a reviewer-behaviour rule written into a SKILL.md is not carried by the agent contract that executes it, and nothing mechanical pairs the two
status: OPEN
origin: PR #644 round 1 (read-context), PR #645 round 1 and its verification round (delta-scope clause (b)) — four recurrences across two branches
start: before the next branch that adds or edits a rule constraining `docs-reviewer` or `code-reviewer` behaviour
---

## The item

`requesting-docs-review/SKILL.md` and `loom-code/agents/docs-reviewer.md`
both state the rules a dispatched reviewer follows. The skill is what an
orchestrator reads; the agent contract is what the reviewer reads. Nothing
checks that a rule in one appears in the other, and the agent's own input
contract says to treat unspecified sections as empty — so a rule that lands
only in the skill is silently inert at the receiving end.

Four recurrences across two branches, every one caught by review rather than
by a check:

- `read-context` (#644 round 1, 🔴) — the field was named in both SKILL.md
  files and in neither the agent's input contract, its permitted-read rule,
  nor its output schema.
- the delta-scope raise rule (#645 round 1, 🔴) — same shape, different rule.
- `out_of_scope:` (#645 round 2, 🟡) — the block reached the verdict schema
  but not §Aggregation rule, so the fail-closed `class:` clause would have
  swept every suppressed observation back into the gate.
- clause (b)'s direction (#645 verification round, 🟡) — corrected in the
  skill, left one-sided in the agent contract, which then permitted exactly
  what the skill forbade.

The fourth happened inside the round that wrote the first one up as a worked
example in Directive 2. Prose recording the lesson does not prevent it.

## The proposed fix, and its precondition

A drift check pairing the two carriers. The mechanizable core is narrower
than "same rules": **every packet field and output field the skill names must
appear in the agent contract.** That form would have caught `read-context`,
`out_of_scope:` and the `Round scope` field. It would NOT have caught clause
(b)'s direction, which is a wording divergence inside a field both files
carry — so the check is a floor, not the whole class, and the entry should
say so when it ships.

**Precondition, non-negotiable**: measure the naive form's fire rate over the
existing plugin before building it, per
`docs/loom/memory/measure-a-checks-fire-rate-before-building-it.md`. A
description-vs-body checker was killed at exactly this step this week (12 of
20 body edits fired it), and a doc-claims-a-CLI-flag checker survived it
(10 of 407). Report instances examined, times fired, times fired correctly.

## Why it is not "just review harder"

The convergence contract's own corollary ranks a standing mechanism above
authorizing another round, and both verification arms on #645 named this
class as the example. A reviewer finds a different subset each pass; a
checker finds the same thing every run.

Compounding it: the agent contract a subagent actually loads comes from the
installed plugin cache, not the repo working tree
(`docs/loom/memory/agent-contract-edits-do-not-reach-this-sessions-subagents.md`),
so the branch that introduces such a rule cannot behaviourally test whether
it landed — which is precisely why a static pairing check is the available
instrument.
