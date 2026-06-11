---
name: spec-expansion
description: Turn a sparse seed (a few lines of feature intent) into a high-recall spec draft — systematically fan out objects, states, paths and edge cases, then emit candidate acceptance criteria in OpenSpec change-folder shape. Use for spec-expansion / requirement fan-out / edge-case coverage when starting a non-trivial coding task from a sparse idea and you want the paths, states and edge cases named BEFORE implementation instead of discovered late by review. 規格擴展・需求展開・邊界案例覆蓋。仕様展開・要件ファンアウト・エッジケース網羅。
version: 0.1.0
---

# spec-expansion

Turn a **sparse seed** into a **high-recall spec draft**. The job: when a
coding task starts from a few lines of intent, the agent silently picks its
own definition of "done" and builds happy-path-only slop. This skill
systematically expands the seed across objects / states / paths / edge cases
so the right *and* complete thing gets specified on the first pass — then
hands the result to `code-toolkit`'s VERIFY layer.

This is the **GENERATE** layer of the GENERATE → DECLARE → VERIFY pipeline.
It produces a spec draft; it does **not** run TDD, write code, or review code
(see Boundary below).

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply the LLM
reasoning (object extraction, OOUX fan-out, lens pruning, scenario drafting)
and the parallel fan-out. There is no external runtime, no API key, no
program to install — the method rides on the host agent you are already in.

## Honesty rails — read before you start

The engine **auto-expands (strong) but cannot auto-complete (a theoretical
floor)**. Three hard boundaries govern every claim you make:

1. **The seed sets the ceiling.** Completeness is relative to all external
   knowledge; a sparse seed + LLM priors are not a complete source. The
   completeness-critic re-seeding raises the ceiling *locally* but cannot
   break it.
2. **Combinatorial ≠ aspectual completeness — and the grid over-generates.**
   The `object × CTA × state` grid enumerates *internal* combinations but
   produces illegal cells while missing system-layer / NFR *aspects*. You
   MUST prune (legality + priority) and rely on the critic to add aspects the
   grid cannot reach.
3. **False completeness is the most dangerous failure.** A filled grid
   *looks* thorough → false confidence. Trust is earned by execution
   (code-toolkit's gate), not by a spec that looks finished.

**Guardrail — ban the word "complete".** Never describe the output as
"complete", "comprehensive", "exhaustive", or "all cases covered". State
**"coverage relative to seed + N lenses"** instead — e.g. "coverage relative
to seed + 6 lenses; blind spots listed below". This is baseline Rule 12
(fail loud) applied to spec recall: an honest coverage statement, never a
false completeness claim.

## The three phases

Run **three explicit phases in order**. Each phase (a) **announces itself**
as it runs — print the exact marker line so the execution trace is visible —
and (b) **emits a visible intermediate artifact** (a named `##` section in
`proposal.md`) before the next phase starts. Provenance is tagged at every
step. Do not collapse the phases into one silent pass: the visibility *is*
the contract — a reader watching the run sees backbone → object model →
matrix appear in order, and can audit each before the spec is emitted.

### Phase ① USM — lay the user-journey backbone

**Announce:** print `— Phase ① USM backbone —` before you start.

**Seed-adequacy pre-flight (gate) — run this BEFORE you fan out.** A sparse
seed sets the ceiling (honesty rail #1); fanning out a too-sparse seed
**manufactures fiction** that *looks* like recall but is invented intent. So
before extracting actors/objects, check the seed against two tripwires:

- **fewer than a couple of distinct actors *or* objects** can be named from
  the seed, **or**
- **the core object's lifecycle (its states / what can happen to it) is
  unstated.**

If either tripwire fires, **stop and surface what's missing — ask the user
(or flag it explicitly as a blind spot) BEFORE expanding.** Name the specific
gap ("seed names 1 object and no lifecycle — need the X states / the second
actor"). Do **not** silently invent the missing actors, objects, or
lifecycle to make the grid look full — that is the manufacture-fiction
failure this gate exists to stop. Only once the seed clears the pre-flight
(or the user fills the gap) do you proceed to extraction.

Lay the **USM backbone**: the happy-path **spine** of ordered user steps (the
left-to-right user-journey of who does what, in sequence). Extraction folds
in here — from the seed, identify the **actors**, their **journey**, the
**objects** (the nouns the system manipulates) and the **CTAs**
(call-to-action verbs — what actors *do* to objects) that the journey
touches. Tag each extracted item `seeded` (straight from the seed text) or
`inferred` (you supplied it from domain priors) — the seed-ceiling boundary
in action: be explicit about what you added.

**Visible artifact:** emit a `## USM backbone` section in `proposal.md` — an
ordered list (or table) of the journey steps that form the spine.

### Phase ② OOUX — fan out the object model

**Announce:** print `— Phase ② OOUX object model —` before you start.

For **each object** the journey touches, fan out **ORCA** — its:
- **Objects** — confirm the object as a first-class noun,
- **Relationships** — links to other objects,
- **CTAs** — the actions performed on it,
- **Attributes** — the data it carries,

and model the object's **states as a state machine** (the legal states and
the transitions between them).

Dispatch this per-object work as **multi-agent fan-out**: dispatch N
subagents (one per object), per `code-toolkit:dispatching-parallel-agents`,
in a single message so the host runs them concurrently. Describe the fan-out
abstractly ("dispatch N subagents") — do not hard-code one host's workflow
primitive, so the skill stays agent-portable. Each per-object expansion is
independent (disjoint objects, no shared state), which is exactly the case
the fan-out convention is for.

**Visible artifact:** emit a `## OOUX object model` section in `proposal.md` —
the object inventory plus, for each object, its state machine (states +
legal transitions).

### Phase ③ 自動拓展矩陣 (auto-expansion matrix) — grid, prune, emit

**Announce:** print `— Phase ③ auto-expansion matrix —` before you start.

**Build the grid (cartesian, mechanical).** Take the cartesian product
`backbone × object × CTA × state`. Each cell is a candidate path/edge. This
is mechanical and deliberately over-generates — pruning happens next.

**Prune through the lens layer.** Walk the grid through fixed **lenses**,
dropping illegal cells and surfacing aspects the cartesian grid cannot see.
Each lens below teaches **when it dominates** and a **keep / flag / drop**
discriminator — apply the discriminator cell-by-cell; the lens layer is the
engine of the high-recall claim, so judge each cell, don't just enumerate:

- **state-transition legality** — *dominates when* the object has a rich
  lifecycle. **KEEP** every legal transition as a path; **FLAG** each illegal
  transition (e.g. `refund → ship`) as an edge case; **DROP** impossible
  cells (e.g. ship before pay).
- **BVA** (boundary-value analysis) — *dominates when* a CTA takes numeric /
  sized / dated input. **KEEP** min / max / off-by-one / empty as distinct
  paths; **FLAG** the just-past-boundary case as the bug-prone edge; **DROP**
  redundant interior values (one nominal mid-range value suffices — extra
  ones are noise).
- **CRUD** — *dominates when* an object is persisted. **KEEP** each
  create / read / update / delete the actors actually perform; **FLAG** a
  missing leg (e.g. no delete path) as a coverage gap; **DROP** CRUD legs the
  object's lifecycle forbids (e.g. update on an immutable record).
- **permissions** — *dominates when* more than one actor role exists. **KEEP**
  the authorized actor × CTA cell **and** the unauthorized-actor-denied path;
  **FLAG** any CTA whose authorization is unstated; **DROP** role × CTA cells
  the role can never reach.
- **empty / error / loading** states — *dominates when* the CTA crosses a
  network / async / collection boundary. **KEEP** empty, error, and loading
  as explicit states happy-path specs skip; **FLAG** any path with no defined
  error state; **DROP** the loading state for a purely synchronous local CTA
  (noise).
- **NFR checklist** — *dominates when* the system has scale / security /
  concurrency / timing obligations OOUX alone cannot reach. **KEEP** the
  performance / security / concurrency / network-failure / timing aspect that
  binds a real obligation; **FLAG** an NFR the seed implies but never
  quantifies (needs human input); **DROP** speculative NFRs no requirement
  asks for (gold-plating noise).

**Sparse-output fallback.** If, after pruning, **no high-priority surviving
paths** remain, **report that honestly** — say so plainly and point back to
the seed-adequacy pre-flight — **do not pad** the matrix with low-value or
invented cells to make it look fuller. An honest near-empty matrix beats
padding (Rule 12, fail loud).

**Visible artifact:** emit a `## Path × edge matrix` section in `proposal.md`
— the grid plus the surviving paths/edges that remain post-prune.

**Emit (hybrid output format).** Emit the surviving paths/edges as the hybrid
output format below. Every emitted item carries a provenance tag. Close with
a coverage statement ("coverage relative to seed + N lenses") — never a
completeness claim.

## Provenance tagging

**Every emitted item MUST be tagged with one of three provenance values:**

- `seeded` — stated in or directly entailed by the seed.
- `inferred` — you derived it from OOUX/USM/lens priors (not in the seed).
- `critic-found` — surfaced by the completeness-critic's loop (re-seeded
  back into the spec on a later pass).

Provenance makes the seed-ceiling boundary auditable: a reader can see how
much of the spec is real intent vs model inference vs critic recovery.

## The hybrid output format

Emit a **directory in OpenSpec change-folder shape** (plain markdown — no
OpenSpec CLI dependency):

```
<output-dir>/
  proposal.md                      # additive richness lives here
  specs/<capability>/spec.md       # OpenSpec-pure delta (validate-clean)
```

### specs/ delta — OpenSpec-pure skeleton

The `specs/` delta is the **load-bearing contract joint** to VERIFY and stays
**OpenSpec-pure** (structure-only `openspec validate`-clean — zero migration
when the OpenSpec CLI wires in). Use the skeleton exactly:

```
## ADDED Requirements

### Requirement: <name>
The system MUST <normative obligation>.   <!-- RFC-2119 keyword on the body line -->

#### Scenario: <name>
- GIVEN <precondition>
- WHEN <action>
- THEN <expected outcome>
```

Each `#### Scenario:` is one testable acceptance criterion → one RED test /
GREEN condition for `code-toolkit:writing-plans`. Keep RFC-2119 keywords
(MUST / SHALL / SHOULD / MAY) on the requirement body line, and keep the
delta free of spec-toolkit-specific sections.

### proposal.md — additive richness

spec-toolkit's differentiating richness goes in `proposal.md` additive
sections (OpenSpec's structure-only validate tolerates extra sections, so the
delta stays pure while the richness lives here). `proposal.md` carries
**five visible sections** — the three per-phase artifacts plus provenance and
blind spots:

- `## USM backbone` — Phase ① artifact: the ordered journey-step spine.
- `## OOUX object model` — Phase ② artifact: the object inventory + each
  object's state machine.
- `## Path × edge matrix` — Phase ③ artifact: the grid plus which
  `backbone × object × CTA × state` paths and edges survive post-prune.
- `## Provenance` — every item tagged seeded / inferred / critic-found.
- `## Blind spots — needs human/field input` — left present and **non-empty**
  (the completeness-critic fills it; it is the critic's load-bearing output —
  aspects no generator can manufacture, e.g. business-domain reality that
  needs human/field input). Never delete this section; never claim it is
  empty because the spec is "complete".

Validate the emitted directory with
`spec-toolkit/scripts/validate_spec_output.py <output-dir>` before handoff.

## Boundary — stops at GENERATE

This skill **stops at GENERATE**. It does **not** run TDD, write production
code, or review code — that is `code-toolkit`'s VERIFY layer. The output
(the OpenSpec change-folder) is the one-directional handoff: spec-toolkit
*writes* it, `code-toolkit:writing-plans` *reads* the `#### Scenario:`
criteria and turns them into RED/GREEN tasks, and code-toolkit's execution
gate is the final truth. The completeness-critic (a sibling skill) critiques
this spec draft for omissions before handoff — it too never touches code.
