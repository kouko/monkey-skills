---
name: design-system
description: |
  Generate a product's visual design system — colors, typography, layout, component tokens — per PRINCIPLES.md. GUI → DESIGN.md (YAML tokens + prose); TUI/CLI → conventions stub. Use BEFORE spec/build to define the look. Flows → interaction-flows.
version: 0.3.0
---

# design-system

Generate the product's **visual design system**: brand voice, palette, type,
spacing, elevation, shapes, and component-token defaults, governed by its
constitution.

It is **modality-aware**: **GUI** gets full visual tokens; **TUI** gets terminal
palette/panel conventions; **CLI** gets output and command/flag conventions.
TUI / CLI currently emit a lightweight stub plus a phase-2 note.

**Ending gate — before you end ANY run of this skill → confirm the artifact exists on disk (`DESIGN.md` for GUI; the Step 4b stub for TUI/CLI) and, for GUI runs, that Step 6's validator ran, FIRST (TUI/CLI validator coverage is phase-2 — the on-disk check still applies). A narrated analysis with no file written is a FAILED run, never a partial success.**

## Scope — visual system only, NOT flows

`DESIGN.md` is the **visual system only** — brand, color, type, spacing,
elevation, shape, and component-token defaults. It is NOT flows, screens,
navigation, or interaction; those belong in `ui-flows.md` via
`interaction-flows`.

Its tokens are a **side-channel** to frontend styling and lint.

## Executor model

The agent running this skill is the executor: derive the palette from brand
voice, choose type and surface treatment, bind component tokens, and check
contrast. No external runtime or API key is required. Deterministic checks are
the bundled stdlib validator and, where available, `npx @google/design.md`.

## Procedure — modality-aware design-system generation

### Step 1 — Read the schema contract

Read **`references/design-md-schema.md`** before writing. It governs the 8
canonical sections, YAML token keys, and **WCAG-AA contrast**. Follow it and
confirm the young Google `DESIGN.md` keys/lint against the authoritative spec
at generation time.

### Step 2 — Read the governing PRINCIPLES.md

Read **`docs/loom/PRINCIPLES.md`** as the visual system's **governing
constraint**; every choice must be defensible against it.

**Read its `## Anchors` section.** Its **3-5 tone & manner adjectives** are the
**governing mood**: **inherit** them verbatim; **do not re-derive** or
contradict them. Read and honor the prose rather than parsing its formatting.

**Fallback — when there is no `## Anchors` tone & manner row:** derive mood
from `docs/loom/PURPOSE.md` plus Product Principles and **say so explicitly**
to the user. **Never silently invent** an inherited mood.

If `PRINCIPLES.md` is absent, surface that the design would be ungoverned,
recommend `loom-design:product-principles`, and proceed only on their say-so;
never invent a constitution.

### Step 3 — Detect / ask the modality

Detect or ask the modality (**GUI / TUI / CLI**), defaulting to GUI:

- **GUI** → go to Step 4a (full 8-section `DESIGN.md`).
- **TUI / CLI** → go to Step 4b (lightweight conventions stub + phase-2 note).

**Before deriving any color, type, component token, or convention not
derivable from `PRINCIPLES.md` or the seed, read
`references/knowledge-triage.md` and run its classification question FIRST.**
Classify and tag/route; do not guess. This applies to both branches.

The reference separates craft, domain-convention, and project-local facts.
Resolve craft/project-local facts through their prescribed sources. Never
invent a domain-semantic token: a SHAPING question must resolve before the
critic, while a DEFERRABLE one remains a tagged open question in `DESIGN.md`.

### Step 4a — GUI: emit the 8-section `DESIGN.md`

Emit a **`DESIGN.md`** following the schema contract from Step 1:

1. Confirm exact YAML token keys against the authoritative Google spec.
2. **Run the surface-treatment candidate round** below; the concept, shape
   tokens, and Elevation & Depth prose hang off the pick.
3. **Commit the visual concept** in **Overview / Brand**: one specific art
   direction, **3-5 generative visual principles**, and the chosen treatment.
4. Emit **all 8 `##` sections in order** (Overview / Brand → Colors →
   Typography → Layout → Elevation & Depth → Shapes → Components → Do's &
   Don'ts), each with rationale. YAML blocks exist only for **colors**,
   **typography**, **spacing**, **rounded**, and **components**; the other
   three stay prose-only. Derive every token from the concept and principles.
5. **Verify WCAG-AA contrast** for every pairing (body ≥ 4.5:1, large text ≥
   3:1); failure is a **blocker**.
6. Run the spec lint `npx @google/design.md` where available and resolve
   violations.

The eight sections have distinct jobs:

- **Overview / Brand** carries the committed concept, inherited mood, chosen
  surface treatment, and generative principles.
- **Colors** uses semantic palette tokens rather than scattered literals.
- **Typography** defines named levels and their family, size, weight,
  line-height, tracking, and relevant font features.
- **Layout** carries the `spacing` scale, including container, grid, gutter,
  and breakpoint choices.
- **Elevation & Depth** explains layering and shadows in prose; it has no YAML
  token group.
- **Shapes** carries `rounded` plus border conventions.
- **Components** maps global tokens into presentational defaults and states;
  behavioral state machines remain out of scope.
- **Do's & Don'ts** records concise usage guardrails in prose.

Use token references instead of duplicated literals where the schema permits.
Keep every rationale traceable to the concept and constitution; familiar
defaults are not self-justifying. Avoid generic generated-UI habits such as an
unreasoned ubiquitous font, cliché purple-blue gradients, one radius on every
component, or uncontrolled accent colors.

**Surface treatment — the candidate round (step 2 above, in full).** This is a
**choice over how depth is conveyed and how corners/borders are shaped** via
Shapes' `rounded`/border tokens and Elevation & Depth prose; never leave it an
unnamed default.

- **This round is downstream of the tone & manner anchor**: its adjectives
  **constrain which treatments are even proposable**.
- **Propose 3-5 surface-treatment candidates** from
  **`references/canon-design-surface.md`**, each with **fit/tension** notes.
  Use the canon as recall insurance; show only fitted candidates.
- **Name 1-2 considered-but-rejected candidates** and **surface them to the
  user with reasons**.
- **The user decides.** "**bespoke — no canon treatment fits**" is a legal
  **escape hatch**, requiring stricter rationale against the adjectives.
- Name and rationalize it in **Overview / Brand**: `Surface treatment: X —
  because <adjectives + constraint>`. **Do not add a 9th `##` section**.
- The pick **constrains the `## Elevation & Depth` prose and the `## Shapes`
  token block**. Elevation & Depth stays prose-only; derive Shapes' `rounded`
  and borders from the pick. Contradictory depth is a defect.
- **Anti-costume law:** a treatment **never overrides a PRINCIPLES value**.
- **The canon's WCAG risk flag is a BLOCKER, not a note.** Surface it and do
  not ship until resolved against WCAG-AA.

The canon is a completeness audit, not a menu to copy. Tone anchors narrow the
candidate set; the user sees only plausible fitted choices. A bespoke pick
loses the external anchor and therefore needs a stronger written explanation.
The selected treatment must agree across depth prose, radii, borders, and
component defaults. For example, a flat treatment cannot silently acquire a
deep shadow ramp. A treatment enriches the visual vocabulary but loses whenever
it conflicts with a product principle or accessibility requirement.

### Step 4b — TUI / CLI: lightweight conventions stub (phase-2)

Emit a **minimal lightweight conventions stub**: TUI terminal palette and
panel layout, or CLI output format, command/flag naming, and help/error style.
Add a **phase-2 note** deferring the full system, validator, and lint. Do not
fake an 8-section `DESIGN.md` for TUI/CLI.

The stub still records the governing principles and known conventions. A TUI
stub should cover terminal color limits, semantic roles, panel hierarchy,
spacing density, and fallback behavior. A CLI stub should cover plain-text and
machine-readable output, command/flag naming, help hierarchy, error wording,
and color/no-color behavior. Apply the same knowledge triage before assigning
domain semantics.

### Step 5 — Emit into the consumer project

Write under **`docs/loom/`**. `DESIGN.md` is **product-level — one per
product**, at that root rather than per feature.

### Step 6 — Validate after flows, then fix

Run the validator and fix every issue before declaring done:

```
argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/interface/validate_design_output.py", "<design-output-dir>"]
```

Pass the argv array directly to process execution; never through a shell. The validator checks file
presence and all 8 GUI headings; token derivation and contrast remain your
responsibility.

It checks the *whole* `docs/loom/<change-id>/`: `ui-flows.md` must exist and
`DESIGN.md` resolves most-specific-first (change folder, then parent). Stage 1
authors `DESIGN.md`, then suspends this step; after `interaction-flows`, the
router resumes Step 6 and fixes every issue. A DESIGN-only run correctly reports
missing flows and is not a completion verdict.

The validator proves structure only. Before completion, independently inspect
that the chosen palette actually meets AA, every token follows the committed
concept and `PRINCIPLES.md`, the lint completed where available, and the final
artifact—not merely an explanation—exists on disk.

## Boundary and handoff

Frontend styling consumes the tokens; `spec-expansion` receives behavioral
detail from `ui-flows.md`, not here. After `DESIGN.md`, hand off to
`interaction-flows` if needed, then `using-loom-design`. This skill writes the
visual system; it does not write frontend code, flows, or behavioral specs.
