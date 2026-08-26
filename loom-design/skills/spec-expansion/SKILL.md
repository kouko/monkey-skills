---
name: spec-expansion
description: |
  Turn a sparse seed (a few lines of feature intent) into a high-recall spec draft — fan out objects, states, paths, edge cases → acceptance criteria in OpenSpec shape. Use for requirement fan-out / edge-case coverage before implementation.
version: 0.3.0
---

# spec-expansion

Turn a **sparse seed** into a **high-recall spec draft** by expanding objects,
states, paths, and edge cases before handing the result to `loom-code` VERIFY.
Its output must remain inspectable, attributable, and directly usable by the
downstream planning and verification stations.

This is the **GENERATE** layer of the GENERATE → DECLARE → VERIFY pipeline.
It produces a spec draft; it does **not** run TDD, write code, or review code
(see Boundary below).

## Honesty rails — read before you start

The engine **auto-expands (strong) but cannot auto-complete (a theoretical
floor)**. Three hard boundaries govern every claim you make:

1. **The seed sets the ceiling.** LLM priors and critic re-seeding cannot turn
   missing external knowledge into fact.
2. **The grid over-generates yet misses aspects.** Prune illegal/noisy cells;
   use the critic for system and NFR aspects the grid cannot reach.
3. **A filled grid is not proof.** Execution, not apparent thoroughness,
   earns trust.

**Ban the word "complete".** Never claim complete/comprehensive/exhaustive
coverage. Say **"coverage relative to seed + N lenses"** and list blind spots.

## Governing constraint — PRINCIPLES.md first (constitution→spec seam)

Before expanding, read `docs/loom/PRINCIPLES.md` when present. It governs
fan-out scope, Phase ③ pruning priorities, and NFR posture; the critic's later
principles lens is not a substitute.

If `PRINCIPLES.md` is absent, surface that the spec is ungoverned. Ask for
`loom-design:product-principles`, or proceed only with an explicit
`no PRINCIPLES — spec is unconstrained` caveat in the proposal. This intake
is read-only.

## Consuming a `ui-flows.md` seed (DESIGN→spec seam)

When the seed is `docs/loom/<change-id>/ui-flows.md`, emit into that same
change folder. Point-don't-copy: link its named sections and add only net-new
state machines, transition guards, edge cases, and scenarios. Read
[`references/execution-details.md`](references/execution-details.md)
§`ui-flows.md` seed for the phase mapping and rich-seed edge case.

The surface inventory, user flows, entry/exit points, and density flags are
already design-owned facts. Re-expressing them here would create a second
source of truth. The spec station instead deepens their behavioral meaning:
inventory and render variants feed the object/state model; flow entry and
exit feed journey navigation; transition character constrains legal guards;
interaction-density decides whether cross-object enumeration runs. A rich
seed still fails the pre-flight if a core object's lifecycle is unstated.

**Validate before fan-out.** Before consuming a `ui-flows.md` seed from a change-folder,
run loom-design's own `mint_critic_verdict.py` to confirm `design-critic`
reviewed this exact content. Run this direct argv from the consumer project root;
`${CLAUDE_PLUGIN_ROOT}` is the absolute installed **PLUGIN repo** root. Keep values
separate; pass it directly to process execution; never through a shell—never pass the command through a shell:

```
argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/spec/mint_critic_verdict.py", "validate", "--change-folder", "<design-change-folder>", "--critic", "design-critic", "--files", "DESIGN.md,ui-flows.md"]
```

Proceed only on exit 0. Otherwise **STOP** and route by the distinct failure:

- **exit 2** — no verdict file: `design-critic` never ran on this change-folder. Route to
  `loom-design:design-critic` before fanning out.
- **exit 3** — fresh verdict is `NEEDS_REVISION`: the critic blocked this draft. Route back
  to the design writer (`loom-design:interaction-flows`) to address the findings.
- **exit 4** — files differ from the minted set, are stale/edited, or became
  unreadable. Re-run design-critic on current content.

## Consuming the persisted intent layer as prior-state

When the capability already has a persisted intent layer, read
[`references/intent-layer.md`](references/intent-layer.md) §Consuming
before Phase ①. This is read-only and point-don't-copy; fan net-new only where
an INDEX exists. An empty layer is not authoritative.
If absent, treat input as a generic seed.

## The three phases

Run three phases in order. Announce each in the conversation language (never
print internal phase markers), emit its named `proposal.md` section before
continuing, and tag provenance throughout.

Do not collapse the phases into one silent drafting pass. The ordered
artifacts are review checkpoints: the backbone constrains which objects are
in scope; the object model defines legal states and transitions; only then
may the matrix form and prune candidate paths. Finish and expose each section
before using it as input to the next phase so a reader can audit where an
inference entered. Announcements describe the user-visible work in plain
language; phase identifiers belong in the artifact, not as chat jargon.

### Phase ① USM — lay the user-journey backbone

**Announce:** say in the conversation language, e.g. "next I'll lay the user-journey backbone".

**Seed-adequacy pre-flight (gate) — run this BEFORE you fan out.** A sparse
seed sets the ceiling (honesty rail #1); fanning out a too-sparse seed
**manufactures fiction** that *looks* like recall but is invented intent. So
before extracting actors/objects, check the seed against two tripwires:

- **fewer than a couple of distinct actors *or* objects** can be named from
  the seed, **or**
- **the core object's lifecycle (its states / what can happen to it) is
  unstated.**

If either fires, stop before fan-out, name the gap, and ask the user or flag a
blind spot. Do not manufacture fiction by inventing actors, objects, or a
lifecycle. Proceed only after the gate clears.

The gate tests whether expansion has enough declared intent to transform,
not whether the model can imagine plausible domain details. A seed naming
one object but no lifecycle must identify the missing states; one with no
second actor/object must identify that missing perspective. If the user
chooses to proceed with the gap, preserve it as an explicit blind spot rather
than silently treating inference as intent.

Lay the ordered happy-path **USM backbone**. Extract actors, journey, objects,
and CTAs; tag each `seeded` or `inferred`.

Also build a navigation graph (stage nodes, typed edges) for Phase ③c. For a
single-surface utility, the backbone may **collapse** to one node while the
navigation graph carries the structure. Read
[`references/execution-details.md`](references/execution-details.md)
§Phase ① navigation edge cases when either branch applies.

Use typed edges `{forward, back, skip, abandon, resume_reenter,
error_escape, retry_self}`. The spine captures the expected forward journey;
the graph records how real users leave, reverse, recover, and return. Do not
force a multi-stage spine onto a persistent utility surface merely to make
the artifact look substantial.

**Visible artifact:** emit a `## USM backbone` section in `proposal.md` — an
ordered list (or table) of the journey steps that form the spine.

### Phase ② OOUX — fan out the object model

**Announce:** say in the conversation language, e.g. "next I'll fan out the object model".

For each object, fan out ORCA: Objects, Relationships, CTAs, and Attributes;
model legal states/transitions as a state machine.

Dispatch this per-object work under
[`references/design-panel-dispatch.md`](references/design-panel-dispatch.md):
use one worker per object concurrently, join all findings, then edit the
shared artifact. Keep dispatch host-neutral.

**Visible artifact:** `## OOUX object model`: inventory, one Mermaid
`stateDiagram-v2` per object, and one `erDiagram` for relations. Fill the
diagrams or replace the body with
`N/A — no flow/state/architecture-shaped content: <one-line reason>`.
Never omit or leave the section bare; the N/A reason must fit the content.

### Phase ③ 自動拓展矩陣 (auto-expansion matrix) — grid, prune, emit

**Announce:** say in the conversation language, e.g. "next I'll build and prune the auto-expansion matrix".

**Build the grid (cartesian, mechanical).** Take the cartesian product
`backbone × object × CTA × state`. Each cell is a candidate path/edge. This
is mechanical and deliberately over-generates — pruning happens next.

**Domain-tag triage FIRST.** Before specifying behavior not derivable from
the seed, `PRINCIPLES.md`, or `ui-flows.md`, read
[`references/domain-tag-triage.md`](references/domain-tag-triage.md) and
classify it: craft/project-local → expand; domain-convention → tagged open
question (`evidence_needed: domain-convention`), never an invented answer.

**Prune through the lens layer.** Apply these six lenses cell-by-cell; read
[`references/execution-details.md`](references/execution-details.md)
§Phase ③ lens discrimination when a decision is ambiguous.

- **state-transition legality** — dominates for rich lifecycles; KEEP legal,
  FLAG illegal attempts, DROP impossible ordering.
- **BVA** — dominates for numeric/sized/dated input; KEEP boundaries, FLAG
  just-past-boundary, DROP redundant interior values.
- **CRUD** — dominates for persisted objects; KEEP supported operations, FLAG
  a missing needed leg, DROP lifecycle-forbidden legs.
- **permissions** — dominates with multiple roles; KEEP allowed and denied
  paths, FLAG unstated authorization, DROP unreachable role/actions.
- **empty / error / loading** — dominates at async/network/collection
  boundaries; KEEP applicable states, FLAG missing errors, DROP sync noise.
- **NFR** — dominates for real scale/security/concurrency/timing obligations;
  KEEP bound obligations, FLAG unquantified implications, DROP speculation.

`KEEP` means the cell becomes a specified path, `FLAG` means it becomes a
question or explicit edge case, and `DROP` means it adds no truthful coverage.
Apply the discriminator independently for every applicable lens rather than
listing lens names beside an unpruned grid. For example, state legality can
retain an authorized transition while permissions simultaneously adds the
unauthorized-denied path; BVA can add minimum/maximum/off-by-one cases without
duplicating arbitrary mid-range values. NFRs are obligations only when the
seed or constitution binds them—otherwise they are gold-plating noise.

If no high-priority paths survive pruning, report it and point to the
seed-adequacy gate; do not pad the matrix.

**Visible artifact:** `## Path × edge matrix`, one row per survivor, columns
`Backbone step | Object | CTA | State | Lens verdict | Expected reaction`
(`Lens verdict`: keep/flag). If empty, use exactly
`N/A — no surviving path/edge: <one-line reason>` — never a padded
table.

**Phase ③b — cross-object combinations.**
**Announce:** say in the conversation language, e.g. "next I'll enumerate cross-object combinations for interaction-dense stages". For each stage, identify co-active objects, enumerate joint states, and specify reactions.

Run ③b only on `interaction-density`: some pair's joint reaction differs from
the union of individual reactions. Otherwise skip that stage.

For a qualifying stage, enumerate the joint states of all co-active objects
and name the system reaction for each combination, especially where that
reaction is not the sum of per-object reactions. On separable stages the
ordinary Phase ③ grid plus the critic provides better signal, so combination
enumeration would only manufacture volume.

On a wide stage (≥4 objects), **MUST run `argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/spec/pairwise.py"]`** and **MUST NOT enumerate** combinations inline. Pass `{"params": {"<Object>": ["<state>", ...]}}` on stdin directly, never through a shell; show argv and payload in the trace. For ≤3 objects, enumerate fully in prompt. Read [`references/execution-details.md`](references/execution-details.md) §Phase ③b combination residue and list uncovered higher-order residue as blind spots.

The tool returns a pairwise-covering set: every pair of parameter values is
represented, but higher-order interactions may remain. That residue is a
blind spot, never evidence that the generated set is exhaustive. Showing the
actual argv and stdin makes tool use auditable and prevents an agent from
substituting unaudited reasoning for the mandated wide-stage computation.

**Phase ③c — journey-navigation coverage.**
**Announce:** say in the conversation language, e.g. "next I'll walk every navigation edge for journey coverage". For every flow with ≥2 stages, apply **0-switch state-transition coverage**: walk each navigation edge once and specify its reaction. This is not lens-gated; the critic handles nuanced resume/re-entry judgments.

0-switch is single-edge coverage, not every edge-pair sequence. For each
legal edge, state what must be restored, where the user lands, whether a
warning appears, and what is revalidated. This systematic pass provides
breadth; the critic remains responsible for deeper per-case judgments such
as exact resume landing points and restoration semantics.

Emit the hybrid format below, tag every item, and close with "coverage
relative to seed + N lenses" plus blind spots.

## Provenance tagging

Every emitted item MUST use one provenance value:

- `seeded` — stated or directly entailed by the seed.
- `inferred` — derived from OOUX/USM/lens priors.
- `critic-found` — recovered by the completeness-critic loop.

Tag the smallest independently reviewable item, not merely the section that
contains it. A seeded object may have an inferred state, and a critic-found
path may contain a seeded CTA; assigning one label to the whole section would
hide that boundary. When a later critic pass adds an omission, retain
`critic-found` even after integrating it into the draft. Provenance records
where an assertion entered the specification, not how confident the writer
currently feels about it, and it never upgrades inference into user intent.

## The hybrid output format

Emit a **directory in OpenSpec change-folder shape** (plain markdown — no
OpenSpec CLI dependency). Default `<output-dir>` = `docs/loom/<change-id>/` in
the consumer project (the loom suite's shared artifact home, alongside
`PRINCIPLES.md` / `DESIGN.md` / `specs/` / `plans/`), unless the user names
another location. **When the seed is a `docs/loom/<X>/ui-flows.md`, emit into
that same folder** — `<X>` IS this change's `<change-id>`; do not mint a
second, differently-cased id (the sit-beside contract with
`loom-design` depends on the ids matching):

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

### Requirement: REQ-<n> — <name>
The system MUST <normative obligation>.   <!-- RFC-2119 keyword on the body line -->

#### Scenario: <name>
- GIVEN <precondition>
- WHEN <action>
- THEN <expected outcome>
```

The `REQ-<n> — ` id half is optional per file — an existing legacy file with
zero ids stays valid prose-only headers (`### Requirement: <name>`); adding
even one id switches that file into id-mode for the id shape, minting, and
adoption rules, see
[`references/requirement-identifiers.md`](references/requirement-identifiers.md).

Each `#### Scenario:` is one testable acceptance criterion → one RED test /
GREEN condition for `loom-code:writing-plans`. Keep RFC-2119 keywords
(MUST / SHALL / SHOULD / MAY) on the requirement body line, and keep the
delta free of loom-design-specific sections.

Requirement bodies state one normative obligation; scenarios make it
observable through GIVEN/WHEN/THEN. Do not move provenance, matrices,
diagrams, blind spots, or explanatory design prose into this delta: those
belong in `proposal.md`. This separation lets the verification station parse
acceptance criteria without treating design commentary as executable scope.

### proposal.md — additive richness

loom-design's differentiating richness goes in `proposal.md` additive
sections (OpenSpec's structure-only validate tolerates extra sections, so the
delta stays pure while the richness lives here). `proposal.md` carries
**seven visible sections** — the five per-phase artifacts plus provenance and
blind spots:

- `## USM backbone` — Phase ① artifact: the ordered journey-step spine.
- `## OOUX object model` — Phase ② artifact: the object inventory + each
  object's state machine and relations, rendered as Mermaid diagram
  blocks (fill-or-declare, pinned N/A line — see Phase ②).
- `## Path × edge matrix` — Phase ③ artifact: the grid plus which
  `backbone × object × CTA × state` paths and edges survive post-prune.
  Rendered as the markdown table Phase ③ specifies, or its pinned N/A line.
- `## Cross-object combinations` — Phase ③b artifact: per interaction-dense
  stage, the joint state combinations of its co-active objects and the
  reaction each requires (wide stages reduced via the pairwise argv contract above).
  **Structurally required — always emitted**. Rendered as a markdown
  table — one row per joint state combination, columns
  `Stage | Co-active objects | Joint state | Required reaction`.
  When no stage is interaction-dense, the body is the single line
  `N/A — no interaction-dense stage: <one-line reason>` and does **not**
  pad. The table form here is this section's own contract (an
  enumeration of joint states, not an options comparison — so it is not
  what `family-relay.md §(b)` routes; the validator enforces the
  table-or-N/A shape directly).
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

**Gate rule — before declaring the draft VERIFY-ready, check for unresolved
SHAPING-class `evidence_needed: domain-convention` tags FIRST** (see
[`references/domain-tag-triage.md`](references/domain-tag-triage.md)): any
such tag blocks VERIFY unless it carries an explicit `deferred: <reason>`
note.

This check happens after all sections exist but before validation/handoff.
Resolve the convention from evidence, or preserve the uncertainty as a
deferred item with a concrete reason; never convert an unanswered domain
question into a normative requirement. Validation proves structural shape,
not that external domain knowledge was recovered, so it cannot replace this
triage gate.

Validate the emitted directory with the validator from the installed plugin
root before handoff. Pass this argv array directly to process execution; never
through a shell: `argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/spec/validate_spec_output.py", "<output-dir>"]`.

### Language policy — layered by artifact role

The hybrid output is **layered by language role**, not uniformly
translated. The machine-precision layers are **written in English**:
the spec-delta requirement lines (RFC-2119 keywords MUST / SHALL /
SHOULD / MAY on the body line) and every `#### Scenario:` GIVEN /
WHEN / THEN criterion. The human-narrative layer — `proposal.md`'s
narrative content (the USM backbone, object model, path/edge matrix,
journey navigation, provenance, and blind-spots sections) — stays in
the session's **conversation language**.

For a zh-Hant / ja session, read the English precision layers through
the local [`adjudication-view`](references/adjudication-view.md)
display layer (BI-4): it renders the English artifact for careful
reading in the profile language without touching the machine-precise
artifact underneath.

## Authoring the persistent intent layer

The hybrid output above is the **per-change** artifact (a `docs/loom/<change-id>/`
folder, consumed once by VERIFY then frozen). The **persistent intent layer** is
the durable spec root that outlives any single change (TOP `docs/loom/spec/MODEL.md`
+ MID `docs/loom/spec/<capability>/README.md`). When authoring or extending it,
Read [`references/intent-layer.md`](references/intent-layer.md) §Authoring
**first** — it carries the TOP file's three canonical section headers
(validator-enforced **verbatim** via the plugin root's
`scripts/validate_intent_layer.py` `_TOP_SECTIONS`), the MID
intent/why/scope altitude, cut rule #4 (TOP-vs-MID placement: "remove this
capability — does this content get deleted?"), and the anti-pattern that MID
must never restate behavior a `#### Scenario:` test owns (human-reviewed
discipline, not a CI gate).

### Requirement status — `[active|deferred]`

Each `### Requirement:` carries an **intent-status** that says whether the
requirement is meant to be verified now or is aspirational. Declare it as a
suffix on the heading:

```
### Requirement: REQ-<n> — <name> [deferred]
### Requirement: REQ-<n> — <name> [active]
### Requirement: REQ-<n> — <name>            ← no suffix ≡ active (the default)
```

- **`active`** is the **DEFAULT** and may be omitted — `### Requirement: REQ-<n> — <name>`
  is exactly equivalent to the same header with `[active]` appended.
- Only `active` and `deferred` are valid. Any other suffix (e.g. `[activ]`,
  `[future]`) is a **malformed declaration** that **FAILs the every-push
  structural lane** of the drift gate — it needs no index and is RED-phase-safe,
  so it is enforced on every push, PR and main alike.
- The `REQ-<n> — ` id half follows the same optional-per-file rule as the
  skeleton above — see
  [`references/requirement-identifiers.md`](references/requirement-identifiers.md)
  for the id shape and adoption rules; this section only adds the status
  suffix.

Status maps onto spec **authority** — a verified `active` requirement is
*canonical* (test-bound), a `deferred`/unverified one is *inspirational* —
and the `active`-coverage check is a merge-pinned PR gate, not a mid-RED
one: full semantics in
[`references/intent-layer.md`](references/intent-layer.md) §Requirement
status.

## Boundary — stops at GENERATE

This skill **stops at GENERATE**. It does **not** run TDD, write production
code, or review code — that is `loom-code`'s VERIFY layer. The output
(the OpenSpec change-folder) is the one-directional handoff: loom-design
*writes* it, `loom-code:writing-plans` *reads* the `#### Scenario:`
criteria and turns them into RED/GREEN tasks, and loom-code's execution
gate is the final truth. The completeness-critic (a sibling skill) critiques
this spec draft for omissions before handoff — it too never touches code.
