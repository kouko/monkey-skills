Source: `writing-plans/SKILL.md` §"Consuming a loom-design change-folder" — serves `writing-plans`.

# Consuming a loom-design change-folder — task-shape and code-target detail

The detection cascade (Layer 0 / branch-slug / non-archived-count), the
mandatory-once-bound rule, the wrong-bind reversal trigger, and the
structural + critic-verdict validator gates stay inline in SKILL.md —
an orchestrator must not miss them while binding or trusting a
change-folder. This file holds the detail SKILL.md points to once a
change-folder is already bound and trusted: how a scenario becomes a
task, what to copy verbatim vs link, and how to fill in the fields the
spec itself cannot supply.

## Scenario → task mapping

Map each `#### Scenario:` (its GIVEN / WHEN / THEN) → **one task's
`Acceptance: RED/GREEN`**. The THEN is the GREEN observable; the
GIVEN/WHEN set up the RED. One `### Requirement:` may **fan to N
tasks** — split per §The splitting framework (a multi-Scenario
Requirement is N candidate tasks, grouped by assertion boundary).

## Point-don't-copy / link back

**NEVER** copy the spec body into the plan — loom-design is SSOT, and
a copied delta silently goes stale the moment loom-design re-edits the
change-folder, so the plan then drives implementers off a spec that no
longer exists. Reference the source `### Requirement:` / `#### Scenario:`
names via the stable join key `<change-id> / Requirement: <name> /
Scenario: <name>` (the `Brief item covered:` field accepts this
referent — see [`plan-format.md`](plan-format.md)). When the spec file
is in id mode, cite `<change-id> / REQ-<n> / Scenario: <name>` instead
(or the bare id for a whole requirement) — the name form stays for
legacy files. The plan **links back** to the spec; it does not
duplicate it.

## Verbatim-copy carve-out (fact vs interpretation)

One exception to point-don't-copy: the THEN **observable**, **magic
values**, and **signatures** are *facts* — copy them **verbatim** into
the RED/GREEN assertion (a paraphrased magic value or signature is a
defect). The surrounding **narrative** and **design rationale** are
*interpretation* — link to them, do not copy. Facts in, prose linked.

## WHAT not WHERE — populate code-target fields by target-repo recon

The change-folder supplies the **WHAT** (behavior / acceptance) but
carries **no file / module / path info** — yet `plan-format.md` makes
`Module` and `Files touched` (the parallelism disjointness oracle)
required per task. Do **not** guess placeholder paths. Populate each
task's `Module` / `Files touched` / `Context paths` by
**reconnaissance of the TARGET repo** — grep / Read / Explore over the
codebase the change lands in, the same Current-State-Evidence recon
brainstorming does — seeded by the proposal's `## OOUX object model`
(OOUX = the proposal's object/relationship model) where present
(object → likely module / file). The spec names the behavior; the
target repo tells you where it lives.

- **MODIFIED / REMOVED deltas.** When the spec carries a
  `## MODIFIED Requirements` or `## REMOVED Requirements` block (not
  just `## ADDED Requirements`), map them to change / removal tasks
  **plus the corresponding test update** — same `#### Scenario:` →
  RED/GREEN discipline (the RED is the failing test that encodes the
  changed / removed behavior; the GREEN is the updated test passing).
