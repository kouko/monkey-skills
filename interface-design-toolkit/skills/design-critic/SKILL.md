---
name: design-critic
description: |
  Adversarial critique of a design output (DESIGN.md + ui-flows.md) via a writer≠judge panel for SURFACE omissions (undrawn states, dead-ends, a11y) per Nielsen. Use to review a design draft for gaps before spec-expansion. Surface only, never code.
---

# design-critic

Turn a design draft into a **gap-hunted** design draft. The job: after the design
station emits `DESIGN.md` + `ui-flows.md`, the designer has silently specified the
happy-path surface and dropped the empty/error states, the dead-ends, the
unreachable screens. This skill runs an **independent heuristic evaluation** of the
interface **surface** so those omissions are caught at design time — the cheapest
stage — instead of propagating into spec and code.

This is the **design-station verification gate** of the GENERATE pipeline (design →
spec → code). It critiques the surface for omissions; it does **not** author design,
expand behavior, or review code (see Boundary below).

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply the LLM
reasoning and the parallel fan-out. There is no external runtime, no API key, no
program to install — the panel rides on the host agent you are already in.

**Inputs.** The artifacts under critique are the design change-folder in the consumer
project — by convention `docs/interface-design-toolkit/DESIGN.md` +
`docs/interface-design-toolkit/ui-flows.md` (one or both may be present; critique
whatever exists, note the missing one). **Wrong-artifact guard:** if you are handed a
**spec** (behavioral requirements / `#### Scenario:` blocks) or **code**, STOP — that
is the wrong skill (`spec-toolkit:completeness-critic` for a spec; code review for
code). Do not run the panel over a non-design artifact and dutifully drop every
finding; decline and name the right skill.

## Why a separate critic — writer ≠ judge

The skill that wrote `ui-flows.md` cannot reliably find its own blind spots: a
generator anchors on the surface it already drew. Self-review by the same context
inherits the same blind spots. So the critique is an **external check** — a panel of
**fresh-context** lens-critics, each decorrelated from the writer and from each
other. This is heuristic evaluation (Nielsen & Molich): independent expert passes
catch what a single self-pass cannot. (Industry: Nielsen/Molich heuristic
evaluation; automated analogue UICrit, arXiv 2407.08850.)

## What you are NOT — the boundary

This critic hunts **surface / usability omissions** on `DESIGN.md` / `ui-flows.md` —
*is the empty state drawn? is there an exit from this screen? is every screen
reachable?* It does **NOT**:

- hunt **behavioral** omissions of the spec (object state machines, edge-case
  fan-out, `#### Scenario:` acceptance blocks) — that is
  **`spec-toolkit:completeness-critic`**'s job, one stage later;
- review code, run TDD, or judge implementation.

**Flag the surface gap here; fan-out the behavior there.** Doing the behavioral
fan-out in this skill would duplicate the spec layer and blur the surface/depth
boundary that the design→spec seam depends on.

## loop-until-dry — the termination rule

Run the panel in **rounds**. Mind the cost: a round is N fresh-context subagent
dispatches (one per lens). Do not blanket re-sweep every round.

1. **Re-seed**: every gap found is fed **back** into the design view as a new seed
   (a missing error screen becomes a surface to evaluate; a dead-end becomes an exit
   to design) for the next round.
2. **Targeted re-seed, not blanket re-sweep**: after round 1, re-dispatch only the
   lens(es) whose re-seeded gap changed that lens's input.
3. **Terminate when dry — `K = 2`**: stop after **2 consecutive** rounds that
   surface no new gap. A **heavily-convergent round-1 union** (most lenses landing
   on the same few gaps) is itself a dryness signal — do not ritually re-sweep all
   lenses when the union has already collapsed to a small deduped set.
4. **Honesty rail**: "dry" means *no new gap under the current lenses* — it does
   **NOT** mean the design is complete (see the blind-spots rule).

## The multi-lens critic panel

The lenses run as a **dispatched panel**, not one agent doing sequential passes.
**Dispatch one subagent per lens, each with fresh context** — phrase the fan-out
portably, not bound to any one harness. **Pin each lens-critic to a general
reasoning agent — never a read-only / search / explore-restricted type**, or a lens
silently refuses the reasoning role and the panel loses it (a false negative).
**Fresh context per lens is the mechanism that decorrelates the critics** — each
lens stays blind to the others' passes, so they do not all stare at the same cells.

**Lens-critic input contract** (per the repo's Agent Launch Convention — pass paths,
the subagent reads them): each lens-critic receives the **artifact paths**
(`DESIGN.md` + `ui-flows.md`), the **`references/design-heuristics.md` path**, its
**persona string**, and its **one lens row** (which heuristic + which omission to
hunt). The general reasoning agent is the host's general-purpose subagent type — never
a search/explore/read-only type.

**MANDATORY — each lens-critic reads `references/design-heuristics.md` in full** before
hunting, so its findings cite the Nielsen heuristic + the 7-dim mapping (the anti-
reinvent grounding). **Do NOT load** `spec-toolkit:completeness-critic`'s machinery or
any spec/behavioral reference — this panel is surface-only; pulling in the spec layer
is the boundary violation the §boundary forbids.

Each lens-critic carries a **distinct persona** (e.g. confused first-timer, 3am
on-call, the user whose network just dropped) and reads
[`references/design-heuristics.md`](references/design-heuristics.md) for its
Nielsen-heuristic grounding. The lenses are **grounded in Nielsen's 10 usability
heuristics × the 7 UX dimensions — not a freshly invented checklist** (inventing one
reinvents Nielsen).

The **5 load-bearing lenses** (full mapping in `references/design-heuristics.md`):

1. **Render-state completeness** (Nielsen H1 — visibility of system status). For
   every surface, is the **empty / loading / error / success** variant designed? A
   surface with only the populated/happy variant is incomplete.
2. **Dead-end & exit / user control** (Nielsen H3 — user control & freedom). Does
   every surface offer a way **forward / back / out**? Are destructive actions
   **reversible (undo)** or confirm-gated? Any **dead-end** is a finding.
3. **Navigation reachability & entry** (Nielsen H2/H6/H7). Is **every screen
   reachable** (no orphans)? Are all **entry points** (deep link, notification, cold
   start, resume) enumerated?
4. **Error prevention & recovery** (Nielsen H5/H9). Are **error** screens designed,
   not just the happy path? Do irreversible actions have a **confirm**? Is there a
   recovery path from every error state?
5. **Modality fit & accessibility** (Nielsen H4/H8). Are render variants for the
   target modality flagged (**GUI** responsive/narrow; **TUI** narrow-terminal;
   **CLI** non-TTY-piped)? Are **a11y** (accessibility) omissions surfaced?

For each lens, ask the **omission** question — "**what surface is missing here?**" —
never invent a design the writer plausibly omitted on purpose; flag the absence.

### Conditional lens — PRINCIPLES.md (omission-framed)

When the consumer project has a `docs/product-principles-toolkit/PRINCIPLES.md`,
add a 6th conditional lens: *"what principle-entailed UI surface did the design
OMIT?"* (e.g. a principle "must work offline" → is the offline/cached render-state
designed?). **N/A no-op when no `PRINCIPLES.md` exists** — announce "principles
lens: N/A (no PRINCIPLES.md)" and skip the dispatch; never invent principles. (This
mirrors `completeness-critic`'s principles lens — omission frame; whether the design
*contradicts* a principle is the code-review conformance layer's job.)

## Consolidate the panel union

Collect the **UNION** of all lens-critics' findings, then **dedup semantically**
(the same dead-end found by two personas is one gap) and **rank** by
(severity × number-of-lenses-that-found-it). **Severity** is a 3-point scale:
**3 = blocks the user's core job** (a primary-flow screen/state never drawn);
**2 = should-add** (a secondary state/exit omitted); **1 = polish** (a11y/density
nicety). Re-seed the ranked load-bearing set into the **design view** (the working
copy of the artifacts under critique — `DESIGN.md` + `ui-flows.md` plus the gaps
found so far) for the next round; the long tail goes to blind spots, never
padded into the design.

## You MUST emit your own blind spots

This is your **load-bearing output** and a non-negotiable rule:

> You MUST output the aspects you **cannot judge** from the text artifacts into a
> `## Blind spots — needs human/field input` section, and that section MUST be
> **non-empty**. An empty Blind spots section is itself a defect — it falsely
> claims omniscience.

Things a text-only design critic cannot judge: real rendered contrast/focus order,
actual tap counts, whether copy reads naturally to the target user, brand fit. Tag
them `needs human/field input`.

**Ban the word "complete".** Never describe the output as "complete",
"comprehensive", or "all states covered" — **do not claim "complete"**. State
**"surface-coverage relative to N lenses; blind spots listed below"** instead. An
honest coverage statement, never a false completeness claim.

## Each lens is designed deletable (Bitter Lesson)

The **panel as a verification mechanism** (writer ≠ judge) is **Bitter-Lesson-proof
— keep it regardless of model strength**. But each **individual lens** is closer to
a crutch — a stronger model may derive its coverage unaided. So **each lens is
deletable**: the panel mechanics (fan-out, union, loop-until-dry) do not depend on
the specific lens set. **Re-baseline periodically** (bare-model-vs-panel) and prune
any lens the current model has subsumed.

## See also

- [`references/design-heuristics.md`](references/design-heuristics.md) — the Nielsen
  × 7-dim lens grounding (cite the heuristic per finding).
- `interaction-flows` — produces the `ui-flows.md` this skill critiques.
- `spec-toolkit:completeness-critic` — the **behavioral** completeness critic, one
  stage later; same panel pattern, different (deeper) artifact.
- `product-principles-toolkit:product-principles` — produces the governing
  `PRINCIPLES.md` the conditional lens reads.
