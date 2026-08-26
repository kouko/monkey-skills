---
name: design-critic
description: Adversarial critique of DESIGN.md + ui-flows.md via a writer≠judge panel for surface omissions, dead-ends, and a11y gaps grounded in Nielsen. Use before spec-expansion; never review specs or code.
version: 0.3.0
---

# design-critic

Hunt omissions in the interface surface after the design station produces
`DESIGN.md` + `ui-flows.md`. This is the design-station verification gate in the
design → spec → code pipeline: it catches missing states, unreachable screens,
and dead-ends before they propagate into requirements or implementation.

## Inputs and hard boundary

Critique the consumer project's product-level `docs/loom/DESIGN.md` and per-change
`docs/loom/<change-id>/ui-flows.md`. Legacy layouts may colocate both; critique
whatever exists and name any missing input.

**Wrong-artifact guard:** STOP if the input is a spec (behavioral requirements or
`#### Scenario:` blocks) or code. Route a spec to
`loom-design:completeness-critic` and code to code review. This critic is
surface-only: it asks whether a state is drawn, a screen is reachable, and an exit
exists. It does not fan-out behavioral state machines, expand acceptance criteria,
review code, or run TDD. Flag the surface gap here; fan-out the behavior at the
spec layer.

## Executor and writer≠judge

You are the executor and supply the reasoning plus panel dispatch; no external
runtime or API key is required. A writer cannot reliably judge its own output
because it remains anchored on what it already drew. The external panel provides
independent judgment; the executor alone consolidates, writes back, and mints.

## Mechanical pre-check

Before panel dispatch, grep both artifacts for these schema violations. Emit a
direct `NEEDS_REVISION` finding for every hit—**no panel needed for that finding**—
but **the panel still runs after the pre-check** for all other omissions.

1. **Out-of-enum `evidence_needed`:** only `craft`, `domain-convention`, and
   `project-local` are valid.
2. **Tier discipline:** run two literal sub-greps:
   - **(2a) untiered tag:** near every `evidence_needed: domain-convention`, require
     a literal `SHAPING` or `DEFERRABLE` label.
   - **(2b) deferred SHAPING:** if a literal `SHAPING` item is non-blocking or
     deferred, require `deferred: <reason>`.
   Whether an item genuinely is SHAPING remains the **panel's judgment**; the
   mechanical check never classifies it.

These rules come from `interaction-flows` / `design-system` reference
`references/knowledge-triage.md`. The pre-check never replaces panel judgment.
Record pre-check findings beside panel findings so their mechanical origin is
visible, but apply the same ranked write-back and provenance rules. An invalid
tag is not permission to investigate the underlying question; it is a schema
defect for the producing station to repair.

## The multi-lens critic panel

Dispatch **one fresh context general reasoning agent per lens**, never a
read-only, search, or explore-restricted agent. Each lens stays blind to the
others; this writer≠judge separation and fresh context decorrelate failures.

Give every lens-critic the artifact paths, the
`references/design-heuristics.md` path, one distinct persona, and one lens row.
Each critic MUST read `references/design-heuristics.md` **in full** before hunting,
then cite the relevant Nielsen heuristic and 7-dimension mapping in each finding.
Personas must differ (for example: confused first-timer, 3am on-call operator,
user whose network dropped). **Do not load** completeness-critic machinery or any
spec/behavior reference. Host dispatch shapes are in
`../using-loom-design/references/interface-claude-code-tools.md` and
`interface-codex-tools.md`.

Every critic returns only candidate surface omissions: artifact location,
missing surface/state/transition, user path, heuristic, severity, persona
observation, and optional evidence tag. It must not edit artifacts, issue a
verdict, or see another critic's findings. The executor alone consolidates,
writes back, validates, and mints.

## Loop-until-dry

Run the panel in rounds, then re-seed every consolidated gap into the design view
for the next round. A missing error screen becomes a surface to inspect; a
dead-end becomes an exit to design.

- After round 1 use **targeted re-seed**, dispatching only lenses whose input
  changed. Never blanket re-sweep.
- Stop at **K = 2 consecutive** rounds with no new gap.
- Treat an overly convergent round-1 union—most lenses finding the same few
  gaps—as a **dryness signal**. Do not ritualistically rerun every lens.
- Dry means no new gap under the current lenses, never that the design is
  complete.

Count a gap as new only when it adds a missing surface, state, transition, entry,
exit, recovery, or modality requirement not already represented by the semantic
union. Wording changes and a second persona naming the same gap are corroboration,
not new findings. Track consecutive dry rounds explicitly. If a dry round leaves
no eligible changed lens, record the unchanged semantic union as the second dry
observation and stop; do not dispatch empty work merely to increment the count.

## Fixed Nielsen lenses

Use these **5 load-bearing lenses**, grounded in Nielsen's usability heuristics
rather than a newly invented checklist. Ask only: **what surface is missing?** Do
not prescribe a design that may have been intentionally omitted.

1. **Render-state completeness (H1, visibility):** for every surface, inspect
   empty, loading, error, and success variants. A happy/populated state alone is
   a finding.
2. **Dead-end & exit / user control (H3):** require a path forward, back, or out.
   Destructive actions need undo/reversibility or confirmation.
3. **Navigation reachability & entry (H2/H6/H7):** find orphan screens and missing
   entry points such as deep link, notification, cold start, and resume.
4. **Error prevention & recovery (H5/H9):** require designed error screens,
   confirmation for irreversible actions, and a recovery path from each error.
5. **Modality fit & accessibility (H4/H8):** inspect GUI responsive/narrow, TUI
   narrow-terminal, CLI non-TTY/piped variants, and a11y/accessibility omissions.

If `docs/loom/PRINCIPLES.md` exists, add a conditional sixth lens: what
principle-entailed UI surface is omitted? For example, an offline principle may
require an offline/cached state. Without that file, announce
**"principles lens: N/A (no PRINCIPLES.md)"** and do not invent principles. This lens finds omissions;
principle contradiction belongs to conformance review.

The fixed five are independent views, not five sequential headings for one
critic. Render-state checks representation, control checks escape and reversal,
navigation checks graph reachability, recovery checks prevention and repair, and
modality checks whether the chosen channel remains usable. Preserve all five even
when one finding crosses their boundaries; cross-lens convergence increases its
rank rather than erasing the distinction between lenses.

## Diversity and consolidation

After every round make a **qualitative overlap** judgment. High panel-wide overlap
is a redundancy red flag: swap in an orthogonal lens, persona, or input view before
the next round. Low overlap shows the panel is earning its cost. Report this in the
round summary. Redundancy is never a completeness signal. It is also distinct from
cross-lens convergence on one finding, which corroborates that gap.

Take the union, **dedup semantically**, and rank by **severity × number-of-lenses-that-found-it**:

- 3: blocks the user's core job; a primary-flow state/screen is absent.
- 2: should-add secondary state or exit.
- 1: polish such as an a11y or density refinement.

Re-seed the ranked load-bearing set into the working design view; place the long
tail in Blind spots rather than padding the design.

For ties, prefer the finding affecting the earlier core path, then the one with
the more concrete artifact location. Preserve the list of contributing lenses on
the deduplicated record so corroboration remains auditable. Never promote a
low-severity polish note merely because several similar personas noticed it over
a core-job blocker grounded in one specialist lens.

A finding may carry `evidence_needed: craft | domain-convention | project-local`
when the correct answer is owned elsewhere. The critic only **flags** one of these
tags; it never runs WebSearch, performs research, or resolves the evidence. This
does not alter the verdict vocabulary.

## Augmentation-only write-back

Extend the design view in place with the consolidated ranked findings, never the
raw union. This is **augmentation only**: never overwrite writer content.

1. Tag every added state, exit, or error-screen stub `critic-found` at its landing
   point in `DESIGN.md` / `ui-flows.md`.
2. Append or extend `## Blind spots — needs human/field input`.
3. Validate afterward with direct process execution:
   `argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/interface/validate_design_output.py", "<design-output-dir>"]`.

Validator failure feeds the verdict. This provenance-tagged exception to the
evaluator-does-not-modify rule remains an augmentation, not a rewrite.

Keep additions minimal: add the absent surface contract or stub needed to expose
the gap, not a speculative finished design. If a finding cannot be placed without
rewriting an existing decision, leave it unresolved, explain where it conflicts,
and let the verdict return it to the writer. The validator is mandatory after the
last write-back, even if every addition appears syntactically harmless.

## Honesty output and round summary

You MUST emit what text artifacts **cannot judge** into
`## Blind spots — needs human/field input`, and it MUST be non-empty. Examples are
rendered contrast/focus order, actual tap counts, naturalness for target users,
and brand fit. Tag each `needs human/field input`.

**Do not claim "complete"**, comprehensive, or all states covered. Say only
**"surface-coverage relative to N lenses; blind spots listed below."**

The final **Round summary** reports rounds run; gaps per round; each round's
qualitative overlap/redundancy judgment and any orthogonal replacement;
`critic-found` additions; the non-empty Blind spots list; and the relative
coverage statement. Finish with exactly one verdict token.

Blind spots are uncertainty disclosures, not a dumping ground for ordinary
surface defects. Keep critic-actionable missing states in the ranked additions;
reserve Blind spots for facts that require rendering, observation, domain
expertise, or field contact. A human-input item can remain even when the panel is
dry, which is why a qualified passing verdict always carries notes.

## Verdict

- **`NEEDS_REVISION`**: a severity-3 gap could not be concretely re-seeded, or
  validation failed. Route the named surfaces to `design-system` /
  `interaction-flows`, then rerun. The outer writer↔critic cycle is **capped at 2**.
  On the second consecutive result after revision, stop; **after minting**
  the verdict, hand back to the user with unresolved findings in plain language.
  Never silently proceed.
- **`PASS_WITH_NOTES`**: the loop is dry, findings were re-seeded as
  `critic-found`, and Blind spots is non-empty. Continue to
  `loom-design:spec-expansion`.

There is **no unqualified `PASS`** and no bare PASS: that would imply no omissions
remain despite mandatory Blind spots. Both values mint with direct execution:
`argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/interface/mint_critic_verdict.py", "mint", "--change-folder", "<design-output-dir>", "--critic", "design-critic", "--verdict-file", "<verdict-file>", "--files", "DESIGN.md,ui-flows.md"]`.
Pass argv arrays directly to process execution; never through a shell.

## Deletable lenses (Bitter Lesson)

Keep the panel's writer≠judge mechanism regardless of model strength, but treat
each individual lens as deletable. Periodically re-baseline bare model versus
panel and prune any lens a stronger model has subsumed without weakening coverage.

## References

- `references/design-heuristics.md`: Nielsen × 7-dimension grounding.
- `interaction-flows`: produces `ui-flows.md`.
- `loom-design:completeness-critic`: behavioral completeness at the next stage.
- `loom-design:product-principles`: produces conditional `PRINCIPLES.md`.
