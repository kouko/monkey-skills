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

## The 5-stage pipeline

Run these stages in order. Stages ② and ③ are the mechanical sweet spot;
stage ④ is the prune; stages emit provenance at every step.

### ① Extract objects + CTAs (extraction)

From the seed, extract the **objects** (the nouns the system manipulates) and
the **CTAs** (call-to-action verbs — what actors *do* to objects). Tag each
extracted item `seeded` (came straight from the seed text) or `inferred`
(you supplied it from domain priors). This is the seed-ceiling boundary in
action: be explicit about what you added.

### ② OOUX fan-out — per object (LLM prior, the sweet spot)

For **each object**, fan out its:
- **attributes** — the data it carries,
- **states** — model these as a small **state machine** (the legal states
  and the transitions between them),
- **relationships** — to other objects,
- **CTAs** — the actions performed on it.

Dispatch this per-object work as **multi-agent fan-out**: dispatch N
subagents (one per object), per `code-toolkit:dispatching-parallel-agents`,
in a single message so the host runs them concurrently. Describe the fan-out
abstractly ("dispatch N subagents") — do not hard-code one host's workflow
primitive, so the skill stays agent-portable. Each per-object expansion is
independent (disjoint objects, no shared state), which is exactly the case
the fan-out convention is for.

### ③ Build the backbone × object × CTA × state grid (cartesian, mechanical)

Lay out the USM **backbone** (the left-to-right user-journey spine) and take
the cartesian product `backbone × object × CTA × state`. Each cell is a
candidate path/edge. This is mechanical and deliberately over-generates —
pruning happens next.

### ④ Lens layer — prune + add aspects

Walk the grid through fixed **lenses**, dropping illegal cells and surfacing
aspects the cartesian grid cannot see:

- **state-transition legality** — keep every legal transition (= "all
  paths"); flag invalid transitions as edge cases; drop impossible cells.
- **BVA** (boundary-value analysis) — data edges (min / max / off-by-one /
  empty).
- **CRUD** — create / read / update / delete completeness per object.
- **permissions** — who may perform each CTA; unauthorized-actor paths.
- **empty / error / loading** states — the UI/runtime states happy-path
  specs skip.
- **NFR checklist** — performance / security / concurrency / network-failure
  / timing aspects (system-layer failures OOUX alone cannot reach).

### ⑤ Emit (hybrid output format)

Emit the surviving paths/edges as the hybrid output format below. Every
emitted item carries a provenance tag. Close with a coverage statement
("coverage relative to seed + N lenses") — never a completeness claim.

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
delta stays pure while the richness lives here):

- `## Provenance` — every item tagged seeded / inferred / critic-found.
- `## Path × edge matrix` — the grid appendix: which `object × CTA × state`
  paths and edges are covered, post-prune.
- `## Blind spots — needs human/field input` — left present (the
  completeness-critic fills it; it is the critic's load-bearing output —
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
