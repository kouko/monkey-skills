---
name: spec-expansion
description: |
  Turn a sparse seed (a few lines of feature intent) into a high-recall spec draft — fan out objects, states, paths, edge cases → acceptance criteria in OpenSpec shape. Use for requirement fan-out / edge-case coverage before implementation.
version: 0.2.1
---

# spec-expansion

Turn a **sparse seed** into a **high-recall spec draft**. The job: when a
coding task starts from a few lines of intent, the agent silently picks its
own definition of "done" and builds happy-path-only slop. This skill
systematically expands the seed across objects / states / paths / edge cases
so the right *and* complete thing gets specified on the first pass — then
hands the result to `loom-code`'s VERIFY layer.

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
   (loom-code's gate), not by a spec that looks finished.

**Guardrail — ban the word "complete".** Never describe the output as
"complete", "comprehensive", "exhaustive", or "all cases covered". State
**"coverage relative to seed + N lenses"** instead — e.g. "coverage relative
to seed + 6 lenses; blind spots listed below". This is baseline Rule 12
(fail loud) applied to spec recall: an honest coverage statement, never a
false completeness claim.

## Consuming a `ui-flows.md` seed (DESIGN→spec seam)

When the seed is a `ui-flows.md` produced by `loom-interface-design:interaction-flows`
(rather than a few raw lines of intent), the interface **surface** is already specified —
the inventory, user flows, entry/exit points and density flags. Do **not** re-derive or
re-express that surface here; that is the design station's output, and copying it in
creates a second source of truth that drifts.

Instead, **point-don't-copy**: in the proposal, **link back** to the named `ui-flows.md`
sections and fan out only the **NET-NEW behavior** the surface implies — object state
machines, transition guard rules, edge cases, and `#### Scenario:` acceptance blocks. The
surface is the input; the behavioral depth is what this skill adds.

Map the seed's sections to the phases below (this table is the canonical seam mapping —
`interaction-flows` points here rather than copying it):

| `ui-flows.md` section | feeds |
|---|---|
| §inventory + render-variant flags | Phase ② OOUX object / state model |
| §User flows + §Entry + §Exit | Phase ③c `## Journey navigation` |
| §Transitions (character) | guard-rule lenses (Phase ③ matrix pruning) |
| interaction-dense surface (density flag) | `## Cross-object combinations` |

The seed-adequacy pre-flight (Phase ①) still applies — a `ui-flows.md` is a *rich* seed,
but if it leaves a core object's lifecycle unstated, surface that gap rather than inventing
it. If no `ui-flows.md` exists, ignore this section and treat the input as a generic seed.

## Consuming the persisted intent layer as prior-state

When the capability you are spec-ing **already has a persisted intent layer** (the
durable `docs/loom/spec/` root this skill authors — see *Authoring the persistent
intent layer* below), read it as **prior-state** so this cycle extends the last one
rather than re-deriving it from scratch. This closes the spec→spec loop: loom-spec
reads its own persisted output as the seed-context for the next change.

**Point-don't-copy.** REFERENCE the persisted files by path and **link back** to the
named sections — **NEVER copy their content** into the change-folder. A copy is a
second source of truth that drifts from the layer it duplicates; the persisted layer
stays the single source, and the change-folder points at it. This read path is
**READ-ONLY** — it never authors or edits the persisted layer (that is the *Authoring
the persistent intent layer* section's job).

Map each persisted prior-state to the phase it feeds (read each WHEN PRESENT):

| persisted prior-state | feeds |
|---|---|
| MID `docs/loom/spec/<capability>/README.md` (intent / why / scope) | Phase ① seed-adequacy + USM backbone |
| TOP `docs/loom/spec/MODEL.md` `## Object state machines` | Phase ② OOUX object/state model (extend, don't redefine) |
| TOP `MODEL.md` `## Invariants` | Phase ③ matrix guard-rule lenses |
| TOP `MODEL.md` `## Out of scope` | Phase ③ pruning (don't fan deliberately-excluded paths) |
| the generated INDEX (capability→req→test), when present | the fan boundary — fan NET-NEW only (#406 semantics) |

**The empty base case — prior-state intake is ADDITIVE and may be empty.** A net-new
capability (or a repo mid-adoption with no layer or index yet) reads whatever exists,
possibly nothing. An empty or absent layer is **never authoritative** — there is no
cold-start deadlock: if no persisted layer exists, ignore this section and treat the
input as a generic seed. The INDEX in particular lives at a later (capstone) repo
location, so reference it **when present**; its absence is covered by this base case.

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

**Also build the backbone as a navigation graph.** Beyond the left-to-right
happy-path spine, model the journey as a **navigation graph**: nodes = stages,
edges typed `{forward, back, skip, abandon, resume_reenter, error_escape,
retry_self}`. The spine captures only `forward`; the typed edges capture how a
real user moves *between* stages (goes back, skips ahead, abandons and resumes,
escapes on error, retries in place). This graph is the input Phase ③c walks.

**Single-surface collapse.** For a **single-surface / utility / floating app
with no sequential journey** (e.g. a persistent edit-and-preview note pane —
where the mode is a place you stay, not a stage you pass through), the USM
backbone may legitimately **collapse to ~1 stage node**. In that case the
**navigation graph (Phase ③c) carries the structure** — the modal escapes,
back / abandon / resume edges — and the linear spine does not. Do **not**
force a multi-stage spine where none exists; forcing one manufactures fiction
(the seed-adequacy honesty rail above). A single-node backbone with a rich
navigation graph is a legitimate, honest output shape, not a degenerate one.

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
subagents (one per object), per `loom-code:dispatching-parallel-agents`,
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

**Phase ③b — cross-object combinations.**
Announce `— Phase ③b cross-object combinations —`.
For each flow-stage, identify the **co-active objects** on that stage (the
objects simultaneously live), enumerate their **joint state combinations**,
and specify the **reaction each combination requires** (what the system must
do when those objects sit in that joint state — and especially where the
joint reaction is *not* just the union of the per-object reactions).

**Gate it on interaction-density.** Run ③b on a stage **only when** that
stage's required reaction depends on the **joint state** of ≥2 objects —
i.e. some object-pair's joint reaction ≠ the union of their individual
reactions (`interaction-density`). Otherwise **skip ③b for that stage** and
let the per-object grid (Phase ③) + the completeness-critic handle it; the
critic out-recalls joint enumeration on separable single-object-failure
stages and prunes its junk, so do not enumerate combinations where the
reaction is just the union of individual reactions.

**Wide stages (≥4 co-active objects).** On a ≥4-object stage you
**MUST run `../../scripts/pairwise.py`** (path relative to this skill's directory — the script ships at the plugin root's `scripts/`) — and **MUST NOT enumerate** a wide
stage's combinations **inline** by reasoning. Inline reasoning-based
enumeration on wide stages is the A/B-validated **leak** (the exhaustive grid
catches gold that pure-prompt enumeration misses, `missed_by_both` up to 11);
the tool exists precisely to prevent it, so reasoning the grid in your head is
never an acceptable substitute. Pipe `{"params": {"<Object>": ["<state>",
...], ...}}` to its stdin and it returns a **pairwise-covering** set of
combinations — and you **MUST show the invocation** (the actual command /
stdin payload) in the output trace so the tool-use is auditable. For
≤3-object stages, full in-prompt enumeration of the joint grid suffices (the
ban is wide-stage-only).
Residue a pairwise set cannot guarantee (gold reachable only via a
higher-order combination) is **blind-spotted, never padded** — carry the
honesty rail: an honest "pairwise-covered + listed residue" beats a fabricated
full grid.

**Phase ③c — journey-navigation coverage.**
Announce `— Phase ③c journey navigation —`.
Apply **0-switch state-transition coverage** to the navigation
graph from Phase ①: **walk every navigation edge exactly once** and, for each
legal transition, specify the **reaction it requires** (what the system must do
when the user takes that edge — restore which state, land on which step, warn,
re-validate, etc.). 0-switch means single-edge coverage: each typed edge
(`forward / back / skip / abandon / resume_reenter / error_escape /
retry_self`) is exercised once, not every edge-pair sequence. Apply this
**broadly to any flow with ≥2 stages** — it is **not** gated behind a lens
trigger; a multi-stage journey always has navigation edges worth specifying.
The completeness-critic remains the **deep complement** for nuanced
resume / re-entry landing-point decisions (exactly *where* to land, *what* to
restore) — L3 systematic coverage gets breadth across every edge, the critic
gets those deep per-case judgments.

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
OpenSpec CLI dependency). Default `<output-dir>` = `docs/loom/<change-id>/` in
the consumer project (the loom suite's shared artifact home, alongside
`PRINCIPLES.md` / `DESIGN.md` / `specs/` / `plans/`), unless the user names
another location:

```
<output-dir>/                      # default: docs/loom/<change-id>/
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
GREEN condition for `loom-code:writing-plans`. Keep RFC-2119 keywords
(MUST / SHALL / SHOULD / MAY) on the requirement body line, and keep the
delta free of loom-spec-specific sections.

### proposal.md — additive richness

loom-spec's differentiating richness goes in `proposal.md` additive
sections (OpenSpec's structure-only validate tolerates extra sections, so the
delta stays pure while the richness lives here). `proposal.md` carries
**seven visible sections** — the five per-phase artifacts plus provenance and
blind spots:

- `## USM backbone` — Phase ① artifact: the ordered journey-step spine.
- `## OOUX object model` — Phase ② artifact: the object inventory + each
  object's state machine.
- `## Path × edge matrix` — Phase ③ artifact: the grid plus which
  `backbone × object × CTA × state` paths and edges survive post-prune.
- `## Cross-object combinations` — Phase ③b artifact: per interaction-dense
  stage, the joint state combinations of its co-active objects and the
  reaction each requires (wide stages reduced via `../../scripts/pairwise.py`).
  **Structurally required — always emitted**; when no stage is
  interaction-dense, its body states that honestly (e.g. "no
  interaction-dense stage — combinations N/A") and does **not** pad.
- `## Journey navigation` — Phase ③c artifact: the 0-switch walk of the
  navigation graph — every legal typed transition (`forward / back / skip /
  abandon / resume_reenter / error_escape / retry_self`) and the reaction it
  requires. **Structurally required — always emitted**; for a single-stage
  flow the body says so (no inter-stage edges to specify).
- `## Provenance` — every item tagged seeded / inferred / critic-found.
- `## Blind spots — needs human/field input` — left present and **non-empty**
  (the completeness-critic fills it; it is the critic's load-bearing output —
  aspects no generator can manufacture, e.g. business-domain reality that
  needs human/field input). Never delete this section; never claim it is
  empty because the spec is "complete".

Validate the emitted directory with
`../../scripts/validate_spec_output.py <output-dir>` (relative to this skill's
directory) before handoff.

## Authoring the persistent intent layer

The hybrid output above is the **per-change** artifact (a `docs/loom/<change-id>/`
folder, consumed once by VERIFY then frozen). The **persistent intent layer** is
the durable spec root that outlives any single change — the cross-cutting model
and per-capability intent that tests cannot encode. It lives in **two altitudes**:

- **TOP** — `docs/loom/spec/MODEL.md`: the cross-cutting model that spans
  capabilities (system-wide invariants, object lifecycles, the global scope
  boundary).
- **MID** — `docs/loom/spec/<capability>/README.md`: one per capability,
  carrying that capability's intent / why / scope.

**TOP `MODEL.md` carries exactly these three canonical sections** (the header
text is load-bearing — `../../scripts/validate_intent_layer.py` enforces it
via `_TOP_SECTIONS`, so match it verbatim):

```
## Invariants
## Object state machines
## Out of scope
```

`## Invariants` are the rules that must always hold across capabilities;
`## Object state machines` are the cross-cutting object lifecycles; `## Out of
scope` is the global boundary of what the system deliberately does not do.

**MID `README.md`** carries the capability's **intent / why / scope** — the
reason this capability exists and what it is responsible for, not how any one
flow behaves.

**Cut rule #4 — TOP vs MID placement.**
Ask: *"remove this capability — does this content get deleted?"*
- **YES** → it belongs in the capability's **MID** `README.md`.
- **NO** (it survives the capability's removal because it spans others) → it
  belongs in **TOP** `MODEL.md`.

**Anti-pattern — MID must NOT restate behavior a test owns.** A MID `README.md`
that re-describes step-by-step what a flow does duplicates what the `####
Scenario:` acceptance tests already own — the residual-rot surface: the prose
and the tests drift apart, and the prose silently goes stale. Keep MID at the
intent/why/scope altitude; let the tests be the single source of truth for
behavior. This discipline is **human-reviewed, NOT a CI gate** — no script
detects restated behavior, so a reviewer must hold the line at authoring time.

### Requirement status — `[active|deferred]`

Each `### Requirement:` carries an **intent-status** that says whether the
requirement is meant to be verified now or is aspirational. Declare it as a
suffix on the heading:

```
### Requirement: REQ-X [deferred]
### Requirement: REQ-X [active]
### Requirement: REQ-X            ← no suffix ≡ active (the default)
```

- **`active`** is the **DEFAULT** and may be omitted — `### Requirement: REQ-X`
  is exactly equivalent to `### Requirement: REQ-X [active]`.
- Only `active` and `deferred` are valid. Any other suffix (e.g. `[activ]`,
  `[future]`) is a **malformed declaration** that **FAILs the every-push
  structural lane** of the drift gate — it needs no index and is RED-phase-safe,
  so it is enforced on every push, PR and main alike.

**Canonical vs inspirational (Tessl framing).** A requirement's status maps onto
Tessl's spec-authority distinction — tests are what turn an *inspirational* spec
into a *canonical* one:

- a **verified `active`** requirement (has passing tests bound via `@req`) =
  **canonical** — authority from test-binding;
- a **`deferred` or unverified** requirement = **inspirational** — intent stated,
  not yet test-bound.

**Merge-boundary gate behavior.** The `active`-coverage check is a
**post-finishing, pre-merge required PR check** (it needs `@req` resolution +
test results, so it is merge-pinned, not run on req emission and not mid-RED):

- **`active` + 0 passing tests = FAIL** — blocks the merge. By the merge boundary
  the TDD RED must have gone GREEN; this is **not** failed mid-RED, where a
  freshly-specced `active` req legitimately has 0 tests (failing it then would
  invert the iron law).
- **`deferred` + 0 tests = surfaced** — shown in the index as *inspirational*,
  **never** a FAIL.

## Boundary — stops at GENERATE

This skill **stops at GENERATE**. It does **not** run TDD, write production
code, or review code — that is `loom-code`'s VERIFY layer. The output
(the OpenSpec change-folder) is the one-directional handoff: loom-spec
*writes* it, `loom-code:writing-plans` *reads* the `#### Scenario:`
criteria and turns them into RED/GREEN tasks, and loom-code's execution
gate is the final truth. The completeness-critic (a sibling skill) critiques
this spec draft for omissions before handoff — it too never touches code.
